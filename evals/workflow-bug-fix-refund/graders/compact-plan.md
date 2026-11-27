---
type: llm
weight: 3
focus:
  source: file
  path: .orchard/runs/plans/refund-sign.md
---
You are shown the plan of a bug fix: a refund made the balance go up. The knowledge base holds an approved
scenario, TS_LED_002 "A refund is returned to the balance", so the expected behaviour is already stated.
PASS only if ALL hold:
1. It is a compact plan that names TS_LED_002 as the scenario that states the expected behaviour.
2. It gives the reproduction and the cause in `balanceCents()` (Sources/Ledger/TransactionStore.swift, the sum
   ignores `kind`).
3. It names the files the fix owns, and the proof is the failing regression test made to pass.
4. Its status is approved or executed (the developer approved a compact plan in advance), not accepted or
   documented.
FAIL otherwise.
