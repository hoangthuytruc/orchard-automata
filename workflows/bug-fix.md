# Workflow: bug-fix

## Trigger

A defect: what was seen, and what was expected.

## Inputs

- The report of the defect: what was seen, what was expected, where, since when; logs, a crash report or a recording when there is one.
- The project profile `.orchard/profile.md`: knowledge base and `scenario_id_pattern`, plan and report folders, locked globs, commands (`build`, `test.unit`, `test.behaviour`, `test.visual`, `test.integration`, `lint`, `pr_check`), base branch, `device_policy`, real-backend rules. Platform values (workspace, scheme, destination) are profile keys.
- The agents map (`.orchard/agents.md`, overridden by `.orchard/agents.local.md`).

## Roles and isolation

- Default isolation: Standard: one implementer for the one package, and a separate reviewer. A plan may raise it with a one-line reason; never below a separate reviewer. When the main session builds the package itself, the run is at Shared and is logged as Shared.

| State | Role | Tier | Skill |
| --- | --- | --- | --- |
| Intake | Verifier (the developer's session) | Developer's choice; strong recommended, light once reproduced | `debug` |
| Plan | Planner | Strong for a full plan; light for a compact plan (the `plan` skill's Stance) | `plan --compact` |
| Implement | Implementer, one package | Set by the plan | `implement` |
| Verify | Verifier (coordinator, scripts) | Light | `verify` |
| Review | Reviewer, separate agent | Strong for the full review; light for a review of fixes | `review` |
| Ready | Documenter (coordinator; separate at Strict) | Light | `handoff` |
| After acceptance | Documenter, only when a scenario changed | Light | `update-docs` |
| Whole run | Coordinator | Light | `run` |

## States

| State | Entry | Action | Exit | Evidence |
| --- | --- | --- | --- | --- |
| Intake | A defect is reported | Reproduce, reduce, one hypothesis at a time, confirm the cause by turning it on and off; write one regression test bound to the scenario when one exists | The test fails on its assertion because of the cause | `diagnosis.md`; the failing test's record in `evidence.jsonl` |
| Plan | Diagnosis written | When an approved scenario states the expected behaviour: compact plan (scenario id, reproduction, cause, files the fix owns, tier, proof). When none does: a full plan, as `feature-development` | Plan status `approved`, set on the developer's word after reading the diagnosis and the intended fix | Plan file status line |
| Implement | Plan `approved`; lock snapshot taken, or recorded as covering nothing | The regression test from Intake made to pass with the least change; nothing outside the owned files | The package returns files changed, the test's result, commands run, what it did not run | Implementer return, saved in the task folder |
| Verify | The package returned | Static analysis, then affected tests cheapest kind first; lock check | Result per check on the final tree, with the tree's state | `verify` evidence file |
| Review | Verify evidence recorded | Full review in round one; review of fixes after a fix round | Findings with type, severity, line, evidence, fix | Review file per round |
| Ready | No blocking finding, or rounds used up | Report, including the regression test failing before the fix and passing after it; draft pull-request body | Report written; plan status `executed` | Test report path |

## Transitions

- `Intake → Plan` when the regression test's failing record names the cause at `path:line`.
- `Plan → Implement` when the plan status is `approved` on the developer's word and `lock_check.py snapshot` has written the snapshot.
- `Implement → Verify` when the package has returned its report and each new test in it has a red-run record in the evidence file, or is reported as not seen failing first (`references/run-flow.md`, section 3).
- `Verify → Implement` when a check fails because of the change and a round is left.
- `Verify → Review` when the affected checks pass on the final tree, or blocked checks are recorded with their reason.
- `Review → Implement` when a blocking finding (Blocker, Risk, High or Medium) is open and a round is left; each fix starts from a failing test.
- `Implement → Plan` when the fix would change a public interface, fixture, text a person sees, stored data or a backend call, or a second package: the compact plan no longer holds; this ends the run early and the plan is redone at full size.
- `Review → Ready` when no blocking finding is open and the once-per-run checks passed after the last edit, or three rounds are used (verdict `blocked` if a required check still fails).

## Decision points

| When | Person decides | Shown |
| --- | --- | --- |
| Before | Approves the diagnosis and the fix, including base branch | Diagnosis and compact plan on one screen |
| After | Accepts or sends back | Test report, with the regression test before and after |
| After acceptance | Reviews the knowledge-base diff when a scenario changed; commits | `update-docs` diff and gate-check result; draft pull-request body |

## Ends early when

- The defect cannot be reproduced: the diagnosis records what was tried.
- No approved scenario states the expected behaviour, and the sources conflict on it with no rule in `docs/boundaries.md` to settle it.
- The fix needs a file the package does not own, a locked file, or one of the changes a compact plan excludes.
- A required profile key is missing, or a confirmed profile value changed.

## Recovery

- No scenario states the expected behaviour → the work becomes a small `feature-development`: a basis first, then a full plan.
- Failing check → `Implement`, next round.
- Lock broken → end early; the report names the file and its hash before and after.
- Third failing loop → end; the report lists the fix as not delivered; its code and the regression test are removed, and `diagnosis.md` keeps the test's text for the next attempt.

## Handoffs

- Commit, push, pull request, merge and release belong to the developer, with the draft pull-request body from `handoff`.
- `update-docs` runs only after the developer says "accept", and only when the fix changed a scenario.
