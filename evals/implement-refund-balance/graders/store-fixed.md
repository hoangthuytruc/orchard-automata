---
type: llm
weight: 2
focus:
  source: file
  path: Sources/Ledger/TransactionStore.swift
---
You are shown the production file after the change. PASS only if ALL hold:
1. The balance computation subtracts refund amounts (for example by signing the amount by `kind`), so a purchase
   of 500 and a refund of 500 give 0.
2. `latest()` no longer force-unwraps: it returns `Transaction?` or an equivalent non-crashing design.
3. No new `!` force unwrap, `try!` or `fatalError` on a data path was introduced.
FAIL otherwise. Other refactors (actor, injected clock) are allowed but not required.
