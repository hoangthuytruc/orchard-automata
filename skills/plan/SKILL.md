---
name: plan
description: Turn a ticket or a plain task into one plan file before any code is written, for a feature, a bug fix, a refactor or a new project. Reads the code, specs, design, tickets and existing scenarios; writes the scenarios with their basis and evidence, the design change, the impact, the work packages with owned files, tier and locks, and every open question once; stops for the developer's approval. Also re-checks a feature's scenarios after a spec or design change, drafts scenarios for a feature with none, and writes a compact plan for a defect an approved scenario already covers. Use for "plan LED-7", "plan this feature", "how should we build X", "impact of this ticket", "design for X", "re-check the scenarios of <Feature>", "write scenarios for <Feature>", "which scenarios have no spec", or before any change big enough to need a design.
argument-hint: "<ticket | task in words | Feature --recheck | Feature --draft | --compact <diagnosis>> [--spec <page>...] [--design <frame>...] [--no-verify]"
---

# plan

Produces one plan file and stops. The plan is the only decision record and the contract every later agent works from; nothing is built before the developer says "approved". `$ORCHARD` is the folder two levels above this file.

| Mode | When | Writes |
| --- | --- | --- |
| plan (default) | New or changed behaviour | The full plan, sections 1–8 of `$ORCHARD/templates/plan.md` |
| `--recheck` | A feature's scenarios after a spec or design change | A plan with scenario changes only: keep, change, add, remove, each with its basis |
| `--draft` | A feature with no scenarios | A plan with the requirement list and the proposed scenarios only |
| `--compact` | A defect an approved scenario already covers, after `debug` | The compact plan at the end of the template |

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| Specs, design, tickets (through the profile's `spec_source`, `design_source`, `tracker`, or files the developer gives); existing scenarios; code as evidence of today's behaviour only; guides | One plan file at `<plans_dir>/<name>.md` | Writes code, tests or scenario files; writes to a tracker, wiki or design tool; settles a conflict no rule settles; uses code or a lone ticket as a basis (unless `source_ranking` makes a ticket alone a basis) | Answers to the open questions, asked once; the base branch; then "approved" | `gate_check.py --coverage` output; each requirement's quote and source version; the status line |

## Why

Requirements inferred from code turn existing bugs into required behaviour. A wrong idea is cheapest to stop before code exists; validation happens here, so the run needs no person. It rests on specification by example, test basis, traceability, work breakdown and decision records.

## Stance

Sceptic. Which source says this, and what would product refuse to ship without? Tier: strong, recommended. In `bug-fix`, a full plan runs on strong and a compact plan on light.

## General steps

1. Fix the scope and name the sources that count. 2. Write each requirement as one statement with its quote. 3. Restate each as an outcome someone can observe. 4. Check both ways: every outcome has a source, and every statement has an outcome or a reason. 5. Bring out conflicts and assumptions, and settle them with the owner before work starts. 6. Split the work into parts that do not overlap.

## Method

1. **Open** as in [AGENTS.md](../../AGENTS.md#a-skill-called-alone), with `--skill plan --task "<name>: <mode>"`.
2. **Ground.** `bash "$ORCHARD/scripts/discover.sh" .`; read the guides it lists and `source_ranking`, `design_source`, `knowledge_base`, `scenario_id_pattern`, `register` from the profile. Name what the change owns and what it leaves to other features. When the knowledge base holds no feature file for the feature (a project just adopted has an empty folder), the plan drafts its scenarios as in `--draft`, and `update-docs` writes them after acceptance.
3. **Read fresh.** The ticket from the tracker the profile names, or a file the developer gives. Each spec page with its version. Each design frame at the pinned version; when `design_source` is a design tool with an exported token, `python3 -I "$ORCHARD/scripts/sources/figma_frames.py" --file <key> --version <id> frames|text|render …`. The feature files and register. Two or three files of the area and of the pattern the code already uses for state, navigation, injection and networking. Record every version in the Sources line.
4. **Requirements.** Every rule, flow step, state, limit, error and exit the sources state: one row with its quote ([references/scenario-draft.md](../../references/scenario-draft.md)). This list is the coverage proof.
5. **Scenarios.** One per behaviour, in the words a person sees, each with a basis (`Spec`, `Design`, `Spec + Design`, `Team decision`) and evidence. Settle conflicts by [docs/boundaries.md](../../docs/boundaries.md#conflicts); record the rule used. For `--recheck`, walk every existing scenario by [references/scenario-gate.md](../../references/scenario-gate.md). Each scenario names its kind of test and, when not a plain example, its oracle ([references/test-strategy.md](../../references/test-strategy.md)); prefer a property where the scenario states a rule, not a single case.
6. **Design change.** Beside the scenarios: at least two real options, one of them "extend the current pattern"; state owner, dependency direction, isolation of each new type (`actor`, `@MainActor`, `Sendable` value), side-effect boundaries, test seams, migration slices ([references/standards.md](../../references/standards.md)). Reject an option with a reason. A cross-team contract (API shape, error codes, analytics, copy keys) is written here.
7. **Impact.** Walk [references/impact-checklist.md](../../references/impact-checklist.md); every perspective gets an answer, "none, because …" included. For every interface, type, stored or wire format the change alters, list its callers and what each relies on (the checklist's "Callers"). Skipped for `--compact`.
8. **Packages.** Each owns its files alone; order, tier with a one-line reason (rule 7 in [docs/workflow-model.md](../../docs/workflow-model.md#tiers)), done-when; shared tree or a working copy each; locked globs from `locked_globs`; real-backend hypotheses; the endpoints integration tests run on, if any ([references/test-strategy.md](../../references/test-strategy.md), section 1). Raise the isolation level only with a one-line reason. Size it honestly: one small package skips the split.
9. **Check coverage.** `python3 -I "$ORCHARD/scripts/gate_check.py" --coverage <plan> --id-pattern '<scenario_id_pattern>'`, for `--compact` too: it recognises the compact table and checks each row. Fix the plan, never the check.
10. **Write the top part** last: one screen, plain words, no paths or test names. Status `draft`. Before the first write: `git check-ignore -q <plan path>`; when not ignored, add `plans_dir` to the exclude file as `adopt` step 7 does (creating its folder when missing) and say so.
11. **Ask once.** All open questions together, once, each with two or three concrete options and one recommended, plus the base branch. Record each answer with who and when. Log `runlog.py event RUN_ID question --note "<n> questions"`. A second round only for a question that depends on an answer given in the first; never to re-ask or widen the first. When the developer cannot be reached in this run (an unattended or eval run), ask nothing: each question goes into "What I need from you" with its options and the one you recommend, no `question` event is logged, and the plan stays `draft`.
    **Plan verification**, on unless the workflow file says `Plan verification: off` or the developer passes `--no-verify` (say in the close that it was skipped, and why): before asking, start one separate agent by [roles/plan-verifier.md](../../roles/plan-verifier.md) on the strong tier with one line, `Check the plan <path> in the repository at <root>. Follow <skill set>/roles/plan-verifier.md.`, and nothing else. Save its return unchanged as `<plans_dir>/<name>/plan-check.md`. Fix what it shows wrong, or carry it into the questions; show the developer the objections with the plan. At approval, `plan_seal.py hash <plan>` must equal the "Text checked" hash, or say that the plan changed since it was checked. Log `runlog.py event RUN_ID tier --role plan-verifier --tier strong --tokens <N|na> --seconds <N>`.
12. **Approve.** Set `Status: approved <date>` only on the developer's word for the whole plan, then seal the approved text: `python3 -I "$ORCHARD/scripts/plan_seal.py" seal <plan>`. A later edit to anything but the status, the Result and the Change note breaks the seal, and `run` will not start on it; a changed plan is approved again and sealed again. A re-check builds nothing: on approval, ask for acceptance and record `accepted <date>`, which lets `update-docs` write the changes.
13. **Close.** `runlog.py finish RUN_ID --outcome delivered --findings <open questions + conflicts>`. Give the plan path, its status and what blocks.

**Compact plan** (`--compact`). Valid only when an approved scenario states the expected behaviour and the fix stays in one package and changes no public interface, fixture, text a person sees, stored data or backend call. Fill the compact table from `diagnosis.md`: scenario id, reproduction, cause, files the fix owns, tier and reason, proof (the failing test made to pass). Keep the rest of the file as the template's compact-plan note says; then steps 9 to 13. No scenario states it: say so and write the full plan.

## Rule that always holds

A scenario without a basis does not exist; packages share no file; the plan is the only decision record.

## Gotchas

- **The plan file must stay out of git.** A `docs/` folder is tracked in most projects; check before the first write.
- **Frame text is not enough.** A Back button, a disabled state or the primary button shows only in a render: render every frame that decides a scenario. Designers also write rules as text outside frames, sometimes in another language; quote and translate them.
- **A design file can be very large.** Use the adapter's cache option and never print raw JSON.
- **A cited spec page may have moved on.** Record its version and compare it on the next run.
- **`15:00` is a time, `1836:136177` is a frame.** Write frames as `F/<id>`.
- **A behaviour no source states is not a "confirm" question.** Take the plain default (for example, restart the flow) and say so; an app-only rule the team wants goes to the owner as a team decision.
- **Values the server decides are not app rules** and not conflicts.
- **Nothing built yet is not nothing to read.** A new project still has specs, frames, a ticket and conventions.
- **"Approved" is the developer's word for the plan.** A yes to one question is not approval.
- **A gate scenario is an outcome product would refuse to ship without.** A check that a control or a text is present, a rule another feature already proves, or a likely duplicate is flagged for the owner, never dropped silently.
