# Plan: led-refund
Status: @STATUS@
Workflow: feature-development · Isolation: Standard · Base branch: main

## In short
The balance will take refunds off instead of adding them, and asking for the latest purchase on an empty ledger
will no longer crash the app.

## What changes for the person using the app
- A refund lowers the balance by its amount.
- Opening the ledger with no purchases shows nothing instead of crashing.

## How it will be built
- The balance counts a refund as a negative amount; stored data keeps its shape.
- The latest purchase becomes optional: none when the ledger is empty.
- Rejected: storing refunds as negative amounts (changes the data shape for one rule).
- Risk: low; one type changes, no stored data changes.

## Scenarios
0 added, 1 changed, 0 removed. In plain words:
- Changed: A refund is returned to the balance: it gains its automated test.
Kept by team decision, for you to confirm: none.

## What I need from you
Nothing; the plan is ready to approve.

## How the work is split
1 package, on the light tier; shared tree. Up to three rounds, with a full review after the first. The scenario
files stay locked until acceptance.

## Not covered
- The daily limit (LED-7), offline sending and the data race in adding a transaction: later plans.

---

# Working detail (for the agents)
Sources: docs/specs/purchases-v3.md (v3) · docs/features/Purchases.feature · code at the fixture commit

## 1. Scope
| This change owns | Out of scope → who owns it |
| --- | --- |
| `TransactionStore.balanceCents()`, `TransactionStore.latest()` | daily limit (LED-7), offline sending, the data race in `add` → later plans |

## 2. Requirements
| # | Requirement | Source and version | Quote | Scenario, or reason for none |
| --- | --- | --- | --- | --- |
| R1 | The balance is purchases minus refunds | spec v3 §1 | "The balance is the sum of all purchases minus all refunds." | TS_LED_001, TS_LED_002 |
| R2 | A refund is added back at once | spec v3 §2 | "A refund is added back to the balance at once." | TS_LED_002 |

## 3. Design change
| Area | Today (path:line) | After | Why |
| --- | --- | --- | --- |
| balance | `Sources/Ledger/TransactionStore.swift:18` sums `amountCents` | signs each amount by `kind` (refund is negative) | spec v3 §1, §2 |
| latest | `Sources/Ledger/TransactionStore.swift:22` force-unwraps `.first!` | returns `Transaction?`, nil when empty | no crash on an empty store |

## 4. Impact
| Perspective | Impact | Owner |
| --- | --- | --- |
| UI and UX | none, because the balance screen shows whatever the store returns | — |
| Business rules | the balance rule changes to spec v3 §1 | app |
| Data and API | none, because no request or reply changes | — |
| Backend | none, because the server is not involved | — |
| Persistence and migration | none, because stored data keeps its shape | — |
| Other features | callers of `latest()` must handle nil | app |
| Platform and permissions | none, because no capability is used | — |
| Analytics | none, because no event changes | — |
| Copy and localization | none, because no text changes | — |
| Accessibility | none, because no screen changes | — |
| Security and privacy | none, because no data leaves the device | — |
| Release | none, because it ships with the next build | — |

## 5. Scenario changes
| Change | Scenario | Steps | Basis | Evidence | Kind | Oracle | Test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| change | TS_LED_002 — A refund is returned to the balance | steps unchanged; gains its test | Spec | v3 §2: "A refund is added back to the balance at once." | unit | | TransactionStoreTests.testRefundReducesBalance |

| Contract (no scenario) | Kind | Test |
| --- | --- | --- |
| latest() on an empty store is nil | unit | TransactionStoreTests.testLatestIsNilWhenEmpty |

### Pending or blocked scenarios the change touches
| Scenario | Tag today | Test that will resolve it, or reason it stays |
| --- | --- | --- |
| TS_LED_002 | @automation-pending | TransactionStoreTests.testRefundReducesBalance |

## 6. Open questions
none

## 7. Work packages
| # | Package | Files it owns | Tier and reason | Depends on | Done when |
| --- | --- | --- | --- | --- | --- |
| 1 | store fix | `Sources/Ledger/TransactionStore.swift`, `Tests/LedgerTests/TransactionStoreTests.swift` | light: cause and design are known | none | both tests pass with the profile's `test.unit` |
Tree: shared, because there is one small package.

## 8. Rounds and locks
Rounds: at most three. Full review on strong after round 1; review of fixes after each fix round.
Locked: `docs/features/*.feature`, `docs/features/*.requirements.md`.
Real-backend checks: none.

## Result (written by run)
| Scenario | Delivered | Test | Note |
| --- | --- | --- | --- |
@RESULT@

## Change note (written by update-docs)
