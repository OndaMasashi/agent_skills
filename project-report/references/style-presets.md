# Style Presets — DOCX書式定義

Phase 4 のDOCX生成時に参照する。選択されたスタイルの値を docx-js に適用する。

---

## 共通設定（全スタイル共通）

```javascript
// ページ設定: A4
const PAGE = {
  size: { width: 11906, height: 16838 },  // DXA (A4)
  margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },  // 1 inch
};

// 目次
const TOC = {
  headingRange: { from: 1, to: 3 },
};

// ヘッダー: プロジェクト名を右寄せ
// フッター: ページ番号を中央
// 表紙→目次→本文で改ページ
```

---

## 1. シンプル (Simple B&W)

最小限の装飾。白黒基調のクリーンなビジネス文書。

```javascript
const SIMPLE = {
  fonts: {
    heading: "Arial",
    body: "Arial",
  },
  sizes: {
    title: 28,        // pt (half-points: 56)
    heading1: 18,      // pt (half-points: 36)
    heading2: 14,      // pt (half-points: 28)
    heading3: 12,      // pt (half-points: 24)
    body: 11,          // pt (half-points: 22)
    caption: 9,        // pt (half-points: 18)
  },
  colors: {
    heading: "000000",
    body: "333333",
    accent: "666666",
    tableBorder: "999999",
    tableHeaderBg: "F0F0F0",
    tableHeaderText: "000000",
    tableAltRowBg: "F9F9F9",
  },
  spacing: {
    heading1Before: 360,  // DXA (before spacing)
    heading1After: 200,
    heading2Before: 240,
    heading2After: 120,
    bodyAfter: 120,
    lineSpacing: 276,     // 1.15倍 (240 = single)
  },
  headingStyle: {
    heading1: { bold: true, bottomBorder: { style: "single", size: 6, color: "999999" } },
    heading2: { bold: true },
    heading3: { bold: true },
  },
  table: {
    borderStyle: "single",
    borderSize: 4,
    borderColor: "999999",
    headerShading: { type: "CLEAR", color: "auto", fill: "F0F0F0" },
    cellPadding: { top: 60, bottom: 60, left: 100, right: 100 },
  },
};
```

---

## 2. ブランドカラー (Branded)

ユーザー指定の primary / accent カラーを適用する。

**ユーザーから取得する値**:
- `primaryColor`: メインカラー（例: "1B4F72"）
- `accentColor`: アクセントカラー（例: "E74C3C"）
- `logoPath`: ロゴ画像パス（任意）

```javascript
// primaryColor, accentColor はユーザー入力値で置換
const BRANDED = {
  fonts: {
    heading: "Arial",
    body: "Arial",
  },
  sizes: {
    title: 30,
    heading1: 20,
    heading2: 15,
    heading3: 12,
    body: 11,
    caption: 9,
  },
  colors: {
    heading: "${primaryColor}",
    body: "333333",
    accent: "${accentColor}",
    tableBorder: "${primaryColor}",
    tableHeaderBg: "${primaryColor}",
    tableHeaderText: "FFFFFF",
    tableAltRowBg: "F5F5F5",
  },
  spacing: {
    heading1Before: 360,
    heading1After: 200,
    heading2Before: 240,
    heading2After: 120,
    bodyAfter: 120,
    lineSpacing: 276,
  },
  headingStyle: {
    heading1: { bold: true, bottomBorder: { style: "single", size: 8, color: "${primaryColor}" } },
    heading2: { bold: true, bottomBorder: { style: "single", size: 4, color: "${accentColor}" } },
    heading3: { bold: true },
  },
  table: {
    borderStyle: "single",
    borderSize: 4,
    borderColor: "${primaryColor}",
    headerShading: { type: "CLEAR", color: "auto", fill: "${primaryColor}" },
    cellPadding: { top: 60, bottom: 60, left: 100, right: 100 },
  },
  // ロゴがある場合、表紙の右上に配置
  logo: {
    width: 120,  // pt
    height: 40,  // pt（アスペクト比に応じて調整）
  },
};
```

---

## 3. フォーマル (Formal)

ネイビー系アクセント。保守的で格式あるレイアウト。

