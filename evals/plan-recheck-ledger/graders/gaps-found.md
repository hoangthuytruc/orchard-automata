---
type: llm
weight: 2
focus:
  source: file
  path: .orchard/runs/plans/purchases-recheck.md
---
You are shown a re-check of scenarios for a small Swift package. In the code, `TransactionStore.balanceCents()`
sums every amount and ignores whether a transaction is a refund. Spec v3 clause 4 says a purchase recorded
offline and rejected by the server stays in the list marked "Rejected" and is not counted; no scenario covers it.
PASS only if BOTH hold:
1. It says the app must change for the refund scenario (TS_LED_002), pointing at the balance code
   (TransactionStore or balanceCents).
2. It proposes at least one new scenario for the offline or rejected purchase of spec clause 4.
FAIL otherwise.
