# First eval run on the sample

Date: 2026-11-26. Roadmap P5. Harness: `claude plugin eval` through `adapters/claude-code/eval.sh`, one run per case and arm (smoke), so each number is a single sample: a signal, not a verdict. Results: `evals/results/` (not tracked).

## Smoke run, all 16 cases

| Case | With skills | Without | Delta | Graders failed with skills |
| --- | --- | --- | --- | --- |
| plan-led7 | 1.00 | 0.50 | +0.50 | none |
| update-docs-led | 0.83 | 0.33 | +0.50 | register-right |
| debug-ledger-latest-crash | 0.86 | 0.50 | +0.36 | regression-test |
| retro-ledger | 1.00 | 0.64 | +0.36 | none |
| workflow-review-only | 1.00 | 0.67 | +0.33 | none |
| handoff-ledger | 0.92 | 0.62 | +0.31 | no-tool-credit |
| debt-ledger-report | 1.00 | 0.70 | +0.30 | none |
| implement-refund-balance | 1.00 | 0.80 | +0.20 | none |
| review-ledger-package | 0.91 | 0.73 | +0.18 | honest-report |
| adopt-ledger | 0.67 | 0.58 | +0.08 | profile-quality |
| test-deterministic-store | 1.00 | 1.00 | 0.00 | none |
| plan-draft-ledger | 0.64 | 0.64 | 0.00 | scenarios-right |
| plan-recheck-ledger | 0.56 | 0.56 | 0.00 | basis-and-verdicts, gate-contract |
| run-led-refund | 0.53 | 0.73 | −0.20 | see below |
| verify-ledger | 0.50 | 0.58 | −0.08 | see below |
| workflow-bug-fix-refund | 0.47 | 0.67 | −0.20 | see below |

Overall: 12 of 16 cases above the threshold, mean delta +0.17. Cost of the smoke run: 18.77 USD.

## What the three negative cases showed

1. **A false alarm in the no-commit guard.** The guard's pattern `git (…|merge)\b` matched `git merge-base`, which `run` uses to check the base branch. No commit was made. The pattern now excludes it (`merge(?![-\w])`) in all 16 cases.
2. **The sandbox blocks git.** `evidence.py` needed git to fingerprint the change, so `verify` and `run` stopped as blocked. `evidence.py state` now hashes the files themselves (`nogit-…`) when git cannot run and a root is given; three selftest cases cover it.
3. **The sandbox blocks SwiftPM's build.** After fix 2, the re-run still stops at `swift build`, because SwiftPM's own sandbox cannot start inside the harness's sandbox. The skills use only the profile's commands and report "blocked" truthfully; the arm without skills improvises with `swiftc` and scores higher. This is a limit of the harness on this machine, not of the skills, and it is not worked around: telling a run to use `--disable-sandbox` made both arms hang in the source plugin's experience.

Re-run of the three cases after fixes 1 and 2: `workflow-bug-fix-refund` 0.80 against 0.60 (+0.20); `verify-ledger` 0.67 against 0.92 (−0.25); `run-led-refund` 0.60 against 0.73 (−0.13). The last two stop on limit 3. Cost: 6.18 USD.

## Still to do

- Run `verify`, `run` and the bug-fix workflow on a machine or harness where `swift build` can run, before trusting their scores.
- Look at the four cases with no gain (`test`, two plan modes, `adopt`) and the single grader failures above, case by case, with `eval.sh full` (three runs each) before changing a skill: one run is too noisy to act on (rule "twice, not once").
