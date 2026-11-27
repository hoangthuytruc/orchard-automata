---
name: retro-ledger
description: The retro skill should read a run log, group the signal that repeats across runs, propose the smallest change for it with the runs behind it, set single events aside, report the figures per workflow and isolation with no baseline under five runs, and change no skill, rule, check or profile.
tags: [retro]
runs: 2
max_turns: 40
timeout_seconds: 900
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
expected_outcome: Proposals at .orchard/runs/retro.md - one proposal for the sleep-in-tests finding seen in three runs (and a send-back), naming the runs, the cause, the smallest change and where it lives; the flaky test and the missing lint key set aside as single events; figures grouped by workflow and isolation with no baseline yet; no skill, reference, script, profile or review-rule file changed; no commit.
---
Use the retro skill on the run log of the Ledger project, which is at .orchard/runs/runlog.jsonl in the current
directory. Write the proposals exactly at .orchard/runs/retro.md.
