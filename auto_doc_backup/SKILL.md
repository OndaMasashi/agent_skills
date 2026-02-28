---
name: auto_doc_backup
description: implementation_planやwalkthroughの自動バックアップを行います。重要なドキュメントが更新された際、所定のフォルダにタイムスタンプ付きで保存することをAIに指示します。
---

> [!IMPORTANT]
> このスキルを使用する際は、まず最初に以下のコマンドを実行して使用状況を記録してください：
> `python C:/work/utility/skills-main/skills-main/skills/usage_logger.py auto_doc_backup`

# Auto Document Backup Skill

## Description

`implementation_plan` または `walkthrough` が作成・更新された際に、プロジェクト内の特定のディレクトリに自動的にバックアップコピーを保存します。

## Guidelines

1. **トリガー条件**:
    - AIが `implementation_plan` 型のアーティファクトを作成または更新したとき。
    - AIが `walkthrough` 型のアーティファクトを作成または更新したとき。

2. **保存先の振り分け**:
    - `implementation_plan`: プロジェクトルートの `/doc_implementation/` フォルダ。
    - `walkthrough`: プロジェクトルートの `/doc_walkthrough/` フォルダ。

3. **ファイル命名規則**:
    - 形式: `[Type]_[YYYYMMDD]_[HHMM].md`
    - 例: `plan_20260118_2100.md` / `walkthrough_20260118_2100.md`

4. **動作フロー**:
    - 保存先フォルダが存在しない場合は、自動的に作成してください。
    - アーティファクトの生成・編集が終わった直後に、バックアップファイルを書き出すツール（`write_to_file`）を実行してください。

## Example Actions

- `implementation_plan` を作成した。
- → `c:/work/project/doc_implementation/plan_20260118_2100.md` に内容をコピー。
- `walkthrough` を更新した。
- → `c:/work/project/doc_walkthrough/walkthrough_20260118_2105.md` に内容をコピー。
