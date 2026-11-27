---
name: verify-ledger-app
description: The verify skill should run the profile commands on the working tree, including the UI test of the iOS app on a simulator of its own, capture a screenshot of the balance screen and record it in the evidence file, report the result as it is, and change nothing.
tags: [verify]
runs: 2
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: Evidence records in .orchard/runs/reports/ledger-app/evidence.jsonl made by evidence.py, among them the UI test and a screenshot at .orchard/runs/reports/ledger-app/screens/TS_LED_002.png; the failing UI assertion reported with its actual and expected balance; what did not run listed with the reason; no file edited; no commit.
---
Use the verify skill on the Ledger project in the current directory. Verify the working tree as it is, with visual
evidence from the iOS app on a simulator. Record the evidence exactly at .orchard/runs/reports/ledger-app/evidence.jsonl
and save the screenshot of the balance screen for scenario TS_LED_002 exactly at
.orchard/runs/reports/ledger-app/screens/TS_LED_002.png. Tell me what ran, what it showed and what did not run.
