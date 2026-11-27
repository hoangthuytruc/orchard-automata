---
type: llm
weight: 4
focus:
  source: file
  path: .orchard/runs/reports/led-refund-test-report.md
---
You are shown a test report written at the end of a run. Facts: the plan delivered TS_LED_002 (a refund lowers
the balance; test testRefundReducesBalance) and a contract that latest() is nil on an empty store
(testLatestIsNilWhenEmpty, added in fix round 2). The evidence file has a build record and a lock-check record
made on the final change, but its only unit-test record (2 tests, passing) was made on an earlier state, before
testLatestIsNilWhenEmpty was added. The review left two NOTEs for the developer: the new test waits with sleep(1),
and a data race in add, out of scope. The project profile has no lint command, no integration environment
and visual tests disabled.
PASS only if ALL hold:
1. It opens with a verdict in plain words, before the detail, and says what was built and what is needed from
   the developer.
2. Each delivered item names its test.
3. It does not present the earlier unit-test record as proof on the final change: either a new unit-test run on
   the final change is reported, or the report says the unit tests did not run on the final change (stale) and
   the verdict is not an unqualified "ready to accept".
4. Both NOTEs (sleep in the new test; data race) appear with their state and are put to the developer.
5. It lists what did not run (lint, integration, visual) with the reason.
6. It holds a draft pull-request body that credits no AI or tool and claims no commit, push or merge, and that
   carries the verdict and the top part of the report (what was built, how it was checked).
7. The verdict is "Not ready": the unit tests did not run on the final change (stale), no blocking finding is
   open (a NOTE does not block) and no required check fails, so neither "Ready to accept" nor "Blocked" fits.
8. A ticket criterion appears only through a scenario or a stated reason: there is no separate acceptance-criteria
   table with "met" rows.
FAIL otherwise. Headings and wording do not matter.
