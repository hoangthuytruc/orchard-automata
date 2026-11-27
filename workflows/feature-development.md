# Workflow: feature-development

## Trigger

A request for new or changed behaviour, with its sources: a ticket, a spec, a design.

## Inputs

- The request and its sources (ticket key or a sentence, spec and design links).
- The project profile `.orchard/profile.md`: knowledge base, plan and report folders, locked globs, commands (`build`, `test.unit`, `test.behaviour`, `test.visual`, `test.integration`, `lint`, `pr_check`), base branch, source ranking, design source, real-backend rules. Platform values (workspace, scheme, destination) are profile keys.
- The agents map (`.orchard/agents.md`, overridden by `.orchard/agents.local.md`).

## Roles and isolation

- Default isolation: Standard.

| State | Role | Tier | Skill |
| --- | --- | --- | --- |
| Intake, Plan | Planner | Developer's choice; strong recommended | `plan` |
| Implement | Implementer, one per package | Set per package by the plan | `implement` |
| Verify | Verifier (coordinator, scripts) | Light | `verify` |
| Review | Reviewer, separate agent | Strong for the full review; light for a review of fixes | `review` |
| Ready | Documenter (coordinator; separate at Strict) | Light | `handoff` |
| After acceptance | Documenter | Light | `update-docs` |
| Whole run | Coordinator | Light | `run` |

## States

| State | Entry | Action | Exit | Evidence |
| --- | --- | --- | --- | --- |
| Intake | A request exists | Fix scope and sources; read code, specs, design, scenarios fresh; list each requirement with its quote | Requirement list with quotes; source versions | Plan file, Sources and Requirements sections |
| Plan | Requirement list exists | Scenarios with bases; design change; impact checklist; work packages with owned files, tier and order; locks; open questions asked once | Plan status `approved`, set on the developer's word | Plan file status line; `gate_check.py --coverage` result |
| Implement | Plan `approved`; lock snapshot taken, or recorded as covering nothing | Per package: failing test bound to a scenario, least code, self-review | Each package returns files changed, tests added, commands run with results, what it did not run | Implementer returns, saved in the task folder |
| Verify | All packages of the round returned | Static analysis, then affected tests cheapest kind first; lock check | Result per check on the final tree, with the tree's state | `verify` evidence file |
| Review | Verify evidence recorded | Full review in round one; review of fixes after a fix round | Findings with type, severity, line, evidence, fix | Review file per round |
| Ready | No blocking finding, or rounds used up | Report: one screen on top, evidence below; draft pull-request body | Report written; plan status `executed` | Test report path |

## Transitions

- `Intake → Plan` when every requirement has a quote and a source version.
- `Plan → Implement` when the plan status is `approved` on the developer's word and `lock_check.py snapshot` has written the snapshot.
- `Implement → Verify` when every package of the round has returned its report and each new test in it has a red-run record in the evidence file, or is reported as not seen failing first (`references/run-flow.md`, section 3).
- `Verify → Implement` when a check fails because of the change and a round is left.
- `Verify → Review` when the affected checks pass on the final tree, or blocked checks are recorded with their reason.
- `Review → Implement` when a blocking finding (Blocker, Risk, High or Medium) is open and a round is left; each fix starts from a failing test.
- `Review → Plan` when a finding shows the plan is wrong; this ends the run early for the developer.
- `Review → Ready` when no blocking finding is open and the once-per-run checks passed after the last edit, or three rounds are used (verdict `blocked` if a required check still fails).

## Decision points

| When | Person decides | Shown |
| --- | --- | --- |
| Before | Approves the plan, including base branch | Plan file: one screen on top, open questions together |
| After | Accepts or sends back | Test report |
| After acceptance | Reviews the knowledge-base diff; commits | `update-docs` diff and gate-check result; draft pull-request body |

## Ends early when

- Sources conflict and no rule in `docs/boundaries.md` settles it.
- A locked file would have to change, or a package needs a file it does not own.
- The plan is wrong for what the code allows.
- A required profile key is missing, or a confirmed profile value changed.

## Recovery

- Missing requirement found during Implement → end early; back to `Plan` with the developer.
- Failing check → `Implement` for the owning package, next round.
- Lock broken → end early; the report names the file and its hash before and after.
- Third failing loop in a package → end that package; the report lists it as not delivered; its code and tests are removed.

## Handoffs

- Commit, push, pull request, merge and release belong to the developer, with the draft pull-request body from `handoff`.
- `update-docs` runs only after the developer says "accept".