```javascript
const FORMAL = {
  fonts: {
    heading: "Arial",
    body: "Arial",
  },
  sizes: {
    title: 28,
    heading1: 18,
    heading2: 14,
    heading3: 12,
    body: 11,
    caption: 9,
  },
  colors: {
    heading: "1B3A5C",       // ダークネイビー
    body: "2C3E50",
    accent: "2E75B6",        // ミディアムブルー
    tableBorder: "1B3A5C",
    tableHeaderBg: "1B3A5C",
    tableHeaderText: "FFFFFF",
    tableAltRowBg: "EBF5FB",
  },
  spacing: {
    heading1Before: 400,
    heading1After: 240,
    heading2Before: 280,
    heading2After: 160,
    bodyAfter: 140,
    lineSpacing: 288,     // 1.2倍
  },
  headingStyle: {
    heading1: { bold: true, bottomBorder: { style: "double", size: 6, color: "1B3A5C" } },
    heading2: { bold: true, bottomBorder: { style: "single", size: 4, color: "2E75B6" } },
    heading3: { bold: true, italics: true },
  },
  table: {
    borderStyle: "single",
    borderSize: 4,
    borderColor: "1B3A5C",
    headerShading: { type: "CLEAR", color: "auto", fill: "1B3A5C" },
    cellPadding: { top: 80, bottom: 80, left: 120, right: 120 },
  },
};
```

---

## 4. モダン (Modern)

鮮やかなアクセント。ゆったりとした余白とサンセリフ中心の現代的デザイン。

```javascript
const MODERN = {
  fonts: {
    heading: "Arial",
    body: "Arial",
  },
  sizes: {
    title: 32,
    heading1: 22,
    heading2: 16,
    heading3: 13,
    body: 11,
    caption: 9,
  },
  colors: {
    heading: "2E75B6",       // ブルーアクセント
    body: "404040",
    accent: "00B0F0",        // ライトブルー
    tableBorder: "D0D0D0",
    tableHeaderBg: "2E75B6",
    tableHeaderText: "FFFFFF",
    tableAltRowBg: "F0F7FC",
  },
  spacing: {
    heading1Before: 480,
    heading1After: 280,
    heading2Before: 320,
    heading2After: 200,
    bodyAfter: 160,
    lineSpacing: 300,     // 1.25倍
  },
  headingStyle: {
    heading1: { bold: true },  // 下線なし: クリーンな印象
    heading2: { bold: true },
    heading3: { bold: true },
  },
  table: {
    borderStyle: "single",
    borderSize: 2,             // 細い罫線
    borderColor: "D0D0D0",
    headerShading: { type: "CLEAR", color: "auto", fill: "2E75B6" },
    cellPadding: { top: 80, bottom: 80, left: 120, right: 120 },
  },
};
```

---

## 5. スタイリッシュ (Stylish)

太字・高コントラスト。ディープネイビー x ビビッドレッドのインパクトあるデザイン。

```javascript
const STYLISH = {
  fonts: {
    heading: "Arial",
    body: "Arial",
  },
  sizes: {
    title: 34,
    heading1: 24,
    heading2: 16,
    heading3: 13,
    body: 11,
    caption: 9,
  },
  colors: {
    heading: "1A1A2E",       // ディープネイビー
    body: "3D3D3D",
    accent: "E94560",        // ビビッドレッド
    tableBorder: "1A1A2E",
    tableHeaderBg: "1A1A2E",
    tableHeaderText: "FFFFFF",
    tableAltRowBg: "F5F0F0",
  },
  spacing: {
    heading1Before: 480,
    heading1After: 240,
    heading2Before: 320,
    heading2After: 160,
    bodyAfter: 140,
    lineSpacing: 288,     // 1.2倍
  },
  headingStyle: {
    heading1: { bold: true, bottomBorder: { style: "thick", size: 10, color: "E94560" } },
    heading2: { bold: true },
    heading3: { bold: true, italics: true },
  },
  table: {
    borderStyle: "single",
    borderSize: 2,
    borderColor: "1A1A2E",
    headerShading: { type: "CLEAR", color: "auto", fill: "1A1A2E" },
    cellPadding: { top: 80, bottom: 80, left: 120, right: 120 },
  },
};
```

---

## 6. エグゼクティブ (Executive)

チャコール x ゴールド。経営層・役員向けの洗練された高級感あるデザイン。

