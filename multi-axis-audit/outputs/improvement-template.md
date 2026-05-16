# Improvement List Entry Template

`--output improvement_list` (または `--output all`) 有効時、プロジェクトの
`improvement_list/` 配下に作成する履歴ファイル。

**保存先**: `{project_root}/improvement_list/{YYYY-MM-DD}_multi_axis_audit.md`

(複数回同日実行があれば `{YYYY-MM-DD}_multi_axis_audit_{HHMM}.md` 形式)

---

## Template

```markdown
# {YYYY-MM-DD} Multi-axis audit

## 対象

{target_paths_or_repo_wide}

## 起動 args

```bash
/multi-axis-audit {original_invocation_args}
```

## 変更内容 (このセッションで行った作業の記録)

1. **計画**:
   - 起動 args の解釈: 軸 {axis_count} 件を確定
   - Round 構成: {round_layout}
   - PJ context-file: {context_file_path_or_none}

2. **実行**:
   - 軸数 / Round / 並列度: {axis_count} 軸 / {round_count} Round / parallelism={parallelism}
   - dispatch 完了 agent 数: {successful_agent_count} / {agent_count}
   - 失敗 / skip 軸: {skipped_axes_or_none}
   - 所要時間: {duration_minutes} 分

3. **HIGH spot-check 結果**:
   - sampled: {sampled_count} / {total_high}
   - false positive: {fp_count} 件 ({fp_rate}%)
   - severity downgrade: {downgrade_count} 件
   - 残 HIGH: {high_after_spot_check} 件

4. **memory snapshot 作成**:
   - `{memory_snapshot_path}`

5. **ROADMAP 起票**:
   - `ROADMAP.md` Sprint {sprint_number} に {high_after_spot_check} HIGH + {med_count} MED + {low_count} LOW タスク追記

6. **並走確認**:
   - open PR: {gh_pr_summary}
   - branch: {git_branch_summary}
   - 衝突可能性: {conflict_status}

## 理由

なぜこの監査を行ったか / 監査トリガ:

> {audit_trigger_or_motivation}

(例: Sprint 末の総合監査 / 新機能 release 前の事前監査 / 規制対応 / incident 後の補完監査)

## 主要発見

### Top 5 risks

1. **[{axis_id}-#{n}]** {risk_1}
2. **[{axis_id}-#{n}]** {risk_2}
3. **[{axis_id}-#{n}]** {risk_3}
4. **[{axis_id}-#{n}]** {risk_4}
5. **[{axis_id}-#{n}]** {risk_5}

### 横断パターン (M-059 / Meta 軸より)

1. {pattern_1}
2. {pattern_2}
3. {pattern_3}

### 軸盲点 (M-060 / M-066)

- {gap_1}
- {gap_2}

## 残作業

- Sprint {sprint_number} で **HIGH {high_after_spot_check} + MED {med_count} + LOW {low_count}** 消化想定 (~{total_estimated_days}d)
- 失敗軸の再実行 (もしあれば): {skipped_axes_or_none}
- 次回監査での見直し候補 (M-066 提言):
  - {process_improvement_1}
  - {process_improvement_2}

## 関連

- Memory: `{memory_snapshot_path}`
- ROADMAP: `ROADMAP.md` Sprint {sprint_number}
- PJ context-file: `{context_file_path_or_none}`
```

---

## placeholder 一覧

| Placeholder | 説明 |
|---|---|
| `{YYYY-MM-DD}` | 監査実行日 |
| `{target_paths_or_repo_wide}` | 監査対象 (例: `backend/ frontend/` or `全コード再走査`) |
| `{original_invocation_args}` | 元起動 args |
| `{axis_count}` | 対象軸数 |
| `{round_layout}` | Round 構成サマリ |
| `{round_count}` | Round 総数 |
| `{parallelism}` | 並列度 (default 5) |
| `{successful_agent_count}` / `{agent_count}` | 成功 / 全 agent 数 |
| `{skipped_axes_or_none}` | skip した軸 ID list |
| `{duration_minutes}` | 所要時間 |
| `{sampled_count}` / `{total_high}` | spot-check sampling 件数 |
| `{fp_count}` / `{fp_rate}` / `{downgrade_count}` | spot-check 結果 |
| `{high_after_spot_check}` / `{med_count}` / `{low_count}` | finding 件数 |
| `{memory_snapshot_path}` / `{sprint_number}` | 成果物リンク |
| `{audit_trigger_or_motivation}` | 監査動機 (user 入力 or 推測) |
| `{total_estimated_days}` | 想定工数合計 |
| `{process_improvement_*}` | M-066 監査 process 改善案 |

## 軽微判断

CLAUDE.md (`c:\work\utility\skills-main\CLAUDE.md` 等) の **改修履歴の管理** ルールに従い:

- 監査結果が **HIGH 0 件 + MED ≤ 3 件** の場合は **軽微** と判定し improvement_list 起票を skip
  - memory snapshot のみ残す
- 起票したが残作業がある場合は「残作業」セクションを必ず記入する
