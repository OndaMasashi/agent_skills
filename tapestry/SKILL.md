---
name: tapestry
description: URLからコンテンツを抽出し、アクションプランを自動生成します。「tapestry <URL>」「weave <URL>」「このURLから計画を作って」「動画から学習計画を」といった指示で使用。YouTube動画、Web記事、PDFを自動検出し、コンテンツ抽出→アクションプラン作成を一括で行います。
metadata:
  author: michalparkola
  version: "1.0.0"
  source: https://github.com/michalparkola/tapestry-skills-for-claude-code
  allowed-tools: Bash,Read,Write
---
# Tapestry: コンテンツ抽出 + アクションプラン

## トリガー

- `tapestry <URL>` / `weave <URL>`
- 「このURLから計画を作って」「動画から学んで実装計画を」

## ワークフロー

1. **URL種別検出**: YouTube / Web記事 / PDF を自動判別
2. **コンテンツ抽出**: 適切なツールで本文・トランスクリプトを取得
3. **アクションプラン作成**: 抽出内容からアクショナブルな学習・実装計画を生成
4. **ファイル保存**: コンテンツファイルとプランファイルを保存

## URL判別ロジック

| パターン | 種別 | 抽出方法 |
|---------|------|---------|
| `youtube.com/watch`, `youtu.be/` | YouTube | yt-dlp で字幕取得 |
| `.pdf` で終わるURL | PDF | curl + pdftotext |
| その他 HTTP/HTTPS | Web記事 | WebFetch / trafilatura |

## YouTube抽出

```bash
# yt-dlpで字幕取得
yt-dlp --write-auto-sub --skip-download --sub-langs en,ja --output "transcript" "$URL"
```

## Web記事抽出

WebFetchツールを使用してURLの内容を取得し、本文を抽出する。

## PDF抽出

```bash
curl -L -o document.pdf "$URL"
pdftotext document.pdf document.txt
```

## アクションプラン生成

抽出したコンテンツから以下を作成:

1. **核心的な学び**: 3-5つのアクショナブルな教訓
2. **実装計画**: 具体的なステップ（Rep 1〜5）
3. **今週のアクション**: Rep 1として今週取り組めること

## 出力フォーマット

```
Content: [タイトル].txt
Plan: アクションプラン - [タイトル].md
```

## 依存ツール

- **YouTube**: yt-dlp（`pip install yt-dlp`）
- **記事**: WebFetchツール
- **PDF**: curl + pdftotext（poppler-utils）
