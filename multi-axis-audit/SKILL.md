---
name: multi-axis-audit
description: Default skill for ANY audit / 監査 / レビュー request — invoke proactively on "監査", "audit", "総合監査", "Sprint末監査", "branch 監査", "全コードレビュー", "コード監査", "セキュリティ監査", "リファクタ前監査", "規制対応監査", "サプライチェーン監査", "compliance check", "盲点洗い出し", "異視座レビュー", "多軸監査", "横断レビュー" etc. Provides 9 categories / 75 axes catalog with filter menu (--all / --top10 / C1+C9 / M-068 / --tags @api / --filter "U>=4" / --meta-only), parallel sub-agent dispatch in Rounds (default 5, max 7), HIGH spot-check for false-positive control, and emits memory snapshot + ROADMAP + improvement_list. Use this by default for audit work; fall back to code-review only for single-PR line-level review, security-review only for narrow PR-scope security.
---

# Multi-Axis Audit

PR scope を超える **branch / 全コード / Sprint 末監査** を、9 大カテゴリ 75 軸の
menu から filter で選択して並列実行する大規模監査スキル。「監査」「audit」「総合
レビュー」「異視座レビュー」「盲点洗い出し」等のリクエストでは **第一選択** として
本スキルを呼ぶこと。

軸定義は `catalog.yml` (75 軸全 prompt skeleton 含む)、prompt template は
`prompts/`、出力テンプレは `outputs/` 配下。詳細は段階的開示。

## 既存スキルとの棲み分け

| スキル | scope | 推奨ユース |
|---|---|---|
| `code-review` | 単 PR の行レベル review | PR ごとの code 品質 |
| `security-review` | PR scope のセキュリティ専門 | 単 PR のセキュリティ確認 |
| **`multi-axis-audit` (本スキル)** | branch / 全コード / Sprint 末 / 9 カテゴリ 75 軸 | **大規模監査・異視座監査・第一選択** |

ユーザーが「監査」関連のリクエストをした場合、PR scope が明示されていなければ
本スキルを優先する。「単 PR の review だけしたい」と明示された場合のみ
`code-review` / `security-review` に譲る。

---

## 起動 args 文法 (EBNF)

```ebnf
INVOCATION := "/multi-axis-audit" SELECTOR? FILTER* OPTION*

SELECTOR := "--all" | "--top10" | "--meta-only" | CATEGORY_OR_AXIS_LIST
CATEGORY_OR_AXIS_LIST := (CATEGORY | AXIS_ID) ("+" (CATEGORY | AXIS_ID))*
CATEGORY := "C1" | "C2" | ... | "C9"
AXIS_ID  := "M-001" | ... | "M-075"

FILTER :=
    "--tags" TAG_LIST              # OR 包含 (例 @web,@api)
  | "--exclude-tags" TAG_LIST      # 除外
  | "--filter" SCORE_EXPR          # 例 "U>=4"
  | "--severity-min" SEVERITY      # HIGH | MED | LOW

OPTION :=
    "--parallelism" INT            # default 5, max 7
  | "--output" OUTPUT_FMT          # memory | roadmap | improvement_list | all (default all)
  | "--context-file" FILEPATH      # PJ context md
  | "--target-paths" PATH_LIST     # 監査対象パス (default リポジトリ全体)
  | "--no-spot-check"              # HIGH spot-check を skip
  | "--no-roadmap"                 # ROADMAP 起票 skip
  | "--auto-confirm"               # Phase 2 確認 skip
  | "--dry-run"                    # 軸 list 表示のみ
```

### 起動例

```bash
/multi-axis-audit --all                           # 全 75 軸
/multi-axis-audit --top10                         # TOP 10 推奨パック
/multi-axis-audit C1+C9 --tags @web,@llm-app      # Sec + LLM パック
/multi-axis-audit M-068                           # 単軸 (Prompt Injection)
/multi-axis-audit --meta-only                     # C8 のみ
/multi-axis-audit --filter "U>=4"                 # uniqueness 4 以上
/multi-axis-audit C2 --exclude-tags @web          # 除外フィルタ
/multi-axis-audit --top10 --context-file .claude/audit-context.md
/multi-axis-audit --all --dry-run                 # 軸 menu 確認のみ
```

