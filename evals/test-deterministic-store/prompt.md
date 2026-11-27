---
name: test-deterministic-store
description: The test skill should remove the sleep-based test, inject time, make add observable without sleeping, and cover empty, refund and month-boundary cases deterministically.
tags: [test]
runs: 2
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: TransactionStoreTests has no sleep; the store takes an injected now or clock; tests cover the empty balance, a refund, and a month boundary with fixed dates and an explicit calendar and time zone; swift test run; no commit.
---
Use the test skill. `TransactionStoreTests` in the Ledger package in the current directory is slow and
nondeterministic. Make the store testable without sleeps and add deterministic tests for: the empty store's
balance, a store with a refund, and `monthTotalCents` at a month boundary (a transaction at 23:59 on the last day
of a month must not count for the next month). Keep the tests in Tests/LedgerTests/TransactionStoreTests.swift.
