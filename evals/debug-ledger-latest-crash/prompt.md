---
name: debug-ledger-latest-crash
description: The debug skill should reproduce the crash, find its cause with an experiment, leave one regression test that fails because of it, write the diagnosis and hand over to implement without fixing the code.
tags: [debug]
runs: 2
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: A diagnosis at .orchard/runs/reports/latest-crash-diagnosis.md with the reproduction, the cause at TransactionStore.swift:22 (force unwrap of first on an empty list), the experiment that confirmed it and a hand-over; one new test on latest() with an empty store that fails today; the production code unchanged; swift test run; no commit.
---
Use the debug skill. Our app crashes on a fresh install when the home screen asks the Ledger package in the
current directory for the latest transaction. The crash log ends with `Fatal error: Unexpectedly found nil while
unwrapping an Optional value` in `TransactionStore.latest()`. Find the cause and leave a regression test for it.
Write the diagnosis exactly at .orchard/runs/reports/latest-crash-diagnosis.md.
