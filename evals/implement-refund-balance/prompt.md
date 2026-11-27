---
name: implement-refund-balance
description: The implement skill should fix the refund sign bug and the empty-store crash test-first, run the tests, leave the work uncommitted and report honestly.
tags: [implement]
runs: 2
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: balanceCents subtracts refunds; latest returns an optional with no force unwrap; tests for refunds and the empty store in Tests/LedgerTests/TransactionStoreTests.swift; swift test run; no scenario file touched; no commit; the report lists commands and results.
---
Use the implement skill. In the Ledger package in the current directory there are two bugs: `balanceCents()` adds
refund amounts instead of subtracting them, and `latest()` crashes when the store is empty (it should return
nil). Fix both, with tests. Keep the tests in Tests/LedgerTests/TransactionStoreTests.swift.
