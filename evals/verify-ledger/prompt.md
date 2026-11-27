---
name: verify-ledger
description: The verify skill should run the profile commands on the uncommitted change cheapest first, record each result with the state of the change through the evidence script, run the lock check and report the broken lock on the register, list what did not run, and change nothing.
tags: [verify]
runs: 2
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: Evidence records in .orchard/runs/reports/led-refund-evidence.jsonl made by evidence.py; the lock check run and its failure on docs/features/Purchases.requirements.md reported as a reason to stop; lint, integration and visual checks listed as not run with the reason; no file edited; no commit.
---
Use the verify skill on the Ledger package in the current directory. The plan
.orchard/runs/plans/led-refund.md is approved and its one package has been implemented; the change is
uncommitted. The lock snapshot taken at approval is .orchard/runs/locks.json. Record the evidence exactly at
.orchard/runs/reports/led-refund-evidence.jsonl and tell me what ran, what it showed and what did not run.
