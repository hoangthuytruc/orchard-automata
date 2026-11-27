---
name: implement
description: Build one work package of an approved plan, or one small task, test first in an iOS or Swift codebase - write the test bound to the scenario, see it fail for the right reason, write the least code that passes, remove what the change made unused, self-review, and stop at green without committing. Edits only the files the package owns. Use for "implement package 2", "implement this", "fix this from the failing test", "make X work", "add tests and implement", or when the run starts an implementer with a brief.
argument-hint: "<plan file and package number | brief file | task in words>"
---

# implement

Red, green, refactor, verify, report. The change ships with the tests that prove it and is left uncommitted. `$ORCHARD` is the folder two levels above this file.

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| One package of the approved plan, or its brief; the code it touches; [references/standards.md](../../references/standards.md), [references/test-strategy.md](../../references/test-strategy.md) | Code and tests in the files the package owns, uncommitted; red-run records through `evidence.py` | Edits a file it does not own or a locked file; weakens, skips or deletes a test; adds a dependency, build setting or CI step; commits | Nothing. It ends early when it needs a file it does not own | The return (format in [references/run-flow.md](../../references/run-flow.md), section 3): each test with the reason it failed first, backed by its red-run record, each command with its exit status. A claim until `verify` records it |

## Why

A test written after the code passes without proving the change. It rests on test-driven development and the smallest change.

## Stance

Minimalist. What is the least change that makes this failing test pass? Tier: set per package by the plan (rule 7 in [docs/workflow-model.md](../../docs/workflow-model.md#tiers)).

## General steps

1. Write the check that will show the outcome, first. 2. See it fail for the expected reason. 3. Make the smallest change that makes it pass. 4. Remove what the change made unnecessary. 5. Stop and report when it has not converged after a fixed number of attempts.

## Method

**Called alone.** Open as in [AGENTS.md](../../AGENTS.md#a-skill-called-alone) with `--skill implement`. A task with no plan gets a few lines first: the behaviours as test names, the files to touch, what is out of scope. Ask only what blocks the work, once; state every other assumption. Then the steps below, using the profile's commands.

**In a run.** The brief (run-flow, section 2) is your whole world: its rows, its owned files, its locked globs, its commands. Do not open the profile check or the run log; the coordinator keeps them.

1. **Discover.** `bash "$ORCHARD/scripts/discover.sh" .`; read the guides it lists and the project's review rules. Use only the commands the brief or the profile gives (`build`, `test.unit`, `test.behaviour`, `lint`, `generate`): never a hand-rolled `xcodebuild` when a project command exists.
2. **Understand the blast radius.** The types to change, their callers, the tests that already cover them, and the neighbour that shows the pattern to follow.
3. **Red.** For each scenario row, write the test at the cheapest kind that can observe the claim (the plan names it), bound to the scenario id as the project binds tests. If the project needs regenerating before a new file is seen, run `generate`. Run the scoped test command as a red run, recorded as [references/run-flow.md](../../references/run-flow.md) section 3 says (alone: in `<reports_dir>/<name>/evidence.jsonl`). Each new test must fail on its assertion, not on a compile error or a crash. Record the reason it failed. Name the test files in the red run (`--files`): from then on they are held by their hash, and you do not edit them. A test that turns out wrong is not adjusted until it passes: stop and return "test defect" with the evidence, or see it fail again in its new form and record that as a new red run.
4. **Green.** The least implementation that passes, in the project's pattern and to the standards: isolation stated per type, no force unwraps or `try!`, clock, ids and randomness injected, accessibility identifiers on new controls, strings through the project's localisation, previews for new screen states.
5. **Refactor.** Remove duplication you introduced; delete imports and symbols your change made unused. Touch nothing unrelated; name unrelated problems in the return.
6. **Check.** The scoped tests, then `lint`. On a failure, fix the cause. Never edit a test after its red run to get there; never weaken an assertion, add a sleep or retry, raise a timeout, skip or delete a test, or lower a coverage floor.
7. **Loops.** A loop is one red-green attempt that ends with the scoped tests still failing. After two failing loops on a light tier, stop and return both failures: the coordinator runs the third on the strong tier. After the third, stop and return where it stands.
8. **Self-review** the diff against the line review in [references/review-checklist.md](../../references/review-checklist.md). Fix what you find.
9. **Return** in the format of [references/run-flow.md](../../references/run-flow.md), section 3. State that nothing is committed. Alone: `runlog.py finish RUN_ID --outcome green|red|blocked`; log `first_try_fail` for a check that failed on its first run.

**Fix rounds.** Each finding starts with a test that fails because of it, then the least fix. The finding's text is quoted in the brief; do not widen the fix beyond it.

**Stop and say, never reach.** A file you do not own, a locked file, or a plan row the code cannot satisfy: stop, name it with the reason, and return. Never edit it.

## Rule that always holds

Edit only owned files; never weaken a check.

## Gotchas

- **A working copy starts from the last commit** and may not build as it is: it lacks the uncommitted work of the main tree and may need the project's local setup first.
- **A new test file may need the project regenerated** before the test command sees it.
- **One simulator, one run.** Two runs on one simulator stall each other. Follow `device_policy`; never start a UI run the brief did not ask for.
- **Project guides override core.** When they conflict with the standards, follow the project and say so in the return.
- **No narrative comments**, and nothing in code or comments that attributes it to an AI or a tool.
