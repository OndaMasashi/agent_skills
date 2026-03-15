# NotebookLM スライド用スタイルJSON フレームワーク v1.0

## 1. 概要

NotebookLMのスライド生成時に「スタイル欄」へ貼り付けるJSON定義の標準フレームワーク。

### 想定ワークフロー

1. ベースとなるPDFスライドを用意する
2. 「4. PDFリバースガイド」のチェックリストに沿ってビジュアル要素を観察する
3. テンプレート（6章）をコピーし、観察結果を当てはめる
4. 5000文字以内に収まるよう調整する（5章参照）

### 制約

- **文字数制限**: NLMスタイル欄は **5000文字** まで
- **スコープ**: ビジュアルスタイルのみ。ストーリー・構成・ページ順序は別途NLMに指示する
- **柔軟性**: 必須フィールドは最小限。PDFのオブジェクト種類やモチーフ等はスタイルに応じて自由に追加する

---

## 2. JSON全体構造

```
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
    ├─ white_space           ... ★必須
    └─ diagram_placement / patterns ... 任意
  content_tone_and_voice    ... トーン・言語
    ├─ style                ... ★必須
    ├─ language             ... ★必須
    └─ vocabulary / structure ... 任意
}
```

★ = 必須フィールド

---

## 3. セクション詳細定義

### 3.1 design_directive

スタイル全体の方向付け。NLMに「何を目指すか」を伝える最上位の指示。

| フィールド | 必須 | 型 | 説明 |
|---|---|---|---|
| `theme_name` | ★ | string | スタイル名。短く印象的に（例: "Modern Engineering Blueprint"） |
| `objective` | ★ | string | このスタイルの視覚的目標。1-2文で「どんな美学でどんな情報を伝えるか」 |
| `target_audience` | ★ | string | 想定する聴衆。NLMがトーンや専門度を調整する手がかり |

### 3.2 visual_identity

#### color_palette

| フィールド | 必須 | 型 | 説明 |
|---|---|---|---|
| `background` | ★ | `{color, description}` | 背景色。HEXコード + 使用意図 |
| `primary_ink` | ★ | `{color, description}` | 主要テキスト・線の色。キー名は `primary_text` も可 |
| `accent` | ★ | `{color, description}` | 強調色。descriptionに「どこに使うか」を含める |
| `secondary_fill` | | `{color, description}` | 副次色。塗りや非アクティブ要素用 |
| `grid_lines` | | `{color, opacity?, style?}` | 背景グリッド。テクニカル系で有効 |
| *(追加色)* | | `{color, description}` | `tertiary`, `gold_accent` 等、自由に追加可 |

**ガイダンス**: 色数は3〜5色が目安。多すぎるとNLMが混乱する。description欄に「いつ・どこに使うか」を書くとNLMの判断精度が上がる。

#### typography

| フィールド | 必須 | 型 | 説明 |
|---|---|---|---|
| `headings` | ★ | `{font, size?, style}` | 見出し用。`style`でBold/Italic等の性格を指定 |
| `body` | ★ | `{font, size?, style}` | 本文用 |
| *(追加カテゴリ)* | | 同上 | `labels`(図中ラベル), `caption`(注釈), `code`(コード) 等 |

**ガイダンス**:
- `font` はNLMが必ずしもそのフォントを使えるとは限らないが「意図する雰囲気」を伝える役割がある
- Google Slides互換フォント推奨: Roboto, Roboto Condensed, Roboto Mono, Noto Sans JP, Arial, Courier New
- 日本語フォント（Noto Sans JP等）は必ず含めること
- `size` は任意だが、階層感を伝えるなら含めると効果的（例: headings 28-36pt, body 16-20pt）

### 3.3 illustration_style_guide

イラスト・図表・ビジュアル要素のスタイル指示。**最も自由度が高いセクション**。

| フィールド | 必須 | 型 | 説明 |
|---|---|---|---|
| `core_aesthetic` | ★ | string | ビジュアルの核となる美学を1文で（例: "Isometric Technical Illustration"） |
| `negative_prompts` | ★ | string[] | 「やってはいけないこと」のリスト。NLMの暴走を防ぐガードレール |
| `parameters` | | object | 詳細パラメータ（下記サブフィールド候補参照） |
| `motifs` | | string[] | 繰り返し使うモチーフ（例: タイプライター、砂時計、歯車） |
| `effects` | | string[] | 視覚エフェクト（例: グロー、パーティクル、ノイズ） |

