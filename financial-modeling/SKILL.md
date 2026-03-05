---
name: financial-modeling
description: 財務モデリングと分析を行います。「DCF分析をして」「財務モデルを作成」「感応度分析」「WACC計算」「モンテカルロシミュレーション」といった指示で使用。企業価値評価、投資分析、財務予測をExcelまたはPythonで実装します。単純なExcel作成にはxlsxスキルを使用してください。
metadata:
  author: Antigravity
  version: "1.0.0"
  category: business-analysis
---

> [!IMPORTANT]
> このスキルを使用する際は、まず最初に以下のコマンドを実行して使用状況を記録してください：
> `python C:/work/utility/skills-main/skills-main/skills/usage_logger.py financial-modeling`

> **思考モード**: このスキルはDCF・感応度分析・モンテカルロ等の複合的な数値推論を伴うため、パラメータ選定・結果解釈の前に `ultrathink` で深く考えること。

# 財務モデリングガイド

## Overview

中小企業の経営分析・事業価値評価に必要な財務モデリング手法を提供します。

## 対応する分析手法

| 手法 | 用途 | 出力 |
|------|------|------|
| **DCF (割引キャッシュフロー)** | 企業価値評価 | Excel / Python |
| **WACC** | 資本コスト計算 | 数値 |
| **感応度分析** | パラメータ変動の影響 | 表・ヒートマップ |
| **モンテカルロ** | リスク評価・確率分布 | ヒストグラム |
| **財務比率分析** | 収益性・安全性・効率性 | 表 |
| **CVP分析** | 損益分岐点 | グラフ |

## DCF分析

```python
import numpy as np

def dcf_valuation(fcf_projections, wacc, terminal_growth_rate, shares_outstanding):
    """DCF法による企業価値評価"""
    n = len(fcf_projections)

    # 各年度のFCFを現在価値に割引
    pv_fcf = [fcf / (1 + wacc) ** (i + 1) for i, fcf in enumerate(fcf_projections)]

    # ターミナルバリュー（永続成長モデル）
    terminal_value = fcf_projections[-1] * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
    pv_terminal = terminal_value / (1 + wacc) ** n

    # 企業価値
    enterprise_value = sum(pv_fcf) + pv_terminal

    return {
        "enterprise_value": enterprise_value,
        "pv_fcf_total": sum(pv_fcf),
        "pv_terminal_value": pv_terminal,
        "equity_value_per_share": enterprise_value / shares_outstanding,
        "terminal_value_pct": pv_terminal / enterprise_value * 100,
    }
```

## WACC計算

```python
def calc_wacc(equity_value, debt_value, cost_of_equity, cost_of_debt, tax_rate):
    """加重平均資本コスト"""
    total = equity_value + debt_value
    wacc = (equity_value / total) * cost_of_equity + (debt_value / total) * cost_of_debt * (1 - tax_rate)
    return wacc
```

## 感応度分析

```python
import pandas as pd

def sensitivity_analysis(base_fcf, wacc_range, growth_range, shares):
    """WACCと成長率の感応度テーブル"""
    results = []
    for wacc in wacc_range:
        row = {}
        for g in growth_range:
            val = dcf_valuation(base_fcf, wacc, g, shares)
            row[f"g={g:.1%}"] = round(val["equity_value_per_share"])
        results.append(row)

    df = pd.DataFrame(results, index=[f"WACC={w:.1%}" for w in wacc_range])
    return df
```

## モンテカルロシミュレーション

```python
import numpy as np
import matplotlib.pyplot as plt

def monte_carlo_dcf(base_fcf, n_simulations=10000):
    """モンテカルロ法によるDCFバリュエーション"""
    results = []
    for _ in range(n_simulations):
        wacc = np.random.normal(0.10, 0.02)
        growth = np.random.normal(0.02, 0.01)
        fcf_var = [f * np.random.normal(1.0, 0.1) for f in base_fcf]
        val = dcf_valuation(fcf_var, max(wacc, 0.01), max(growth, 0.001), 1000000)
        results.append(val["equity_value_per_share"])

    plt.figure(figsize=(10, 6))
    plt.hist(results, bins=50, edgecolor='black', alpha=0.7)
    plt.axvline(np.median(results), color='red', linestyle='--', label=f'中央値: {np.median(results):,.0f}')
    plt.xlabel("1株あたり価値")
    plt.ylabel("頻度")
    plt.title("モンテカルロシミュレーション結果")
    plt.legend()
    plt.savefig("monte_carlo.png", dpi=150)

    return {
        "mean": np.mean(results),
        "median": np.median(results),
        "std": np.std(results),
        "p5": np.percentile(results, 5),
        "p95": np.percentile(results, 95),
    }
```

## 財務比率分析

```python
def financial_ratios(revenue, cogs, operating_income, net_income,
                     total_assets, total_equity, current_assets, current_liabilities,
                     interest_expense=0, total_debt=0):
    """主要財務指標の計算"""
    return {
        "収益性": {
            "売上総利益率": (revenue - cogs) / revenue,
            "営業利益率": operating_income / revenue,
            "当期純利益率": net_income / revenue,
            "ROA": net_income / total_assets,
            "ROE": net_income / total_equity,
        },
        "安全性": {
            "流動比率": current_assets / current_liabilities,
            "自己資本比率": total_equity / total_assets,
            "負債比率": total_debt / total_equity if total_equity > 0 else None,
            "インタレストカバレッジ": operating_income / interest_expense if interest_expense > 0 else None,
        },
        "効率性": {
            "総資産回転率": revenue / total_assets,
        },
    }
```

## CVP分析（損益分岐点）

```python
def breakeven_analysis(fixed_costs, variable_cost_per_unit, price_per_unit):
    """損益分岐点分析"""
    contribution_margin = price_per_unit - variable_cost_per_unit
    breakeven_units = fixed_costs / contribution_margin
    breakeven_revenue = breakeven_units * price_per_unit
    return {
        "breakeven_units": breakeven_units,
        "breakeven_revenue": breakeven_revenue,
        "contribution_margin": contribution_margin,
        "contribution_margin_ratio": contribution_margin / price_per_unit,
    }
```

## ワークフロー

1. 財務データの入力（CSV/Excel/手入力）
2. 必要な分析手法の選択（ユーザー指示に基づく）
3. 計算実行
4. 結果をExcel（xlsxスキル）またはグラフで出力
5. 感応度分析やシナリオ分析で堅牢性を検証
