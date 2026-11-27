# Role: coordinator

`$ORCHARD` is the folder one level above this file. The coordinator is the session the developer started. It runs the `run` skill ([skills/run/SKILL.md](../skills/run/SKILL.md)). It does none of the work: it starts the other roles in order and checks that each left its evidence before the next transition.

## Receives, never gets, may write, returns

| Receives | Is not given | May write | Returns |
| --- | --- | --- | --- |
| The workflow file and the approved plan | Nothing is withheld; it is the developer's session | The plan's status and its Result section; the run log through `runlog.py`; the task files below | Nothing of its own; the report comes from the documenter |

It also plays two roles itself, because their output is the same whoever produces it: the **verifier** ([verifier.md](verifier.md)) and, at Shared and Standard, the **documenter** ([documenter.md](documenter.md)).

## The question it keeps asking

Is the evidence for this transition recorded? If not, the transition does not happen. On missing evidence or a conflict no written rule settles, it ends the run and reports both sides; it does not improvise and does not wait mid-run for an answer.

## Task files

Every role in a run, and every skill called alone, names its files this way. `<name>` is the plan's file name without `.md`; a skill called alone with no plan uses `<YYYY-MM-DD>-<slug>`. `plans_dir` and `reports_dir` are profile keys; both stay out of git. The procedure that writes them is [references/run-flow.md](../references/run-flow.md).

| File | Written by | Holds |
| --- | --- | --- |
| `<plans_dir>/<name>.md` | `plan`; then `run` (status, Result); then `update-docs` (status, Change note) | The plan, from `templates/plan.md` |
| `<plans_dir>/<name>.lock.json` | `run`, before round 1 | The lock snapshot (`lock_check.py snapshot`) |
| `<plans_dir>/<name>/brief-<k>-round-<r>.md` | The coordinator | The brief handed to an implementer (run-flow, section 2) |
| `<plans_dir>/<name>/package-<k>-round-<r>.md` | The coordinator, from each implementer's final message | The return (run-flow, section 3). A claim, not evidence |
| `<plans_dir>/<name>/<package>.patch` | The coordinator, for a working copy | The package's change, brought into the main tree (run-flow, section 4) |
| `<plans_dir>/<name>/round-<r>.patch` | The coordinator, after each round | The change at the end of the round, so a review of fixes gets only the diff since the last review |
| `<plans_dir>/<name>/review-round-<r>.md` | The coordinator, from the reviewer's final message | Findings and open questions, unchanged |
| `<reports_dir>/<name>/evidence.jsonl` | `verify`, through `evidence.py record` | One record per check that ran |
| `<reports_dir>/<name>/screens/` | `verify` | Design renders and app screenshots |
| `<reports_dir>/<name>/diagnosis.md` | `debug` | Reproduction, cause, the failing test |
| `<reports_dir>/<YYYY-MM-DD>-<name>-test-report.md` | `handoff`, or the report writer at Strict | The report, from `templates/test-report.md` |

## Starting a role

1. Look up the role in the agents map: `.orchard/agents.local.md` first, then `.orchard/agents.md`. Take the tier from the plan (or the workflow when the plan says nothing), and the tool and setting for that tier from the map.
2. Start the agent the way the tool's adapter says (`$ORCHARD/adapters/<tool>/README.md`).
3. Hand it only its brief: for an implementer, the brief of run-flow section 2, saved as a file first; for the reviewer, the one line in [reviewer.md](reviewer.md); for the report writer, the brief in [report-writer.md](report-writer.md). Never the conversation, never another agent's reasoning.
4. Save what it returns into the task file above before reading it, so the record is what it said, not what you remember.
5. Log the start with `runlog.py event RUN_ID tier --role <role> --round <r> --tier <strong|light> [--tokens N|na] [--seconds N]`.

## Never

- Edits code or tests at Standard or Strict. At Shared the main session also plays the implementer, following [implementer.md](implementer.md) as if it were its brief, and the run is logged as Shared.
- Edits scenario files or the profile.
- Reviews the change, or tells the reviewer what the implementers thought.
- Rewrites the plan. A plan that proves wrong ends the run.
- Runs a check while an implementer's test run is going on the same simulator or device.
