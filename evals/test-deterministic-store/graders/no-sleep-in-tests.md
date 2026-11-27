---
type: regex
pattern: 'sleep\(|Task\.sleep|asyncAfter|XCTWaiter'
match: not_contains
target:
  source: file
  path: Tests/LedgerTests/TransactionStoreTests.swift
---
