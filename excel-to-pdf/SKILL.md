---
name: excel-to-pdf
description: ExcelファイルをPDFに変換します。「ExcelをPDFに変換して」「xlsxをPDF化」といった指示で、書式を保持したPDF出力を行います。LibreOffice利用の高忠実度変換とPython純正の軽量変換に対応。ExcelやPDFの作成・編集自体には使わないでください（それぞれxlsx, pdfスキルを使用）。
---
# Excel→PDF変換ガイド

## Overview

ExcelファイルをPDFに変換する2つの方式を提供します。

| 方式 | 忠実度 | 速度 | 要件 |
|------|--------|------|------|
| **LibreOffice (推奨)** | 高（書式・罫線・グラフ完全再現） | 数秒 | LibreOffice |
| **Python (フォールバック)** | 中（データテーブル中心） | 数秒 | openpyxl, reportlab |

## 判断フロー

1. LibreOfficeが利用可能か確認（`soffice --version`）
2. 利用可能 → Method 1（LibreOffice）を使用
3. 利用不可 → Method 2（Python）を使用
4. または `convert.py` スクリプトに自動判断させる

## Method 1: LibreOffice変換（推奨）

```bash
# 基本コマンド
soffice --headless --convert-to pdf --outdir <出力先ディレクトリ> <input.xlsx>

# 例: 同じディレクトリにPDF出力
soffice --headless --convert-to pdf "report.xlsx"
```

### sofficeパス

| OS | パス |
|----|------|
| Windows | `"C:\Program Files\LibreOffice\program\soffice.exe"` |
| macOS | `/Applications/LibreOffice.app/Contents/MacOS/soffice` |
| Linux | `soffice`（通常PATHに存在） |

### Python経由

```python
import subprocess
subprocess.run([
    "soffice", "--headless", "--convert-to", "pdf",
    "--outdir", output_dir, input_path
], check=True)
```

## Method 2: Python変換（フォールバック）

LibreOffice未インストール時に使用。データテーブルを読み取り、reportlabでPDF化します。

```python
from openpyxl import load_workbook
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

wb = load_workbook("input.xlsx", data_only=True)
ws = wb.active

data = []
for row in ws.iter_rows(values_only=True):
    data.append([str(c) if c is not None else "" for c in row])

doc = SimpleDocTemplate("output.pdf", pagesize=landscape(A4))
table = Table(data)
table.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("FONTNAME", (0, 0), (-1, -1), "HeiseiMin-W3"),  # 日本語対応
    ("FONTSIZE", (0, 0), (-1, -1), 8),
]))
doc.build([table])
```

## ユーティリティスクリプト

変換スクリプト `convert.py` が同梱されています：

```bash
# 全シート変換（デフォルト）
python convert.py <input.xlsx> [output.pdf]

# 特定シートのみ変換（名前指定）
python convert.py <input.xlsx> --sheets "Sheet1,Sheet3"

# 特定シートのみ変換（0始まりインデックス指定）
python convert.py <input.xlsx> --sheets 0

# 1シート目だけPDF化
python convert.py <input.xlsx> --sheets 0
```

LibreOfficeの検出と変換方式の自動選択を行います。

## 注意事項

- **シート選択**: デフォルトは全シート変換。`--sheets` で名前またはインデックス指定可（両方式対応）
- **日本語フォント**: reportlab使用時は `HeiseiMin-W3`（明朝）または `HeiseiKakuGo-W5`（ゴシック）を指定
- **印刷範囲**: LibreOfficeはExcel内の印刷設定を尊重。Python方式は全データを出力
- **数式**: data_only=True で計算済み値を取得（事前にExcelで開いて保存が必要な場合あり）
