---
name: ml-data-guardian
description: "MLパイプラインの特徴量生成・外部データ結合・予測データ作成・提出ファイル生成時に、train/testデータの整合性チェックを能動的に提案するスキル。トリガー: 「特徴量を生成」「予測データを作成」「パイプライン実行」「提出ファイル作成」「テストデータ作成」「外部データをマージ」等のMLパイプライン作業。単純なEDAやデータ探索にはdata-analysisを、CSV要約にはcsv-data-summarizerを使用してください。"
metadata:
  author: Antigravity
  version: "1.0.0"
  category: development
  tags: [ml, validation, data-quality, pipeline]
---

> [!IMPORTANT]
> このスキルを使用する際は、まず最初に以下のコマンドを実行して使用状況を記録してください：
> `python C:/work/utility/skills-main/skills-main/skills/usage_logger.py ml-data-guardian`

# ML Data Guardian — MLパイプライン整合性チェック

## コア原則

**CVの合格は予測データの正常性を保証しない。**

交差検証(CV)は訓練データ内で評価されるため、予測データ（テストデータ）固有の問題は検出できない。外部データの欠損、merge失敗、スキーマ変更などは、パイプライン各工程で予防的にチェックしなければ提出後まで発覚しない。

## 能動的提案プロトコル

### いつ提案するか

以下のマイルストーンを検知したら、作業を進める**前に**ユーザーへチェック実行を提案する:

| マイルストーン | 検知シグナル |
|---------------|-------------|
| 特徴量生成完了 | feature engineering スクリプト実行、新カラム追加 |
| 外部データ結合 | merge/join/concat 操作、外部CSV読み込み |
| Train/Test分布確認 | データ分割、テストデータ確定、予測用データ作成 |
| 予測値生成 | model.predict() 実行、予測ファイル出力 |
| 提出ファイル作成 | submission CSV 生成、最終出力ファイル作成 |

### どう提案するか

```
「データ整合性チェックを実行しますか？
 [{マイルストーン名}] の段階で以下の検証が推奨されます：
 - {該当チェック項目のリスト}」
```

### ルール

- **1会話1マイルストーン1回**: 同じマイルストーンへの再提案はしない
- **拒否時は即続行**: ユーザーが断ったら説明や説得をせず作業を続ける
- **結果を明示**: チェック実行時は PASS / WARNING / FAIL を明確に表示する

## チェックポイント詳細

### CP1: 特徴量生成完了

特徴量生成スクリプト実行後、train と test（予測用）データの特徴量を比較する。

**チェック項目:**
- 特徴量ごとのNaN率（train vs test）
- カラムスキーマの一致（train にあって test にない列、またはその逆）

```python
import pandas as pd

def check_feature_consistency(train_df, test_df, threshold=0.1):
    """特徴量の整合性チェック"""
    results = []

    # カラムスキーマ比較
    train_only = set(train_df.columns) - set(test_df.columns)
    test_only = set(test_df.columns) - set(train_df.columns)
    if train_only:
        results.append(f"FAIL: train にのみ存在する列: {train_only}")
    if test_only:
        results.append(f"FAIL: test にのみ存在する列: {test_only}")

    # NaN率比較
    common_cols = sorted(set(train_df.columns) & set(test_df.columns))
    train_nan = train_df[common_cols].isnull().mean()
    test_nan = test_df[common_cols].isnull().mean()
    diff = (test_nan - train_nan).abs()
    flagged = diff[diff > threshold]
    if not flagged.empty:
        results.append(f"WARNING: NaN率乖離 (>{threshold}):")
        for col in flagged.index:
            results.append(
                f"  {col}: train={train_nan[col]:.3f}, test={test_nan[col]:.3f}"
            )

    # 全列NaNチェック（致命的）
    all_nan_cols = test_df.columns[test_df.isnull().all()].tolist()
    if all_nan_cols:
        results.append(f"FAIL: test で全行NaNの列: {all_nan_cols}")

    if not results:
        results.append("PASS: 特徴量の整合性に問題なし")
    for r in results:
        print(r)
```

### CP2: 外部データ結合

外部データ（API取得、スクレイピング、手動作成など）の merge/join 後に実行する。

**チェック項目:**
- Joinのマッチ率（結合前後の行数変化）
- merge によって新たに発生したNaN

```python
def check_merge_quality(original_df, merged_df, merge_keys, new_columns):
    """外部データ結合の品質チェック"""
    results = []

    # 行数変化
    row_diff = len(merged_df) - len(original_df)
    if row_diff != 0:
        results.append(
            f"WARNING: 行数変化 {len(original_df)} -> {len(merged_df)} (差: {row_diff})"
        )

    # 新規列のNaN率
    for col in new_columns:
        if col in merged_df.columns:
            nan_rate = merged_df[col].isnull().mean()
            if nan_rate == 1.0:
                results.append(f"FAIL: {col} が全行NaN（結合キー不一致の可能性）")
            elif nan_rate > 0.5:
                results.append(f"WARNING: {col} のNaN率 = {nan_rate:.1%}")

    # キー列のマッチ率
    if merge_keys:
        for key in merge_keys:
            if key in merged_df.columns:
                match_rate = merged_df[key].notna().mean()
                results.append(f"INFO: キー列 '{key}' マッチ率 = {match_rate:.1%}")

    if not results:
        results.append("PASS: 結合品質に問題なし")
    for r in results:
        print(r)
```

### CP3: Train/Test 分布比較

テストデータ確定後、特徴量の分布が訓練データと大きく乖離していないか確認する。

