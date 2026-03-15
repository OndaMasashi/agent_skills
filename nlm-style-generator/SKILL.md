---
name: nlm-style-generator
description: "NotebookLMのスライド/インフォグラフィック用スタイルJSONを生成。PDF・画像・スクリーンショットからビジュアルスタイルをリバースエンジニアリングし、5000文字以内のJSON定義を出力する。Use when user asks to create NLM/NotebookLM style JSON, generate slide style, or reverse-engineer visual style for NotebookLM. Trigger phrases: NLMスタイル, NotebookLMスタイル, スライドのスタイルJSON, インフォグラフィックのスタイル. Do NOT use for general PDF reading, image analysis, or NotebookLM audio/video generation."
---

> [!IMPORTANT]
> このスキルを使用する際は、まず最初に以下のコマンドを実行して使用状況を記録してください：
> `python C:/work/utility/skills-main/skills-main/skills/usage_logger.py nlm-style-generator`

# NLM Style Generator

NotebookLMのスライド/インフォグラフィック生成時に「スタイル欄」へ貼り付けるJSON定義を生成する。

## 制約

- **文字数制限**: NLMスタイル欄は **5000文字** まで
- **スコープ**: ビジュアルスタイルのみ。ストーリー・構成・ページ順序は別途NLMに指示する
- **柔軟性**: 必須フィールドは最小限。PDFのオブジェクト種類やモチーフ等はスタイルに応じて自由に追加する

## ワークフロー

### Step 1: リファレンス素材の受け取り

入力ソースに応じて読み取り方法を選択:

| 入力 | 方法 |
| --- | --- |
| PDF | Read tool で `pages: "1-5"` 指定。必要に応じて追加ページも読む |
| 画像/スクリーンショット | Read tool で視覚的に分析 |
| Webサイト | スクリーンショットの提供を依頼、または URL から WebFetch |
| テキスト指示のみ | ユーザーの方向性からデザインを設計 |

### Step 2: 体系的分析

PDFリバースガイドチェックリスト（後述）に沿って各要素を観察し、分析結果を構造化サマリーとしてユーザーに提示する。

**注意**: HEXカラーはPDF/画像からの推定値。ユーザーに「推定値です。必要に応じて調整してください」と明記すること。

### Step 3: スタイルJSON生成

1. ミニマル版テンプレート（後述）をベースに必須フィールドを埋める
2. リファレンス素材に明確な根拠がある場合のみ任意フィールドを追加
3. 詳細なフィールド定義が必要な場合 → [references/style_json_framework.md](references/style_json_framework.md) セクション3を参照
4. リッチなスタイルを生成する場合 → 同ファイルのフル版テンプレート（セクション6.1）を使用

### Step 4: 検証・圧縮

```bash
python scripts/validate_style_json.py <output_path>
```

5000文字を超過した場合、圧縮テクニック表（後述）を優先度順に適用して再検証。

### Step 5: 出力

- プリアンブル「スタイルは下記を適用すること。」を先頭に付与
- ファイルに保存（ユーザー指定パス or 提案）
- 文字数と主なスタイル選択を簡潔に説明

---

## JSON全体構造

```text
{
  design_directive          ... テーマの方向性（★全必須）
  visual_identity           ... 色とフォント
    ├─ color_palette        ... ★3色必須 + 任意追加
    └─ typography           ... ★2種必須 + 任意追加
  illustration_style_guide  ... イラスト・図のスタイル
    ├─ core_aesthetic       ... ★必須
    ├─ negative_prompts     ... ★必須
    └─ parameters / motifs / effects ... 任意
  slide_layout_structure    ... レイアウト・余白
    ├─ grid                 ... ★必須
    ├─ white_space          ... ★必須
    └─ diagram_placement / patterns ... 任意
  content_tone_and_voice    ... トーン・言語
    ├─ style                ... ★必須
    ├─ language             ... ★必須
    └─ vocabulary / structure ... 任意
}
```

★ = 必須フィールド

## セクション別ガイダンス

### design_directive

- `theme_name`: 短く印象的なスタイル名（例: "Modern Engineering Blueprint"）
- `objective`: 視覚的目標を1-2文で
- `target_audience`: 想定する聴衆

### color_palette

- 色数は **3〜5色** が目安。多すぎるとNLMが混乱する
- `description` 欄に「いつ・どこに使うか」を書くとNLMの判断精度が上がる
- 必須: `background`, `primary_ink`（`primary_text`も可）, `accent`（`accent_highlight`も可）
- 任意: `secondary_fill`, `grid_lines`, その他自由に追加可

### typography

- Google Slides互換フォント推奨: Roboto, Roboto Condensed, Roboto Mono, Noto Sans JP, Arial, Courier New
- **日本語フォント（Noto Sans JP等）は必ず含める**
- `font` はNLMが必ずしも使えるとは限らないが「意図する雰囲気」を伝える役割
- 必須: `headings`, `body`。任意: `labels`, `caption`, `code` 等

### illustration_style_guide

**最も自由度が高いセクション。** リファレンス素材の特徴を最大限反映する。

- `core_aesthetic`: ビジュアルの核となる美学を1文で
- `negative_prompts`: NLMの暴走を防ぐガードレール。4〜5個に厳選

**parameters のサブフィールド候補**（全て任意、観察できたものを記述）:

| サブフィールド | 説明 |
| --- | --- |
| `perspective` | 投影法（アイソメトリック、正投影、パース等） |
| `line_work` | 線の太さ・品質・手描き感の有無 |
| `shading` | 陰影の付け方（ハッチング、べた塗り、なし等） |
| `fill` | オブジェクトの塗り方針（透明、単色、パターン等） |
| `metaphors` | 概念→視覚化の対応マッピング |
| `color_rule` | イラスト内での色の使い方ルール |
| `objects` | 特徴的なオブジェクト種類の列挙 |
| `texture` | テクスチャ指定（紙質、ノイズ、グレイン等） |

