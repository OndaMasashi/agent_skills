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
| `youtube.com/watch`, `youtu.be/`, `/shorts/` | YouTube | youtube-fetch スキル |
| `.pdf` で終わるURL | PDF | curl + pdftotext |
| その他 HTTP/HTTPS | Web記事 | WebFetch / trafilatura |

## YouTube抽出

`youtube-fetch` スキルの手順で取得する（題名・概要欄・チャプター・時刻つき字幕を 1 つの Markdown にまとめる）。取り方をこのスキルに書き写さないこと（YouTube 側の変更への対応を 1 か所にまとめるため）。

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

- **YouTube**: youtube-fetch スキル（uv が要る）
- **記事**: WebFetchツール
- **PDF**: curl + pdftotext（poppler-utils）
