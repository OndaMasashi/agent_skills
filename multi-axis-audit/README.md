# Multi-Axis Audit

> **第一選択スキル**: 「監査」「audit」「総合レビュー」「異視座レビュー」「盲点洗い出し」等のリクエストでは、PR scope が明示されていない限り本スキルを起動する。

9 大カテゴリ 75 軸の監査軸 menu から filter で選択し、並列 sub-agent dispatch で
**branch / 全コード / Sprint 末監査** を一気に走らせる。HIGH spot-check で false positive を抑え、
memory snapshot + ROADMAP + improvement_list を自動生成。

## ファイル構成

```text
multi-axis-audit/
├── SKILL.md                       # スキル本体 (5 phase ワークフロー)
├── README.md                      # このファイル
├── catalog.yml                    # 75 軸定義 (M-001〜M-075 全 prompt skeleton 含む)
├── prompts/
│   ├── axis-auditor-prompt.md     # 1 軸 1 agent dispatch テンプレ
│   ├── spot-check-prompt.md       # HIGH spot-check (FP 検出) テンプレ
│   └── meta-audit-prompt.md       # C8 Meta agent (他 Round 出力を読む)
├── outputs/
│   ├── memory-template.md         # session-snapshot 出力テンプレ
│   ├── roadmap-template.md        # ROADMAP.md Sprint section テンプレ
│   └── improvement-template.md    # improvement_list 履歴テンプレ
├── config.yml.example             # subagent_overrides 等の上書き例
└── audit-context.md.example       # PJ context-file の雛形
```

## 起動例

### TOP 10 推奨パック (最低限・時間がない時)

```bash
/multi-axis-audit --top10
```

### 全 75 軸 (Sprint 末の総合監査)

```bash
/multi-axis-audit --all
```

### Sec + LLM パック (LLM 機能を持つ Web app)

```bash
/multi-axis-audit C1+C9 --tags @web,@llm-app
```

### 単軸 (検証したい 1 軸のみ)

```bash
/multi-axis-audit M-068    # Prompt Injection 耐性のみ
```

### メタ俯瞰 (既存監査の盲点抽出)

```bash
/multi-axis-audit --meta-only
```

### ユニーク軸のみ (新規視座)

```bash
/multi-axis-audit --filter "U>=4"
```

### PJ context 付き (推奨)

```bash
/multi-axis-audit --top10 --context-file .claude/audit-context.md
```

### dry-run (軸 menu 確認のみ、実行しない)

```bash
/multi-axis-audit C1+C9 --dry-run
```

## ユースケース

| シーン | 起動例 | 想定時間 |
|---|---|---|
| Sprint 末の総合監査 | `--all` | 30 分〜2 時間 |
| branch / リファクタ後の構造監査 | `C4+C8 --top10` | 20 分 |
| 本番 incident 後の補完監査 | `C1+C2 --tags @api` | 30 分 |
| LLM 機能追加後の専門監査 | `C9` | 15 分 |
| 規制対応前の compliance | `C1+C6 --tags @api` | 30 分 |
| supply chain 緊急確認 | `C7 --top10` | 10 分 |
| 監査自体の盲点チェック | `--meta-only` | 15 分 |
| 新機能 PR の事前監査 (PR scope) | (推奨せず → `code-review` を使う) | — |

## filter 文法 (EBNF)

```ebnf
INVOCATION := "/multi-axis-audit" SELECTOR? FILTER* OPTION*

SELECTOR := "--all" | "--top10" | "--meta-only" | CATEGORY_OR_AXIS_LIST
CATEGORY_OR_AXIS_LIST := (CATEGORY | AXIS_ID) ("+" (CATEGORY | AXIS_ID))*
CATEGORY := "C1" | ... | "C9"
AXIS_ID  := "M-001" | ... | "M-075"

FILTER :=
    "--tags" TAG_LIST              # OR 包含
  | "--exclude-tags" TAG_LIST      # 除外
  | "--filter" SCORE_EXPR          # 例 "U>=4"
  | "--severity-min" SEVERITY      # HIGH | MED | LOW
TAG := "@web" | "@api" | "@batch" | "@datapipe" | "@infra" | "@ml"
     | "@llm-app" | "@llm-dev" | "@cli" | "@all"
SCORE_EXPR := /(U|I|E)(>=|<=|=|>|<)\d/

OPTION :=
    "--parallelism" INT            # default 5, max 7
  | "--output" OUTPUT_FMT          # memory | roadmap | improvement_list | all
  | "--context-file" FILEPATH
  | "--target-paths" PATH_LIST
  | "--no-spot-check"
  | "--no-roadmap"
  | "--auto-confirm"
  | "--dry-run"
```

