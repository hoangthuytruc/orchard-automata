---
name: test
description: Write, harden or repair automated tests for iOS or Swift code so each fails for the right reason - unit tests (Swift Testing or XCTest), in-process behaviour tests, visual tests, deterministic seams (injected clock, ids, randomness, transport), flaky-test diagnosis with the failure rate before and after, and suite audits. Changes only the proof of behaviour that exists, plus the smallest seam the test needs. Use for "add tests for X", "this test is flaky", "make this test deterministic", "audit the test suite", "how should I test this", "this test is slow or random", or when code has no tests.
argument-hint: "<type, file, feature or test name> [write|flaky|audit]"
---

# test

Three modes, chosen from the argument or the context: **write** (add tests to a target), **flaky** (diagnose and fix a nondeterministic test), **audit** (health of a suite). The deliverable is deterministic tests that fail for the right reason, or a ranked audit. Nothing is committed. A test strategy for a planned change belongs to `plan`. `$ORCHARD` is the folder two levels above this file.

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| The code under test, its existing tests, [references/test-strategy.md](../../references/test-strategy.md) (read first, every time), [references/standards.md](../../references/standards.md) | Tests and the smallest seam the code needs; for audit, a report at `<reports_dir>/test-audit-<date>.md` | Changes behaviour; weakens a test; records snapshots, or runs UI, monkey or real-backend suites unasked; commits | Whether to keep the tests; for a new dependency (a property-testing library), the decision | Each test with the reason it failed first; for flaky, the failure rate before and after, with the command |

## Why

A weak test gives false confidence, and that confidence is reused on every later change. It rests on test design techniques, test doubles and deterministic tests.

## Stance

Falsifier. What would make this test fail, and is that the right reason? Tier: light, recommended; strong for a flaky test.

## General steps

1. State the claim precisely. 2. Choose the cheapest observation that could contradict it. 3. Choose the inputs: the typical case, the boundaries, the invalid. 4. Remove chance: fix time, order and randomness. 5. Confirm that the check fails when the claim is false.

## Method

1. **Open** as in [AGENTS.md](../../AGENTS.md#a-skill-called-alone), with `--skill test --task "<mode>: <target>"`.
2. **Discover.** `bash "$ORCHARD/scripts/discover.sh" .`; read the guides it lists, especially a testing guide. Use only `test.unit`, `test.behaviour`, `test.visual` from the profile, scoped as narrowly as the project allows.
3. **Read** the code under test and the tests that already exist for it.

**write**

4. Name each contract (happy, empty, failure, boundary, cancellation, stale result) and pick its kind by the claim: a value or rule is a unit test; how the app reacts is a behaviour test, in-process unless the claim needs real screens; how a screen looks is a visual test. Prefer a property over a table of boundary values when the claim is a rule (round trip, idempotency, invariant).
5. Add the seams the code lacks (clock, ids, randomness, transport) with the smallest production change, in the project's style.
6. Write the tests. Run the scoped command. A test written for a bug or a missing branch must fail before the behaviour exists; break the claim on purpose when it already exists, and see the test fail.

**flaky**

4. Follow the flaky procedure in [references/test-strategy.md](../../references/test-strategy.md): reproduce with repetition and random order (at most ten runs, or the runner's iteration option), record the rate and the exact message; classify (wall clock, unawaited work or a race, shared state, order, real network or simulator state, a timeout tuned to a fast machine); fix the cause in the code or the seam; prove it with the same repetition. Log `runlog.py event RUN_ID flaky --note "<test>: <rate before> → <rate after>"`.

**audit**

4. Collect the suite-audit signals from the test strategy for the scope. Rank: tests that can give a false green first (no assertion, swallowed failures, skipped), then nondeterminism (sleeps, time, shared state), then gaps (untested types on main journeys), then speed. Write the report; give the top five in chat. No fixes.

**Close.** Tests added or changed by name, commands run with exit statuses, what was not run. `runlog.py finish RUN_ID --outcome green|red|delivered --findings <audit items or 0>`.

## Rule that always holds

The cheapest kind that can observe the claim; no sleeps.

## Gotchas

- **Tests find UI by accessibility identifier, never by visible text**, and wait on element state, never on time. Where an element cannot carry an identifier, mark the exception the way the project requires.
- **A retry, a sleep, a longer timeout, `.serialized` without a stated reason, or a skip is never the fix** for a flaky test.
- **A pass on rerun is a failure to diagnose**, not a pass.
- **No real personal data in fixtures; no live network in unit tests.**
- **Project guides override core.** Say so when you follow them against the test strategy.
