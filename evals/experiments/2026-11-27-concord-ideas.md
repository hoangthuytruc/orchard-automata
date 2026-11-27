# Six ideas taken from a second harness

Date: 2026-11-27. After a principles comparison with another agent harness (its testing skill is credited in
`THIRD_PARTY_NOTICES.md`; nothing was copied from the harness itself), six ideas were built here in this project's
own terms.

## Changed

| # | Idea | What was built | Where |
| --- | --- | --- | --- |
| 1 | The implementer cannot change a test once it is red | A red run names its test files (`evidence.py record --files`), the record keeps their hash, `evidence.py held` lists any that changed since, and `verdict.py` answers "Not ready" for one | `scripts/evidence.py`, `scripts/verdict.py`; run-flow section 3; `skills/implement`; `roles/implementer.md` |
| 2 | Approval is bound to the plan text | `plan_seal.py seal` at approval, `check` before round 1 and before the report; the status line, the Result and the Change note are outside the seal; `verdict.py` answers "Not ready" for a broken seal and lists a missing one as a gap | `scripts/plan_seal.py` (new); `skills/plan`, `skills/run`; run-flow sections 1 and 7 |
| 3 | Every failed loop has a cause | `runlog.py event loop_failed --cause plan_gap, executor, test_defect, flaky, environment or blocked`; the report counts them; `retro` reads them first | `scripts/runlog.py`; run-flow section 7; `roles/coordinator.md`; `skills/retro` |
| 4 | Affected callers | A "Callers" step before the impact perspectives, also for a compact plan; a "Callers" block in the review checklist | `references/impact-checklist.md`, `references/review-checklist.md`, `skills/plan`, `roles/reviewer.md` |
| 5 | Each hunk of a fix is tied to a finding | The review of fixes accounts for every hunk; one that fixes no finding is reviewed as new work | `references/review-checklist.md` part E; run-flow section 5; `roles/reviewer.md` |
| 6 | An independent plan verifier | A role that checks every plan before approval; on by default by the developer's decision the same day (first built off by default), turned off per workflow or with `plan --no-verify`; its result names the hash of the text it read | `roles/plan-verifier.md` (new); `skills/plan`; workflow files and template; `docs/workflow-model.md` |

Terms added to `docs/terms.md`: held test, plan seal, failure cause, caller.

## Evidence

**Scripts (ideas 1 to 3):** `scripts/selftest.py`, on a copy of `sample/Ledger`: 134 checks, all passed. The new
cases, by name: "evidence held: test file edited after its red run -> exit 1, named"; "a source edit does not break
it"; "a new red run of the edited test restores it"; "the latest red run per file counts -> holds"; "test file
removed -> exit 1"; "plan seal: status, Result and Change note written by later steps -> still holds"; "a work
package edited after approval -> exit 1, section named"; "runlog event: loop_failed without --cause -> exit 64";
"runlog report" showing "failed loops by cause: plan_gap 1, executor 1"; "verdict: a test file changed after its red
run -> Not ready"; "verdict: the plan edited after its seal -> Not ready"; "verdict: an unsealed plan is a gap, not a
reason".

**Plan verifier (idea 6), measured once.** One separate agent, started with the role's one-line prompt, on the
draft plan fixture `evals/fixtures/led-7-plan.md` in a copy of the sample, outside this repository.

| Measure | Value |
| --- | --- |
| Tokens | 119,679 (as the tool reported) |
| Time | 95 s |
| Objections | 14: 3 Wrong, 11 Missing |
| Text checked | hash `0ff90d9c7447`, equal to `plan_seal.py hash` of the plan afterwards |
| Files changed by the verifier | none (`git status` empty) |

What it found that no script here finds: recording a purchase makes no server call today, so the banner scenario
needs a request the plan never names; the planned unit test cannot observe a banner whose state lives in the app
target; the existing banner scenario TS_LED_003 can no longer happen once the app stops counting; the balance fix
names no callers and leaves out the sibling month total with the same defect; the planned balance test has no seam
to read the store without a sleep. It also listed what it checked and found right, and six questions for the
developer.

Caveat: the fixture is a short plan written for another eval case, with no requirements, design change, impact or
packages sections, so six of the fourteen objections are about what the fixture leaves out on purpose, and
`gate_check.py --coverage` already reports the missing requirements. The measurement shows the role works and what
one check costs; it does not show how often a full plan written by `plan` would have objections.

## Not verified

- Ideas 1 to 3 were proved on the scripts. No run of `run`, `implement` or `plan` has used them end to end, so
  whether an implementer stops on a test defect, and whether the coordinator picks the right cause, is not shown.
- Ideas 4 and 5 are prose rules: no reviewer or planner was run with them.
- The held-test check sees a file, not a test: an earlier test edited in the same step as a new red run in that file
  is left to the review of fixes.
- No eval run, and no grader for any of the six.