```javascript
const EXECUTIVE = {
  fonts: {
    heading: "Arial",
    body: "Arial",
  },
  sizes: {
    title: 30,
    heading1: 20,
    heading2: 15,
    heading3: 12,
    body: 11,
    caption: 9,
  },
  colors: {
    heading: "2C3E50",       // チャコール
    body: "34495E",
    accent: "C9A84C",        // ゴールド
    tableBorder: "2C3E50",
    tableHeaderBg: "2C3E50",
    tableHeaderText: "F5F0E1",  // ウォームホワイト
    tableAltRowBg: "FAF8F2",
  },
  spacing: {
    heading1Before: 440,
    heading1After: 260,
    heading2Before: 300,
    heading2After: 180,
    bodyAfter: 160,
    lineSpacing: 300,     // 1.25倍
  },
  headingStyle: {
    heading1: { bold: true, bottomBorder: { style: "single", size: 6, color: "C9A84C" } },
    heading2: { bold: true },
    heading3: { bold: true },
  },
  table: {
    borderStyle: "single",
    borderSize: 4,
    borderColor: "2C3E50",
    headerShading: { type: "CLEAR", color: "auto", fill: "2C3E50" },
    cellPadding: { top: 80, bottom: 80, left: 140, right: 140 },
  },
};
```

---

## 7. テック (Tech)

GitHub Dark風。ダークヘッダー x ブルーアクセントのエンジニアリング報告向けデザイン。

```javascript
const TECH = {
  fonts: {
    heading: "Arial",
    body: "Arial",
  },
  sizes: {
    title: 30,
    heading1: 20,
    heading2: 15,
    heading3: 13,
    body: 11,
    caption: 9,
  },
  colors: {
    heading: "0D1117",       // ギットハブダーク
    body: "333333",
    accent: "58A6FF",        // ブルーリンク
    tableBorder: "30363D",
    tableHeaderBg: "0D1117",
    tableHeaderText: "C9D1D9",
    tableAltRowBg: "F0F6FC",
  },
  spacing: {
    heading1Before: 400,
    heading1After: 240,
    heading2Before: 280,
    heading2After: 160,
    bodyAfter: 140,
    lineSpacing: 276,     // 1.15倍
  },
  headingStyle: {
    heading1: { bold: true, bottomBorder: { style: "single", size: 6, color: "58A6FF" } },
    heading2: { bold: true },
    heading3: { bold: true },
  },
  table: {
    borderStyle: "single",
    borderSize: 2,
    borderColor: "30363D",
    headerShading: { type: "CLEAR", color: "auto", fill: "0D1117" },
    cellPadding: { top: 60, bottom: 60, left: 100, right: 100 },
  },
};
```

---

## Mermaid図のスタイル連動

各スタイルプリセットに対応する Mermaid テーマと色設定。mmdc の `-c` オプションで JSON config を指定して適用する。

### mmdc 設定テンプレート

```json
{
  "theme": "<theme>",
  "themeVariables": {
    "primaryColor": "<tableHeaderBg>",
    "primaryTextColor": "<tableHeaderText>",
    "primaryBorderColor": "<tableBorder>",
    "lineColor": "<accent>",
    "secondaryColor": "<tableAltRowBg>",
    "tertiaryColor": "<tableAltRowBg>",
    "fontFamily": "<fonts.body>",
    "fontSize": "14px"
  }
}
```

### スタイル別マッピング

| スタイル | mmdc theme | primaryColor | lineColor | 背景 |
|---------|-----------|-------------|-----------|------|
| シンプル | neutral | F0F0F0 | 666666 | transparent |
| ブランドカラー | base | ${primaryColor} | ${accentColor} | transparent |
| フォーマル | dark | 1B3A5C | 2E75B6 | transparent |
| モダン | default | 2E75B6 | 00B0F0 | transparent |
| スタイリッシュ | dark | 1A1A2E | E94560 | transparent |
| エグゼクティブ | neutral | 2C3E50 | C9A84C | transparent |
| テック | base | 0D1117 | 58A6FF | transparent |

mmdc実行コマンド例:

```bash
mmdc -i diagram.mmd -o diagram.png -w 1600 --scale 2 -b transparent -c mermaid-config.json
```

※ `mermaid-config.json` は一時ファイルとして生成し、DOCX出力後に削除する。

---

## スタイル適用の注意事項

1. **ShadingType**: 必ず `CLEAR` を使用（`SOLID` は使わない）
2. **テーブル幅**: テーブルレベルとセルレベルの両方で指定し、合計を一致させる
3. **WidthType**: テーブルには `DXA` を使用（`PERCENTAGE` は使わない）
4. **フォント**: 日本語テキストにはフォントが適用されない場合があるため、`eastAsia` フォント指定も考慮する
5. **色指定**: `#` なしの6桁16進数で指定（例: "1B3A5C"）
6. **行間**: DXA単位。240 = シングル、276 = 1.15倍、360 = 1.5倍
