# youtube-fetch スキルの追加（YouTube の情報取得の手順を統一）

## 対象

- `youtube-fetch/SKILL.md`（新規）
- `youtube-fetch/scripts/fetch_youtube.py`（新規）
- `youtube-fetch/references/visual.md`（新規）
- `tapestry/SKILL.md`（YouTube の取得部分を youtube-fetch へ委ねる形に変更）
- カタログ 4 箇所（`skill_catalog.md` / `generate_skill_catalog.js`（v18 のまま再生成）/
  `~/.claude/skills-catalog.md` / `~/.agent/skills-catalog.md`）
- `skills-main/CLAUDE.md`（カテゴリ一覧に追加、カタログの版を v15 → v18 の実態に合わせた）

## 変更内容

- `fetch_youtube.py`: URL を受け取り、題名・チャンネル・公開日・長さ・概要欄・チャプター・時刻つき字幕を
  `<動画ID>.md` 1 枚に書き出す。主経路は yt-dlp、失敗時は youtube-transcript-api へ自動で切り替える。
  依存は PEP 723 で宣言し `uv run --script` で実行する（毎回の pip インストールをやめる）
- 字幕は「話されている言語の手動 → 同じ言語の自動（`-orig`）→ ja/en の手動 → その他の手動 → 自動翻訳」の順に選ぶ。
  自動字幕に誤判定の `en-US-orig` と正しい `ja-orig` が同居する動画があったため、`info["language"]` で選ぶ
- 字幕は 30 秒ごとの段落にまとめ、チャプターの位置に見出しを入れる（37 分の動画で 1,023 行 → 322 段落）
- `visual.md`: 映像を確かめるときの動画取得（480p 全体）・一覧画像・場面の切り替わり検出の手順。
  区間指定の取得（`--download-sections`）が 480p・4 秒で 400 秒を超えても終わらなかったため、`timeout` を必須にした

## 理由

YouTube の情報取得の手順が毎回違っていた（2026-09-26 時点で 3 通り）。

- ai-avator: 作業フォルダへ yt-dlp を pip で入れ、VTT 字幕を自作スクリプトで文字化
- works-gallery のセッション: youtube-transcript-api を仮想環境に入れて取得
- tapestry: VTT を取るだけの 1 行（文字化なし）

どれも記録が残らず、次のセッションで一から探し直していた。

## 確認したこと

- 日本語の自動字幕（37 分）・英語の手動字幕・ai-avator の動画（14 分）の 3 本で取得できた。
  ai-avator で当時取った字幕と文字数がほぼ一致（5,312 / 5,300 字）
- 予備の経路へ強制的に切り替えても同じ 1,023 行が取れた
- 存在しない ID は exit 1、字幕なし（部品を差し替えて再現）は exit 2
- 初回 77 秒（依存の取得）、2 回目以降は約 8 秒
- /refine（code-simplifier）で整理した後も、出力が整理前と 1 文字も変わらないことを確認

## 残作業

/code-review と security-reviewer の指摘のうち未対応のもの（2026-09-26 時点）:

- 通常: 字幕の取得が空・失敗で終わると、取れていた動画情報（概要欄・公開日・チャプター）まで捨てて予備の経路へ回る。
  関連して、字幕を `ydl.urlopen` で直接取っているので yt-dlp 本体のヘッダー設定を通らない（タイムアウトも無い）
- 通常: 自動翻訳の字幕が「自動生成」とだけ表示され、翻訳だと分からない
- 通常: 概要欄に ``` が含まれると、Markdown の囲みを抜けて見出しや字幕を偽造できる
- 通常: 公開日が UTC の日付のままで、日本時間の 0〜9 時に公開された動画は 1 日前になる
- 通常: 警告を消しているため「字幕が取れなかった」と「字幕が無い」を区別できない。
  動画の形式が 1 つも選べないと、yt-dlp の経路全体が失敗する
- 様子見: 予備の経路の字幕の選び方が主経路と違う／韓国語の字幕の単語がつながる／
  引数の誤りも exit 2 になる／`embed/videoseries` を動画 ID と誤認する ほか
