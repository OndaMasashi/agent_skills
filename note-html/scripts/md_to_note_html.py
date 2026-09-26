#!/usr/bin/env python3
"""Markdown 記事を note 貼り付け用の HTML に変換する。

note のエディタが保持するタグ（h2/h3, p, strong, em, blockquote, ul/ol, a, hr, pre）
だけを出力し、非対応の記法（表・h4以下・画像等）は自動変換したうえで警告する。

usage:
    python md_to_note_html.py article.md
    python md_to_note_html.py article.md -o out.html --tags "#AI #生成AI #LLM"
"""

import argparse
import html
import os
import re
import sys

# ---------------------------------------------------------------- inline


def _esc(s):
    return html.escape(s, quote=False)


def inline(text, warn):
    """インライン記法を HTML に変換する。プレースホルダで多重変換を防ぐ。"""
    slots = []

    def stash(payload):
        slots.append(payload)
        return "\x00%d\x00" % (len(slots) - 1)

    # 画像は note では手動アップロードが必要
    def img(m):
        warn.append("画像 %s は出力に含めていません（note では手動アップロードが必要）"
                    % (m.group(2) or "?"))
        alt = m.group(1) or "画像"
        return stash("<strong>［画像：%s／手動で挿入］</strong>" % _esc(alt))

    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)[^)]*\)", img, text)

    # マークダウンリンク
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        lambda m: stash('<a href="%s">%s</a>' % (html.escape(m.group(2)), _esc(m.group(1)))),
        text,
    )

    # インラインコード（note は文中コードを保持しないので素のテキストに戻す）
    def code(m):
        warn.append("インラインコード `%s` を素のテキストにしました（note は文中コード非対応）"
                    % m.group(1)[:30])
        return stash(_esc(m.group(1)))

    text = re.sub(r"`([^`]+)`", code, text)

    text = _esc(text)

    # 裸URL
    text = re.sub(
        r"(?<![\"'>=])(https?://[^\s<>\"'）」、。]+)",
        lambda m: '<a href="%s">%s</a>' % (html.escape(m.group(1)), m.group(1)),
        text,
    )

    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w_])_([^_\n]+)_(?![\w_])", r"<em>\1</em>", text)

    for i, payload in enumerate(slots):
        text = text.replace("\x00%d\x00" % i, payload)
    return text


# ---------------------------------------------------------------- blocks

RE_H = re.compile(r"^(#{1,6})\s+(.*)$")
RE_HR = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
RE_UL = re.compile(r"^\s*[-*+]\s+(.*)$")
RE_OL = re.compile(r"^\s*\d+[.)]\s+(.*)$")
RE_BQ = re.compile(r"^\s*>\s?(.*)$")
RE_URL_ONLY = re.compile(r"^\s*(https?://\S+)\s*$")
RE_TAIL_PAREN = re.compile(r"^(.*?)((?:（[^（）]*）|\([^()]*\))\s*)$")


def merge_url(item_html, url, warn):
    """出典行パターン（テキスト＋次行に裸URL）をリンクに畳む。

    末尾の（...）は範囲外に残す。既にリンクがある項目には追記しない。
    """
    if "<a href=" in item_html:
        return item_html + '　<a href="%s">%s</a>' % (html.escape(url), url)
    m = RE_TAIL_PAREN.match(item_html)
    head, tail = (m.group(1).rstrip(), m.group(2)) if m else (item_html, "")
    if not head:
        head, tail = item_html, ""
    warn.append("出典行をリンクに畳みました: %s" % re.sub(r"<[^>]+>", "", head)[:40])
    return '<a href="%s">%s</a>%s' % (html.escape(url), head, tail)


