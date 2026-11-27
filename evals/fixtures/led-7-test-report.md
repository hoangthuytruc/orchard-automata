# Test report: led-7

## Verdict
Ready to accept: refunds lower the balance and the limit banner shows when the server refuses a purchase.

## What was not built
- A rejected offline purchase stays marked "Rejected": the offline queue is a later ticket. Its code and tests were removed.

---

# Detail
Plan: .orchard/runs/plans/led-7.md · Workflow: feature-development · Isolation: Standard · Rounds: 1

## Scenarios
| Scenario | Delivered | Kind | Test | Result on final change | Screenshot or recording | Network log | Code reference | Check record |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TS_LED_002 | yes | unit | TransactionStoreTests.testRefundReducesBalance | passed | no picture: not captured in this run (no simulator available) | none: no network call | Sources/Ledger/TransactionStore.swift | swift test |
| N1 | yes | unit | DailyLimitTests.testBannerShowsResetTimeOnDailyLimit | passed | no picture: the sample app has no daily-limit screen | none: no network call | Sources/Ledger/TransactionStore.swift | swift test |
| N2 | no | | | not built | | | | |

## Findings
None open.

Accepted by the developer on 2026-11-25.
