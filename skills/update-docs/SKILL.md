---
name: update-docs
description: After the developer accepts a run, write the delivered scenario changes into the project's knowledge base (feature files and requirements register) in the project's own format, each with its basis, evidence and test; leave out what was not delivered; run the scenario check; show the diff. The only skill allowed to write the scenario files. Changes no code or tests, never commits. Use for "update the docs", "update the knowledge base", "write the scenarios into the feature file", "apply the approved scenarios", "update the register", "close the plan", or after "accept".
argument-hint: "<plan file>"
---

# update-docs

Records what the app now does. It runs only on a plan with status `accepted <date>`, and writes only what was delivered and accepted. `$ORCHARD` is the folder two levels above this file.

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| The accepted plan; the accepted test report; the project's format for its scenario files | The files under `knowledge_base` and `register`; the plan's Change note and status `documented <date>` | Changes code or tests; writes a scenario not delivered; reuses an id; writes a pending or gap tag; writes to a tracker, wiki or design tool; commits | Review of the diff; the commit | `lock_check.py verify` before writing; `gate_check.py` and `knowledge_base_check` after; `git diff` of the knowledge base |

## Why

Documentation written before acceptance records intent, and the next plan builds on fiction. It rests on living documentation and a single source of truth.

## Stance

Recorder. What was delivered and accepted, and nothing more? Tier: light, recommended.

## General steps

1. Wait until the result is accepted. 2. Take only what was delivered and accepted. 3. Write it into the one place of record, in that place's format. 4. Check the record against the result. 5. Show the change to the owner.

## Method

1. **Open** as in [AGENTS.md](../../AGENTS.md#a-skill-called-alone), with `--skill update-docs`.
2. **Status.** The plan's status must be `accepted <date>`. Anything else: stop with one line saying what is missing.
3. **Lock.** `python3 -I "$ORCHARD/scripts/lock_check.py" verify <plans_dir>/<name>.lock.json`: the locked files must be as the run left them. A mismatch: stop, name the file and both hashes. (A re-check has no snapshot; skip this step.)
4. **Read** the plan's scenario changes and Result, and the test report's Scenarios table. Read the project's guide for its scenario files: format, tags, id rules.
5. **Select.** Delivered, with a passing record on the final change: written. Not delivered, or no passing test: left out, listed in the Change note with the reason. Leftover code of an undelivered scenario still in the tree: stop and send the work back to `run`.
6. **Write the feature files.** Add, change and remove scenarios in the project's format, order and rules, per [references/scenario-register.md](../../references/scenario-register.md). Provisional ids `N1`, `N2` get the next free real ids matching `scenario_id_pattern`; ids are never reused. Frames are written `F/<id>`.
7. **Keep the register in step.** One row per scenario: basis (`Spec`, `Design`, `Spec + Design`, or a `Team decision` with who and date), evidence, tests. Only tags allowed on a scenario written or changed here: the untested tags of [references/scenario-register.md](../../references/scenario-register.md) (core default, or the profile's `tag_policy_untested` override).
8. **Check.** `python3 -I "$ORCHARD/scripts/gate_check.py" <feature file> <register> --id-pattern '<scenario_id_pattern>' --strict-ids <ids written or changed>` (add `--only-strict` when the register does not cover the whole feature yet), then `knowledge_base_check`. Fix the files until clean, never the check.
9. **Show the diff.** `git diff -- <knowledge_base paths> <register paths>`.
10. **Close.** Write the Change note in the plan: what was written, what was left out and why, spec updates product must make. Set `Status: documented <date>`. Delete the lock snapshot. `runlog.py finish RUN_ID --outcome green|blocked --findings <left out>`.

## Rule that always holds

Only what was delivered and accepted; no code.

## Gotchas

- **The feature file may have changed since the plan was written.** Re-read each scenario's title and steps when you write its row; a moved id or a reworded step is a question for the developer, not a merge to guess.
- **A register may be missing, or in an older format with no basis column.** Rewrite it for the whole feature only when the plan covers the whole feature; otherwise add this plan's rows, check them with `--only-strict`, and say what remains.
- **A bound test can be the wrong test.** Open it. A name or body that does not match the scenario goes back to `run`.
- **A scenario is never tagged manual to make the check pass.**
- **Generated reading copies** of the feature files are regenerated with the project's own command, never edited by hand.
- **A change to a shared guide is drafted for the developer**, never written.
