---
name: run
description: Drive a workflow file from an approved plan to the test report without asking anyone - snapshot the locks, start one implementer per work package with a brief that is its whole world, verify every round with scripts, start a separate read-only reviewer, run fix rounds on the tier each finding calls for (at most three), run the once-per-run checks after the last edit, and hand over a report. Does none of the work itself; records isolation, tiers and step-ups in the run log. Never commits. Use for "run the plan", "execute the plan", "build LED-7 from the plan", "continue the rounds", "fix the review findings", or right after a plan is approved.
argument-hint: "<plan file> [--workflow feature-development|bug-fix] [--accept | --send-back \"<words>\"]"
---

# run

The coordinator. It reads the workflow file and the plan's status, starts each role in order, and lets work move to the next state only when that state's exit evidence is recorded. It follows the rules of a run in [docs/workflow-model.md](../../docs/workflow-model.md#rules-of-a-run) and the procedure in [references/run-flow.md](../../references/run-flow.md); it plays [roles/coordinator.md](../../roles/coordinator.md). `$ORCHARD` is the folder two levels above this file.

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| The workflow file (`.orchard/workflows/<W>.md`, else `$ORCHARD/workflows/<W>.md`); the approved plan; the agents map | The plan's status (`executed`, then `accepted <date>`) and Result; the task files; the run log | Writes code, tests or scenario files at Standard or Strict; reviews; rewrites the plan; waits mid-run for an answer; commits | "approved" before; "accept" or a send-back after | The task files of each state ([roles/coordinator.md](../../roles/coordinator.md#task-files)); `runlog.py` records |

## Why

Orchestration is where trust leaks: a state skipped, an author reviewing their own work. It rests on state machine workflows and separation of roles.

## Stance

Referee. Is the evidence for this transition recorded? Tier: light, recommended: it does none of the work.

## General steps

1. Read the defined steps and the current state. 2. Hand each step to the role that owns it, with only what it needs. 3. Before each move, check that the required evidence exists. 4. On missing evidence or a conflict, stop and report; do not improvise. 5. Do none of the work yourself.

## Method

1. **Profile.** The profile check in [AGENTS.md](../../AGENTS.md#a-skill-called-alone). Exit 2, or exit 3 with a changed value: end early before any work.
2. **Start the log** with the isolation level from the plan header (else the workflow default): `python3 -I "$ORCHARD/scripts/runlog.py" start --workflow <W> --skill run --task "<name>" --isolation <shared|standard|strict>`. Log each package's tier: `runlog.py event RUN_ID tier --role implementer --tier <t> --note "package <k>: <reason>"`, and the tier planning or diagnosis ran on, when the developer says.
3. **Before round 1** ([references/run-flow.md](../../references/run-flow.md)): the plan status must be `approved <date>`, else end with one line; the base branch in the plan header must be an ancestor of `HEAD` (`git merge-base --is-ancestor <base> HEAD`), else end early; record `git rev-parse HEAD`, `git status --short` and `evidence.py state`; snapshot the lock with `python3 -I "$ORCHARD/scripts/lock_check.py" snapshot <plans_dir>/<name>.lock.json <locked_globs>`.
4. **Implement.** At Standard and Strict, start one implementer per package, even for one package, with the brief from run-flow section 2, saved as a file first ([roles/implementer.md](../../roles/implementer.md)), the way the agents map and the tool's adapter say. Packages with no dependency between them run side by side, at most `workers` at once. A shared tree or a working copy each, as the plan says; bring working copies into one tree as run-flow says. A conflict ends the run: the split was wrong. At Shared, the main session builds the package itself by `implement`, and the run stays logged as Shared. Save each return as `<plans_dir>/<name>/package-<k>-round-<r>.md`, and the change as `round-<r>.patch` beside it.
5. **Verify** (`verify --round`). `Implement → Verify` needs every return of the round saved and its red runs checked ([references/run-flow.md](../../references/run-flow.md), section 3). A check that fails because of the change opens a fix round for the owning package when a round is left.
6. **Review.** Round 1: a full review by [roles/reviewer.md](../../roles/reviewer.md) on the strong tier, given the root, "working tree" and the plan path, nothing else. After a fix round: a review of fixes on the light tier. Save it unchanged as `<plans_dir>/<name>/review-round-<r>.md`. Log each blocking finding as `finding`. A second full review only when a fix round changed more than the findings asked, or a review of fixes raised new findings.
7. **Fix rounds.** Blocking: Blocker, Risk, High, Medium. One implementer per package with a blocking finding, on the tier the finding calls for, each fix starting with a test that fails because of the finding; then step 5 and step 6. A package that failed two loops runs its third on the strong tier with both failures in its brief: log `step_up --note "<failure before it>"`. After that, it stops: the package is not delivered. At most three rounds.
8. **Once per run.** After the last edit: `verify --final`. A failure with a round left opens a fix round like a blocking finding; with none left, the verdict is `blocked`.
9. **Not delivered.** Code and tests for scenarios not delivered are removed by an implementer, as a package of its own; then step 8 again on what it touched.
10. **Ready.** Fill the plan's Result; set `Status: executed`. The report by `handoff` in this session at Shared and Standard; at Strict, start the report writer ([roles/report-writer.md](../../roles/report-writer.md)). `runlog.py finish RUN_ID --outcome green|red|blocked|ended_early --findings <open>`. Give the developer the report path and the verdict.
11. **After.** `--send-back "<words>"`: log `send_back --note "<their words>"`; one more fix round with a review of fixes, then steps 8 and 10. `--accept`, or "accept" in the developer's words: set `Status: accepted <date>`; `runlog.py rate RUN_ID --accepted <n> --rejected <n> --rework-minutes <n> --verify-minutes <n>` with the figures the developer gives. Then `update-docs` may run.

**Ends early** only when going on would mean guessing (the list in the workflow file): log `ended_early --note "<conflict>"`, write both sides into the report, finish with `--outcome ended_early`. Never wait mid-run for an answer.

## Rule that always holds

A transition needs recorded evidence. The reviewer is never the author; the coordinator does none of the work.

## Gotchas

- **A working copy starts from the last commit** and may not build as it is; it lacks the main tree's uncommitted work and may need the project's local setup.
- **Agents do not see this conversation or any memory.** Everything a package needs is in its brief.
- **A locked file may already be modified when the work starts.** The lock compares content hashes against the snapshot, not `git status`.
- **A new test file may need the project regenerated** before the test command sees it.
- **One simulator, one run.** Never start a check while an implementer's run is going; log time spent waiting as `wait`.
- **Tokens come from the tool's report or nowhere.** When the tool does not report them, log `--tokens na`.