**parameters のサブフィールド候補**（全て任意、PDFから観察できたものを記述）:

| サブフィールド | 説明 |
|---|---|
| `perspective` | 投影法（アイソメトリック、正投影、パース等） |
| `line_work` | 線の太さ・品質・手描き感の有無 |
| `shading` | 陰影の付け方（ハッチング、べた塗り、なし等） |
| `fill` | オブジェクトの塗り方針（透明、単色、パターン等） |
| `metaphors` | 概念→視覚化の対応マッピング（例: "混沌=もつれ、秩序=グリッド"） |
| `color_rule` | イラスト内での色の使い方ルール |
| `objects` | PDFに登場する特徴的なオブジェクト種類の列挙 |
| `texture` | テクスチャ指定（紙質、ノイズ、グレイン等） |

**negative_prompts の定番候補**:

```
"No photorealism", "No 3D renders", "No cartoon characters",
"No corporate Memphis style", "No gradients", "No drop shadows",
"No cluttered backgrounds", "No animations or transitions"
```

### 3.4 slide_layout_structure

| フィールド | 必須 | 型 | 説明 |
|---|---|---|---|
| `grid` | ★ | string | グリッドの方針（例: "厳密なモジュラーグリッド"、"非対称レイアウト"） |
| `white_space` | ★ | string | 余白の扱い方針（例: "十分な余白を確保"、"高密度に情報を詰める"） |
| `diagram_placement` | | object | 図表の配置パターン。キーで分類して記述 |
| `patterns` | | string[] | スライドの種類パターン一覧 |
| `margin` | | string | マージンの具体指定 |

**ガイダンス**: `diagram_placement`（オブジェクト形式で詳述）と `patterns`（配列で列挙）は同じ意図の異なる表現。PDFに明確なレイアウトルールがあればオブジェクト形式、列挙で十分なら配列で書く。

### 3.5 content_tone_and_voice

| フィールド | 必須 | 型 | 説明 |
|---|---|---|---|
| `style` | ★ | string | トーンを形容詞で指定（例: "分析的・精密・ナラティブ駆動"） |
| `language` | ★ | string or object | 出力言語。最低限「日本語」を指定。技術用語の扱い等の補足も可 |
| `vocabulary` | | string | 使用すべき語彙の方向性（例: "工学・経済用語を使用"） |
| `structure` | | object | 情報提示のパターン（例: 課題→解決→効果）。※ストーリー構成ではなく表現の型 |

---

## 4. PDFリバースガイド

ベースPDFからスタイルJSONを起こす際の観察チェックリスト。

### design_directive を決めるために

- [ ] このPDF全体の雰囲気を3語で表現すると？
- [ ] 想定読者は誰か？（資料の文脈から推測）
- [ ] テーマに名前をつけるなら？

### color_palette を決めるために

- [ ] 背景色をスポイトで取得（複数ページで統一か確認）
- [ ] 本文テキストの色（純黒か、グレー系か、カラーか）
- [ ] 強調に使われている色は何色か（見出し、アイコン、図の一部）
- [ ] 副次的に使われている色があるか（図の塗り、セクション区切り）
- [ ] 背景にグリッドやパターンがあるか

### typography を決めるために

- [ ] 見出しのフォントの印象（セリフ/サンセリフ、太さ、字間）
- [ ] 本文のフォントの印象
- [ ] 図表ラベルや注釈に別のフォントが使われているか
- [ ] 日本語と英語でフォントが使い分けられているか
- [ ] フォントサイズの階層は何段階か

### illustration_style_guide を決めるために

- [ ] イラスト/図はあるか？ どんなスタイルか（線画、フラット、写実、アイソメトリック等）
- [ ] 影の付け方（ハッチング、ドロップシャドウ、なし）
- [ ] 図中の色使い（モノクロ+アクセント？ フルカラー？）
- [ ] 繰り返し登場するモチーフやアイコンはあるか
- [ ] 明らかに避けているビジュアル表現はあるか → negative_prompts のヒント
- [ ] 特徴的なオブジェクト種類（矢印、ブロック図、フローチャート等）