引数なし起動 (`/multi-axis-audit`) は `--top10` フォールバック。

## 大カテゴリ一覧 (catalog.yml 由来)

| ID | カテゴリ | 軸数 |
|---|---|---|
| C1 | Security & Privacy | 6 |
| C2 | Reliability & Operability | 20 |
| C3 | Performance & Scale | 4 |
| C4 | Code Quality & Maintainability | 12 |
| C5 | UX / a11y / i18n | 10 |
| C6 | Data Integrity & Lineage | 3 |
| C7 | Supply Chain & Build | 3 |
| C8 | Meta Audit / 思考方法 | 9 |
| C9 | LLM Agent 駆動開発リスク | 8 |
| **合計** | | **75** |

## TOP 10 推奨軸 (`--top10` の中身)

選定基準: U ≥ 4 AND I ≥ 3 AND 適用 PJ 範囲が広い。

1. **M-042** Tacit Assumption (単位/順序/一意性)
2. **M-060** Negative Space / 不在監査
3. **M-008** Fail-Safe vs Fail-Secure 明示
4. **M-068** Prompt Injection 耐性
5. **M-069** Excessive Agency / Tool Whitelist
6. **M-053** Data Lineage / Provenance
7. **M-054** Ergodicity Audit (Path vs Ensemble)
8. **M-011** Iatrogenics / 防御の逆効果
9. **M-014** Fail Philosophy 一貫性
10. **M-026** Second-Order Effects / 介入カスケード

## 成果物

| 出力 | 保存先 | option |
|---|---|---|
| memory snapshot | `~/.claude/projects/{slug}/memory/session-snapshot-{date}-multi-axis-audit-{HHMM}.md` | `--output memory` (default ON) |
| ROADMAP entry | `{project_root}/ROADMAP.md` Sprint section | `--output roadmap` / `--no-roadmap` で skip |
| improvement_list | `{project_root}/improvement_list/{date}_multi_axis_audit.md` | `--output improvement_list` |

`--output all` (default) で全て生成。

## 既存スキルとの棲み分け

| スキル | scope | 推奨ユース |
|---|---|---|
| `code-review` | 単 PR の行レベル | PR ごとの code 品質 |
| `security-review` | PR scope のセキュリティ | 単 PR セキュリティ |
| **`multi-axis-audit`** | **branch / 全コード / Sprint 末 / 75 軸** | **大規模監査・第一選択** |

「監査」キーワードでは第一選択で本スキル。明確に「PR review だけ」と指定された
場合のみ `code-review` / `security-review` に譲る。

## skills-catalog 登録 (Development カテゴリ)

```markdown
| Multi-Axis Audit | multi-axis-audit | 監査, audit, 総合監査, Sprint末監査, branch監査, 全コードレビュー, コード監査, 異視座監査, 多軸監査, 盲点洗い出し, セキュリティ監査, リファクタ前監査, 規制対応監査, サプライチェーン監査, compliance check | **監査系リクエストの第一選択スキル**。9 大カテゴリ 75 軸 menu (--all/--top10/Cn/M-XXX/--tags/--filter/--meta-only) で軸選択、並列 sub-agent dispatch (Round 制御, 並列 5 default / max 7)、HIGH spot-check、memory snapshot + ROADMAP + improvement_list 生成 |
```

## 受け入れ基準 / 動作確認

詳細は [`SKILL.md`](SKILL.md) の §エラーハンドリングと、依頼書 (`c:\tmp\skill-spec-multi-axis-audit.md`) §7 DoD を参照。

主要シナリオ:

- **シナリオ A**: `/multi-axis-audit --top10` → 10 軸 dispatch + memory snapshot 出力
- **シナリオ B**: `/multi-axis-audit C1+C9 --tags @web,@llm-app --filter "U>=4" --dry-run` → 該当軸のみ menu 表示
- **シナリオ C**: `--context-file <path>` で context が agent prompt に注入される
- **シナリオ D**: HIGH 5 件以上で spot-check が自動実行され、memory snapshot に FP 率記録

## バージョン管理

`catalog.yml` の `version:` (default `1.0.0`) は catalog 更新時に semver で更新。
prompt skeleton の文言変更 → minor、軸追加 → minor、軸 ID 削除 → major。
