---
name: workflow-review-only
description: The review-only workflow should have a separate read-only reviewer judge an uncommitted change, find the seeded defects in it with file:line, type, severity and a fix, name the missing tests instead of running them, and change nothing.
tags: [workflow, review]
runs: 2
max_turns: 40
timeout_seconds: 900
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: Findings from the orchard-reviewer agent anchored to DailyLimit.swift and SyncClient.swift lines - any status of 400 or more taken as the daily limit, resets_at parsed without a time zone, force unwraps on server data, the token printed to the log, no tests for the new code; no build or test run; no file edited; no commit.
---
Use the review-only workflow on the uncommitted change in the Ledger package in the current directory (it adds
handling for the daily-limit reply). Give me the findings.
