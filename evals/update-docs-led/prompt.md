---
name: update-docs-led
description: The update-docs skill should write only the delivered, accepted scenario changes into the feature file and its register - a new id for the added scenario, a binding instead of a pending tag, the contradicted scenario removed, the undelivered one left out - run the knowledge-base check and change no code or test.
tags: [update-docs]
runs: 2
max_turns: 60
timeout_seconds: 1500
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: docs/features/Purchases.feature has TS_LED_002 bound to its test with no pending tag, a new scenario TS_LED_007 for the limit banner on the server refusal, no TS_LED_004, no rejected-offline scenario; docs/features/Purchases.requirements.md has rows with basis, evidence and test for TS_LED_002 and TS_LED_007; gate_check.py run; the plan status is documented; no source or test file changed; no commit.
---
Use the update-docs skill. I accepted the work of the plan at .orchard/runs/plans/led-7.md (test report:
.orchard/runs/reports/led-7-test-report.md) for the Ledger package in the current directory. Update the knowledge
base from it.
