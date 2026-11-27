---
name: handoff
description: Write the test report a developer accepts or sends back from - one screen on top in plain words (verdict, what was built, what was not, how it was checked, what is needed from the developer), and below it one piece of evidence per scenario and design frame, findings with their final state, checks run on the final change, what did not run, and a draft pull-request body that carries the top part, the verdict and the pictures. Quotes the verdict a script computes; decides nothing. Use for "write the test report", "hand this over", "is it proven", "draft the PR body", or when the run reaches Ready.
argument-hint: "<plan file>"
---

# handoff

Arranges the evidence so a person can decide in minutes. It adds no evidence of its own: every claim links to a record `verify` made on the final change. `$ORCHARD` is the folder two levels above this file.

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| The plan; `evidence.jsonl`; the review files; `screens/`; `diagnosis.md` for a bug fix ([task files](../../roles/coordinator.md#task-files)) | `<reports_dir>/<YYYY-MM-DD>-<name>-test-report.md` from `$ORCHARD/templates/test-report.md`, with a draft pull-request body | Decides; writes a verdict of its own; commits; opens a pull request; hides a gap; pairs a near match as proof; paraphrases a result it can quote; mentions an AI or a tool | Accept, or send back in their own words | `verdict.py` output, quoted as the verdict; `evidence.py table` and `stale` output, quoted in the report |

## Why

A report the developer must reconstruct gets rubber-stamped or redone. It rests on a traceability matrix and acceptance testing.

## Stance

Editor. What does the developer need on one screen to decide? Tier: light, recommended; a separate agent at the Strict level ([roles/report-writer.md](../../roles/report-writer.md)).

## General steps

1. Name the decision and who makes it. 2. State the verdict first, in that person's words. 3. Say what was done, what was not, and how it was checked. 4. Link every claim to its evidence. 5. State what is needed from them.

## Method

1. **Open.** Alone: as in [AGENTS.md](../../AGENTS.md#a-skill-called-alone), with `--skill handoff`. In a run, the coordinator plays this role, or starts the report writer at Strict.
2. **Is the evidence current?** `python3 -I "$ORCHARD/scripts/evidence.py" stale <evidence.jsonl>`. Every listed record is reported as "ran on an earlier version", not as a pass. The final change is `evidence.py state --root .`.
3. **The verdict.** `python3 -I "$ORCHARD/scripts/verdict.py" <evidence.jsonl> <plan file> --reviews <the review files' folder, or the review file> --root .`, with `--ended-early "<both sides, quoted>"` when the run ended early. It prints `Ready to accept`, `Not ready` or `Blocked`, the reasons, and the gaps that do not change it (missing pictures). Its first line is the report's verdict and its reasons are quoted under it; the verdict is never written, softened or raised by hand. When the script cannot run, the verdict is `Not ready` with that reason.
4. **Detail first**, from the template, in this order:
   - **Scenarios.** One row per scenario of the plan: delivered or not, kind, test, result on the final change, and the evidence record. A bound test is opened and read: a name or body that does not match the scenario is not proof.
   - **Ticket criteria.** A ticket's acceptance criterion reaches the report only through a scenario: the plan maps each criterion to a scenario (and so to that scenario's evidence) or states its reason for none, which the report quotes under "Not delivered" or "Not run". There is no separate criteria table.
   - **Design frames.** One row per frame in scope: the design render beside the app screenshot in the same state. When no app state matches, say so. The match is for a person to judge.
   - **Findings.** Every finding from the review files with its final state: fixed in round n, open, or for the developer.
   - **Checks run.** `python3 -I "$ORCHARD/scripts/evidence.py" table <evidence.jsonl>`, pasted as printed.
   - **Not run.** Every kind with no record, why, and what would run it.
   - **Real-backend checks.** Hypothesis, environment, request shape, status, reply shape, cleaned up, and for each gap its class, owner and severity by [references/gap-classification.md](../../references/gap-classification.md).
   - **Manual checks for a person.** What no automated check reaches, and every design comparison.
   - **Not delivered.** Each scenario not built, why, and confirmation that its code and tests were removed.
   - **Bug fix.** The regression test failing before the fix (from `diagnosis.md`) and passing after it.
5. **Top part last**, one screen, plain words, no paths, type names, test names or commands:
   - **Verdict**: the first line of `verdict.py`, with its reasons in plain words. Its gaps (a scenario with no picture) are named with the reason under "What was built".
   - What was built, in the person's words; what was not; how it was checked, with numbers, not adjectives; what was not checked.
   - What I need from you: each NOTE, Low finding, NIT and open question, with a recommendation.
6. **Draft pull-request body**, filled from the project's PR template when the profile's `pr_template` names one, else a short summary. It carries the report's top part (verdict with its reasons, what was built and not, how it was checked, what is needed from the reviewer) and links or embeds the visual evidence: each screenshot and recording, named by scenario. The plan, the report and the evidence files stay out of git: the body carries what a reviewer needs from them. No mention of an AI or a tool.
7. **Close.** Alone: `runlog.py finish RUN_ID --outcome delivered`. Give the report path and the verdict. Screenshots and the report go to the developer as soon as they exist, without being asked.

## Rule that always holds

Every claim links to evidence from the final change; the decision stays with the developer.

## Gotchas

- **Every claim links real evidence** ([what counts](../../docs/principles.md#what-counts-as-evidence)): its test record, and where they exist its screenshot or recording, network log and code reference. Scenario text and test names alone are not evidence. A scenario with no evidence at all is not delivered. A missing picture is listed as a gap with its reason; it does not change the verdict by itself, and the developer decides whether the other evidence is enough.
- **Each finding is listed with its final state only.** Time and tokens go to the run log, not the report.
- **Never quote tokens, credentials or personal data** from a real-backend check; quote shapes and status codes.
