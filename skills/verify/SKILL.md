---
name: verify
description: Record what ran against this exact change, and what it showed - run the project's own checks cheapest first on the affected selection, stop at the first failure, record each command with its exit status, summary and the state of the change it ran against, check locked files by hash, settle an unsure server behaviour with one targeted call, put each design frame beside an app screenshot, and list what did not run. Judges nothing. Use for "verify this change", "run the checks", "what passes now", "is the evidence current", or when the run reaches Verify.
argument-hint: "[plan file] [--round | --final]"
---

# verify

Produces evidence, not opinions: one record per check, written by a script at the moment it ran. The agent that wrote the code is the least reliable witness that it works, so nothing here comes from an implementer's account. `$ORCHARD` is the folder two levels above this file.

`--round` (default) runs the checks that run every round. `--final` runs them, then the once-per-run checks, after the last edit.

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| The change, the profile's commands, the lock snapshot, the plan's scenarios, real-backend rows and design frames | `<reports_dir>/<name>/evidence.jsonl`; renders and screenshots in `<reports_dir>/<name>/screens/` ([task files](../../roles/coordinator.md#task-files)) | Edits code, tests or scenario files; reruns a failed check in hope of a pass; widens to a full suite to feel safe; calls production | Nothing; a check it cannot run is recorded as not run | The evidence file itself; `evidence.py stale` printing nothing |

## Why

The agent that wrote the code is the least reliable witness that it works. It rests on the test pyramid, fail fast and test impact analysis.

## Stance

Witness. What ran against this exact change, and what did it print? Tier: light, recommended: scripts do the work.

## General steps

1. Fix the exact version of the thing being checked. 2. Run the checks cheapest first, and stop at the first failure. 3. Record each observation as it was produced: what ran, on what, with what result. 4. Discard any observation made on an earlier version. 5. List what was not observed.

## Method

Every check below runs through the recorder, so the record is the script's, not yours:
`python3 -I "$ORCHARD/scripts/evidence.py" record <reports_dir>/<name>/evidence.jsonl --check <key> --selection "<what was selected>" -- <command>`
`<key>` is the profile command key that ran (`build`, `lint`, `test.unit`, `test.behaviour`, `test.visual`, `test.integration`, `knowledge_base_check`, `pr_check`), or `lock` and `coverage` for the two scripts. The exit code passes through.

1. **Open.** Alone: as in [AGENTS.md](../../AGENTS.md#a-skill-called-alone), with `--skill verify`. In a run, the coordinator plays this role ([roles/verifier.md](../../roles/verifier.md)).
2. **Fix the version.** `python3 -I "$ORCHARD/scripts/evidence.py" state --root .` and note it. No edit may happen from here to the end of this step's checks; if one does, start again.
3. **Select.** Map the changed files (`git diff HEAD --name-only` plus untracked) to tests with `affected_map`. When it is `none`, every unit test is affected. Write the selection into `--selection`; the report names what was skipped.
4. **Static analysis**, whole change: `build`; `lint` (when `none configured`, record not run); `knowledge_base_check`; the lock (`lock_check.py verify <plans_dir>/<name>.lock.json`); a test traced to every scenario (`gate_check.py --coverage <plan> --id-pattern '<scenario_id_pattern>'`).
5. **Unit tests**, affected selection, `test.unit`.
6. **Behaviour tests in-process**, affected selection, `test.behaviour`, when the profile has one.
7. **Stop at the first failure.** Every later check is recorded as not run, "stopped after <check> failed". A failure is read, not retried: open the summary in the record, and the raw log only when the summary is not enough. A test that passes on a rerun is logged `runlog.py event RUN_ID flaky` and reported as a failure to diagnose.
8. **Once per run** (`--final` only, after the last edit):
   - Visual tests, when `test.visual` is not `disabled`.
   - Behaviour tests through the UI, affected selection, on a simulator held per `device_policy`. Never while an implementer's run is going.
   - Integration tests, `test.integration`, only on the endpoints the plan names and only in `backend_environments`; with no endpoint named, they are not run ([references/test-strategy.md](../../references/test-strategy.md), section 1).
   - Real-backend checks for the plan's hypotheses, as [references/run-flow.md](../../references/run-flow.md) section 8 says, by the four rules in [references/test-strategy.md](../../references/test-strategy.md), section 5, which also say what is not run when the profile has no `backend_cleanup`. Integration tests follow the same rules. A reply that contradicts the plan is classified by [references/gap-classification.md](../../references/gap-classification.md).
   - **Visual evidence wherever it can be captured** ([what counts as evidence](../../docs/principles.md#what-counts-as-evidence)). For each scenario a screen can show, when the app runs on a simulator in this run: a state, `evidence.py record <evidence.jsonl> --check screenshot --selection <scenario id> -- xcrun simctl io <device> screenshot screens/<scenario id>.png`, with the app driven to that state by the scenario's test or its launch arguments; a journey, start `xcrun simctl io <device> recordVideo --codec=h264 screens/<scenario id>.mp4` in the background, run the scenario's UI test, stop the recording with an interrupt, and record it with `--check recording`. Network behaviour: keep the request and reply shapes the integration test or real-backend check logged, masked. When no picture can be captured, record one line of reason; the claim rests on its other evidence.
   - Design frames: render each pinned frame in scope (`scripts/sources/figma_frames.py … render` when the design source is that tool), and screenshot the app in the same state (`xcrun simctl io <device> screenshot <path>`) into `screens/`. A frame with no matching app state says so; never pair a near one. These have a person as oracle: they go under manual checks.
   - **Last, the project's pre-pull-request checks**, `pr_check`, once per run, whole change, after every other check: `evidence.py record <evidence.jsonl> --check pr_check --selection all -- "<pr_check>"` (one quoted argument runs through the shell).
9. **Stale.** `python3 -I "$ORCHARD/scripts/evidence.py" stale <evidence.jsonl>`. Exit 1: each listed record ran on an earlier state. Run it again, or keep it only when `affected_map` shows the later edits did not touch what it covers; otherwise it is reported as not verified.
10. **Not run.** List every kind with no record and why: no command in the profile, disabled, stopped after a failure, no simulator, no backend, no endpoint named in the plan, no clean-up method in the profile. List every scenario a screen can show that has no screenshot or recording, with the reason, as a named gap for the developer.
11. **Close.** Alone: `runlog.py finish RUN_ID --outcome green|red|blocked`, and print `evidence.py table <evidence.jsonl>`. In a run, return the table and the not-run list to the coordinator; log `first_try_fail` and `wait` events.

## Rule that always holds

Evidence is output of this run; a rerun is not a fix.

## Gotchas

- **One simulator, one run.** Two runs on the same simulator stall or kill each other and no test runs. Check whether another session is testing; use `device_policy` to get one of your own.
- **A locked file may already be modified when work starts.** That is why the lock compares content hashes against the snapshot, not `git status`.
- **A new test file may need the project regenerated** before the test command sees it.
- **A whole UI suite is never the affected selection.** Name the classes or the scope option the profile gives.
