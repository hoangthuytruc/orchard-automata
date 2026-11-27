---
name: plan-led7
description: The plan skill should turn ticket LED-7 into one plan file - requirements with quotes, design change from the code, the impact checklist, scenario changes with a basis each, conflicts settled by the source ranking or asked, open questions with a recommendation, work packages with owned files and a tier, locked files - without touching code, tests or the scenario file, and stop before approval.
tags: [plan]
runs: 2
max_turns: 60
timeout_seconds: 1500
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: A draft plan at .orchard/runs/plans/led-7.md - the limit banner driven by the server 409 DAILY_LIMIT reply with the reset time and no app-side counting; the 5-versus-10 conflict settled by the spec or asked; scenario changes each with a basis label and evidence; TS_LED_004 removed or changed; the 140-character note limit a team decision to confirm; twelve impact perspectives answered; the 409 contract written; work packages with files and a tier; scenario files locked; no code, test or scenario file changed.
---
Use the plan skill to plan ticket LED-7 for the Ledger package in the current directory. The ticket is
docs/tickets/LED-7.md. The project profile at .orchard/profile.md names the sources and how they rank; there is no tracker, wiki or design-tool access here. Write the plan exactly at .orchard/runs/plans/led-7.md. I cannot answer questions now:
record the open questions with your recommendation, split the work, and stop before approval. Do not change any
code, test or scenario file.
