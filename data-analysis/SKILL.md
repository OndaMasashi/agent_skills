---
name: data-analysis
description: データの探索的分析(EDA)、可視化、レポート生成を包括的に行います。「データを分析して」「EDAを実行」「分析レポートを作成」「データ品質チェック」といった指示で使用。pandas, matplotlib, seaborn, plotlyを活用し、統計分析から仮説生成までカバーします。単純なCSV分析にはcsv-data-summarizerを、財務分析にはfinancial-modelingを使用してください。
metadata:
  author: Antigravity (inspired by liangdabiao/claude-data-analysis)
  version: "1.0.0"
  source: https://github.com/liangdabiao/claude-data-analysis
---

> [!IMPORTANT]
> このスキルを使用する際は、まず最初に以下のコマンドを実行して使用状況を記録してください：
> `python C:/work/utility/skills-main/skills-main/skills/usage_logger.py data-analysis`

# データ分析アシスタント

## Overview

6つの分析観点を体系的にカバーする包括的データ分析ワークフロー。

| 観点 | 内容 |
|------|------|
| **データ探索** | 構造把握、基本統計、分布、外れ値検出 |
| **可視化** | 散布図、ヒートマップ、箱ひげ図、時系列グラフ |
| **品質検証** | 欠損値、重複、型不整合、異常値 |
| **コード生成** | 再利用可能な分析スクリプト出力 |
| **レポート作成** | Markdown/HTML形式の分析レポート |
| **仮説生成** | データパターンからの仮説提案 |

## 分析ワークフロー

### Step 1: データ探索

```python
import pandas as pd

df = pd.read_csv("data.csv")  # or read_excel, read_json

# 基本情報
print(f"Shape: {df.shape}")
print(f"\nデータ型:\n{df.dtypes}")
print(f"\n基本統計:\n{df.describe(include='all')}")
print(f"\n欠損値:\n{df.isnull().sum()}")
print(f"\nユニーク値:\n{df.nunique()}")

# 外れ値検出 (IQR法)
numeric_cols = df.select_dtypes(include='number').columns
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).sum()
    if outliers > 0:
        print(f"  {col}: {outliers}件の外れ値")
```

### Step 2: 可視化

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 日本語フォント設定（Windows）
plt.rcParams['font.family'] = 'MS Gothic'

# 数値列の分布
fig, axes = plt.subplots(1, min(len(numeric_cols), 4), figsize=(16, 4))
for i, col in enumerate(numeric_cols[:4]):
    sns.histplot(df[col], ax=axes[i] if len(numeric_cols) > 1 else axes, kde=True)
    axes[i].set_title(col) if len(numeric_cols) > 1 else axes.set_title(col)
plt.tight_layout()
plt.savefig("distributions.png", dpi=150)

# 相関マトリックス
if len(numeric_cols) >= 2:
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='RdBu_r', center=0)
    plt.title("相関マトリックス")
    plt.tight_layout()
    plt.savefig("correlation.png", dpi=150)

# カテゴリ × 数値のクロス分析
cat_cols = df.select_dtypes(include='object').columns
if len(cat_cols) > 0 and len(numeric_cols) > 0:
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x=cat_cols[0], y=numeric_cols[0])
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("category_analysis.png", dpi=150)
```

### Step 3: 品質検証

```python
def data_quality_report(df):
    """データ品質レポート"""
    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "duplicate_rows": df.duplicated().sum(),
        "missing_values": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().sum() / len(df) * 100).to_dict(),
    }

    # 型の不整合チェック
    for col in df.columns:
        if df[col].dtype == 'object':
            numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
            if 0 < numeric_count < len(df[col].dropna()):
                report.setdefault("mixed_types", []).append(col)

    return report
```

### Step 4: レポート生成

分析結果をMarkdownレポートとして出力する際の構成：

```markdown
# データ分析レポート: [データセット名]

## 1. データ概要
- レコード数、カラム数、期間
- データソースと取得日

## 2. 主要な発見
- 発見1: [統計的根拠]
- 発見2: [統計的根拠]

## 3. 可視化
- [グラフ画像の埋め込み]

## 4. データ品質
- 欠損値の状況
- 外れ値の検出結果

## 5. 推奨アクション
- 次のステップの提案
```

## 対応データ形式

- CSV（`.csv`）
- Excel（`.xlsx`, `.xls`）
- JSON（`.json`）
- SQLクエリ結果

## 注意事項

- 日本語データは文字コードに注意（UTF-8 / Shift_JIS / CP932）
- 大規模データ（100万行超）は `df.sample(n=10000)` でサンプリング
- plotlyを使用する場合は `pip install plotly` が必要