def table_to_list(rows, warn):
    """note は表に非対応。表を箇条書きへ変換する。"""
    if not rows:
        return ""
    header, body = rows[0], rows[1:]
    warn.append("表（%d列×%d行）を箇条書きに変換しました。読み返して不自然なら元の md を箇条書きに書き換えてください"
                % (len(header), len(body)))
    out = ["<ul>"]
    for r in body:
        cells = (r + [""] * len(header))[: len(header)]
        if len(header) == 2:
            line = "<strong>%s</strong>：%s" % (cells[0], cells[1])
        else:
            rest = " ／ ".join(
                "%s: %s" % (header[i], cells[i]) for i in range(1, len(header)) if cells[i]
            )
            line = "<strong>%s</strong> ── %s" % (cells[0], rest)
        out.append("<li>%s</li>" % line)
    out.append("</ul>")
    return "\n".join(out)


def convert(md, warn, merge_ref_urls=True):
    """Markdown 本文を note 互換 HTML に変換し、(title, body_html) を返す。"""
    lines = md.replace("\r\n", "\n").split("\n")
    title, out, i, n = None, [], 0, len(lines)

    def flush_para(buf):
        if buf:
            out.append("<p>%s</p>" % inline(" ".join(buf).strip(), warn))
        return []

    para = []
    while i < n:
        line = lines[i]

        if line.strip().startswith("```"):
            para = flush_para(para)
            fence, i, code = line.strip()[:3], i + 1, []
            while i < n and not lines[i].strip().startswith(fence):
                code.append(lines[i])
                i += 1
            i += 1
            warn.append("コードブロックを <pre> で出力しました。note 側で表示崩れがないか確認してください")
            out.append("<pre>%s</pre>" % _esc("\n".join(code)))
            continue

        m = RE_H.match(line)
        if m:
            para = flush_para(para)
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1:
                if title is None:
                    title = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
                else:
                    warn.append("2つ目の h1「%s」は h2 に落としました" % text[:30])
                    out.append("<h2>%s</h2>" % inline(text, warn))
            else:
                if level > 3:
                    warn.append("h%d「%s」を h3 にしました（note は大見出し・小見出しの2段のみ）"
                                % (level, text[:30]))
                out.append("<h%d>%s</h%d>" % (min(level, 3), inline(text, warn), min(level, 3)))
            i += 1
            continue

        if RE_HR.match(line):
            para = flush_para(para)
            out.append("<hr>")
            i += 1
            continue

        # 表
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", lines[i + 1]):
            para = flush_para(para)
            rows = []
            while i < n and "|" in lines[i]:
                raw = lines[i].strip().strip("|")
                if not re.match(r"^[\s:|-]+$", raw):
                    rows.append([inline(c.strip(), warn) for c in raw.split("|")])
                i += 1
            out.append(table_to_list(rows, warn))
            continue

        if RE_BQ.match(line):
            para = flush_para(para)
            buf = []
            while i < n and RE_BQ.match(lines[i]):
                buf.append(RE_BQ.match(lines[i]).group(1))
                i += 1
            joined = "<br>".join(inline(b, warn) for b in buf if b.strip())
            out.append("<blockquote><p>%s</p></blockquote>" % joined)
            continue

        if RE_UL.match(line) or RE_OL.match(line):
            para = flush_para(para)
            ordered = bool(RE_OL.match(line))
            items = []
            while i < n:
                m2 = RE_OL.match(lines[i]) if ordered else RE_UL.match(lines[i])
                if not m2:
                    break
                text, url = m2.group(1), None
                i += 1
                # 継続行（インデント）を取り込む
                while i < n and lines[i].strip() and not RE_UL.match(lines[i]) \
                        and not RE_OL.match(lines[i]) and lines[i].startswith((" ", "\t")):
                    cont = lines[i].strip()
                    mu = RE_URL_ONLY.match(cont)
                    if mu and merge_ref_urls:
                        url = mu.group(1)
                    else:
                        text += " " + cont
                    i += 1
                item = inline(text, warn)
                if url:
                    item = merge_url(item, url, warn)
                items.append("<li>%s</li>" % item)
            tag = "ol" if ordered else "ul"
            out.append("<%s>\n%s\n</%s>" % (tag, "\n".join(items), tag))
            continue

        if not line.strip():
            para = flush_para(para)
            i += 1
            continue

        para.append(line.strip())
        i += 1

    flush_para(para)
    return title, "\n\n".join(b for b in out if b)


