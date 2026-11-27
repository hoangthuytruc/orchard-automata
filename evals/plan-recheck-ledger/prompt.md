---
name: plan-recheck-ledger
description: The plan skill's re-check mode should check each scenario of the feature file against the current spec and the design notes, give each a basis with quoted evidence, remove what only a legacy page supports, treat an unsourced app rule as a team decision to confirm, not treat a server-decided number as an app rule, find the spec clause with no scenario, and change nothing but its plan file.
tags: [plan]
runs: 2
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: A re-check at .orchard/runs/plans/purchases-recheck.md that keeps TS_LED_001 and TS_LED_002 on the spec (002 also needing an app change), TS_LED_003 on design frame 210:31, flags the hard-coded 5 in TS_LED_004 as server-decided, removes TS_LED_005 (legacy page only), lists TS_LED_006 as a team decision to confirm, proposes a scenario for the rejected offline purchase, and edits neither the feature file nor the code.
---
Use the plan skill to re-check the scenarios in docs/features/Purchases.feature for the Ledger package in the
current directory: they are our product quality gate. The project profile at .orchard/profile.md names the sources and how they rank; there is no tracker, wiki or design-tool access here. Write the re-check exactly at
.orchard/runs/plans/purchases-recheck.md. Do not change the feature file or any code; I will approve first.
