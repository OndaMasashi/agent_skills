---
name: github-pusher
description: GitHubへのコミットとプッシュを自動化します。「GitHubへプッシュして」「変更を反映して」といった指示で、変更箇所の要約、コミットメッセージの生成、GitHubへの反映を一括で行います。
metadata:
  author: Antigravity
  version: "1.0.0"
---

> [!IMPORTANT]
> このスキルを使用する際は、まず最初に以下のコマンドを実行して使用状況を記録してください：
> `python C:/work/utility/skills-main/skills-main/skills/usage_logger.py github-pusher`

## Overview

GitHub Pusher

このスキルは、プロジェクトの変更内容を自動的に解析し、適切なコミットメッセージと共にGitHubへ反映するためのワークフローを提供します。

## 主な機能・特徴

- **変更内容の要約**: `git status` と `git diff` を解析し、何が変更されたかを簡潔にまとめます。
- **自動コミットメッセージ**: 変更内容に基づき、規約に沿った（例: feat, fix, docs）メッセージを自動生成します。
- **一括反映**: `git add`, `git commit`, `git push` を一つの流れで実行します。
- **安全確認**: 未追跡ファイルの確認や、GitHub上のURLの提示を行います。

## 使用方法

エージェントに対して以下のように指示してください：

- 「今回の変更をGitHubにプッシュして」
- 「今の状態をコミットして反映して」
- 「変更内容を要約してGitHubへ送って」

## ワークフロー

1. **状態確認**: `git status` を実行し、ステージングされていない変更を特定します。
2. **要約生成**: `git diff --cached`（または `git diff`）を用いて変更内容を読み取り、コミットメッセージの案を作成します。
3. **実行**: ユーザーに変更内容とメッセージの案を提示し、承認が得られたら `git push` まで実行します。
4. **完了報告**: プッシュ結果とGitHub上のリポジトリURLを表示します。