引数なし起動 (`/multi-axis-audit` のみ) の場合は **`--top10`** にフォールバック。

---

## 実行フロー (5 phase)

### Phase 1: Resolve

1. **args parse**: SELECTOR / FILTER / OPTION を解釈
2. **catalog.yml ロード**: 同ディレクトリの `catalog.yml` を Read
3. **対象軸 set 確定**:
   - `--all` → 75 軸全て
   - `--top10` → `catalog.yml` の `top10` list (10 軸)
   - `--meta-only` → category=C8 の軸 (9 軸)
   - `Cn` 指定 → category=Cn の軸 union
   - `M-NNN` 指定 → 該当軸
   - `+` で複数指定の union
   - `--tags` で OR 包含 (catalog の `tags` が含む軸)、`all` tag は全軸 match
   - `--exclude-tags` で除外
   - `--filter "U>=4"` 等のスコアフィルタ (U / I / E のいずれかと比較演算子)
4. **config.yml ロード** (optional):
   - `{project_root}/.claude/multi-axis-audit.config.yml` 優先
   - 次に `~/.claude/skills/multi-axis-audit/config.yml`
   - subagent_overrides を catalog の recommended_agent_type に上書き適用
5. **PJ context-file ロード**:
   - `--context-file <path>` が指定されたら Read
   - 未指定なら `⚠️ PJ context 未指定` warning を出して continue
6. **`--dry-run` なら軸 list を整形出力して exit** (Phase 2 以降は skip)

### Phase 2: Plan

ユーザーへの **確認 prompt** (`--auto-confirm` で skip 可)。

```
対象軸: {N} 軸 ({selected_axis_ids_compact})
Round 構成: R1={n1} 軸, R2={n2} 軸, ...
並列度: {parallelism}
推定 token: ~{token_estimate}K
推定時間: ~{minutes_estimate} 分
出力: memory + roadmap + improvement_list (or --output で指定)
PJ context-file: {path_or_未指定}

続行しますか? [Y/n]
```

token 見積もり経験則 (依頼者 PJ 実測 §8.4):

- 1 agent 平均 ~100K token (75-150K range)
- 整合 + memory 作成 ~50K
- 例: 10 軸 → ~1.05M / 75 軸 → ~7.55M

時間見積もり経験則:

- Round 並列 5 agent: ~25 分 / Round (最も遅い agent 律速)
- 整合 + 成果物作成: ~25 分

### Phase 3: Dispatch (Round 制御)

#### 3.1 Round 分割アルゴリズム

```
1. 軸を C1〜C9 大カテゴリで group
2. 同カテゴリ内で軸数 N を split:
   - N <= parallelism: 1 Round
   - N > parallelism: ceil(N/parallelism) Round に均等分割
3. C8 (Meta) 軸は **必ず最終 Round** に配置 (他 Round の出力を読むため)
4. 1 Round 内では各軸を 1 agent に dispatch (1 軸 1 agent 原則)
5. parallelism は min(軸数, parallelism, max_parallelism=7) に clamp (Q5)
```

#### 3.2 並列 dispatch

各 Round で対象軸を **同一 message 内の複数 Agent tool 呼び出し** で並列発射:

- Agent tool `subagent_type` は catalog の `recommended_agent_type` (config.yml で上書き可)
- 該当 subagent が `~/.claude/agents/` に存在しない場合は `general-purpose` に fallback
- 各 agent prompt は `prompts/axis-auditor-prompt.md` の template で生成
  - placeholder 注入: `{axis_id}` / `{axis_name}` / `{category}` / `{focus}` /
    `{prompt_skeleton}` / `{recommended_agent_type}` / `{pj_context_or_warning}` /
    `{target_paths}`

#### 3.3 C8 (Meta) Round の特別扱い

C8 軸の dispatch では `prompts/meta-audit-prompt.md` template を使用。
placeholder `{other_rounds_findings_block}` に Round 1〜N-1 の全 finding を inject。