### slide_layout_structure を決めるために

- [ ] マージンは広いか狭いか
- [ ] テキストと図の配置にグリッド感があるか
- [ ] 図表はページのどこに置かれる傾向があるか（中央、右寄り等）
- [ ] 代表的なレイアウトパターンは何種類あるか

### content_tone_and_voice を決めるために

- [ ] 文体は敬体か常体か
- [ ] 専門用語の扱い（英語そのまま？ カタカナ？ 日本語訳？）
- [ ] 箇条書き中心か、文章中心か

---

## 5. 5000文字圧縮テクニック

優先度順に適用する。

| 優先度 | テクニック | 効果 |
|---|---|---|
| 1 | **description を簡潔に** — 「なぜその色か」ではなく「どこに使うか」だけに | 大 |
| 2 | **キー名を短縮** — `font_family`→`font`, `accent_highlight`→`accent`, `body_text`→`body`, `detailed_parameters`→`parameters` | 中 |
| 3 | **日本語で書く** — 英語より情報密度が高い。技術用語は英語のまま | 中 |
| 4 | **任意フィールドを取捨選択** — `size`, `opacity` 等の数値はNLMが推測可能 | 中 |
| 5 | **negative_prompts を厳選** — 4〜5個に絞る | 小 |
| 6 | **structure を省略** — `style` だけでトーンが十分伝わるなら不要 | 小 |

**目安**: 必須フィールドのみ → 約2,000〜2,500文字。任意フィールド込み → 約3,500〜4,500文字。

---

## 6. テンプレート

### 6.1 フル版テンプレート

全フィールド入り。PDFリバース時にコピーして使用し、不要な任意フィールドは削除する。

```json
{
  "design_directive": {
    "theme_name": "<スタイル名>",
    "objective": "<このスタイルの視覚的目標を1-2文で>",
    "target_audience": "<想定する聴衆>"
  },
  "visual_identity": {
    "color_palette": {
      "background": {"color": "#______", "description": "<使用意図>"},
      "primary_ink": {"color": "#______", "description": "<使用意図>"},
      "accent": {"color": "#______", "description": "<どこに使うか>"},
      "secondary_fill": {"color": "#______", "description": "<使用意図>"},
      "grid_lines": {"color": "#______", "opacity": 0.3, "style": "<グリッドの種類>"}
    },
    "typography": {
      "headings": {"font": "<フォント名>", "size": "<サイズ>", "style": "<太さ・字間等の性格>"},
      "body": {"font": "<フォント名>", "size": "<サイズ>", "style": "<読みやすさの方針>"},
      "labels": {"font": "<フォント名>", "size": "<サイズ>", "style": "<用途説明>"}
    }
  },
  "illustration_style_guide": {
    "core_aesthetic": "<ビジュアルの核となる美学を1文で>",
    "parameters": {
      "perspective": "<投影法>",
      "line_work": "<線の太さ・品質>",
      "shading": "<陰影の付け方>",
      "fill": "<オブジェクトの塗り方針>",
      "metaphors": {
        "<概念A>": "<視覚表現A>",
        "<概念B>": "<視覚表現B>"
      },
      "color_rule": "<イラスト内での色の使い方>"
    },
    "motifs": ["<モチーフ1>", "<モチーフ2>"],
    "effects": ["<エフェクト1>", "<エフェクト2>"],
    "negative_prompts": [
      "No photorealism",
      "No <禁止事項1>",
      "No <禁止事項2>",
      "No animations or transitions"
    ]
  },
  "slide_layout_structure": {
    "grid": "<グリッドの方針>",
    "white_space": "<余白の扱い>",
    "diagram_placement": {
      "<パターン名1>": "<配置ルール>",
      "<パターン名2>": "<配置ルール>"
    }
  },
  "content_tone_and_voice": {
    "style": "<トーンを形容詞で>",
    "vocabulary": "<使用すべき語彙の方向性>",
    "language": "日本語出力。技術用語は英語またはカタカナのまま維持",
    "structure": {
      "<要素1>": "<表現の型>",
      "<要素2>": "<表現の型>"
    }
  }
}
```

### 6.2 ミニマル版テンプレート（5000文字制限対応）

必須フィールドのみ。冒頭文付きでそのままNLMに貼り付け可能。

```
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
