---
name: adopt-ledger
description: The adopt skill should draft the project profile from repository discovery, give each value its source file and hash, mark what no file states as missing instead of guessing, and leave the profile as a draft for the developer to confirm.
tags: [adopt]
runs: 2
max_turns: 40
timeout_seconds: 900
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: A draft profile at .orchard/profile.md - build and test.unit from README.md, build_system SwiftPM from Package.swift, knowledge_base docs/features with a file source, file sources stamped with a hash by profile_check.py, keys no file states marked missing or put to the developer, status draft; no source, test or scenario file changed; no commit.
---
Use the adopt skill to set up the skill set for the Ledger package in the current directory. Write the draft
project profile exactly at .orchard/profile.md and list what you need me to confirm. I cannot answer now.
