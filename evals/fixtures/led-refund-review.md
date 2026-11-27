# Review: led-refund

Plan: .orchard/runs/plans/led-refund.md

## Round 1: full review (strong tier)

| # | Type | Severity | Where | Finding | Fix | State |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Risk | Medium | Tests/LedgerTests/TransactionStoreTests.swift | No test proves the plan's contract that `latest()` is nil on an empty store. Counterexample: reverting `latest()` to `.first!` leaves every test green. | Add `testLatestIsNilWhenEmpty` | fixed in round 2 |
| 2 | NOTE | | Tests/LedgerTests/TransactionStoreTests.swift:18 | `testRefundReducesBalance` waits for the async `add` with `sleep(1)`, like the existing test: slow, and timing-dependent on a loaded machine. | Make `add` synchronous or awaitable and drop the sleep | open, for the developer |
| 3 | NOTE | | Sources/Ledger/TransactionStore.swift:11 | `add` appends on a private queue while every read runs on the caller's thread: a data race. Out of this plan's scope. | A later plan: actor or synchronised reads | for the developer |

## Round 2: review of the fixes (light tier)

No new findings. Finding 1 is fixed by `testLatestIsNilWhenEmpty`.
