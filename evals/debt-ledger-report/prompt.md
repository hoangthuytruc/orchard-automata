---
name: debt-ledger-report
description: The debt skill should write a ranked, evidence-backed report with impact, likelihood and effort per item and a first step each, without changing any source file.
tags: [debt]
runs: 2
max_turns: 40
timeout_seconds: 900
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: A report at docs/tech-debt/ledger.md with a ranked list (impact, likelihood, effort, evidence as path:line, first step) covering the singleton plus DispatchQueue concurrency debt, crash-risk force unwraps, the token in UserDefaults, the completion-handler sync API, the sleep-based and missing tests; no edits to Sources, Tests or scenario files; no commit.
---
Use the debt skill to produce a technical debt report for the Ledger package in the current directory. Save it
exactly at docs/tech-debt/ledger.md.
