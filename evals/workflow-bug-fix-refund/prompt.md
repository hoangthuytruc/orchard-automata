---
name: workflow-bug-fix-refund
description: The bug-fix workflow should reproduce the refund sign defect with a failing test, see that approved scenario TS_LED_002 already states the expected behaviour and so write a compact plan, then fix, verify, review by a separate agent and report the test failing before and passing after, without asking mid-run and without committing.
tags: [workflow, run, debug]
runs: 2
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: A compact plan at .orchard/runs/plans/refund-sign.md naming TS_LED_002, the reproduction, the cause in balanceCents and the files the fix owns; balanceCents subtracts refunds; a regression test; the orchard-reviewer agent started; a test report at .orchard/runs/reports/refund-sign-test-report.md showing the test failing before and passing after; docs/features unchanged; no commit.
---
Users report that a refund makes the balance of the Ledger package in the current directory go up instead of
down. Fix it with the bug-fix workflow, starting with the debug skill. I approve in advance a compact plan: if the
fix fits one, go on to the test report without waiting for me; if it needs a full plan, stop and show it to me.
Write the plan exactly at .orchard/runs/plans/refund-sign.md and the test report exactly at .orchard/runs/reports/refund-sign-test-report.md.
