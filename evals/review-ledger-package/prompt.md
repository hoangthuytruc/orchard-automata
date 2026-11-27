---
name: review-ledger-package
description: The review skill should start the read-only reviewer and return ranked findings that include the data race, the empty-store crash, the refund sign bug and the token in UserDefaults, each with file:line, a type and severity, and a fix, citing the project review rule for the token.
tags: [review]
runs: 2
max_turns: 40
timeout_seconds: 900
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: A ranked review from a separate reviewer agent whose findings cover the unsynchronized shared state across a DispatchQueue, latest() crashing on empty, refunds added instead of subtracted, the auth token stored in UserDefaults (rule LR-1) with force-unwrapped decode, with file:line, a type and severity and a concrete fix per finding, plus the missing tests; no file edited.
---
Use the review skill to review the Ledger package in the current directory as if it were a pull request adding
it to our iOS app. Give ranked findings.
