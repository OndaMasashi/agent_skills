---
name: csv-data-summarizer
description: CSVファイルを自動分析し、統計サマリーと可視化を即時生成します。「CSVを分析して」「データを要約して」「CSVの傾向を見せて」といった指示で使用。pandas, matplotlib, seabornを用いた包括的な分析を質問なしで即実行します。Excel/スプレッドシートの作成・編集には使わないでください（xlsxスキルを使用）。
metadata:
  author: coffeefuelbump
  version: "2.1.0"
  source: https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill
  dependencies: python>=3.8, pandas>=2.0.0, matplotlib>=3.7.0, seaborn>=0.12.0
---
# CSV Data Summarizer

CSVファイルをアップロードまたは指定されたら、**質問せずに即座に包括的な分析を実行する**。

## 重要な行動原則

- ユーザーに「何をしたいですか？」と聞かない
- 選択肢を提示しない
- 即座に分析を実行し、結果を全て表示する

## 自動分析フロー

1. **データ読込・構造把握**: pandas DataFrameに読込、カラム型・日付列・数値列・カテゴリ列を特定
2. **データ型に応じた分析を自動選択**:
   - 売上/EC系 → 時系列トレンド、売上分析、商品別パフォーマンス
   - 顧客系 → 分布分析、セグメンテーション、地域パターン
   - 財務系 → トレンド分析、統計サマリー、相関分析
   - 業務系 → 時系列、パフォーマンス指標、分布
   - アンケート系 → 頻度分析、クロス集計、分布
3. **意味のある可視化のみ生成**:
   - 時系列プロット → 日付/タイムスタンプ列が存在する場合のみ
   - 相関ヒートマップ → 複数の数値列が存在する場合のみ
   - カテゴリ分布 → カテゴリ列が存在する場合のみ
   - ヒストグラム → 数値分布が関連する場合
4. **包括的な出力を一度に生成**:
   - データ概要（行数、列数、型）
   - データ型に関連する主要統計・指標
   - 欠損データ分析
   - 関連する複数の可視化
   - パターンに基づくアクショナブルなインサイト

## コード例

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# データ読込
df = pd.read_csv("data.csv")

# 基本統計
print(f"行数: {len(df)}, 列数: {len(df.columns)}")
print(df.describe())
print(f"\n欠損値:\n{df.isnull().sum()}")

# 数値列の相関
numeric_cols = df.select_dtypes(include='number').columns
if len(numeric_cols) >= 2:
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm')
    plt.title("相関ヒートマップ")
    plt.tight_layout()
    plt.savefig("correlation.png", dpi=150)

# カテゴリ列の分布
cat_cols = df.select_dtypes(include='object').columns
for col in cat_cols[:3]:
    plt.figure(figsize=(8, 4))
    df[col].value_counts().head(10).plot(kind='bar')
    plt.title(f"{col}の分布")
    plt.tight_layout()
    plt.savefig(f"dist_{col}.png", dpi=150)
```

## 注意事項

- 日本語を含むCSVは `encoding='utf-8'` または `encoding='cp932'` で読込
- matplotlib日本語対応: `plt.rcParams['font.family'] = 'MS Gothic'`（Windows）
- 大規模データ（10万行超）はサンプリングして可視化
