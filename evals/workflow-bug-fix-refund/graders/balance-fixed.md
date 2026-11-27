---
type: llm
weight: 2
focus:
  source: file
  path: Sources/Ledger/TransactionStore.swift
---
You are shown the production file after a bug fix. PASS only if BOTH hold: (1) the balance computation subtracts
refund amounts (for example by signing the amount by `kind`), so a purchase of 500 and a refund of 500 give 0;
(2) no new `!` force unwrap, `try!` or `fatalError` on a data path was introduced. FAIL otherwise.
