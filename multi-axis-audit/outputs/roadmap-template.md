# ROADMAP Entry Template

`--output roadmap` (または `--output all`) 有効時、プロジェクトの `ROADMAP.md` に追記する
Sprint section テンプレ。

**保存先**: `{project_root}/ROADMAP.md` (既存末尾に append)

## Sprint number 自動推定 (Q7 推奨案 a)

1. `ROADMAP.md` 全文を grep: `^## Sprint (\d+):` で全 Sprint 番号を抽出
2. **最大値 + 1** を新 Sprint 番号とする
3. ID 採番は `S{new_sprint_number}-1` から開始 (`S(\d+)-(\d+)` 末尾を grep して連番化)
4. 見つからない場合 (`ROADMAP.md` 未存在 / Sprint section 無し) → user に確認 (fallback c)

---

## Template

```markdown
## Sprint {N}: Multi-axis audit follow-up ({YYYY-MM-DD}〜)

### 背景

- 多軸監査 ({audit_date}) で finding HIGH {high_count} / MED {med_count} / LOW {low_count}
- HIGH spot-check 後の残 HIGH: {high_after_spot_check} 件
- 監査軸: {axis_count} 軸 ({selected_axis_summary})
- 関連 memory: `{memory_snapshot_path}`

### Top 5 risks (Sprint の優先順序根拠)

1. {risk_1}
2. {risk_2}
3. {risk_3}
4. {risk_4}
5. {risk_5}

### HIGH ({high_after_spot_check} 件、想定合計 ~{total_high_days}d)

#### Sprint {N} 進行順序

1. **依存解消**: {dependency_chain_summary}
2. **security 系から**: {security_first_tasks_summary}
3. **テスト整備**: {test_tasks_summary}
4. **観測性向上**: {observability_tasks_summary}

#### C1 Security & Privacy

- [ ] **S{N}-1** [{axis_id}-#{n}] `{file}:{line}` — {1-line summary} (推定 {Xd})
- [ ] **S{N}-2** [{axis_id}-#{n}] `{file}:{line}` — {1-line summary} (推定 {Xd})

#### C2 Reliability & Operability

- [ ] **S{N}-3** ...
- [ ] **S{N}-4** ...

#### C3 Performance & Scale

- [ ] **S{N}-5** ...

#### C4 Code Quality & Maintainability

- [ ] **S{N}-6** ...

#### C5 UX / a11y / i18n

- [ ] **S{N}-7** ...

#### C6 Data Integrity & Lineage

- [ ] **S{N}-8** ...

#### C7 Supply Chain & Build

- [ ] **S{N}-9** ...

#### C9 LLM Agent 駆動開発リスク

- [ ] **S{N}-10** ...

### MEDIUM ({med_count} 件、簡潔リスト)

- [ ] **S{N}-{m1}** [{axis_id}-#{n}] `{file}:{line}` — {1-line}
- [ ] **S{N}-{m2}** ...

### LOW (S{N}-LOW バッチ、{low_count} 件)

> 個別タスク化せず、空き時間 / Boy Scout rule で消化。grep-able な ID で memory snapshot とリンク。

- [ ] **S{N}-LOW-1** [{axis_id}-#{n}] `{file}:{line}` — {1-line}
- [ ] **S{N}-LOW-2** ...

### メタ補足 (M-059 / M-066 等)

- 横断パターン {n_patterns} 件は別タスク化せず、上記 S{N}-* の進行順序判断材料として使用
- 監査 process 改善 ({process_improvement_count} 件) は次回監査前に check

### 関連

- Memory: [{memory_snapshot_filename}]({memory_snapshot_path})
- Improvement list: [{improvement_list_filename}]({improvement_list_path})
- 起動 args: `/multi-axis-audit {original_invocation_args}`
```

---

## placeholder 一覧

| Placeholder | 説明 |
|---|---|
| `{N}` | 新 Sprint 番号 (自動推定または user 指定) |
| `{YYYY-MM-DD}` | 監査実行日 = Sprint 開始日 |
| `{audit_date}` | 監査実行日 (同上) |
| `{high_count}` / `{med_count}` / `{low_count}` | finding 件数 |
| `{high_after_spot_check}` | spot-check 後 HIGH 件数 |
| `{axis_count}` | 対象軸数 |
| `{selected_axis_summary}` | 軸群サマリ (例: `C1+C9 --tags @web`) |
| `{memory_snapshot_path}` | memory snapshot ファイルパス |
| `{total_high_days}` | HIGH 想定工数合計 (各 finding ~0.5d 仮定で集計) |
| `{file}:{line}` | finding の file:line |
| `{1-line summary}` | finding の症状 1 行 |
| `{Xd}` | 個別 task の想定工数 (default 0.5d) |
| `{original_invocation_args}` | 元起動 args |
| `{n_patterns}` | 横断パターン件数 |

## ID 採番 fallback

`ROADMAP.md` 末尾の `S(\d+)-(\d+)` パターンが検出できない場合:

1. user に新 Sprint 番号を問い合わせ (`AskUserQuestion` 等で)
2. 確認できたら指定値で起票
3. それでも不明なら起票 skip (memory には記録、`--no-roadmap` 動作と同等)
