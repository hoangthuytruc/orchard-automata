---
type: regex
pattern: 'first!|try!|\]!'
match: not_contains
target:
  source: file
  path: Sources/Ledger/TransactionStore.swift
---
