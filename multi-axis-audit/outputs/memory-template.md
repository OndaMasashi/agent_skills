# Memory Snapshot Template

SKILL.md の Phase 5 (Deliver) で生成する memory snapshot のテンプレ。
placeholder `{xxx}` を Phase 4 で集計した値に置換して保存する。

**保存先**: `~/.claude/projects/{project_slug}/memory/session-snapshot-{YYYY-MM-DD}-multi-axis-audit-{HHMM}.md`

- `{project_slug}` は cwd path を slug 化 (Q4 推奨)。例: `c:\work\my-project` → `c--work-my-project`
- `{HHMM}` は時刻付きでファイル名衝突を防ぐ (Q3 推奨)

---

```markdown
---
name: {YYYY-MM-DD} 多軸監査 ({axis_count} 軸, {agent_count} agent)
description: {one_line_top5_summary}
type: project
---

# {YYYY-MM-DD} Multi-Axis Audit

## Exec Summary

- **軸数**: {axis_count} ({selected_axis_ids})
- **agent 数**: {agent_count} (Round 構成: {round_layout})
- **並列度**: {parallelism}
- **PJ context-file**: {context_file_path_or_none}
- **finding 総数**: HIGH {high_count} / MED {med_count} / LOW {low_count}
- **HIGH spot-check 結果**: {fp_rate}% ({fp_count}/{sampled_count})
- **HIGH spot-check 後の HIGH 件数**: {high_after_spot_check}
- **所要時間**: {duration_minutes} 分
- **過去監査との比較**: {comparison_summary_or_first_audit}

{fp_rate_warning_if_over_20pct}

## Top 5 Risks

1. **[{axis_id}-#{n}]** {1-line risk summary} (file:line)
2. ...
3. ...
4. ...
5. ...

## 横断パターン (M-059 / Meta 軸から)

1. **{pattern_name_1}**
   - 関連 finding: [{related_axis_ids_and_numbers}]
   - 共通根本原因: {1-2 行}
   - 上位概念での修正: {1-2 行}
2. ...

## HIGH findings ({high_after_spot_check} 件)

### [{axis_id}-#{n}] {1-line}

- **severity**: HIGH
- **file:line**: `{file}:{line}`
- **症状**: {symptom_1_line}
- **根本原因**: {root_cause_1_2_lines}
- **修正案**: {fix_proposal_1_2_lines}
- **既存軸との関係**: {axis_relationship}
- **(spot-check で severity_downgrade されたら)** 元 severity / 新 severity と判定根拠

(... 全 HIGH finding を 1 ブロックずつ)

## MEDIUM findings ({med_count} 件)

| ID | file:line | 1-line summary | 修正案 |
| :--- | :--- | :--- | :--- |
| [{axis_id}-#n] | `path:line` | ... | ... |
| ... | ... | ... | ... |

## LOW findings ({low_count} 件)

| ID | file:line | 1-line summary |
| :--- | :--- | :--- |
| [{axis_id}-#n] | `path:line` | ... |
| ... | ... | ... |

## メタ監査者の補足 (C8 系 finding)

### 軸盲点

- {gap_1}
- {gap_2}

### 横断観点 (M-067 loop topology / M-061 time horizon 等)

- {observation_1}

### 監査 process 自体への提言 (M-066)

- {process_proposal_1}

## 除外 finding (HIGH spot-check で false positive 判定、Q9)

> agent 誤読 / 過剰判定 / 既に fix 済 と判定された finding。skill 改善材料として保存。

### [{axis_id}-#{n}] (除外)

- **元 severity**: HIGH
- **claimed file:line**: `{file}:{line}`
- **claimed 症状**: ...
- **spot-check 判定根拠**: ...
- **示唆**: agent type / prompt skeleton / 用語の見直し候補

(... 除外 finding を 1 ブロックずつ。0 件なら "なし" と記述)

## 失敗軸 (agent 実行失敗で skip した軸、Q6)

- **{axis_id}**: retry 1 回 / fallback general-purpose の双方で失敗 → skip
  - 原因: {error_summary}

(失敗 0 件なら "なし")

## 並走確認結果

- **open PR**: {gh_pr_list_summary}
- **branch 状態**: {git_branch_summary}
- **衝突可能性**: なし / あり ({conflict_summary})

## 起動 args (再現用)

```bash
/multi-axis-audit {original_invocation_args}
```

## 関連成果物

- ROADMAP entry: {roadmap_file_path_or_none} (Sprint {sprint_number})
- improvement_list: {improvement_list_file_path_or_none}
```

---

## placeholder 一覧 (主要)

| Placeholder | 説明 | 例 |
|---|---|---|
| `{YYYY-MM-DD}` | 監査実行日 | `2026-05-16` |
| `{project_slug}` | cwd path slug | `c--work-my-project` |
| `{axis_count}` | 対象軸数 | `75` / `10` |
| `{selected_axis_ids}` | 軸 ID list (CSV) | `M-001,M-002,...` |
| `{agent_count}` | dispatch した agent 数 | `15` |
| `{round_layout}` | Round 構成 | `R1=5,R2=5,R3=5` |
| `{high_count}` / `{med_count}` / `{low_count}` | finding 件数 | `18 / 38 / 27` |
| `{fp_rate}` | false positive 率 (spot-check) | `11` (%) |
| `{fp_count}` / `{sampled_count}` | FP 件数 / sampling 件数 | `2 / 18` |
| `{high_after_spot_check}` | spot-check 後 HIGH 件数 | `16` |
| `{duration_minutes}` | 所要時間 | `65` |
| `{comparison_summary_or_first_audit}` | 過去監査比較 | `Sprint 11 audit 比 HIGH +6` / `初回監査` |
| `{fp_rate_warning_if_over_20pct}` | FP 率 20% 超なら warning ブロック、未満なら空 | (multi-line warning or empty) |
| `{context_file_path_or_none}` | context-file path | `.claude/audit-context.md` / `(未指定)` |
| `{original_invocation_args}` | 元起動 args | `--top10 --context-file .claude/audit-context.md` |
| `{sprint_number}` | ROADMAP 起票 Sprint 番号 | `12` |

## FP 率警告ブロック (`{fp_rate_warning_if_over_20pct}`)

FP 率 ≥ 20% の場合のみ以下を挿入:

```markdown
> ⚠️ **HIGH false positive 率が 20% を超えています ({fp_rate}%)**。
> - 軸の選定が PJ context と合っていない可能性
> - agent type の選定 (subagent_overrides) を見直し
> - prompt skeleton の文言を実コードに即した形に refine
> - 次回起動時に `--filter` で精度の高い軸群に絞ることを推奨
```
