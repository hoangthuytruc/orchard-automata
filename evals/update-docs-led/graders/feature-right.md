---
type: llm
weight: 4
focus:
  source: file
  path: docs/features/Purchases.feature
---
You are shown a feature file after an accepted plan was written into it. Before, it held TS_LED_001 to TS_LED_006;
TS_LED_002 carried @automation-pending. The accepted plan: TS_LED_002 gains its test
(TransactionStoreTests.testRefundReducesBalance); a new scenario, the limit banner shows with the reset time when
the server refuses a purchase (409 DAILY_LIMIT), was delivered; a new scenario about a rejected offline purchase
was NOT delivered; TS_LED_004 is removed. Ids are never reused, so the new scenario takes TS_LED_007.
PASS only if ALL hold:
1. TS_LED_002 no longer carries @automation-pending and is bound to testRefundReducesBalance (for example with
   @covered-by:TransactionStoreTests.testRefundReducesBalance).
2. A new scenario for the limit banner on the server's refusal, with the reset time, exists with id TS_LED_007
   and a binding to DailyLimitTests.testBannerShowsResetTimeOnDailyLimit, and carries no @automation-pending,
   @manual, @gap or @pending tag.
3. No scenario about a rejected offline purchase was added.
4. TS_LED_004 (the sixth purchase refused without asking the server) is gone.
5. TS_LED_001, TS_LED_003, TS_LED_005 and TS_LED_006 are still there.
FAIL otherwise.
