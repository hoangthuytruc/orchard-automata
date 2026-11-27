# Seeded defects in the sample

For graders and for the run log's `seeded_missed` count. Never show this file, or point to it, in a prompt: an
agent under test must find these on its own. Lines are those of `sample/Ledger` as committed; a change to the sample
must update this list.

## In the sample code

| # | Defect | Where | Kind | Found by (cases) |
| --- | --- | --- | --- | --- |
| S1 | Data race: `add` appends on a private serial queue (`queue.async`) while `transactions`, `balanceCents`, `latest` and `monthTotalCents` read on the caller's thread | `Sources/Ledger/TransactionStore.swift:13` (write), `:6` (unsynchronised public read), `:18`, `:22`, `:27` (reads) | concurrency | review-ledger-package, debt-ledger-report, test-deterministic-store |
| S2 | Force unwrap crash: `latest()` returns `.first!` and crashes on an empty store | `Sources/Ledger/TransactionStore.swift:22` | crash | debug-ledger-latest-crash, implement-refund-balance, run-led-refund, review-ledger-package |
| S3 | Refunds added as positive amounts: `balanceCents` sums `amountCents` and ignores `kind` | `Sources/Ledger/TransactionStore.swift:18` | logic (spec v3 §1, §2; scenario TS_LED_002) | implement-refund-balance, run-led-refund, workflow-bug-fix-refund, review-ledger-package, plan-recheck-ledger |
| S4 | Auth token stored in `UserDefaults` (project rule LR-1) | `Sources/Ledger/SyncClient.swift:11` (write), `:16` (read) | security | review-ledger-package, debt-ledger-report |
| S5 | Wall-clock `Date()` read inside `monthTotalCents`: the month cannot be fixed in a test | `Sources/Ledger/TransactionStore.swift:26` | determinism | test-deterministic-store, review-ledger-package, debt-ledger-report |
| S6 | `sleep(1)` in the only test, to wait for the asynchronous `add` | `Tests/LedgerTests/TransactionStoreTests.swift:8` | test determinism, speed | test-deterministic-store, review-ledger-package, debt-ledger-report |
| S19 | S3 seen through the app: the UI test `testPurchaseThenRefundShowsBalance` fails, the balance reads "$85.00" where spec v3 §1 gives "$65.00" (seed 50.00, purchase 25.00, refund 10.00); the screenshot of the balance screen shows the same wrong total | `App/LedgerAppUITests/LedgerAppUITests.swift:17` (assertion); cause `Sources/Ledger/TransactionStore.swift:18` | logic, through the UI (same defect as S3) | verify-ledger-app |

Others found while porting (not required by any grader, credited when reported):

| # | Defect | Where | Kind |
| --- | --- | --- | --- |
| S7 | `monthTotalCents` also ignores `kind`: a refund adds to the month's total | `Sources/Ledger/TransactionStore.swift:29` | logic |
| S8 | Force unwrap of the token when not signed in: `UserDefaults.standard.string(forKey:)!` crashes before sign-in | `Sources/Ledger/SyncClient.swift:16` | crash |
| S9 | `try!` decode and `data!` on the server reply: a malformed body or a missing body crashes | `Sources/Ledger/SyncClient.swift:22` | crash |
| S10 | HTTP status never read: a 401, 409 or 500 body is decoded as a list of transactions (and crashes, S9) | `Sources/Ledger/SyncClient.swift:17` | error handling |
| S11 | Completion called on a background thread for an error, on the main thread for success | `Sources/Ledger/SyncClient.swift:19` vs `:23` | concurrency, API contract |
| S12 | Every sync appends every transaction again to `TransactionStore.shared`: duplicates, no de-duplication by id; hidden singleton dependency | `Sources/Ledger/SyncClient.swift:24-25`, `Sources/Ledger/TransactionStore.swift:4` | logic, design (project smell) |
| S13 | Completion-handler `URLSession` API instead of async/await | `Sources/Ledger/SyncClient.swift:14`, `:17` | debt |
| S14 | Force unwrap on `NumberFormatter.string(from:)`; amount converted through `Double` (rule LR-3 is borderline: the conversion happens at formatting) | `Sources/Ledger/LedgerFormatter.swift:11` | crash risk, money |
| S15 | Shared currency formatter uses the current locale: output differs per machine, so any test of it is nondeterministic | `Sources/Ledger/LedgerFormatter.swift:4-8` | determinism |
| S16 | `Transaction` defaults `date` to `Date()` and `id` to `UUID()`: time and ids not injected | `Sources/Ledger/Transaction.swift:14` | determinism |
| S17 | Swift 5 language mode hides the data race from the compiler's strict concurrency checks | `Package.swift:11-12` | debt |
| S18 | Missing tests: refund, empty store, month boundary | `Tests/LedgerTests/TransactionStoreTests.swift` | evidence |

