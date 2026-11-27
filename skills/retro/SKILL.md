---
name: retro
description: Improve the skill set from its own run log - group signals that repeat across runs (ended early, review findings, first-try failures, flaky tests, send-backs, step-ups), name the cause of each group, propose the smallest change that removes it and where it lives (core, project profile or review rules, personal), prove a core change on the sample, and let the owner accept or reject each. Edits nothing before acceptance; never loosens a rule. Use for "retro", "what keeps going wrong", "improve the skills from the runs", "is verification getting cheaper", "run log report".
argument-hint: "[--since 30d] [--workflow <name>]"
---

# retro

Turns repeated signals into proposals. It reads what scripts recorded at the time, never what an agent remembers, and it never rewrites a rule itself. `$ORCHARD` is the folder two levels above this file.

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| `runlog.py report`; the run log (`$ORCHARD_RUNLOG`, else `~/.orchard/runlog.jsonl`); the task files the records point to | One proposal file at `<reports_dir>/retro-<date>.md`; after acceptance only, the accepted change | Edits a skill, rule, check or profile before acceptance; proposes from one occurrence; proposes to lower a threshold, remove a check or widen what an agent may decide; runs during a run | Accept or reject each proposal | The run ids behind each proposal; the report figures; for a core change, an eval case that fails before and passes after |

## Why

A mistake corrected by hand on every run means verification never gets cheaper. It rests on retrospectives, blameless reviews and regression evaluation.

## Stance

Pattern-finder. Has this happened twice, and what is the smallest rule that removes it? Tier: strong, recommended.

## General steps

1. Collect records of what happened, written at the time. 2. Group what repeats, and set single events aside. 3. Name the cause of each group. 4. Propose the smallest change that removes it. 5. Prove the change on a known case. 6. Let the owner decide.

## Method

1. **Open** as in [AGENTS.md](../../AGENTS.md#a-skill-called-alone), with `--skill retro --task "retro <since>"`.
2. **Figures.** `python3 -I "$ORCHARD/scripts/runlog.py" report --since <30d> --group workflow,isolation`. Quote, per group: the share of runs that ended early, review findings per run, the share sent back at acceptance, minutes to verify a run; tokens and time per accepted task; seeded defects the reviewer missed on the sample. A group under five runs says "no baseline yet": give no trend for it. Findings per run is never read alone: fewer findings can mean better code or a weaker reviewer.
3. **Collect.** Read the records for events of type `ended_early`, `loop_failed` (with its cause: this is the first split, since a plan gap, an executor failure and a test defect call for different changes), `finding`, `first_try_fail`, `flaky`, `send_back`, `step_up`, `question`, `wait`, with their notes and the task files they point to.
4. **Group** by what repeats: the same rule cited, the same check failing first try, the same conflict ending runs, the same correction at acceptance. A group needs at least two runs; a single event is a note, set aside and listed as such.
5. **Name the cause** of each group: a missing rule, an unclear rule, a missing check, a wrong profile value, a weak eval.
6. **Propose**, one per cause: the runs that show it, the smallest change that removes it, and where it lives by [docs/scopes.md](../../docs/scopes.md): core (a skill, a reference, a check script, an eval), the project's profile or review rules, or personal settings; a lesson true for one task changes nothing. Prefer a script before more prose: a prose rule broken twice becomes a check when a script can see it. Also propose for removal a rule no run has cited or tripped in a long while.
7. **Prove a core change** before asking. In a temporary copy of the skill set, never the real one: write an eval case on the sample that shows the problem (`$ORCHARD/evals/README.md` gives the format); run it without the change and see it fail; apply the change and see it pass, with the eval runner the tool's adapter names. Where no runner is available, the proposal says "unproved" and why. A project or personal change is shown by the runs that corrected the value by hand.
8. **Write the proposal file** and give the developer the list: cause, runs, change, where, proof. Log `runlog.py event RUN_ID question --note "<n> proposals"`.
9. **Accept.** Only on the developer's word for that proposal, apply it, re-run its eval case, and run `python3 -I "$ORCHARD/scripts/leak_check.py"` for a core change. Rejected proposals stay in the file with the reason.
10. **Close.** `runlog.py finish RUN_ID --outcome delivered --findings <proposals>`.

## Rule that always holds

Twice, not once; never loosen. A threshold, a check, or what an agent may decide changes only on a person's own proposal.

## Gotchas

- **The run log is personal.** It holds tokens and time per developer; quote figures and run ids in a proposal, never paste records into core.
- **A proposal is not a rule.** Not during a run, and not before acceptance, does any agent edit skills, rules, checks or the profile.
