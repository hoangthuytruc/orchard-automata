---
name: run-led-refund
description: The run skill should drive the feature-development workflow from an approved one-package plan to the test report without asking - an implementer agent writes the tests first, the evidence and lock check are recorded by script, a separate reviewer judges the change, the report is written and the plan marked executed, with no commit and no scenario-file edit.
tags: [run, workflow]
runs: 2
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: balanceCents subtracts refunds and latest() returns an optional; tests for both; evidence.py and lock_check.py run; an implementer agent and the orchard-reviewer agent started; the run log written by runlog.py; docs/features unchanged; a test report at .orchard/runs/reports/led-refund-test-report.md; the plan status executed with its Result filled; no commit.
---
Use the run skill to carry out the approved plan .orchard/runs/plans/led-refund.md for the Ledger package in the current directory with the
feature-development workflow. Write the test report exactly at .orchard/runs/reports/led-refund-test-report.md. I will read the report and accept later.
