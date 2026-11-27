---
type: llm
weight: 2
focus:
  source: file
  path: Tests/LedgerTests/TransactionStoreTests.swift
---
You are shown the test file after the change. PASS only if ALL hold:
1. A test asserts the empty store's balance is 0 (and, optionally, that the empty latest is nil).
2. A test includes a refund transaction and asserts a precise expected balance or total.
3. A month-boundary test uses fixed `Date` values with an explicit `Calendar` and `TimeZone` (not the current
   date) and asserts that a transaction at the end of one month is not counted in the next.
4. There is no `sleep`, `Task.sleep`, `asyncAfter`, `XCTWaiter`-on-time or raised timeout.
FAIL otherwise. XCTest or Swift Testing are both acceptable.
