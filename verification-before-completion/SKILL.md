---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

Before saying that tests pass, a build succeeds, a bug is fixed, or a task is done, run the command that shows it in this session and read its output. State the result with that evidence; if the output contradicts the claim, report the actual status instead.

| Claim | Evidence | Not sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | An earlier run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Original symptom no longer reproduces | Code changed, assumed fixed |
| Regression test works | Fails with the fix reverted, passes with it restored | Test passes once |
| Agent completed | VCS diff shows the changes | The agent's success report |
| Requirements met | Each requirement in the plan checked against the result | Tests passing |

Run the full command when the claim covers the whole suite or build. One check at the point of the claim is enough; there is no need to re-run it before each intermediate step.
