#!/usr/bin/env python3
"""日本語の読者向け長文を実測して、文体の癖を機械的に検出する。

標準ライブラリのみ。Windows / macOS / Linux で動作。

  python prose_check.py draft.md
  python prose_check.py "docs/*.md"                    # glob 可（クォート推奨）
  python prose_check.py "手本/*.md" "draft/*.md"        # 手本と並べて基準を作る
  python prose_check.py *.md --jargon 巻き取る,握る,温度感  # 内輪語を追加指定
  python prose_check.py *.md --detail                  # 該当行を全部出す
  python prose_check.py *.md --json                    # 機械可読出力

判定は「良い文章か」ではなく「書き手の癖が出ていないか」。

**合格ラインは持たない。** 文体の数値は原稿のジャンル・書き手・媒体で変わるため、
このスクリプトは数値を出すだけで OK/NG を判定しない。基準がほしいときは、
自分がお手本にしたい原稿を一緒に渡して、同じ表に並べて見比べる。
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
import sys
import unicodedata
from collections import Counter
from pathlib import Path

# ------------------------------------------------------- 癖パターン定義
# (キー, 表示名, 正規表現, 補足)
TIC_PATTERNS = [
    ("dash", "ダッシュ（——）", r"——", "日本語の書き言葉では不自然。読点か句点分割か括弧に置換する"),
    (
        "hedge",
        "語尾のぼかし",
        r"(たぶん|おそらく|かなり|だいぶ|そこそこ|ある程度|と思っています|という形です|ということです|かと思います|のような気がします)",
        "不確実さが実際にあるなら書いてよい。断定できる箇所でぼかすと数字の信頼度を自分で下げる。目安 1 ファイル 2 個",
    ),
    (
        "reader_proxy",
        "読者の心を代弁する枕",
        r"(と思われたかもしれません|と感じたかもしれません|当然の疑問|もっともな疑問|疑問に思われた|お思いでしょう)",
        "★AI 生成文の最大の指紋。全部削っても情報は 1 文字も減らない"
        "（ただしブランド文体で共感導入を指定されている場合は例外。SKILL.md の併用ルール参照）",
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
        "理由を示す型なので解説文では有効。連発すると単調になるだけ。目安 1 ファイル 3 回",
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
        "誤解を先に潰す対比としては有効。読みにくければ 2 文に分ける",
    ),
    (
        "num_space",
        "数字前後の半角スペース",
        r"[0-9][ 　]+(年|月|日|万|億|円|個|回|話|章|人|件|%|パーセント|通り|種類)",
        "「2026年」「20万円」は詰めるのが正",
    ),
    (
        "jotai",
        "敬体に常体が混入",
        r"(?<!」)(?<![「『])[^。！？「」]{3,}(だ|である|だろう|であろう|なのだ)。",
        "文体が波打つ。ただし短い常体をリズムで挟むのは技法。会話・引用は誤検知",
    ),
    # --- 係り受けと主述（G 章）---------------------------------------
    (
        "bracket_particle",
        "カギカッコに助詞を直付け",
        r"「[^」]{8,}(ました|ません|ます|ない|です|する|る|た|い|す)」(が|を|に|へ)",
        "G2. 引用の中が文なのに助詞を付けている。「〜という主張」のように名詞で受ける",
    ),
    (
        "redundant",
        "冗長表現",
        r"(することができ|することが可能|を行うことにより|を行うことで|といったこと|ということ(が|を|は)|というもの(が|を|は))",
        "G5.「することができます」→「できます」。意味を変えずに縮む",
    ),
]

# 「の」の連続（G3）。単純に「span 内に の が 3 つ」で採ると、修飾の「の」ではなく
# 準体助詞（〜するのは）や形式名詞（〜のもの・〜のほう）を大量に拾う。実原稿 6 万字で
# 39 件中ほぼ全件が誤検知だったため、連続する「Xの」ユニットを数えたうえで 3 段で絞る。
# ユニットから助詞（に・を・へ・と・が・は）を外すのは、「家に行った人の」のような
# 連体修飾節を 1 ユニットとして数えないため（節が挟まれば「の」は連続していない）。
NO_CHAIN_UNITS = re.compile(r"(?:[^、。「」（）\sにをへとがは]{1,8}の){3,}")
# 「の」の直後がこれらなら準体助詞（例:「〜するのは」「〜なのか」）
NOMINALIZER_NEXT = set("はかにでだがをもとへや、。？！")
FORMAL_NOUNS = ("もの", "ほう", "ため", "こと", "とき", "ところ", "うち")


def has_no_chain(s: str) -> bool:
    """修飾の「の」が 3 連続しているか。準体助詞・形式名詞は数えない。"""
    for m in NO_CHAIN_UNITS.finditer(s):
        seg = m.group()
        if any(w in seg for w in FORMAL_NOUNS):
            continue
        if any(
            seg[i + 1] in NOMINALIZER_NEXT
            for i, ch in enumerate(seg)
            if ch == "の" and i + 1 < len(seg)
        ):
            continue
        return True
    return False


# 正規表現では取れず、文そのものの性質で判定するもの
# (キー, 表示名, 述語, 補足)
TIC_PREDICATES = [
    (
        "no_chain",
        "「の」の連続",
        has_no_chain,
        "G3. 3 連続すると係り先が読めなくなる。1 つを動詞句や読点に置き換える",
    ),
    (
        "long_sent",
        "一文が長すぎる",
        lambda s: len(s) > 80,
        "G6. 80 字超は主述が離れてねじれやすい。句点で割るか、修飾を前に出す",
    ),
    (
        "comma_heavy",
        "読点が多い",
        lambda s: s.count("、") >= 4,
        "G4. 1 文に読点 4 個以上。息継ぎではなく係り先の切れ目で打つ。単語の列挙（A、B、C、D）は誤検知なので無視してよい",
    ),
]

# 検出側は正規表現も述語も「文を渡すと真偽が返る関数」に揃えて 1 ループで回す
TIC_RULES = [
    (key, label, re.compile(pattern).search, hint)
    for key, label, pattern, hint in TIC_PATTERNS
] + list(TIC_PREDICATES)

# 件数がこの数を超えたときだけ報告する（少数の出現は癖ではない）
TIC_MIN = {
    "abstract": 8,
    "jotai": 6,
    "nodesu": 4,
    "no_chain": 3,
    "redundant": 3,
    "long_sent": 3,
    "comma_heavy": 3,
    "bracket_particle": 2,
}

# 書き手の呼称。2 種類以上が同居していたら統一漏れ（E3）
PERSONA = ("筆者", "当方", "弊社", "当社", "我々", "私ども", "小職", "本稿")

# 文頭接続詞（起伏をつける語）
CONJ = (
    "しかし|ところが|だから|そして|つまり|ただ|ただし|また|さらに|なぜなら|それでも|一方|"
    "もっとも|とはいえ|むしろ|そもそも|ならば|もし|要するに|逆に|実際|なお|ですから|そのうえ|"
    "そこで|やがて|ちなみに|加えて|とはいうものの|それどころか"
)
CONJ_HEAD = re.compile(rf"({CONJ})")

# 文の区切り。句点だけでなく疑問符・感嘆符でも 1 文の終わりとみなす。
# 全角のみ。半角の ? ! は URL のクエリやコード片に頻出し、そこで文が割れてしまうため。
SENT_END = "。？！"
SENT_SPLIT = re.compile(rf"(?<=[{SENT_END}])")

# 文末（敬体）。疑問符・感嘆符で終わる文も敬体として数える
PLAIN_END = re.compile(rf"(です|ます|ました|ません|でした|ですね)[{SENT_END}]$")

# 本文とみなさない行（見出し・表・箇条書き・引用・コードフェンス）
SKIP_LINE = re.compile(r"^\s*(#|\||-\s|\*\s|\d+\.\s|>|```|!\[)")

# 実測では出ないので、人間が読んで確かめる項目
MANUAL_CHECKS = (
    "主語と述語が対応しているか（長い一文で起きる。G1）",
    "見出しがつなぎ言葉になっていないか（見出しは読者の頭にある問いへの答え）",
    "章をまたぐ一貫性（予告した章番号・同一指標の呼称・目次と実タイトル）",
    "感情が「あった → それでも仕組みが勝った」の 2 段で置かれているか",
    "具体的な数字・状況を抽象化して薄めていないか（消すのは内部記号と流用可能な設定値だけ）",
)


def split_paragraph(buffer: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """連続する本文行を 1 段落として繋ぎ、(開始行番号, 文) に切り分ける。

    行単位で切ると、改行で折り返された 1 文の前半が「句点で終わらない断片」として
    捨てられ、平均字数が実際より短く出る。段落に繋いでから切ることでこれを防ぐ。
    """
    if not buffer:
        return []
    # 各行の開始位置を覚えておき、文の先頭がどの行から始まったかを引けるようにする
    starts, joined = [], ""
    for lineno, line in buffer:
        starts.append((len(joined), lineno))
        joined += line

    def lineno_at(offset: int) -> int:
        found = starts[0][1]
        for pos, lineno in starts:
            if pos <= offset:
                found = lineno
            else:
                break
        return found

    sentences, offset = [], 0
    for chunk in SENT_SPLIT.split(joined):
        s = chunk.strip().replace("**", "")
        if s and s[-1] in SENT_END:
            sentences.append((lineno_at(offset), s))
        offset += len(chunk)
    return sentences


def load_sentences(path: Path, exclude: str | None) -> tuple[str, list[tuple[int, str]]]:
    """ファイル全文と、本文の (行番号, 文) リストを返す。"""
    # utf-8-sig: BOM 付きで書かれた原稿でも先頭行を見出しとして正しく除外するため
    text = path.read_text(encoding="utf-8-sig")
    ex = re.compile(exclude) if exclude else None
    located: list[tuple[int, str]] = []
    buffer: list[tuple[int, str]] = []
    in_fence = False
    for i, line in enumerate(text.split("\n"), 1):
        is_fence = line.strip().startswith("```")
        # 本文でない行は段落の切れ目。溜めていた行をここで 1 段落として確定する
        if is_fence or in_fence or not line.strip() or SKIP_LINE.match(line):
            located += split_paragraph(buffer)
            buffer = []
            if is_fence:
                in_fence = not in_fence
            continue
        if ex and ex.search(line):
            located += split_paragraph(buffer)
            buffer = []
            continue
        buffer.append((i, line))
    located += split_paragraph(buffer)
    return text, located


def analyse(path: Path, jargon: list[str], exclude: str | None) -> dict | None:
    text, located = load_sentences(path, exclude)
    if not located:
        return None

    sents = [s for _, s in located]
    lens = [len(s) for s in sents]
    n = len(sents)
    # 文頭接続詞は「割合」と「語ごとの偏り」の両方で使うので 1 度の走査で拾う
    conj_heads = [m.group(1) for s in sents if (m := CONJ_HEAD.match(s))]
    sections = max(1, len(re.findall(r"^##\s", text, re.M)))

    metrics = {
        "sentences": n,
        "avg_len": sum(lens) / n,
        "short_ratio": sum(1 for x in lens if x <= 25) / n,
        "plain_end_ratio": sum(1 for s in sents if PLAIN_END.search(s)) / n,
        "conj_ratio": len(conj_heads) / n,
        # 何割を測った数値なのかを明示する。低いほど箇条書き・表が主体で、
        # 文体指標（平均字数・文末分布）の代表性が下がる
        "body_ratio": sum(lens) / max(1, len(text)),
        # 太字密度（節あたり）
        "bold_per_section": len(re.findall(r"\*\*[^*\n]+\*\*", text)) / sections,
    }

    # 同一接続詞の偏り: 6 回以上、かつ接続詞つき文の 3 割超を占めるものだけ報告
    conj_heavy = {
        w: c
        for w, c in Counter(conj_heads).items()
        if c >= 6 and c / len(conj_heads) > 0.30
    }

    # 癖パターン（正規表現・文の性質のどちらも同じ形で判定する）
    tics = {}
    for key, label, matches, hint in TIC_RULES:
        hits = [(ln, s) for ln, s in located if matches(s)]
        if len(hits) >= TIC_MIN.get(key, 1):
            tics[key] = {"label": label, "hint": hint, "count": len(hits), "hits": hits}

    # 書き手の呼称ゆれ（2 種類以上の同居）。他の検出と同じく本文だけを見る
    persona = {w: c for w in PERSONA if (c := sum(s.count(w) for s in sents))}
    persona_mix = persona if len(persona) >= 2 else {}

    # 内輪語
    jargon_hits = {}
    for w in jargon:
        hits = [(ln, s) for ln, s in located if w in s]
        if hits:
            jargon_hits[w] = hits

    # 逐語の重複（20 字以上の同一文が 2 回以上）
    dup = {s: c for s, c in Counter(sents).items() if c >= 2 and len(s) >= 20}

    return {
        "file": path.name,
        "metrics": metrics,
        "conj_heavy": conj_heavy,
        "persona_mix": persona_mix,
        "tics": tics,
        "jargon": jargon_hits,
        "dup": dup,
    }


def json_ready(result: dict) -> dict:
    """JSON 出力用に、行番号つきの該当箇所を件数へ畳んだコピーを返す。"""
    slim = dict(result)
    slim["tics"] = {
        key: {k: v for k, v in tic.items() if k != "hits"}
        for key, tic in result["tics"].items()
    }
    slim["jargon"] = {w: len(hits) for w, hits in result["jargon"].items()}
    return slim


def collect_findings(result: dict) -> list[tuple[int, str, str, list]]:
    """1 ファイル分の検出を (件数, 表示名, 補足, 該当箇所) に揃えて件数順に返す。"""
    findings = [
        (v["count"], v["label"], v["hint"], v["hits"]) for v in result["tics"].values()
    ]
    findings += [
        (len(hits), f"内輪語「{w}」", "読者の文脈では別の意味に取られうる", hits)
        for w, hits in result["jargon"].items()
    ]
    findings += [
        (c, f"接続詞「{w}」の偏り", "この語だけで接続詞の 3 割超。半分は別の語に振るか削る", [])
        for w, c in result["conj_heavy"].items()
    ]
    if result["persona_mix"]:
        mix = "／".join(
            f"{w}{c}" for w, c in sorted(result["persona_mix"].items(), key=lambda x: -x[1])
        )
        findings.append(
            (sum(result["persona_mix"].values()), "書き手の呼称ゆれ", f"{mix} が同居。1 つに統一する", [])
        )
    findings += [
        (c, "逐語の重複", f"同一文が {c} 回: {s[:40]}…", []) for s, c in result["dup"].items()
    ]
    return sorted(findings, key=lambda f: -f[0])


def width(s: str) -> int:
    """端末上の表示幅。日本語などの全角文字を 2 桁として数える。"""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def pad(s: str, cells: int, right: bool = False) -> str:
    """表示幅で桁を揃える。全角混じりでも列がずれないようにする。"""
    space = " " * max(0, cells - width(s))
    return space + s if right else s + space


TABLE_WIDTH = 30 + 1 + 5 + 1 + 7 + 1 + 9 + 1 + 9 + 1 + 8 + 1 + 7


def metric_row(name: str, sentences: str, m: dict) -> str:
    """骨格テーブルの 1 行。ファイル行と中央値行で同じ書式を使う。"""
    return " ".join(
        (
            pad(name, 30),
            pad(sentences, 5, right=True),
            pad(f"{m['avg_len']:.1f}字", 7, right=True),
            pad(f"{m['short_ratio']*100:.0f}%", 9, right=True),
            pad(f"{m['plain_end_ratio']*100:.0f}%", 9, right=True),
            pad(f"{m['conj_ratio']*100:.0f}%", 8, right=True),
            pad(f"{m['body_ratio']*100:.0f}%", 7, right=True),
        )
    )


def print_skeleton(results: list[dict], skipped: list[str]) -> None:
    """■ 文体の骨格 — 実測値の表と、複数ファイルなら中央値。"""
    print("■ 文体の骨格\n")
    header = " ".join(
        (
            pad("file", 30),
            pad("文数", 5, right=True),
            pad("平均", 7, right=True),
            pad("25字以下", 9, right=True),
            pad("平板文末", 9, right=True),
            pad("接続詞", 8, right=True),
            pad("本文率", 7, right=True),
        )
    )
    print(header)
    print("-" * TABLE_WIDTH)
    for r in results:
        print(metric_row(r["file"], str(r["metrics"]["sentences"]), r["metrics"]))
    if len(results) >= 2:
        med = {
            k: statistics.median(r["metrics"][k] for r in results)
            for k in ("avg_len", "short_ratio", "plain_end_ratio", "conj_ratio", "body_ratio")
        }
        print("-" * TABLE_WIDTH)
        print(metric_row("（中央値）", "-", med))

    thin = [r["file"] for r in results if r["metrics"]["body_ratio"] < 0.30]
    if thin:
        print(f"\n  注: {', '.join(thin[:5])} は本文率が 30% 未満。箇条書き・表が主体のため、"
              "\n      文体指標（平均字数・文末分布）の代表性は低い。癖の検出だけ見るのがよい。")
    if skipped:
        print(f"\n  注: {', '.join(skipped[:5])} は本文の文が 0 件のため表に出していない"
              "\n      （見出し・箇条書きだけのファイル）。手本原稿を渡したつもりなら、指定を確認する。")


def print_tics(results: list[dict], detail: bool) -> None:
    """■ 癖の検出 — ファイルごとに件数の多い順で並べる。"""
    print("\n■ 癖の検出\n")
    found = False
    for r in results:
        findings = collect_findings(r)
        if not findings:
            continue
        found = True
        print(f"  ── {r['file']}")
        for count, label, hint, hits in findings:
            print(f"     {count:3}  {label}  … {hint}")
            if detail and hits:
                for ln, s in hits[:20]:
                    print(f"          L{ln}: {s[:60]}")
        print()
    if not found:
        print("  検出なし\n")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("paths", nargs="+", help="対象ファイル（glob 可）。手本原稿を一緒に渡すと比較できる")
    ap.add_argument("--jargon", default="", help="内輪語をカンマ区切りで（例: 巻き取る,握る,温度感,刺さる）")
    ap.add_argument("--exclude", default=None, help="除外する行の正規表現（免責文など）")
    ap.add_argument("--detail", action="store_true", help="該当行を全件表示")
    ap.add_argument("--json", action="store_true", help="JSON で出力")
    args = ap.parse_args()

    matched = {Path(p) for pat in args.paths for p in glob.glob(pat, recursive=True)}
    files = sorted(f for f in matched if f.is_file())
    if not files:
        print("対象ファイルが見つかりません", file=sys.stderr)
        return 1

    jargon = [w.strip() for w in args.jargon.split(",") if w.strip()]
    analysed = [(f, analyse(f, jargon, args.exclude)) for f in files]
    results = [r for _, r in analysed if r]
    # 本文の文が 0 件のファイルは表に出せないが、黙って消すと
    # 「手本と並べたつもりが下書き 1 本だけの表」を比較結果と誤読する
    skipped = [f.name for f, r in analysed if not r]

    if args.json:
        print(json.dumps([json_ready(r) for r in results], ensure_ascii=False, indent=2))
        return 0

    print(
        "\n※ 文体の数値に合格ラインは無い。ジャンル・書き手・媒体で変わる。"
        "\n   基準がほしいときは、お手本にしたい原稿を一緒に渡して同じ表で見比べる。\n"
    )
    print_skeleton(results, skipped)
    print_tics(results, args.detail)

    print("■ 自動では出ない項目（人間が読む）\n")
    for item in MANUAL_CHECKS:
        print(f"  - {item}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