**チェック項目:**
- 特徴量ごとの mean/std 比較
- 値域（min/max）の逸脱

```python
def check_distribution_drift(train_df, test_df, std_threshold=2.0):
    """訓練/テストデータの分布比較"""
    results = []
    numeric_cols = train_df.select_dtypes(include="number").columns
    common_cols = sorted(set(numeric_cols) & set(test_df.columns))

    for col in common_cols:
        tr = train_df[col].dropna()
        te = test_df[col].dropna()
        if len(tr) == 0 or len(te) == 0:
            continue
        mean_diff = abs(tr.mean() - te.mean())
        tr_std = tr.std()
        if tr_std > 0 and mean_diff / tr_std > std_threshold:
            results.append(
                f"WARNING: {col} 平均値乖離 "
                f"(train={tr.mean():.3f}, test={te.mean():.3f}, "
                f"差={mean_diff/tr_std:.1f}σ)"
            )
        if te.min() < tr.min() or te.max() > tr.max():
            results.append(
                f"INFO: {col} 値域逸脱 "
                f"(train=[{tr.min():.3f}, {tr.max():.3f}], "
                f"test=[{te.min():.3f}, {te.max():.3f}])"
            )

    if not results:
        results.append("PASS: 分布に大きな乖離なし")
    for r in results:
        print(r)
```

### CP4: 予測値生成

model.predict() 実行後、入力データと予測値の妥当性を確認する。

**チェック項目:**
- 入力特徴量にNaNが含まれていないか
- 予測値の分布が妥当か（ドメイン固有の常識チェック）

```python
def check_predictions(input_df, predictions, expected_range=(0, 1)):
    """予測値の妥当性チェック"""
    results = []

    # 入力特徴量のNaN
    nan_cols = input_df.columns[input_df.isnull().any()].tolist()
    if nan_cols:
        nan_rates = input_df[nan_cols].isnull().mean()
        results.append(f"WARNING: 予測入力にNaN含有列:")
        for col in nan_cols:
            results.append(f"  {col}: NaN率 = {nan_rates[col]:.1%}")

    # 予測値の範囲チェック
    lo, hi = expected_range
    out_of_range = ((predictions < lo) | (predictions > hi)).sum()
    if out_of_range > 0:
        results.append(
            f"FAIL: 予測値が期待範囲 [{lo}, {hi}] 外: {out_of_range}件"
        )

    # 予測値の基本統計
    results.append(
        f"INFO: 予測値統計 — "
        f"mean={predictions.mean():.4f}, std={predictions.std():.4f}, "
        f"min={predictions.min():.4f}, max={predictions.max():.4f}"
    )

    for r in results:
        print(r)
```

### CP5: 提出ファイル作成

提出前の最終チェック。全チェックポイントの総まとめ。

**チェック項目:**
- 行数が期待値と一致するか
- NaN が含まれていないか
- 値域が期待範囲内か

```python
def check_submission(submission_df, expected_rows=None, id_col="ID",
                     pred_col="Pred", expected_range=(0, 1)):
    """提出ファイルの最終チェック"""
    results = []

    # 行数チェック
    if expected_rows and len(submission_df) != expected_rows:
        results.append(
            f"FAIL: 行数不一致 (期待={expected_rows}, 実際={len(submission_df)})"
        )

    # NaNチェック
    nan_count = submission_df.isnull().sum().sum()
    if nan_count > 0:
        nan_detail = submission_df.isnull().sum()
        nan_cols = nan_detail[nan_detail > 0]
        results.append(f"FAIL: NaN検出 ({nan_count}件):")
        for col, cnt in nan_cols.items():
            results.append(f"  {col}: {cnt}件")

    # 重複IDチェック
    if id_col in submission_df.columns:
        dup_count = submission_df[id_col].duplicated().sum()
        if dup_count > 0:
            results.append(f"FAIL: ID重複 {dup_count}件")

    # 予測値の範囲
    if pred_col in submission_df.columns:
        vals = submission_df[pred_col]
        lo, hi = expected_range
        out = ((vals < lo) | (vals > hi)).sum()
        if out > 0:
            results.append(f"FAIL: 予測値が範囲外 [{lo},{hi}]: {out}件")
        results.append(
            f"INFO: 予測値統計 — "
            f"mean={vals.mean():.4f}, std={vals.std():.4f}"
        )

    if not any("FAIL" in r for r in results):
        results.insert(0, "PASS: 提出ファイルの最終チェック合格")
    for r in results:
        print(r)
```

## クイックリファレンス

| CP | マイルストーン | FAIL条件（即対応） | WARNING条件（要確認） |
|----|--------------|-------------------|---------------------|
| 1 | 特徴量生成 | 全行NaN列あり / スキーマ不一致 | NaN率乖離 >10% |
| 2 | 外部データ結合 | 新規列が全NaN | NaN率 >50% / 行数変化 |
| 3 | 分布比較 | — | 平均値乖離 >2σ / 値域逸脱 |
| 4 | 予測値生成 | 予測値が期待範囲外 | 入力にNaN含有 |
| 5 | 提出ファイル | NaN / 行数不一致 / ID重複 | — |

## ネガティブトリガー

以下の場合はこのスキルを発動しない:
- 単純なデータ探索・EDA → **data-analysis** スキルを使用
- CSV ファイルの要約 → **csv-data-summarizer** スキルを使用
- ハイパーパラメータチューニング・モデル選択（データ整合性と無関係）
- 可視化のみの作業
