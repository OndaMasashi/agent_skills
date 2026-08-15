#!/usr/bin/env python3
"""日本語の読者向け長文を実測して、文体の癖を機械的に検出する。

標準ライブラリのみ。Windows / macOS / Linux で動作。

  python prose_check.py draft.md
  python prose_check.py "docs/note/*.md"          # glob 可（クォート推奨）
  python prose_check.py *.md --jargon 玉,刺さる,閉じる  # 内輪語を追加指定
  python prose_check.py *.md --detail             # 該当行を全部出す
  python prose_check.py *.md --json               # 機械可読出力

判定は「良い文章か」ではなく「書き手の癖が出ていないか」。
数値は目安であって合否ではない。WARN が出た箇所を人間が読んで決める。
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------- 目標値
# 実測に基づく目安（note 連載 9 話・5.1 万字の改稿前後から算出）
TARGETS = {
    "avg_len": (26.0, 34.0),  # 1 文の平均字数。下回ると断定の連打で冷たい
    "short_ratio": (0.0, 0.52),  # 25 字以下の文の割合
    "plain_end_ratio": (0.0, 0.82),  # 文末が です/ます 系の割合
    "conj_ratio": (0.09, 0.20),  # 文頭に接続詞がある文の割合
}

# ------------------------------------------------------- 癖パターン定義
# (キー, 表示名, 正規表現, 補足)
TIC_PATTERNS = [
    ("dash", "ダッシュ（——）", r"——", "日本語の書き言葉では不自然。読点か句点分割か括弧に置換する"),
    (
        "hedge",
        "語尾のぼかし",
        r"(たぶん|おそらく|かなり|だいぶ|そこそこ|ある程度|と思っています|という形です|ということです|かと思います|のような気がします)",
        "実測値を出している本文の説得力を自分で削る。1 ファイル 2 個までを目安に",
    ),
    (
        "reader_proxy",
        "読者の心を代弁する枕",
        r"(と思われたかもしれません|と感じたかもしれません|当然の疑問|もっともな疑問|疑問に思われた|お思いでしょう|でしょうか。しかし)",
        "★AI 生成文の最大の指紋。全部削っても情報は 1 文字も減らない",
    ),
    (
        "empty_bridge",
        "中身のない繋ぎ",
        r"(結果を先に(書き|言い)ます|理屈はこうです|ここが本題です|ここからが本題|振り返ります|一文にまとめます|整理します。|結論から(書き|言い)ます)",
        "削っても意味が変わらない。削る",
    ),
    (
        "nodesu",
        "「〜のは、〜からです」構文",
        r"のは、[^。]{2,40}からです",
        "1 ファイル 3 回まで。主語を先に立てて言い切ると読む速度が上がる",
    ),
    (
        "abstract",
        "抽象名詞への逃げ",
        r"(形|線|材料|部分|構造|性質|要素|側面)(で|が|を|に|は|の)",
        "初出で定義しないまま繰り返しやすい。定義済みのキーワードなら無視してよい",
    ),
    (
        "double_neg",
        "否定の並列",
        r"でもなく、[^。]*でもありません",
        "2 文に分ける",
    ),
    (
        "num_space",
        "数字前後の半角スペース",
        r"[0-9][ 　]+(年|月|日|万|億|円|個|回|話|章|人|件|%|パーセント|通り|種類)",
        "「2026 年」「20 万円」は詰めるのが正",
    ),
    (
        "jotai",
        "敬体に常体が混入",
        r"(?<!」)(?<![「『])[^。！？「」]{3,}(だ|である|だろう|であろう|なのだ)。",
        "文体が波打つ。ただし短い常体をリズムで挟むのは技法。会話・引用は誤検知",
    ),
]

# 件数がこの数を超えたときだけ報告する（少数の出現は癖ではない）
TIC_MIN = {"abstract": 8, "jotai": 6, "nodesu": 4}

# 文頭接続詞（起伏をつける語）
CONJ = (
    "しかし|ところが|だから|そして|つまり|ただ|ただし|また|さらに|なぜなら|それでも|一方|"
    "もっとも|とはいえ|むしろ|そもそも|ならば|もし|要するに|逆に|実際|なお|ですから|そのうえ|"
    "そこで|やがて|ちなみに|加えて|とはいうものの|それどころか"
)

PLAIN_END = r"(です|ます|ました|ません|でした|ですね)。$"

# 本文とみなさない行（見出し・表・箇条書き・引用・コードフェンス）
SKIP_LINE = re.compile(r"^\s*(#|\||-\s|\*\s|\d+\.\s|>|```|!\[)")


def load_sentences(path: Path, exclude: str | None):
    """本文の文リストと (文, 行番号) を返す。"""
    text = path.read_text(encoding="utf-8")
    ex = re.compile(exclude) if exclude else None
    sents, located, in_fence = [], [], False
    for i, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line.strip() or SKIP_LINE.match(line):
            continue
        if ex and ex.search(line):
            continue
        for s in re.split(r"(?<=。)", line):
            s = s.strip().replace("**", "")
            if s.endswith("。"):
                sents.append(s)
                located.append((s, i))
    return text, sents, located


def analyse(path: Path, jargon: list[str], exclude: str | None):
    text, sents, located = load_sentences(path, exclude)
    if not sents:
        return None

    lens = [len(s) for s in sents]
    n = len(sents)
    plain = sum(1 for s in sents if re.search(PLAIN_END, s))
    conj = sum(1 for s in sents if re.match(rf"({CONJ})", s))

    metrics = {
        "sentences": n,
        "avg_len": sum(lens) / n,
        "short_ratio": sum(1 for x in lens if x <= 25) / n,
        "plain_end_ratio": plain / n,
        "conj_ratio": conj / n,
    }

    # 同一接続詞の偏り: 6 回以上、かつ接続詞つき文の 3 割超を占めるものだけ報告
    conj_counts = Counter(
        m.group(1) for s in sents if (m := re.match(rf"({CONJ})", s))
    )
    conj_heavy = {
        k: v for k, v in conj_counts.items() if v >= 6 and conj and v / conj > 0.30
    }

    # 癖パターン
    tics = {}
    for key, label, pat, hint in TIC_PATTERNS:
        hits = [(ln, s) for s, ln in located if re.search(pat, s)]
        if len(hits) >= TIC_MIN.get(key, 1):
            tics[key] = {"label": label, "hint": hint, "count": len(hits), "hits": hits}

    # 内輪語
    jargon_hits = {}
    for w in jargon:
        hits = [(ln, s) for s, ln in located if w in s]
        if hits:
            jargon_hits[w] = hits

    # 太字密度（節あたり）
    sections = max(1, len(re.findall(r"^##\s", text, re.M)))
    bold = len(re.findall(r"\*\*[^*\n]+\*\*", text))
    metrics["bold_per_section"] = bold / sections

    # 逐語の重複（20 字以上の同一文が 2 回以上）
    dup = {s: c for s, c in Counter(sents).items() if c >= 2 and len(s) >= 20}

    return {
        "file": path.name,
        "metrics": metrics,
        "conj_heavy": conj_heavy,
        "tics": tics,
        "jargon": jargon_hits,
        "dup": dup,
    }


def verdict(key, value):
    lo, hi = TARGETS[key]
    return "OK " if lo <= value <= hi else "WARN"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="対象ファイル（glob 可）")
    ap.add_argument("--jargon", default="", help="内輪語をカンマ区切りで（例: 玉,刺さる,閉じる,乖離）")
    ap.add_argument("--exclude", default=None, help="除外する行の正規表現（免責文など）")
    ap.add_argument("--detail", action="store_true", help="該当行を全件表示")
    ap.add_argument("--json", action="store_true", help="JSON で出力")
    a = ap.parse_args()

    files = sorted({Path(p) for pat in a.paths for p in glob.glob(pat)})
    files = [f for f in files if f.is_file()]
    if not files:
        print("対象ファイルが見つかりません", file=sys.stderr)
        return 1

    jargon = [w.strip() for w in a.jargon.split(",") if w.strip()]
    results = [r for f in files if (r := analyse(f, jargon, a.exclude))]

    if a.json:
        for r in results:
            r["tics"] = {k: {kk: vv for kk, vv in v.items() if kk != "hits"} for k, v in r["tics"].items()}
            r["jargon"] = {k: len(v) for k, v in r["jargon"].items()}
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    print(
        "\n※ 目安値は「敬体（です・ます）で書かれた読者向けの本文」を前提にしている。"
        "\n   技術文書・仕様書・箇条書き主体の md に当てても意味のある数値は出ない。\n"
    )
    print("■ 文体の骨格（数値は目安。WARN は読んで判断する）\n")
    print(f"{'file':30} {'文数':>5} {'平均':>7} {'25字以下':>9} {'平板文末':>9} {'接続詞':>8}")
    print("-" * 76)
    for r in results:
        m = r["metrics"]
        print(
            f"{r['file'][:30]:30} {m['sentences']:5} "
            f"{m['avg_len']:6.1f}字 {m['short_ratio']*100:7.0f}% {m['plain_end_ratio']*100:7.0f}% {m['conj_ratio']*100:6.0f}%"
        )
    print()
    for r in results:
        m = r["metrics"]
        flags = [f"{k}={verdict(k, m[k])}" for k in TARGETS if verdict(k, m[k]) == "WARN"]
        if flags:
            print(f"  WARN {r['file']}: {' / '.join(flags)}")
    print(f"\n  目安: 平均 {TARGETS['avg_len'][0]:.0f}〜{TARGETS['avg_len'][1]:.0f}字 / "
          f"25字以下 ≤{TARGETS['short_ratio'][1]*100:.0f}% / "
          f"平板文末 ≤{TARGETS['plain_end_ratio'][1]*100:.0f}% / "
          f"接続詞 {TARGETS['conj_ratio'][0]*100:.0f}〜{TARGETS['conj_ratio'][1]*100:.0f}%")

    print("\n■ 癖の検出\n")
    any_tic = False
    for r in results:
        lines = []
        for v in r["tics"].values():
            lines.append((v["count"], v["label"], v["hint"], v["hits"]))
        for w, hits in r["jargon"].items():
            lines.append((len(hits), f"内輪語「{w}」", "読者の文脈では別の意味に取られうる", hits))
        if r["conj_heavy"]:
            for k, v in r["conj_heavy"].items():
                lines.append((v, f"接続詞「{k}」の偏り", "この語だけで接続詞の 3 割超。半分は別の語に振るか削る", []))
        if r["dup"]:
            for s, c in r["dup"].items():
                lines.append((c, "逐語の重複", f"同一文が {c} 回: {s[:40]}…", []))
        if not lines:
            continue
        any_tic = True
        print(f"  ── {r['file']}")
        for cnt, label, hint, hits in sorted(lines, reverse=True):
            print(f"     {cnt:3}  {label}  … {hint}")
            if a.detail and hits:
                for ln, s in hits[:20]:
                    print(f"          L{ln}: {s[:60]}")
        print()
    if not any_tic:
        print("  検出なし\n")

    print("■ 自動では出ない項目（人間が読む）\n")
    for s in [
        "見出しがつなぎ言葉になっていないか（見出しは読者の頭にある問いへの答え）",
        "話をまたぐ一貫性（予告の話数・同一指標の呼称・目次と実タイトル）",
        "感情が「あった → それでも仕組みが勝った」の 2 段で置かれているか",
        "具体的な数字・状況を抽象化して薄めていないか（消すのは内部記号と流用可能な設定値だけ）",
    ]:
        print(f"  - {s}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
