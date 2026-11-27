# Experiment: what planning and isolation cost on one seeded bug

Date: 2026-11-26. Roadmap P3, step 2. Status: one bug measured. This shows the measuring works; it sets no default.

## Set-up

- **Bug.** The refund sign in `TransactionStore.balanceCents()` (`SEEDED.md`): a purchase of 10.00 and a refund of 4.00 show 14.00, not 6.00. The approved scenario `@TS_LED_002` states the expected 6.00, so the compact plan applies.
- **Same start for every arm.** One `debug` run produced the diagnosis and the regression test `testRefundIsSubtractedFromBalance_TS_LED_002`. Both were committed into one base commit, and the three arms were copied from it. Every arm had the same regression test, the same tiers, the same review brief and the same verify scripts.
- **Arms.**
  - A: a full plan, at Standard (a separate implementer).
  - B: a compact plan, at Standard (a separate implementer).
  - C: the same compact plan as B, at Shared. The implementer is one agent that plays the main session: it gets the plan and the diagnosis, not a brief.
- **Roles.** Planner, implementer and reviewer each ran as a separate agent, so the tool reported their tokens and time. Verify was run by scripts (`evidence.py`, `lock_check.py`). The coordinator was the developer's session; its tokens are not available.
- **Approval.** The plans were marked approved for the experiment, under the owner's instruction to carry out P3 on the sample. No person read them before the run.
- **Model.** Every role ran on the same model, so tier labels did not change the model, and they do not confound the arms.

## Results

| | Shared diagnosis | A: full plan, Standard | B: compact plan, Standard | C: compact plan, Shared |
| --- | --- | --- | --- | --- |
| Plan tokens / seconds | — | 146,350 / 172 | 115,681 / 103 | (B's plan) 115,681 / 103 |
| Implementer tokens / seconds | — | 106,779 / 69 | 92,223 / 40 | 103,952 / 46 |
| Reviewer tokens / seconds | — | 126,064 / 80 | 119,768 / 49 | 123,165 / 62 |
| Verify (scripts), seconds | — | 7 | 8 | 8 |
| **Total tokens, excluding diagnosis** | 114,840 (157 s) | **379,193** | **327,672** | **342,798** |
| **Time, roles in sequence** | | **~328 s** | **~200 s** | **~219 s** |
| Files changed | | 2 (fix + table test of 5 cases) | 1 | 1, byte-identical to B |
| Checks on the final tree | | build, unit, PR check, lock: all pass | all pass | all pass |
| Blocking findings | | 0 | 0 | 0 |
| Non-blocking findings | | 2 (NOTE race in the test helper; NIT tuple labels) | 0 | 0 |
| Open questions from review | | 1 (negative amounts from the server) | 2 (negative balance untested; where the sign rule lives) | 1 (negative balance untested) |
| Fix rounds | | 0 | 0 | 0 |
| Minutes for a person to verify | | not measured | not measured | not measured |
| Corrections before acceptance | | not measured: no acceptance step was run | | |

## What it shows, for this one bug

- **What planning costs (A against B).** The full plan cost 31,000 more planning tokens (+27%) and 69 more seconds. It bought a table test of five boundary cases, which closed the gap that both B's and C's reviewers raised as an open question: an untested negative balance. It also added two minor findings in its own new test code. On a reproduced one-line defect with an approved scenario, the compact plan delivered the same fix for 14% fewer tokens.
- **What isolation costs (B against C).** The code was identical. The separate implementer (B) used 11,700 fewer tokens than the session that read the whole plan and diagnosis (C). That is the reverse of the expectation that Shared is cheapest. Caveat: in a real Shared run, the main session also carries the whole conversation, so C's real cost would be higher still, and this set-up cannot measure it.
- **Measurement gaps found.** The developer's minutes to verify, and the corrections at acceptance, need a person and were not measured. The coordinator's tokens are not reported. `runlog.py report` derives minutes from the start and finish times, not from the per-role seconds, so it showed 0.0 minutes for records written after the fact (fixed below).

## Not concluded

One bug cannot set a default. Following the roadmap, the default level and plan size wait for several bugs (the sample has five more seeded defects in `SEEDED.md`), or for real ones in P4.

## Changes made to the skill set because of this run

- `evidence.py` keeps the failing assertion line and shows it in the table (debug report, point 4).
- `debug` names its evidence file, binds the test to a scenario without editing the locked file, allows the reproduction test to become the regression test, and reports defects seen on the way.
- `AGENTS.md`: a skill that is a workflow step logs that workflow's name, and logs its tier once.
- The other points raised by the agents are listed in `evals/experiments/2026-11-26-followups.md`, with what was done about each.
