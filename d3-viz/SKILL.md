---
name: d3-viz
description: D3.jsを使ったインタラクティブなデータ可視化を作成します。「D3でグラフを作って」「インタラクティブなチャートを」「ネットワーク図を」「ヒートマップをD3で」といった指示で使用。棒グラフ、折れ線、散布図、ネットワーク図、コード図、ヒートマップ等に対応。React/Vue/Svelte/バニラJS対応。静的なmatplotlib/seabornグラフにはdata-analysisスキルを使用。
metadata:
  author: chrisvoncsefalvay
  version: "1.0.0"
  source: https://github.com/chrisvoncsefalvay/claude-d3js-skill
---

> [!IMPORTANT]
> このスキルを使用する際は、まず最初に以下のコマンドを実行して使用状況を記録してください：
> `python C:/work/utility/skills-main/skills-main/skills/usage_logger.py d3-viz`

# D3.js Visualization

## When to use d3.js

**Use for:** カスタムチャート、インタラクティブ可視化、ネットワーク図、地理可視化、アニメーション付きトランジション
**Alternative:** 3D → Three.js、静的グラフ → matplotlib/seaborn

## Setup

```javascript
import * as d3 from 'd3';
// or CDN: <script src="https://d3js.org/d3.v7.min.js"></script>
```

## 基本構造

```javascript
function drawChart(data) {
  const svg = d3.select('#chart');
  svg.selectAll("*").remove();

  const width = 800, height = 400;
  const margin = { top: 20, right: 30, bottom: 40, left: 50 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const xScale = d3.scaleLinear().domain([0, d3.max(data, d => d.x)]).range([0, innerW]);
  const yScale = d3.scaleLinear().domain([0, d3.max(data, d => d.y)]).range([innerH, 0]);

  g.append("g").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(xScale));
  g.append("g").call(d3.axisLeft(yScale));

  g.selectAll("circle").data(data).join("circle")
    .attr("cx", d => xScale(d.x)).attr("cy", d => yScale(d.y))
    .attr("r", 5).attr("fill", "steelblue");
}
```

## 主要チャートパターン

### 棒グラフ
`d3.scaleBand()` + `rect` 要素

### 折れ線グラフ
`d3.line()` + `.curve(d3.curveMonotoneX)` + `path`

### 散布図
`circle` + `xScale/yScale` + オプションでサイズ・色エンコーディング

### 円グラフ
`d3.pie()` + `d3.arc()`

### ヒートマップ
`d3.scaleBand()` × 2 + `d3.scaleSequential(d3.interpolateYlOrRd)` + `rect`

### コード図
`d3.chord()` + `d3.ribbon()` — 関係性の可視化

### Force-directed ネットワーク
`d3.forceSimulation()` + `forceLink/forceManyBody/forceCenter`

## インタラクティビティ

- **ツールチップ**: `mouseover/mousemove/mouseout` + 絶対配置div
- **ズーム/パン**: `d3.zoom().scaleExtent([0.5, 10])`
- **クリック**: `on("click", (event, d) => ...)`
- **ドラッグ**: `d3.drag().on("start/drag/end", ...)`

## トランジション

```javascript
elements.transition().duration(750).delay((d, i) => i * 50)
  .ease(d3.easeBounceOut).attr("r", 10);
```

## ベストプラクティス

- データバリデーション: `filter(d => d.value != null && !isNaN(d.value))`
- アクセシビリティ: `svg.attr("role", "img").attr("aria-label", "...")`
- パフォーマンス: 1000要素超はCanvasを検討
- レスポンシブ: `ResizeObserver` または `window.resize`