# ---------------------------------------------------------------- template

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>note投稿用｜__PAGETITLE__</title>
<style>
  :root{--ink:#1a1a1a;--sub:#6b6b6b;--line:#e3e3e3;--bg:#fafafa;--accent:#2b6cb0;--warn:#8a6d00;--warnbg:#fffbe6}
  *{box-sizing:border-box}
  body{margin:0;padding:24px 16px 80px;background:var(--bg);color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Hiragino Kaku Gothic ProN","Yu Gothic",YuGothic,Meiryo,sans-serif;
    line-height:1.9;font-size:16px}
  .wrap{max-width:760px;margin:0 auto}
  .panel{background:#fff;border:1px solid var(--line);border-radius:10px;padding:20px 22px;margin-bottom:14px}
  .panel h1{font-size:15px;margin:0 0 14px;color:var(--sub);font-weight:600}
  .label{font-size:12px;color:var(--sub);margin:0 0 6px;font-weight:600}
  .titlebox{background:#f5f7fa;border:1px solid var(--line);border-radius:6px;padding:12px 14px;
    font-size:16px;font-weight:700;line-height:1.7;margin-bottom:12px}
  .tags{display:flex;gap:7px;flex-wrap:wrap}
  .tag{display:inline-block;font-size:13.5px;font-weight:600;line-height:1;background:#eef4fb;color:#1b4f80;
    border:1px solid #cfe0f2;padding:7px 11px;border-radius:14px;cursor:pointer;user-select:none}
  .tag:hover{background:#dceafa}
  .tags.alt .tag{background:#f4f4f4;color:#555;border-color:#e0e0e0}
  .btnrow{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:14px}
  button{font:inherit;font-size:14px;font-weight:600;cursor:pointer;border:1px solid var(--accent);
    background:var(--accent);color:#fff;padding:9px 18px;border-radius:6px}
  button.ghost{background:#fff;color:var(--accent)}
  button:hover{opacity:.85}
  #msg{font-size:13px;color:#1a7f37;font-weight:600}
  .note{background:var(--warnbg);border:1px solid #f0e0a0;border-radius:8px;padding:14px 18px;
    margin-bottom:26px;font-size:13.5px;line-height:1.85;color:#5c4a00}
  .note b{color:var(--warn)}
  .note ul{margin:8px 0 0;padding-left:1.2em}
  .note li{margin:3px 0}
  #article{background:#fff;border:1px solid var(--line);border-radius:10px;padding:36px 34px 44px}
  #article h2{font-size:21px;line-height:1.6;margin:2.6em 0 .9em;padding-bottom:.4em;
    border-bottom:2px solid var(--ink);font-weight:700}
  #article h2:first-child{margin-top:0}
  #article h3{font-size:17.5px;line-height:1.6;margin:2.2em 0 .7em;font-weight:700}
  #article p{margin:1.5em 0}
  #article a{color:var(--accent);text-decoration:underline;text-underline-offset:2px}
  #article blockquote{margin:1.7em 0;padding:.9em 1.2em;border-left:3px solid #cfd8e3;background:#f7f9fc}
  #article blockquote p{margin:.4em 0}
  #article ul,#article ol{margin:1.4em 0;padding-left:1.4em}
  #article li{margin:.5em 0}
  #article pre{background:#f5f5f5;padding:14px;overflow-x:auto;font-size:13.5px;line-height:1.7}
  #article hr{border:0;border-top:1px solid var(--line);margin:2.6em 0}
  ::selection{background:#cfe3ff}
</style>
</head>
<body>
<div class="wrap">
  <div class="panel">
    <h1>note 投稿用 ／ 貼り付け手順</h1>
    <p class="label">① タイトル欄に入れる（本文には含めない）</p>
    <div class="titlebox" id="title">__TITLE__</div>
__TAGBLOCK__
    <p class="label">__BODYSTEP__ 本文をコピーして、note の本文欄に貼り付ける</p>
    <div class="btnrow">
      <button onclick="copyTitle()" class="ghost">タイトルをコピー</button>
__TAGBUTTON__
      <button onclick="copyArticle()">本文をコピー</button>
      <span id="msg"></span>
    </div>
  </div>

  <div class="note">
    <b>貼り付け後に確認すること</b>
    <ul>
      <li>note は<b>見出し（大・小）／太字／引用／箇条書き／リンク／区切り線</b>を保持します。この HTML はその範囲だけで組んであります。</li>
      <li>リンクは<b>文中リンク</b>として入ります。<b>埋め込みカード</b>にしたい箇所は、貼り付け後にその行で URL を単独入力し直してください。</li>
      <li>フォントや色は note 側の書式に置き換わります（このページの見た目は再現されません）。</li>
__EXTRAWARN__
    </ul>
  </div>

  <div id="article">
__BODY__
  </div>
</div>

<script>
function flash(t, ok){
  var m=document.getElementById('msg');
  m.textContent=t; m.style.color=(ok===false)?'#b42318':'#1a7f37';
  clearTimeout(window.__t); window.__t=setTimeout(function(){m.textContent='';},5000);
}
function selectNode(el){
  var r=document.createRange(); r.selectNodeContents(el);
  var s=window.getSelection(); s.removeAllRanges(); s.addRange(r);
}
async function copyRich(el, okMsg){
  if(navigator.clipboard && window.ClipboardItem){
    try{
      await navigator.clipboard.write([new ClipboardItem({
        'text/html': new Blob([el.innerHTML],{type:'text/html'}),
        'text/plain': new Blob([el.innerText],{type:'text/plain'})})]);
      flash(okMsg); return;
    }catch(e){}
  }
  selectNode(el);
  try{ if(document.execCommand('copy')){ flash(okMsg); return; } }catch(e){}
  flash('自動コピーができませんでした。範囲を選択したので Ctrl+C（Mac は ⌘+C）を押してください', false);
}
function copyPlain(t, okMsg){
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(t).then(function(){flash(okMsg);})
      .catch(function(){fallbackPlain(t, okMsg);});
  } else { fallbackPlain(t, okMsg); }
}
function fallbackPlain(t, okMsg){
  var ta=document.createElement('textarea');
  ta.value=t; ta.style.position='fixed'; ta.style.opacity='0';
  document.body.appendChild(ta); ta.select();
  var ok=false; try{ ok=document.execCommand('copy'); }catch(e){}
  document.body.removeChild(ta);
  flash(ok?okMsg:'コピーできませんでした。手で選択してください', ok);
}
function copyTag(el){ copyPlain(el.textContent, el.textContent+' をコピーしました'); }
function copyTags(){
  var list=[]; document.querySelectorAll('#tags .tag').forEach(function(t){list.push(t.textContent);});
  copyPlain(list.join(' '), 'タグ'+list.length+'個をコピーしました');
}
function copyTitle(){ copyPlain(document.getElementById('title').textContent, 'タイトルをコピーしました'); }
function copyArticle(){ copyRich(document.getElementById('article'), '本文をコピーしました。note の本文欄に貼り付けてください'); }
</script>
</body>
</html>
"""

TAGBLOCK = """    <p class="label">② ハッシュタグ欄に入れる（note は最大10個。タグをクリックすると1つずつコピーできます）</p>
    <div class="tags" id="tags">
__MAINTAGS__
    </div>
__ALTBLOCK__
"""

ALTBLOCK = """    <p class="label" style="margin-top:10px">差し替え候補</p>
    <div class="tags alt">
__ALTTAGS__
    </div>
"""


def chips(tags):
    return "".join('<span class="tag" onclick="copyTag(this)">%s</span>' % _esc(t) for t in tags)


def split_tags(s):
    if not s:
        return []
    return [t if t.startswith("#") else "#" + t
            for t in re.split(r"[\s,、]+", s.strip()) if t]


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description="Markdown を note 貼り付け用 HTML に変換する")
    ap.add_argument("input", help="入力 .md ファイル")
    ap.add_argument("-o", "--output", help="出力 .html（既定: 入力と同じ場所に .html）")
    ap.add_argument("--title", help="タイトル（既定: 本文の h1）")
    ap.add_argument("--tags", help='ハッシュタグ。例: "#AI #生成AI #LLM"（最大10）')
    ap.add_argument("--alt-tags", help="差し替え候補のタグ")
    ap.add_argument("--no-merge-ref-urls", action="store_true",
                    help="出典行（テキスト＋次行の裸URL）をリンクに畳まない")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        sys.exit("入力ファイルが見つかりません: %s" % args.input)
    # utf-8-sig: Windows で作られた BOM 付き .md でも先頭見出しを取りこぼさない
    with open(args.input, encoding="utf-8-sig") as f:
        md = f.read()

    warn = []
    title, body = convert(md, warn, merge_ref_urls=not args.no_merge_ref_urls)
    title = args.title or title
    if not title:
        title = os.path.splitext(os.path.basename(args.input))[0]
        warn.append("h1 が無いのでファイル名をタイトルにしました。--title で指定できます")

    main_tags, alt_tags = split_tags(args.tags), split_tags(args.alt_tags)
    if len(main_tags) > 10:
        warn.append("タグが %d 個ありますが note の上限は 10 個です。先頭10個だけ使ってください"
                    % len(main_tags))

    if main_tags:
        tagblock = TAGBLOCK.replace("__MAINTAGS__", "      " + chips(main_tags))
        tagblock = tagblock.replace(
            "__ALTBLOCK__",
            ALTBLOCK.replace("__ALTTAGS__", "      " + chips(alt_tags)) if alt_tags else "")
        tagbutton = '      <button onclick="copyTags()" class="ghost">タグをまとめてコピー</button>\n'
        bodystep = "③"
        extra = ("      <li>ハッシュタグは<b>本文に入れていません</b>。note は公開設定で登録したタグを"
                 "記事末に自動表示するため、本文にも書くと二重になります。</li>")
    else:
        tagblock, tagbutton, bodystep, extra = "", "", "②", ""

    out_html = (TEMPLATE
                .replace("__PAGETITLE__", _esc(title))
                .replace("__TITLE__", _esc(title))
                .replace("__TAGBLOCK__", tagblock)
                .replace("__TAGBUTTON__", tagbutton)
                .replace("__BODYSTEP__", bodystep)
                .replace("__EXTRAWARN__", extra)
                .replace("__BODY__", body))

    out_path = args.output or os.path.splitext(args.input)[0] + ".html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out_html)

    counts = {t: len(re.findall("<%s[ >]" % t, body)) for t in
              ("h2", "h3", "p", "ul", "ol", "li", "blockquote", "strong", "a", "hr", "pre")}
    print("出力: %s" % out_path)
    print("タイトル: %s" % title)
    if main_tags:
        print("タグ(%d): %s" % (len(main_tags), " ".join(main_tags)))
    print("本文構成: " + " / ".join("%s=%d" % (k, v) for k, v in counts.items() if v))
    for bad in ("<table", "<h4", "<h5", "<h6", "<img", "<code"):
        if bad in body:
            print("!! note 非対応タグが残っています: %s" % bad)
    if warn:
        print("\n要確認 (%d件):" % len(warn))
        for w in warn:
            print("  - " + w)
    else:
        print("\n警告なし")


if __name__ == "__main__":
    main()
