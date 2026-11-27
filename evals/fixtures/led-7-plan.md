# Plan: led-7
Status: @STATUS@
Workflow: feature-development · Isolation: Standard · Base branch: main

## In short
Refunds now lower the balance, and when the server refuses a purchase because the daily limit is reached, the app
shows the limit banner with the reset time. The app does not count purchases itself.

## Scenarios
1 changed, 2 added, 1 removed. In plain words:
- Changed: A refund is returned to the balance: it gains its automated test.
- Added: The limit banner shows when the server refuses a purchase (required by spec v3 and the design's banner).
- Added: A rejected offline purchase stays marked "Rejected" (required by spec v3).
- Removed: The sixth purchase of the day is refused: the app must not count purchases itself.
Kept by team decision, for you to confirm: none.

---

# Working detail (for the agents)
Sources: docs/specs/purchases-v3.md (v3) · docs/design/figma-LED-7.md (frames 210:14, 210:31, 210:44) · docs/features/Purchases.feature

## 5. Scenario changes
| Change | Scenario | Steps | Basis | Evidence | Kind | Oracle | Test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| change | TS_LED_002 — A refund is returned to the balance | steps unchanged; gains its test | Spec | v3 §2: "A refund is added back to the balance at once." | unit | | TransactionStoreTests.testRefundReducesBalance |
| add | N1 — The limit banner shows when the server refuses a purchase | Given the server answers a new purchase with 409 DAILY_LIMIT and a reset time · When the person records a purchase · Then the limit banner shows with the reset time | Spec + Design | v3 §3: "The app then shows the limit banner and the reset time."; design frame 210:31 | unit | | DailyLimitTests.testBannerShowsResetTimeOnDailyLimit |
| add | N2 — A rejected offline purchase stays marked "Rejected" | Given a purchase recorded offline · When the server rejects it · Then it stays in the list marked "Rejected" and is not counted | Spec | v3 §4: "it stays in the list marked \"Rejected\" and is not counted in the balance" | unit | | OfflineQueueTests.testRejectedPurchaseIsMarked |
| remove | TS_LED_004 — The sixth purchase of the day is refused | | | contradicts v3 §3: "The app does not count purchases itself." | | | |

## 8. Rounds and locks
Locked: `docs/features/*.feature`, `docs/features/*.requirements.md`.

## Result (written by run)
| Scenario | Delivered | Test | Note |
| --- | --- | --- | --- |
@RESULT@
Not delivered, and why: N2, the offline queue is a later ticket; its code and tests were removed.

## Change note (written by update-docs)
