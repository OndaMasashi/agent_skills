# Axis Auditor Subagent Prompt Template

各監査軸 (M-001 〜 M-075) を 1 subagent に dispatch するためのテンプレート。
SKILL.md の Phase 3 (Dispatch) でこのテンプレを placeholder 展開して Agent tool に渡す。

`{axis_id}`, `{axis_name}`, `{category}`, `{focus}`, `{prompt_skeleton}`,
`{recommended_agent_type}`, `{pj_context_or_warning}`, `{target_paths}` を置換すること。

---

```
Task tool ({recommended_agent_type}):
  description: "Audit axis {axis_id}: {axis_name}"
  prompt: |
    あなたは {recommended_agent_type} ロールとして、監査軸 **{axis_id}** を担当します。
    軸の prompt skeleton に従い、対象コードベースを監査してください。

    ## 軸定義

    - **ID**: {axis_id}
    - **名前**: {axis_name}
    - **大カテゴリ**: {category}
    - **1-line 焦点**: {focus}

    ## 軸 prompt skeleton (これを忠実に実行)

    {prompt_skeleton}

    対象パス: {target_paths}

    ## PJ Context (注入)

    {pj_context_or_warning}

    このコンテキストを踏まえて軸を実行してください。PJ 固有用語は文脈から推定する。
    context-file が無い場合は「⚠️ PJ context 未指定」と finding に付記してください。

    ## 出力形式 (厳守)

    finding を以下フォーマットで出力 (1 件 1 ブロック):

    ```
    ### [{axis_id}-#{n}] {1-line summary}
    - severity: HIGH | MED | LOW
    - file: {repo-relative path}
    - line: {N or N-M}
    - 症状: 1 行
    - 根本原因: 1-2 行
    - 修正案: 1-2 行 (可能なら code diff or SQL diff のスケッチ)
    - 既存軸との関係: 独立 / 補完 (M-XXX) / 統合 (M-XXX)
    ```

    severity 判定基準:
    - **HIGH**: 本番影響 / セキュリティ / データ破損 / 法規制違反 / SLA 抵触
    - **MED**: 運用負担増 / 開発生産性低下 / 中長期リスク
    - **LOW**: スタイル / 軽微な改善余地

    ## 重要な制約

    1. **claimed file:line を必ず Read で実コード確認** してから finding を出す。推測禁止。
    2. **PJ 固有用語の捏造禁止**。文脈から推定不能なら「PJ 確認要」と finding に明記。
    3. **finding 数の water-down 禁止**。軸の焦点に該当しなければ 0 件で問題ない (false positive のほうが有害)。
    4. **重複統合**: 同じ file:line で同じ症状なら 1 finding に統合し counter を 1+other ではなく 1 件として記録。

    ## 並走確認 (作業前)

    `gh pr list --state open` と `git branch -a` を確認し、開いている PR や
    feature branch があれば finding 末尾の「並走確認」セクションに記載せよ。
    別セッションが既に同じ問題を fix している可能性を排除する。

    ## 自己レビュー (報告前)

    報告前に以下を確認:
    - [ ] 全 finding の file:line を Read で実コード確認したか
    - [ ] severity 判定基準と一致するか
    - [ ] PJ 固有用語の captures が無く汎用化されているか
    - [ ] 軸の焦点から外れた「ついで finding」を入れていないか (out-of-scope と分離)

    ## 報告フォーマット

    1. **finding 件数サマリ**: HIGH N / MED N / LOW N
    2. **finding 本体** (上記フォーマット)
    3. **out-of-scope メモ** (この軸では検出されないが気付いた点、任意)
    4. **並走確認結果**
    5. **status**: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

    status=BLOCKED の場合: 何が分からないか具体的に述べる。
    status=NEEDS_CONTEXT の場合: どんな情報が必要か明示する。
```

---

## Placeholder 一覧

| Placeholder | 充填元 | 例 |
|---|---|---|
| `{axis_id}` | catalog.yml `axes[].id` | `M-068` |
| `{axis_name}` | catalog.yml `axes[].name` | `Prompt Injection 耐性` |
| `{category}` | catalog.yml `axes[].category` | `C9` |
| `{focus}` | catalog.yml `axes[].focus` | `Direct / Indirect / Stored 経路…` |
| `{prompt_skeleton}` | catalog.yml `axes[].prompt_skeleton` | (multi-line block) |
| `{recommended_agent_type}` | catalog.yml `axes[].recommended_agent_type` (config.yml で上書き可) | `security-reviewer` |
| `{pj_context_or_warning}` | `--context-file` 内容 / 無ければ `⚠️ PJ context 未指定で汎用 prompt 実行` | (multi-line) |
| `{target_paths}` | 起動時の対象 path (省略時はリポジトリ全体) | `backend/ frontend/` |

## Fallback ルール

`recommended_agent_type` が `~/.claude/agents/` に存在しない場合は
`general-purpose` に fallback する (SKILL.md Phase 3 で実装)。
fallback した場合は finding 末尾に `agent_type_fallback: general-purpose` と記載すること。