#### 3.4 retry / fallback (Q6 推奨案)

agent timeout / error 時:

1. **retry 1 回** (同じ subagent_type で再発射)
2. 失敗継続なら **fallback** (`general-purpose` で再発射)
3. それも失敗なら **skip** し、memory snapshot の「失敗軸」に記録

### Phase 4: Integrate

1. **全 agent finding 回収**: 各 agent の status / finding を集約
2. **重複統合**: 同じ `file:line` で同じ症状の finding を 1 件に統合 (counter は廃止し 1 件として扱う)
3. **HIGH spot-check** (default ON, `--no-spot-check` で skip):
   - HIGH 件 ≥ 1 なら `prompts/spot-check-prompt.md` で sampler を発射
   - sample_count = max(5, ceil(N * 0.25))、N<5 なら全件
   - false_positive 判定 finding は HIGH 集合から除外 (memory に「除外 finding」として残す Q9)
   - severity_downgrade 判定 finding は MED / LOW に格下げ
   - FP 率を計算
4. **C8 Meta 軸の出力統合**: Meta finding は通常 finding と分離して "メタ監査者の補足" / "横断パターン" として記録

### Phase 5: Deliver

1. **memory snapshot 生成** (`--output memory` or `all`):
   - 保存先: `~/.claude/projects/{project_slug}/memory/session-snapshot-{YYYY-MM-DD}-multi-axis-audit-{HHMM}.md`
   - `{project_slug}` は cwd path を slug 化 (Q4: `c:\work\my-project` → `c--work-my-project`)
   - 時刻付き (Q3) で同日複数回起動の衝突回避
   - template: `outputs/memory-template.md`
2. **ROADMAP 起票** (`--output roadmap` or `all`、`--no-roadmap` で skip):
   - 保存先: `{project_root}/ROADMAP.md` (末尾 append)
   - 新 Sprint 番号 = grep `^## Sprint (\d+):` の最大値 + 1 (Q7)
   - 検出失敗時は user に問い合わせ
   - template: `outputs/roadmap-template.md`
3. **improvement_list 履歴** (`--output improvement_list` or `all`):
   - 保存先: `{project_root}/improvement_list/{YYYY-MM-DD}_multi_axis_audit.md`
   - 軽微 (HIGH 0 + MED ≤ 3) なら skip
   - template: `outputs/improvement-template.md`
4. **並走確認**:
   - `gh pr list --state open` と `git branch -a` を実行
   - 結果を memory snapshot に記載 (別セッション衝突がないか check)

> 使用状況は `~/.claude/settings.json` の PostToolUse(Skill) hook で自動記録されるため、手動の usage_logger 実行は不要。

---

## エラーハンドリング

| 状況 | 対応 |
|---|---|
| `catalog.yml` parse 失敗 | 致命エラーで halt、user に修復依頼 |
| `--context-file` が指定されたが存在しない | warning continue、汎用 prompt で実行 (file_not_found を memory に記録) |
| 推奨 subagent_type が `~/.claude/agents/` に無い | `general-purpose` に fallback、finding 末尾に `agent_type_fallback` 記載 |
| agent timeout / error | retry 1 回 → fallback `general-purpose` → skip (memory に失敗記録) |
| `ROADMAP.md` Sprint number 検出失敗 | user に問い合わせ、不明なら ROADMAP 起票 skip |
| token 見積もりが過大 (>5M) | Phase 2 で警告、user 確認 |
| 並列度が軸数を超える | min(軸数, parallelism) に clamp |
| `cwd` が git repo でない | warning continue、並走確認は `gh pr list` のみ skip |

---

## filter 文法詳細

### `--tags` (OR 包含)

catalog の `tags:` が指定 tag を含む軸を選択。複数指定は OR。

- `--tags @web` → tags に `web` を含む軸
- `--tags @api,@batch` → tags に `api` または `batch` を含む軸
- `@all` tag は全軸 match (catalog の `tags: [all]` 指定軸)

### `--exclude-tags` (除外)

