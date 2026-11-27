---
name: debug
description: Find why something fails in an iOS or Swift codebase - reproduce it on demand, reduce it to the smallest case, test one hypothesis at a time, confirm the cause by turning it on and off, and leave one regression test that fails because of the cause. Never fixes. Use for "why does this crash", "find the cause of", "this fails sometimes", "debug this", "it worked before", "reproduce this bug", or as the first step of a bug fix.
argument-hint: "<what you saw> --expected <what you expected> [--since <commit>]"
---

# debug

Produces a diagnosis and one failing test, and stops. The fix is an `implement` job that starts from that test. `$ORCHARD` is the folder two levels above this file.

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| The failing behaviour as reported, logs, crash reports, the code, its tests, history (`git log`, `git bisect`) | `<reports_dir>/<name>/diagnosis.md` and `<reports_dir>/<name>/evidence.jsonl`; one regression test in the project's tests | Fixes the code; changes behaviour; writes more than one test; edits scenario files; commits; calls production | What was seen and what was expected; access to a log or a device when the defect needs one | The reproduction command with its output; each hypothesis with the experiment and its result; the regression test failing on its assertion, recorded through `evidence.py` |

## Why

A fix for a symptom without a reproduced cause adds a second defect and no proof. It rests on the scientific method and bisection.

## Stance

Scientist. Can I reproduce it, and which one experiment splits the hypotheses? Tier: strong, recommended; light once the defect is reproduced.

## General steps

1. Reproduce the problem on demand. 2. Reduce it to the smallest case that still shows it. 3. State one hypothesis and the experiment that would refute it. 4. Run it, keep or discard the hypothesis, and repeat. 5. Confirm the cause by turning the problem on and off. 6. Leave a check that fails because of the cause.

## Method

1. **Open** as in [AGENTS.md](../../AGENTS.md#a-skill-called-alone), with `--skill debug --task "<symptom>"`. Name the task folder `<date>-<slug>` ([task files](../../roles/coordinator.md#task-files)).
2. **Discover.** `bash "$ORCHARD/scripts/discover.sh" .`; read the guides. Use only the profile's commands.
3. **Write the claim.** Seen, expected, where, since when. Check whether an approved scenario states the expected behaviour (`grep` the `knowledge_base` for it); note its id or "none". Code is not the expected behaviour.
4. **Reproduce.** The cheapest way that shows it: a unit or in-process behaviour test, a script, the app on a simulator per `device_policy`. Run it through `evidence.py record … --check <kind>` so the failing output is recorded. Not reproduced after a fixed effort: stop, write what was tried, outcome `blocked`. No fix is proposed for what is not reproduced.
5. **Reduce.** Remove inputs, steps and state until the failure disappears; keep the last case that still fails. With a known good commit, `git bisect run <the reduced command>` names the change that introduced it.
6. **Hypotheses, one at a time.** Write each with the experiment that would refute it and the result you would expect. Run it. Keep or discard, and record both in the diagnosis. Common iOS causes to rank first: an unawaited task or a race between two tasks; state shared across actors or threads; a wall-clock, time-zone or locale dependency; a force unwrap or `try!` on a value the server or the disk can omit; a stale async result applied after a newer one; a sign or rounding error in money or units; order dependence between tests.
7. **Confirm the cause.** Turn it off and on: the smallest change to the cause makes the reduced case pass, and reverting it makes it fail again. Revert it fully; the confirming change is not the fix.
8. **Leave one regression test** at the cheapest kind that observes the claim, deterministic (clock, ids and randomness injected). The reproduction test may become the regression test; reduce and confirm experiments may edit it temporarily, and each edit is reverted. Bind it to the scenario id through the test's name and a one-line comment; the scenario files are locked, so never add a tag there. When determinism would need a code change, the test does the least it can without one (for example, waits for a condition with a bounded timeout, never a fixed sleep) and the diagnosis names the seam the fix should add. Run it: it must fail on its assertion, for the cause, not on a compile error. Record it through `evidence.py record --check <profile command key> --selection regression`; record experiments with `--selection experiment-<n>`. Their rows show as stale once reverted, which is expected.
9. **Write `diagnosis.md`:** claim; reproduction command and output; reduced case; hypotheses with experiments and results; cause at `path:line`; the regression test and its failing assertion line; the scenario id or "none"; what the fix must not touch, when known; "Seen on the way": other defects noticed, each with `path:line`, not investigated and not fixed.
10. **Close.** `runlog.py finish RUN_ID --outcome delivered|blocked`. Hand over: with a scenario id, the next step is `plan --compact`; with none, the expected behaviour needs a basis first and the work becomes a small feature.

## Rule that always holds

No fix before reproduction. `debug` never fixes; it leaves one failing test.

## Gotchas

- **A pass on rerun is not a pass.** An intermittent failure is reproduced with repetition and random order, and its rate recorded.
- **One simulator, one run.** Two runs on one simulator stall each other.
- **Never print tokens or personal data** from a log or a crash report into the diagnosis; quote shapes and codes.
