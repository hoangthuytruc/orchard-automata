---
type: llm
weight: 2
focus:
  source: file
  path: Tests/LedgerTests/TransactionStoreTests.swift
---
You are shown the test file after the change. PASS only if ALL hold:
1. A test asserts that a refund reduces the balance with a precise expected value (for example 500 purchase and
   200 refund give 300, or purchase plus equal refund give 0).
2. A test asserts the empty-store behaviour of `latest()` (nil or equivalent) without crashing.
3. No test was deleted or weakened; the previous add-increases-balance behaviour is still covered.
4. No new `sleep` or `Task.sleep` was added (an existing one may remain or be replaced by direct synchronous or
   awaited calls).
FAIL otherwise. XCTest or Swift Testing are both acceptable.
