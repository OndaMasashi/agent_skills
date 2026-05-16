# HIGH Spot-Check Subagent Prompt Template

監査全体の HIGH 件 false positive 率を抑えるためのチェック工程。
SKILL.md の Phase 4 (Integrate) で起動する。

大規模監査の実績 (HIGH 18 件中 2 件 ≒ 11% が agent 誤読 false positive と判明した事例)
を踏まえ、本工程を **default ON** とした。`--no-spot-check` で skip 可能。

---

## 起動条件

- Phase 3 dispatch 完了後、全 finding を回収
- severity=HIGH の finding が 1 件以上ある場合に起動 (HIGH 0 件なら skip)

## Sampling ルール

```
HIGH 総数 N に対し:
- sample_count = max(5, ceil(N * 0.25))
- ただし N < 5 の場合は全件 (sample_count = N)
- sample は重複統合後の HIGH 全集合から均等乱択 (軸偏りを避ける)
```

実装メモ: 統合後 HIGH=18 → sample=5、HIGH=40 → sample=10、HIGH=4 → sample=4。

---

## Subagent Prompt Template

```
Task tool (general-purpose):
  description: "HIGH spot-check ({sample_count}/{total_high})"
  prompt: |
    あなたは監査品質保証の役割です。
    以下の HIGH finding {sample_count} 件について、claimed file:line を
    実コードに照合し、false positive (agent 誤読) を検出してください。

    ## Sampling 対象 (HIGH 全 {total_high} 件から {sample_count} 件抽出)

    {sampled_findings_block}

    各 finding は以下フォーマット:
    - [軸ID-#n] severity: HIGH
    - file: <path> / line: <N>
    - 症状: ...
    - 根本原因: ...
    - 修正案: ...

    ## 検証手順 (各 finding ごとに)

    1. **Read tool で claimed file:line を実コード読み込み**
       - line 範囲は前後 ±10 行を含めて context を確保
       - file が存在しない / 行番号が範囲外 → 即 false positive
    2. **claimed 症状 と 実コード を照合**
       - 症状が実コードに本当に存在するか
       - 「risk あり」claim の前提条件 (e.g., user input 経路) が実際に成立するか
       - 既に fix 済 / mitigated / unreachable な経路でないか
    3. **判定**:
       - `true_positive`: 実コードで確かに HIGH 相当の問題が観察される
       - `false_positive`: agent 誤読 / 過剰判定 / 既に fix 済
       - `severity_downgrade`: 問題はあるが HIGH→MED が妥当
    4. **判定根拠**: 必ず実コードからの引用 1-3 行を添える

    ## 出力形式

    ```yaml
    spot_check_results:
      - finding_id: M-XXX-#N
        verdict: true_positive | false_positive | severity_downgrade
        new_severity: HIGH | MED | LOW   # downgrade 時のみ
        evidence: |
          <実コード引用 1-3 行>
        rationale: <1-2 行>
    summary:
      sampled: {sample_count}
      true_positive: N
      false_positive: N
      severity_downgrade: N
      false_positive_rate: 0.XX  # false_positive / sampled
    ```

    ## 重要な制約

    - **claim を鵜呑みにしない**。必ず Read で実コード確認 (これがこの工程の存在意義)
    - **silent skip 禁止**。読めない file は file_not_found として false_positive 扱い
    - **bias 排除**: agent type が誰だったかで verdict を曲げない
    - **記録**: false positive と判定した finding も memory snapshot に「除外 finding (理由付き)」
      として残す (Q9 推奨案 a)。skill 改善イテレーションの学習材料にするため
```

---

## Phase 4 への返却データ

spot-check 完了後、SKILL.md は以下処理を行う:

1. `false_positive` 判定 finding を **HIGH 集合から除外** (除外リストとして memory に保存)
2. `severity_downgrade` 判定 finding は MED または LOW に **格下げ**
3. `false_positive_rate` を memory snapshot の Exec Summary に記録
   - 形式: `false positive 率: {N}% ({fp}/{sampled})`
4. FP 率が 20% 超なら memory snapshot に **警告** を追加
   - 「軸選定 / agent type 選定 / prompt skeleton の見直しを推奨」
