# /// script
# requires-python = ">=3.10"
# dependencies = ["yt-dlp", "youtube-transcript-api"]
# ///
"""YouTube 動画の題名・公開日・概要欄・チャプター・時刻つき字幕を 1 つの Markdown に書き出す。

使い方:
    uv run --script fetch_youtube.py <URL または動画ID> [--out DIR] [--via auto|yt-dlp|transcript-api]

経路:
    1. yt-dlp          … 動画情報と字幕をまとめて取る（主経路）
    2. transcript-api  … yt-dlp で字幕が取れなかったときだけ字幕を取る
                         （yt-dlp が丸ごと失敗したときは、題名・投稿者を oEmbed から取る。概要欄は取れない）

終了コード:
    0 = 字幕まで取れた / 1 = 何も取れない / 2 = 引数の誤り
    3 = 動画情報は取れたが、この動画には字幕が無い
    4 = 動画情報は取れたが、字幕を取得できなかった（字幕が有るかどうかは確かめられていない）
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BLOCK_SEC = 30  # 字幕をこの秒数ごとに 1 段落へまとめる
TIMEOUT_SEC = 30
PREF_LANGS = ["ja", "en"]
NO_SPACE_LANGS = ("ja", "zh")  # 単語の間に空白を入れない言語（韓国語は空白で区切るので入れない）
JST = dt.timezone(dt.timedelta(hours=9))
EXIT_CODES = {"ok": 0, "none": 3, "failed": 4}
KIND_LABELS = {"manual": "手動", "auto": "自動生成（誤変換あり）"}
# 動画の形式が選べないことだけを言う yt-dlp の警告（動画が取れなかった理由には数えない）
FORMAT_WARNINGS = r"JavaScript runtime|No video formats|Requested format"
# ログインしないと見られない動画。字幕の一覧も塞がれるので、字幕が無いとは言い切れない
NEEDS_LOGIN = ("needs_auth", "subscriber_only", "premium_only")

ID_PATTERNS = [
    r"(?:v=|/shorts/|/live/|/embed/|youtu\.be/)([A-Za-z0-9_-]{11})",
    r"^([A-Za-z0-9_-]{11})$",
]


def video_id_of(url: str) -> str | None:
    text = url.strip()
    for pat in ID_PATTERNS:
        m = re.search(pat, text)
        if m:
            return m.group(1)
    return None


def watch_url(vid: str) -> str:
    return f"https://www.youtube.com/watch?v={vid}"


def fmt_time(sec: float, long: bool) -> str:
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if long else f"{m:02d}:{s:02d}"


def lang_matches(key: str, lang: str) -> bool:
    return key == lang or key.startswith(lang + "-")


def one_line(text: object, limit: int | None = 200) -> str:
    """改行と制御文字を空白 1 つに畳む。第三者が決めた文字列を Markdown の 1 行に入れるときに通す
    （題名に改行を仕込んで見出しを偽造する、といったことをさせない）。"""
    text = " ".join(re.sub(r"[\x00-\x1f\x7f]", " ", str(text)).split())
    return text if limit is None or len(text) <= limit else text[:limit] + "…"


# 結果の形（どの経路も同じ）:
#   {"meta": 動画情報, "lines": [(秒, 文)] または None, "track": (言語, 種類) または None,
#    "status": "ok" | "none" | "failed", "note": 字幕が取れなかった理由}
#   種類は "manual" / "auto" / "translated"（自動翻訳）
def _result(
    meta: dict,
    status: str,
    *,
    note: str = "",
    lines: list[tuple[float, str]] | None = None,
    track: tuple[str, str] | None = None,
) -> dict:
    return {"meta": meta, "lines": lines, "track": track, "status": status, "note": note}


# ---------- 経路 1: yt-dlp ----------

class _WarningLog:
    """yt-dlp の警告を捨てずに集める。「字幕が無い」と「取れなかった」を見分けるのに使う。"""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def debug(self, msg: str) -> None:
        # PO token（YouTube が求める追加の認証）が無くて字幕を捨てたという知らせは、標準の接続方式では
        # 警告ではなく詳細ログにしか出ない（yt-dlp の _report_pot_subtitles_skipped）。詳細ログから拾う
        if re.search(r"PO token", msg, re.I) and re.search(r"subtitle", msg, re.I):
            self.messages.append(msg)

    def info(self, msg: str) -> None:
        pass

    def warning(self, msg: str) -> None:
        self.messages.append(msg)

    error = warning


def pick_track(info: dict) -> tuple[str, str] | None:
    """(字幕の言語キー, 種類) を返す。話されている言語を翻訳より優先する。"""
    manual = {k: v for k, v in (info.get("subtitles") or {}).items() if k != "live_chat"}
    auto = info.get("automatic_captions") or {}
    # 自動字幕のキーには誤判定の en-US-orig と正しい ja-orig が同居することがある（実測）。
    # 「-orig」の有無だけでは話されている言語が決まらないので、info["language"] で選ぶ。
    # language は "en-US" のように地域つきで来ることがあるので、言語の部分だけを使う
    orig = (info.get("language") or "").split("-")[0] or None
    auto_orig = [k for k in auto if k.endswith("-orig")]
    auto_translated = [k for k in auto if not k.endswith("-orig")]
    if not orig and len(auto_orig) == 1:
        # language が取れない（動画の形式が選べないときに起きる）が、元の言語の自動字幕が 1 本だけならその言語とみなす
        orig = auto_orig[0].removesuffix("-orig").split("-")[0]

    def first(keys, langs):
        for lang in langs:
            for k in keys:
                if lang_matches(k.removesuffix("-orig"), lang):
                    return k
        return None

    if orig:
        if k := first(manual, [orig]):
            return k, "manual"
        if k := first(auto_orig, [orig]):
            return k, "auto"
    if k := first(manual, PREF_LANGS):
        return k, "manual"
    if manual:
        return next(iter(manual)), "manual"
    if k := first(auto_orig, PREF_LANGS):
        return k, "auto"
    if auto_orig:
        return auto_orig[0], "auto"
    if k := first(auto_translated, PREF_LANGS):
        return k, "translated"
    return None


def parse_json3(raw: str) -> list[tuple[float, str]]:
    lines = []
    for ev in json.loads(raw).get("events", []):
        if ev.get("aAppend") or "segs" not in ev:
            continue
        text = "".join(s.get("utf8", "") for s in ev["segs"]).replace("\n", " ").strip()
        if text:
            lines.append((ev.get("tStartMs", 0) / 1000, text))
    return lines


def publish_date(info: dict) -> tuple[str, str] | None:
    """(公開日, 基準) を返す。時刻が分かれば日本時間に直す。
    時刻が無いときの upload_date は、どの時間帯の日付かが決まっていない（yt-dlp は UTC か太平洋時間の日付を入れる）。"""
    ts = info.get("release_timestamp") or info.get("timestamp")
    if ts:
        return dt.datetime.fromtimestamp(ts, JST).date().isoformat(), "日本時間"
    d = info.get("upload_date")
    return (f"{d[:4]}-{d[4:6]}-{d[6:]}", "YouTube の日付。日本時間とは 1 日ずれることがある") if d else None


def _download_subtitle(ydl, formats: list[dict]) -> list[tuple[float, str]]:
    """字幕を json3 形式で読み、(秒, 文) の並びにする。読めなければ例外を投げる。"""
    fmt = next((f for f in formats if f.get("ext") == "json3"), None)
    if not fmt:
        raise RuntimeError("json3 形式がありません")
    with ydl.urlopen(fmt["url"]) as r:
        raw = r.read().decode("utf-8")
    lines = parse_json3(raw) if raw.strip() else []
    if not lines:
        raise RuntimeError("中身が空でした")
    return lines


def via_ytdlp(vid: str) -> dict:
    from yt_dlp import YoutubeDL

    log = _WarningLog()
    opts = {
        "skip_download": True,
        "quiet": True,
        "noplaylist": True,
        "logger": log,
        "verbose": True,  # 詳細ログを _WarningLog に流す（PO token の知らせを拾うため。画面には出ない）
        "socket_timeout": TIMEOUT_SEC,
        # 動画の形式が 1 つも選べなくても（JS 実行環境が無いときなど）、動画情報と字幕は取る
        "ignore_no_formats_error": True,
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(watch_url(vid), download=False)
        if not info.get("formats") and not (info.get("duration") or info.get("upload_date")):
            # ignore_no_formats_error を付けると、動画が存在しない・非公開のときも中身の空の情報が返る。
            # 形式だけでなく長さも公開日も無ければ、動画そのものが取れていない
            reason = next(
                (m for m in log.messages if not re.search(FORMAT_WARNINGS, m)), "動画情報を取得できませんでした"
            )
            raise RuntimeError(one_line(reason))
        meta = {
            "title": info.get("title"),
            "channel": info.get("channel") or info.get("uploader"),
            "channel_url": info.get("channel_url"),
            "published": publish_date(info),
            "duration": info.get("duration"),
            "language": info.get("language"),
            "description": info.get("description"),
            "chapters": info.get("chapters") or [],
        }
        track = pick_track(info)
        if not track:
            # 字幕の一覧が塞がれていた印（PO token 不足・年齢確認・ログインが要る等）があれば「取れなかった」。
            # 印が 1 つも無いときだけ「この動画には字幕が無い」と言い切る
            blocker = next((m for m in log.messages if not re.search(FORMAT_WARNINGS, m)), None)
            if blocker is None and info.get("availability") in NEEDS_LOGIN:
                blocker = f"視聴にログインが要る動画（availability={info['availability']}）"
            if blocker:
                return _result(meta, "failed", note=one_line(blocker))
            return _result(meta, "none", note="yt-dlp が字幕を 1 本も見つけなかった")

        key, kind = track
        formats = (info["subtitles"] if kind == "manual" else info["automatic_captions"])[key]
        try:
            lines = _download_subtitle(ydl, formats)
        except Exception as e:  # 字幕が取れなくても、取れた動画情報は捨てない
            return _result(meta, "failed", note=one_line(f"字幕 {key}: {e}"))
        return _result(meta, "ok", lines=lines, track=(key.removesuffix("-orig"), kind))


# ---------- 経路 2: youtube-transcript-api ----------

def oembed(vid: str) -> dict:
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(watch_url(vid), safe="")
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SEC) as r:
            d = json.load(r)
        return {"title": d.get("title"), "channel": d.get("author_name"), "channel_url": d.get("author_url")}
    except Exception:
        return {}


def _timeout_session():
    """youtube-transcript-api は既定で待ち時間の上限なしに通信するので、上限つきの通信部品を渡す。"""
    import requests

    class _Session(requests.Session):
        def request(self, *args, **kwargs):
            kwargs.setdefault("timeout", TIMEOUT_SEC)
            return super().request(*args, **kwargs)

    return _Session()


def via_transcript_api(vid: str) -> dict:
    """字幕が無いと分かったときは status "none"、一覧にあるのに中身が取れないときは "failed" を返す。
    字幕の一覧すら取れないときは例外のまま上へ投げる。"""
    from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled, YouTubeTranscriptApi

    meta = {"chapters": [], **oembed(vid)}
    try:
        tlist = list(YouTubeTranscriptApi(http_client=_timeout_session()).list(vid))
    except (TranscriptsDisabled, NoTranscriptFound):
        tlist = []
    if not tlist:
        return _result(meta, "none", note="transcript-api でも字幕が無かった")

    def first(generated: bool):
        for lang in PREF_LANGS:
            for t in tlist:
                if t.is_generated == generated and lang_matches(t.language_code, lang):
                    return t
        return None

    t = first(False) or first(True) or tlist[0]
    try:
        lines = [(s.start, s.text.replace("\n", " ").strip()) for s in t.fetch() if s.text.strip()]
    except Exception as e:  # 字幕は一覧にあったので、「無い」ではなく「取れなかった」
        return _result(meta, "failed", note=one_line(f"字幕 {t.language_code}: {e}"))
    if not lines:
        return _result(meta, "failed", note=f"字幕 {t.language_code} の中身が空でした")
    kind = "auto" if t.is_generated else "manual"
    return _result(meta, "ok", lines=lines, track=(t.language_code, kind))


# ---------- 経路の切り替え ----------

def fetch_video(vid: str, via: str) -> tuple[dict | None, str | None, list[str]]:
    """(取得結果, 経路名, 失敗した経路のエラー) を返す。何も取れなければ取得結果は None。"""
    res, route, errors = None, None, []
    if via in ("auto", "yt-dlp"):
        try:
            res, route = via_ytdlp(vid), "yt-dlp"
        except Exception as e:  # YouTube 側の変更で壊れることがあるので、予備の経路へ回す
            errors.append(f"yt-dlp: {one_line(e)}")
        else:
            if res["status"] == "failed":
                errors.append(f"yt-dlp: {res['note']}")
    if (res is None or res["status"] != "ok") and via in ("auto", "transcript-api"):
        try:
            alt = via_transcript_api(vid)
        except Exception as e:  # 予備の経路は字幕の一覧すら取れなかった。yt-dlp の判定をそのまま使う
            errors.append(f"transcript-api: {one_line(e)}")
        else:
            if alt["status"] == "failed":
                errors.append(f"transcript-api: {alt['note']}")
            if res is None:
                res, route = alt, "transcript-api"
            elif alt["status"] == "ok":  # 字幕だけ差し替え、動画情報は yt-dlp のものを残す
                res, route = {**alt, "meta": res["meta"]}, "yt-dlp + transcript-api"
            elif alt["status"] == "failed" and res["status"] == "none":
                # 予備の経路が字幕を一覧に見つけた（中身は取れなかった）。字幕は有るので「無い」とは言わない
                res = {**res, "status": "failed", "note": alt["note"]}
            # 予備の経路の「無い」では書き換えない。yt-dlp が「取れなかった」なら、
            # 予備の経路の「無い」も同じ理由で塞がれた結果かもしれない
    return res, route, errors


# ---------- 書き出し ----------

def subtitle_label(res: dict) -> str:
    if res["status"] == "none":
        return "なし（この動画には字幕が無い）"
    if res["status"] == "failed":
        return f"取得できなかった（{res['note']}）"
    lang, kind = res["track"]
    if kind == "translated":
        orig = res["meta"].get("language")
        src = f"{orig} から " if orig else ""
        return f"{lang}・自動翻訳（{src}機械翻訳したもので、話された言葉そのものではない）"
    return f"{lang}・{KIND_LABELS[kind]}"


def fenced(text: str) -> list[str]:
    """本文に出てくる最長のバッククォートの連続より長い囲みで包む（本文が囲みを閉じられないように）。"""
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return [fence + "text", text, fence]


def subtitle_paragraphs(
    lines: list[tuple[float, str]], chapters: list[dict], joiner: str, long: bool
) -> list[str]:
    """字幕を BLOCK_SEC 秒ごとの段落にまとめ、チャプターの境目に見出しを挟む。"""
    out: list[str] = []
    starts = [c["start_time"] for c in chapters]
    ci, block, block_start = 0, [], None

    def flush():
        if block:
            out.append(f"[{fmt_time(block_start, long)}] " + joiner.join(block))
            out.append("")

    for t, text in lines:
        new_chapter = ci < len(starts) and t >= starts[ci]
        if new_chapter or block_start is None or t - block_start >= BLOCK_SEC:
            flush()
            block, block_start = [], t
            while ci < len(starts) and t >= starts[ci]:
                out += [f"### {fmt_time(starts[ci], long)} {chapters[ci]['title']}", ""]
                ci += 1
        block.append(text)
    flush()
    return out


def build_markdown(vid: str, res: dict, route: str) -> str:
    meta, lines, track = res["meta"], res["lines"], res["track"]
    long = (meta.get("duration") or (lines[-1][0] if lines else 0)) >= 3600
    # 題名・チャンネル名・チャプター名は投稿者が決める文字列なので、改行を畳んでから 1 行に入れる
    # （概要欄は囲みの中に入れるので改行を残す）
    out = [f"# {one_line(meta.get('title') or vid, None)}", "", f"- URL: {watch_url(vid)}"]
    if meta.get("channel"):
        ch = meta["channel"] + (f"（{meta['channel_url']}）" if meta.get("channel_url") else "")
        out.append(f"- チャンネル: {one_line(ch, None)}")
    if meta.get("published"):
        date, basis = meta["published"]
        out.append(f"- 公開日: {date}（{basis}）")
    if meta.get("duration"):
        out.append(f"- 長さ: {fmt_time(meta['duration'], True)}")
    out.append(f"- 字幕: {subtitle_label(res)}")
    out.append(f"- 取得経路: {route}（{dt.date.today().isoformat()} 取得）")
    out.append("")

    out += ["## 概要欄", ""]
    if meta.get("description") is None:
        out.append("（この経路では取得できない）")
    else:
        out += fenced(meta["description"].rstrip())
    out.append("")

    chapters = [{**c, "title": one_line(c["title"], None)} for c in meta.get("chapters") or []]
    if chapters:
        out += ["## チャプター", ""]
        out += [f"- {fmt_time(c['start_time'], long)} {c['title']}" for c in chapters]
        out.append("")

    if lines:
        no_space = any(lang_matches(track[0], lang) for lang in NO_SPACE_LANGS)
        out += ["## 字幕", ""]
        out += subtitle_paragraphs(lines, chapters, "" if no_space else " ", long)
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("url")
    ap.add_argument("--out", default=".", help="書き出し先フォルダ（既定: カレント）")
    ap.add_argument("--via", choices=["auto", "yt-dlp", "transcript-api"], default="auto")
    args = ap.parse_args()

    vid = video_id_of(args.url)
    if not vid:
        ap.error(f"動画IDを読み取れません: {args.url}")  # 引数の誤りとして終了コード 2 で止まる
    res, route, errors = fetch_video(vid, args.via)
    for e in errors:
        print(f"[経路の失敗] {e}", file=sys.stderr)
    if res is None:
        print("何も取得できませんでした（非公開・年齢制限・メンバー限定・YouTube 側の変更の可能性）", file=sys.stderr)
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{vid}.md"
    path.write_text(build_markdown(vid, res, route), encoding="utf-8")

    print(f"書き出し: {path.resolve()}")
    print(f"題名: {one_line(res['meta'].get('title'), None)}")
    print(f"経路: {route} / 字幕: {subtitle_label(res)} / {len(res['lines'] or [])} 行")
    return EXIT_CODES[res["status"]]


if __name__ == "__main__":
    sys.exit(main())