## In the sample's sources and scenarios

| # | Defect | Where | Settled by |
| --- | --- | --- | --- |
| D1 | TS_LED_004 makes the app count purchases; spec v3 §3 says the server decides and the app does not count | `docs/features/Purchases.feature:27-32` | spec wins on behaviour |
| D2 | TS_LED_005 (CSV export) is backed only by the superseded legacy page | `docs/features/Purchases.feature:36-40`, `docs/specs/purchases-legacy.md:3` | newer spec wins |
| D3 | TS_LED_006 (140-character note) has no spec or design basis; only code (`NoteRule`, added by the plan scaffolds) | `docs/features/Purchases.feature:42-46` | team decision, for the owner to confirm |
| D4 | No scenario for spec v3 §4 (rejected offline purchase) | `docs/specs/purchases-v3.md:8-9` | a new scenario is proposed |
| D5 | Limit conflict: ticket says 5 a day in the user's time zone, design counter says "3 of 10", spec says the server decides | `docs/tickets/LED-7.md:10`, `docs/design/figma-LED-7.md:3`, `docs/specs/purchases-v3.md:5-7` | spec wins on behaviour (profile source ranking; ticket is not a basis) |
| D6 | Reset time: design says "Resets at midnight" (`figma-LED-7.md`) or "Resets at 00:00" (`frames.md`); backend sends UTC; ticket says the user's time zone | `docs/design/figma-LED-7.md:4`, `docs/design/frames.md:4`, `docs/tickets/LED-7.md:11,16` | the profile's `design_source` (figma-LED-7.md) is the pinned design; the time zone is a question |
| D7 | Ticket criterion 1 states the balance formula confusingly ("subtracted from the starting amount, plus refunds") | `docs/tickets/LED-7.md:9` | spec v3 §1 |
| D8 | Feature header cites `gate/specs/purchases-v3.md`, a path that no longer exists | `docs/features/Purchases.feature:1` | not graded |
| D9 | QA comment: a purchase recorded at 23:59 that syncs after midnight | `docs/tickets/LED-7.md:17` | question or decided rule (plan-led7) |

## In case fixtures (not in the sample)

### Review-only diff (`workflow-review-only`, written by `apply_review_diff` in `fixtures/scaffold-lib.sh`)

| # | Defect | Where |
| --- | --- | --- |
| R1 | Any status of 400 or more is taken as the daily limit; 409 and `code == "DAILY_LIMIT"` are never checked | `Sources/Ledger/DailyLimit.swift:16` |
| R2 | `resets_at` (ISO-8601 UTC) parsed with a `DateFormatter` with no time zone, no `Z` and no POSIX locale | `Sources/Ledger/DailyLimit.swift:9-12`, `:18` |
| R3 | `try!`, `as!` and `!` on server data | `Sources/Ledger/DailyLimit.swift:17-18` |
| R4 | The auth token is printed to the log | `Sources/Ledger/SyncClient.swift:16` (after the diff) |
| R5 | No test covers the new code | — |

### Other planted conditions

| Case | Condition | Expected |
| --- | --- | --- |
| verify-ledger | The locked register `docs/features/Purchases.requirements.md` is edited after the lock snapshot | lock check fails; the breach is named; no move to review |
| handoff-ledger | The only unit-test evidence record was made before the last test was added (stale state) | not presented as proof on the final change |
| handoff-ledger | Review finding 2 (Low, `sleep(1)` in the new test at `TransactionStoreTests.swift:18`) is open | put to the developer |
| retro-ledger | `fixtures/runlog.jsonl`: the sleep-in-tests finding in runs LED-8, LED-9, LED-12 (and a send-back in LED-9); one flaky test; one missing lint key | one proposal, for the repeated signal only; no baseline (no group has five runs) |