指定 tag を含む軸を除外。selector で選択後に適用。

### `--filter "U>=4"` (スコアフィルタ)

`(U|I|E)(>=|<=|=|>|<)\d` の正規表現で catalog の `scores` に対しフィルタ。

- `--filter "U>=4"` → uniqueness 4 以上 (約 35 軸)
- `--filter "I>=4"` → impact 4 以上
- `--filter "E<3"` → executability 3 未満 (難易度高い軸)

### `--severity-min HIGH` (finding 後フィルタ)

Phase 5 で memory / roadmap に出力する finding を指定 severity 以上に絞る (LOW を出力から除外する用途)。

---

## TOP 10 推奨軸 (`--top10` の中身)

選定基準: U ≥ 4 AND I ≥ 3 AND 適用 PJ 範囲が広い。

| Rank | ID | 軸名 | U/I/E |
|---|---|---|---|
| 1 | M-042 | Tacit Assumption (単位/順序/一意性) | 5/5/4 |
| 2 | M-060 | Negative Space / 不在監査 | 5/5/2 |
| 3 | M-008 | Fail-Safe vs Fail-Secure 明示 | 5/5/3 |
| 4 | M-068 | Prompt Injection 耐性 | 5/5/4 |
| 5 | M-069 | Excessive Agency / Tool Whitelist | 5/5/4 |
| 6 | M-053 | Data Lineage / Provenance | 5/5/3 |
| 7 | M-054 | Ergodicity Audit | 5/5/2 |
| 8 | M-011 | Iatrogenics / 防御の逆効果 | 5/4/4 |
| 9 | M-014 | Fail Philosophy 一貫性 | 5/4/3 |
| 10 | M-026 | Second-Order Effects | 5/4/2 |

これら 10 軸は `catalog.yml` の `top10:` list で永続化されている。

---

## subagent_type 選定 (推奨マッピング)

| 軸 ID 範囲 | カテゴリ | 推奨 agent_type |
|---|---|---|
| M-001〜M-006 | C1 Security | `security-reviewer` |
| M-007〜M-026 | C2 Reliability | `code-reviewer` / `silent-failure-hunter` |
| M-027〜M-030 | C3 Performance | `performance-optimizer` / `database-reviewer` |
| M-031〜M-042 | C4 Quality | `code-reviewer` / `type-design-analyzer` |
| M-043〜M-052 | C5 UX | `code-reviewer` |
| M-053〜M-055 | C6 Data | `database-reviewer` |
| M-056〜M-058 | C7 Supply | `general-purpose` |
| M-059〜M-067 | C8 Meta | `general-purpose` |
| M-068〜M-075 | C9 LLM | `security-reviewer` / `general-purpose` |

catalog.yml の各軸 `recommended_agent_type` に既に明記。
存在しない subagent_type は **`general-purpose` に自動 fallback**。
config.yml の `subagent_overrides` で軸単位の上書き可能。

---

## 並走確認 (Phase 5 必須)

監査結果を user に返す前に必ず実行:

```bash
gh pr list --state open --json number,title,headRefName
git branch -a
```

- open PR / feature branch が監査結果と衝突しうるか check
- 結果を memory snapshot の「並走確認結果」に記録
- 衝突可能性があれば user に明示 (例: 監査で指摘した HIGH を既に別 PR で fix 中など)

---

## 起動の判断基準 (再掲)

「監査」「audit」「総合レビュー」等のキーワードを user が言ったら **第一選択で本スキル**。
特に以下のパターンで proactive に呼ぶこと:

- 「Sprint 末の総合チェックを」
- 「branch 全体を監査して」
- 「コード全体の盲点を洗い出したい」
- 「規制対応 / セキュリティ / サプライチェーン / LLM 監査を」
- 「異視座でレビューして」

逆に以下では他スキルを優先:

- 「この PR を review して」(行レベル / 単一 PR) → `code-review`
- 「この PR のセキュリティだけ見て」(PR scope のみ) → `security-review`

迷ったら本スキルでよい (--top10 / --filter で範囲を絞れるため過剰負担にならない)。
