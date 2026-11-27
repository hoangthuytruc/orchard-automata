---
name: handoff-ledger
description: The handoff skill should arrange the evidence of a finished run into a test report with one plain screen on top, notice that the unit-test record predates the last change, carry the open finding to the developer, list what did not run and draft a pull-request body, without deciding acceptance.
tags: [handoff]
runs: 2
max_turns: 40
timeout_seconds: 900
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: A test report at .orchard/runs/reports/led-refund-test-report.md that opens with a verdict, names a test per delivered item, does not present the stale unit-test record as proof on the final change, lists both NOTEs for the developer, lists lint, integration and visual as not run, and holds a draft pull-request body with no AI or tool credit; plan status still executed; no code changed; no commit.
---
Use the handoff skill. The run of the plan .orchard/runs/plans/led-refund.md for the Ledger package in the current directory has finished:
the change is uncommitted, the evidence is .orchard/runs/reports/led-refund-evidence.jsonl and the review is
.orchard/runs/reports/led-refund-review.md. Write the test report exactly at .orchard/runs/reports/led-refund-test-report.md, with a draft pull-request body.
I will decide on acceptance after reading it.
