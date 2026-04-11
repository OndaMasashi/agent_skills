---
name: nlm-style-generator
description: "NotebookLMのスライド/インフォグラフィック用スタイルJSONを生成。PDF・画像・スクリーンショットからビジュアルスタイルをリバースエンジニアリングし、5000文字以内のJSON定義を出力する。Use when user asks to create NLM/NotebookLM style JSON, generate slide style, or reverse-engineer visual style for NotebookLM. Trigger phrases: NLMスタイル, NotebookLMスタイル, スライドのスタイルJSON, インフォグラフィックのスタイル. Do NOT use for general PDF reading, image analysis, or NotebookLM audio/video generation."
---
# NLM Style Generator

NotebookLMのスライド/インフォグラフィック生成時に「スタイル欄」へ貼り付けるJSON定義を生成する。

## 制約

- **文字数制限**: NLMスタイル欄は **5000文字** まで
- **目標文字数**: **4000〜4800文字**。5000文字の枠を最大限活用し、各セクションを具体的に記述することでNLMの再現精度を高める
- **出力形式**: minify JSON（改行・インデントなし）で出力する。文字数制限への余裕が生まれる
- **出力ファイル名**: `style.json`。同名ファイルが既に存在する場合は `style_2.json`, `style_3.json` 等で回避
- **スコープ**: ビジュアルスタイルのみ。ストーリー・構成・ページ順序は別途NLMに指示する
- **柔軟性**: 必須フィールドは最小限。PDFのオブジェクト種類やモチーフ等はスタイルに応じて自由に追加する

## 汎用スタイル原則

生成するスタイルJSONは **汎用的に使える** ことを重視する。入力素材がどの業界のものであっても、抽出するのは視覚的特徴のみ。

- **抽出すべき**: 色、フォント、レイアウト、イラストスタイル、トーン、余白、グリッド感、質感
- **抽出すべきでない**: 業種名、役務名、地域名、人種、固有名詞、業界用語
- **OK な表現**: 「自然を感じさせる緑系」「草木や葉をモチーフに」「温かみのあるアースカラー」
- **NG な表現**: 「農業向け」「医療系」「東京都の施策向け」「〇〇社ブランド」

`design_directive` の `objective` / `target_audience` も汎用的に書く:

- NG: `"農業従事者向けの報告書スタイル"`
- OK: `"自然素材を感じさせるナチュラルモダン、専門職向けの落ち着いたトーン"`

`motifs` / `objects` も視覚的特徴として記述し、業種ラベルを付けない:

- NG: `"農業アイコン"`, `"医療機器イラスト"`
- OK: `"葉・枝のシルエット"`, `"精密な線画オブジェクト"`

## ワークフロー

### Step 1: リファレンス素材の受け取り

入力ソースに応じて読み取り方法を選択:

| 入力 | 方法 |
| --- | --- |
| PDF | **pdf スキルが利用可能ならスキルを発動**して読み取る。スキルが使えない場合は Read tool で `pages: "1-5"` 指定 |
| 画像/スクリーンショット | Read tool で視覚的に分析 |
| Webサイト | 下記「Webページからの取得方法」を参照 |
| テキスト指示のみ | ユーザーの方向性からデザインを設計 |

**Webページからの取得方法:**

URLが指定された場合、以下の優先順で取得を試みる:

1. **chrome-devtools MCP**（推奨）: `navigate_page` → `take_screenshot` でページ全体のスクリーンショットを取得し、Read tool で視覚分析。最もスタイル情報が正確に取れる
2. **WebFetch**: HTMLソースからCSS変数・カラーコード・フォント指定等を抽出。視覚的な分析はできないがテキストベースの情報は取れる
3. **ユーザーにスクリーンショットを依頼**: 上記が使えない場合のフォールバック

### Step 2: 体系的分析

PDFリバースガイドチェックリスト（後述）に沿って各要素を観察し、分析結果を構造化サマリーとしてユーザーに提示する。

**注意**:

- HEXカラーはPDF/画像からの推定値。ユーザーに「推定値です。必要に応じて調整してください」と明記すること
- 分析時は「汎用スタイル原則」に従い、業種・固有名詞に依存しない視覚的特徴の抽出に集中すること

### Step 3: スタイルJSON生成

1. **フル版テンプレート**（[references/style_json_framework.md](references/style_json_framework.md) セクション6.1）をベースに開始する
2. チェックリストで観察できた要素は **全て記述** する — 任意フィールドも積極的に埋める
3. 特に `illustration_style_guide` の `parameters` を厚く書く（スライドの見た目に最も影響する）
4. `description` 欄には「どこに使うか」+「どんな効果を狙うか」を両方書く
5. **目標: 4000〜4800文字**。不足時はリッチ化チェックリスト（後述）で肉付けする
6. 5000文字超過時のみ圧縮テクニック表（後述）を適用
7. 詳細なフィールド定義は [references/style_json_framework.md](references/style_json_framework.md) セクション3を参照

### Step 4: 検証・圧縮

```bash
python scripts/validate_style_json.py <output_path>
```

5000文字を超過した場合、圧縮テクニック表（後述）を優先度順に適用して再検証。

### Step 5: 出力

- プリアンブル「スタイルは下記を適用すること。」+ 改行 + minified JSON の構成でファイルに書き出す
- ファイル名は `style.json`（同名が存在する場合は `style_2.json` 等）
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
"No cluttered backgrounds", "No animations or transitions",
"No industry-specific icons or symbols"
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

## リッチ化チェックリスト

JSON生成後、4000文字未満の場合は以下を順にチェックして肉付けする:

- [ ] color_palette: 4〜5色あるか？ description は「どこに＋どんな効果」を書いているか？
- [ ] typography: headings/body 以外に labels, caption, code を追加できるか？ size を指定しているか？
- [ ] illustration_style_guide.parameters: perspective, line_work, shading, fill, color_rule を記述したか？
- [ ] motifs: 具体的なモチーフを3つ以上列挙したか？
- [ ] effects: テクスチャやエフェクトの指定があるか？
- [ ] negative_prompts: 5個以上あるか？（素材固有の禁止事項を含む）
- [ ] slide_layout_structure: diagram_placement or patterns を追加したか？
- [ ] content_tone_and_voice: vocabulary, structure を追加したか？

---

## 5000文字超過時の圧縮テクニック

**5000文字を超過した場合のみ**、優先度順に適用する。

| 優先度 | テクニック | 効果 |
| --- | --- | --- |
| 1 | **description を簡潔に** — 「なぜその色か」ではなく「どこに使うか」だけに | 大 |
| 2 | **キー名を短縮** — `font_family`→`font`, `accent_highlight`→`accent` 等 | 中 |
| 3 | **日本語で書く** — 英語より情報密度が高い。技術用語は英語のまま | 中 |
| 4 | **任意フィールドを取捨選択** — `size`, `opacity` 等の数値はNLMが推測可能 | 中 |
| 5 | **negative_prompts を厳選** — 4〜5個に絞る | 小 |
| 6 | **structure を省略** — `style` だけでトーンが十分伝わるなら不要 | 小 |

**目標: 4,000〜4,800文字**。超過した場合のみ上記を適用して5000文字以内に収める。

---

## ミニマル版テンプレート（フォールバック用）

通常はフル版テンプレート（references セクション6.1）を使用すること。ユーザーが明示的に軽量版を要求した場合のみ使用。

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
