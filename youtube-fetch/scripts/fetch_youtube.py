# /// script
# requires-python = ">=3.10"
# dependencies = ["yt-dlp", "youtube-transcript-api"]
# ///
"""YouTube 動画の題名・公開日・概要欄・チャプター・時刻つき字幕を 1 つの Markdown に書き出す。

使い方:
    uv run --script fetch_youtube.py <URL または動画ID> [--out DIR] [--via auto|yt-dlp|transcript-api]

経路:
    1. yt-dlp          … 動画情報と字幕をまとめて取る（主経路）
    2. transcript-api  … yt-dlp が失敗したときだけ字幕を取る（題名・投稿者は oEmbed から。概要欄は取れない）

終了コード: 0 = 字幕まで取れた / 2 = 動画情報は取れたが字幕が無い / 1 = 何も取れない
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
PREF_LANGS = ["ja", "en"]
CJK_LANGS = ("ja", "zh", "ko")

ID_PATTERNS = [
    r"(?:v=|/shorts/|/live/|/embed/|youtu\.be/)([A-Za-z0-9_-]{11})",
    r"^([A-Za-z0-9_-]{11})$",
]


def video_id_of(url: str) -> str:
    text = url.strip()
    for pat in ID_PATTERNS:
        m = re.search(pat, text)
        if m:
            return m.group(1)
    raise SystemExit(f"動画IDを読み取れません: {url}")


def watch_url(vid: str) -> str:
    return f"https://www.youtube.com/watch?v={vid}"


def fmt_time(sec: float, long: bool) -> str:
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if long else f"{m:02d}:{s:02d}"


def lang_matches(key: str, lang: str) -> bool:
    return key == lang or key.startswith(lang + "-")


# ---------- 経路 1: yt-dlp ----------

def pick_track(info: dict) -> tuple[str, bool] | None:
    """(字幕の言語キー, 自動字幕か) を返す。話されている言語を翻訳より優先する。"""
    manual = {k: v for k, v in (info.get("subtitles") or {}).items() if k != "live_chat"}
    auto = info.get("automatic_captions") or {}
    # 自動字幕のキーには誤判定の en-US-orig と正しい ja-orig が同居することがある（実測）。
    # 「-orig」の有無だけでは話されている言語が決まらないので、info["language"] で選ぶ
    orig = info.get("language")
    auto_orig = [k for k in auto if k.endswith("-orig")]
    auto_translated = [k for k in auto if not k.endswith("-orig")]

    def first(keys, langs):
        for lang in langs:
            for k in keys:
                if lang_matches(k.removesuffix("-orig"), lang):
                    return k
        return None

    if orig:
        if k := first(manual, [orig]):
            return k, False
        if k := first(auto_orig, [orig]):
            return k, True
    if k := first(manual, PREF_LANGS):
        return k, False
    if manual:
        return next(iter(manual)), False
    if k := first(auto_orig, PREF_LANGS):
        return k, True
    if auto_orig:
        return auto_orig[0], True
    if k := first(auto_translated, PREF_LANGS):
        return k, True
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


def via_ytdlp(vid: str) -> dict:
    from yt_dlp import YoutubeDL

    opts = {"skip_download": True, "quiet": True, "no_warnings": True, "noplaylist": True}
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(watch_url(vid), download=False)
        meta = {
            "title": info.get("title"),
            "channel": info.get("channel") or info.get("uploader"),
            "channel_url": info.get("channel_url"),
            "upload_date": info.get("upload_date"),
            "duration": info.get("duration"),
            "language": info.get("language"),
            "description": info.get("description"),
            "chapters": info.get("chapters") or [],
        }
        track = pick_track(info)
        if not track:
            return {"meta": meta, "lines": None, "track": None}
        key, is_auto = track
        formats = (info["automatic_captions"] if is_auto else info["subtitles"])[key]
        fmt = next((f for f in formats if f.get("ext") == "json3"), None)
        if not fmt:
            raise RuntimeError(f"字幕 {key} に json3 形式がありません")
        raw = ydl.urlopen(fmt["url"]).read().decode("utf-8")
        lines = parse_json3(raw) if raw.strip() else []
        if not lines:
            raise RuntimeError(f"字幕 {key} の中身が空でした")
        return {"meta": meta, "lines": lines, "track": (key.removesuffix("-orig"), is_auto)}


# ---------- 経路 2: youtube-transcript-api ----------

def oembed(vid: str) -> dict:
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(watch_url(vid), safe="")
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            d = json.load(r)
        return {"title": d.get("title"), "channel": d.get("author_name"), "channel_url": d.get("author_url")}
    except Exception:
        return {}


def via_transcript_api(vid: str) -> dict:
    from youtube_transcript_api import YouTubeTranscriptApi

    meta = {"chapters": [], **oembed(vid)}
    tlist = list(YouTubeTranscriptApi().list(vid))
    if not tlist:
        return {"meta": meta, "lines": None, "track": None}

    def first(generated: bool):
        for lang in PREF_LANGS:
            for t in tlist:
                if t.is_generated == generated and lang_matches(t.language_code, lang):
                    return t
        return None

    t = first(False) or first(True) or tlist[0]
    lines = [(s.start, s.text.replace("\n", " ").strip()) for s in t.fetch() if s.text.strip()]
    return {"meta": meta, "lines": lines, "track": (t.language_code, t.is_generated)}


# ---------- 経路の切り替え ----------

def fetch_video(vid: str, via: str) -> tuple[dict | None, str | None, list[str]]:
    """(取得結果, 経路名, 失敗した経路のエラー) を返す。何も取れなければ取得結果は None。"""
    res, route, errors = None, None, []
    if via in ("auto", "yt-dlp"):
        try:
            res, route = via_ytdlp(vid), "yt-dlp"
        except Exception as e:  # YouTube 側の変更で壊れることがあるので、予備の経路へ回す
            errors.append(f"yt-dlp: {e}")
    if (res is None or res["lines"] is None) and via in ("auto", "transcript-api"):
        try:
            alt = via_transcript_api(vid)
        except Exception as e:
            errors.append(f"transcript-api: {e}")
        else:
            if res is None:
                res, route = alt, "transcript-api"
            elif alt["lines"]:  # 字幕だけ差し替え、動画情報は yt-dlp のものを残す
                alt["meta"] = res["meta"]
                res, route = alt, "yt-dlp + transcript-api"
    return res, route, errors


# ---------- 書き出し ----------

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
    out = [f"# {meta.get('title') or vid}", "", f"- URL: {watch_url(vid)}"]
    if meta.get("channel"):
        ch = meta["channel"] + (f"（{meta['channel_url']}）" if meta.get("channel_url") else "")
        out.append(f"- チャンネル: {ch}")
    if meta.get("upload_date"):
        d = meta["upload_date"]
        out.append(f"- 公開日: {d[:4]}-{d[4:6]}-{d[6:]}")
    if meta.get("duration"):
        out.append(f"- 長さ: {fmt_time(meta['duration'], True)}")
    if track:
        kind = "自動生成（誤変換あり）" if track[1] else "手動"
        out.append(f"- 字幕: {track[0]}・{kind}")
    else:
        out.append("- 字幕: なし")
    out.append(f"- 取得経路: {route}（{dt.date.today().isoformat()} 取得）")
    out.append("")

    out += ["## 概要欄", ""]
    if meta.get("description") is None:
        out.append("（この経路では取得できない）")
    else:
        out += ["```text", meta["description"].rstrip(), "```"]
    out.append("")

    chapters = meta.get("chapters") or []
    if chapters:
        out += ["## チャプター", ""]
        out += [f"- {fmt_time(c['start_time'], long)} {c['title']}" for c in chapters]
        out.append("")

    if lines:
        joiner = "" if track and track[0].startswith(CJK_LANGS) else " "
        out += ["## 字幕", ""]
        out += subtitle_paragraphs(lines, chapters, joiner, long)
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

    n = len(res["lines"] or [])
    print(f"書き出し: {path.resolve()}")
    print(f"題名: {res['meta'].get('title')}")
    print(f"経路: {route} / 字幕: {res['track'] or 'なし'} / {n} 行")
    return 0 if n else 2


if __name__ == "__main__":
    sys.exit(main())
