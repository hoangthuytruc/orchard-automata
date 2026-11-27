---
name: plan-draft-ledger
description: The plan skill's drafting mode should turn the current spec and design notes into proposed scenarios for a feature that has none - first listing what the sources require, then one scenario per behaviour with a basis and evidence, leaving out legacy-only behaviour and server-decided numbers, putting an unsourced app rule to the owner, and writing no feature file.
tags: [plan]
runs: 2
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: A draft at .orchard/runs/plans/purchases-draft.md with a requirement list from the spec, proposed scenarios for the balance, refunds, the server-driven limit banner with its reset time, offline sending and the rejected offline purchase, Contact support from design frame 210:31, no CSV export scenario, the 140-character note limit as a team decision to confirm, and no feature file or code change.
---
The Purchases feature of the Ledger package in the current directory has no behaviour scenarios yet. Use the
plan skill to write them from scratch as our product quality gate. The project profile at .orchard/profile.md names the sources and how they rank; there is no tracker, wiki or design-tool access here. Write the draft exactly at
.orchard/runs/plans/purchases-draft.md. Do not create a feature file and do not change any code; I will approve
the draft first.
