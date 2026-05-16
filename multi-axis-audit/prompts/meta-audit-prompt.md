# Meta Audit Subagent Prompt Template

C8 Meta 軸 (特に M-059 Cross-Cutting / M-066 Audit Meta-Process / M-067 Loop Topology)
専用のテンプレート。他 Round の全 finding 出力を読み、軸盲点・横断パターンを抽出する。

C8 軸は **必ず最終 Round に配置** する (spec §3.3.1)。
理由: 他 Round の finding 出力を入力として読む必要があるため。

---

## 起動条件

- Phase 3 の他 Round 全てが完了
- 対象軸 set に C8 軸が含まれる (M-059, M-060, M-061, M-062, M-063, M-064, M-065, M-066, M-067)

## Subagent Prompt Template

```
Task tool (general-purpose):
  description: "Meta audit: axis {axis_id}"
  prompt: |
    あなたはメタ監査者です。本セッションで他の監査軸が出した finding を
    全て読み、軸 **{axis_id} ({axis_name})** の prompt skeleton に従って
    **横断観点 / 軸盲点 / 思考方法** の出力を生成してください。

    ## 軸定義

    - ID: {axis_id}
    - 名前: {axis_name}
    - 1-line 焦点: {focus}
    - prompt skeleton: |
        {prompt_skeleton}

    ## 他 Round の finding (横断入力)

    以下は本セッションで他の監査軸 (M-001〜M-058, M-068〜M-075 のうち実行されたもの)
    が出した finding の集合です。これを読み込んで分析対象としてください。

    {other_rounds_findings_block}

    ## PJ Context (注入)

    {pj_context_or_warning}

    ## メタ監査の観点 (軸ごとに焦点が異なる)

    ### M-059 (Cross-Cutting Pattern Meta-Audit)
    - 複数軸に共通して現れる根本原因を抽出
    - 個別 LOW だが横断で見ると HIGH な pattern を抽出
    - 修正の root cause を絞れる上位概念を抽出
    - 少なくとも 5 件の cross-cutting pattern を提示

    ### M-060 (Negative Space / 不在監査)
    - 他軸の finding は「あるもの」の検査。本軸は「無いもの」を列挙
    - counter-pair (start↔stop, encrypt↔rotate, alert↔recovery 等) の片側のみ存在を全件 list
    - finding 集合に逆の counter-pair が出ているかを check

    ### M-066 (Audit Meta-Process)
    - 今回の監査自体の bias / 盲点 / framing 限界を列挙
    - 軸選定の漏れ、与えた素材の不足、用語の恣意性
    - 次回監査 process の改善 5 件

    ### M-067 (Feedback Loop Topology)
    - 他軸 finding に出てくる自動 loop (retry / scale / alert / recover) を pickup
    - polarity / delay / governor / 干渉を表化
    - Meadows の 12 leverage points で介入未実施の高 leverage を提案

    ### M-061-M-065 など他の C8 軸
    - 各軸の prompt skeleton を忠実に実行
    - 他 Round finding を素材として使う

    ## 出力形式

    通常の finding フォーマット (axis-auditor-prompt.md と同じ) に加え、
    **横断パターン** セクションを追加:

    ```
    ## 横断パターン (M-059 形式、Meta 軸全般で出力)

    ### Pattern 1: {pattern name}
    - 関連 finding: [M-XXX-#1, M-YYY-#3, M-ZZZ-#2, ...]
    - 共通する根本原因: 1-2 行
    - 上位概念での修正提案: 1-2 行
    - severity (横断合算): HIGH | MED

    ### Pattern 2: ...
    ```

    ## 重要な制約

    1. **他軸 finding の単純再掲は禁止**。横断視点でのみ価値を提供
    2. **軸盲点指摘は具体的に**: 「セキュリティが足りない」ではなく
       「M-XXX で X が出ているのに、Y 経路が見られていない」のレベル
    3. **メタ批判の自家撞着回避**: 「監査自体に bias がある」と書く際は具体例 1 つ以上
    4. **status 判定**:
       - DONE: 横断パターン ≥ 3 件 (M-059 系) or 軸固有 finding ≥ 5 件 (他 Meta 軸)
       - DONE_WITH_CONCERNS: 出力数が少ないが他 Round の finding 自体が少ない
       - BLOCKED: 他 Round の finding 入力が空 (実行順序エラー)

    ## 報告フォーマット

    1. finding 件数サマリ
    2. finding 本体 (軸固有)
    3. 横断パターン (Meta 軸の主要価値)
    4. メタ批判 (監査 process 自体への提言、M-066 系のみ必須)
    5. 並走確認結果
    6. status
```

---

## Round 配置ルール (再掲)

- C1-C7 / C9 軸 → Round 1, 2, ... (parallelism=5 で均等分割)
- **C8 軸は必ず最終 Round** に配置
- C8 軸内でも複数あれば最終 Round 内で並列実行可能

例: 対象 30 軸のうち C8 = 4 軸 (parallelism=5)
- Round 1: 5 軸 (C1-C7/C9 から)
- Round 2: 5 軸 (同上)
- Round 3: 5 軸 (同上)
- Round 4: 5 軸 (同上)
- Round 5: 5 軸 (同上)
- Round 6: 4 軸 (**C8 のみ**、他 5 Round の finding を input にして並列実行)