**negative_prompts の定番候補**:

```text
"No photorealism", "No 3D renders", "No cartoon characters",
"No corporate Memphis style", "No gradients", "No drop shadows",
"No cluttered backgrounds", "No animations or transitions"
```

### slide_layout_structure

- `grid`: グリッドの方針（例: "厳密なモジュラーグリッド"、"非対称レイアウト"）
- `white_space`: 余白の扱い方針
- `diagram_placement`（オブジェクト形式で詳述）と `patterns`（配列で列挙）は同じ意図の異なる表現。PDFに明確なレイアウトルールがあればオブジェクト形式、列挙で十分なら配列で書く

### content_tone_and_voice

- `style`: トーンを形容詞で指定
- `language`: 最低限「日本語」を指定。技術用語の扱い等の補足も可
- 任意: `vocabulary`（語彙の方向性）, `structure`（情報提示の型）

---

## PDFリバースガイドチェックリスト

リファレンス素材を分析する際、以下を順に確認する。

**design_directive:**

- [ ] 全体の雰囲気を3語で表現すると？
- [ ] 想定読者は誰か？（資料の文脈から推測）
- [ ] テーマに名前をつけるなら？

**color_palette:**

- [ ] 背景色（複数ページで統一か確認）
- [ ] 本文テキストの色（純黒か、グレー系か、カラーか）
- [ ] 強調に使われている色（見出し、アイコン、図の一部）
- [ ] 副次的に使われている色（図の塗り、セクション区切り）
- [ ] 背景にグリッドやパターンがあるか

**typography:**

- [ ] 見出しのフォントの印象（セリフ/サンセリフ、太さ、字間）
- [ ] 本文のフォントの印象
- [ ] 図表ラベルや注釈に別のフォントが使われているか
- [ ] 日本語と英語でフォントが使い分けられているか
- [ ] フォントサイズの階層は何段階か

**illustration_style_guide:**

- [ ] イラスト/図のスタイル（線画、フラット、写実、アイソメトリック等）
- [ ] 影の付け方（ハッチング、ドロップシャドウ、なし）
- [ ] 図中の色使い（モノクロ+アクセント？ フルカラー？）
- [ ] 繰り返し登場するモチーフやアイコン
- [ ] 明らかに避けているビジュアル表現 → negative_prompts のヒント
- [ ] 特徴的なオブジェクト種類（矢印、ブロック図、フローチャート等）

**slide_layout_structure:**

- [ ] マージンは広いか狭いか
- [ ] テキストと図の配置にグリッド感があるか
- [ ] 図表の配置傾向（中央、右寄り等）
- [ ] 代表的なレイアウトパターンは何種類か

**content_tone_and_voice:**

- [ ] 文体は敬体か常体か
- [ ] 専門用語の扱い（英語そのまま？ カタカナ？ 日本語訳？）
- [ ] 箇条書き中心か、文章中心か

---

## 5000文字圧縮テクニック

優先度順に適用する。

| 優先度 | テクニック | 効果 |
| --- | --- | --- |
| 1 | **description を簡潔に** — 「なぜその色か」ではなく「どこに使うか」だけに | 大 |
| 2 | **キー名を短縮** — `font_family`→`font`, `accent_highlight`→`accent` 等 | 中 |
| 3 | **日本語で書く** — 英語より情報密度が高い。技術用語は英語のまま | 中 |
| 4 | **任意フィールドを取捨選択** — `size`, `opacity` 等の数値はNLMが推測可能 | 中 |
| 5 | **negative_prompts を厳選** — 4〜5個に絞る | 小 |
| 6 | **structure を省略** — `style` だけでトーンが十分伝わるなら不要 | 小 |

**目安**: 必須フィールドのみ → 約2,000〜2,500文字。任意フィールド込み → 約3,500〜4,500文字。

---

## ミニマル版テンプレート

必須フィールドのみ。プリアンブル付きでそのままNLMに貼り付け可能。

```text
スタイルは下記を適用すること。

{
  "design_directive": {
    "theme_name": "<スタイル名>",
    "objective": "<視覚的目標>",
    "target_audience": "<想定聴衆>"
  },
  "visual_identity": {
    "color_palette": {
      "background": {"color": "#______", "description": "<使用意図>"},
      "primary_ink": {"color": "#______", "description": "<使用意図>"},
      "accent": {"color": "#______", "description": "<どこに使うか>"}
    },
    "typography": {
      "headings": {"font": "<フォント名>", "style": "<性格>"},
      "body": {"font": "<フォント名>", "style": "<方針>"}
    }
  },
  "illustration_style_guide": {
    "core_aesthetic": "<ビジュアルの美学>",
    "negative_prompts": ["No <禁止1>", "No <禁止2>", "No <禁止3>"]
  },
  "slide_layout_structure": {
    "grid": "<グリッド方針>",
    "white_space": "<余白の扱い>"
  },
  "content_tone_and_voice": {
    "style": "<トーン>",
    "language": "日本語出力。技術用語は英語のまま"
  }
}
```

## 参照

- フル版テンプレート（全フィールド入り）やフィールドの型・説明の詳細は [references/style_json_framework.md](references/style_json_framework.md) を参照
- 検証スクリプト: `python scripts/validate_style_json.py <file_path>` — JSON構文・必須フィールド・5000文字制限をチェック
