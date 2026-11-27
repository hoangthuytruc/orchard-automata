# Orchard Automata: entry for any agent tool

This repository is a skill set for iOS development that any agent tool can follow. It is plain Markdown and a few Python 3 scripts (standard library only). Nothing here is tied to one tool, one model or one project.

The governing idea is zero trust: an agent's statement is a claim, never a result. Read [docs/principles.md](docs/principles.md) before the first skill; every skill obeys it and points to it rather than restating it.

## Where things live

| Folder | Holds |
| --- | --- |
| `skills/<name>/SKILL.md` | The twelve skills. Each one is a procedure an agent follows |
| `roles/` | The briefs for the roles a workflow starts: coordinator, planner, implementer, verifier, reviewer, documenter, report writer |
| `workflows/` | The three shipped workflows: `feature-development`, `bug-fix`, `review-only` |
| `references/` | Standards, the review checklist, the test strategy and the other references the skills cite |
| `scripts/` | The checks the skills run: profile, lock, scenario gate, evidence, run log, leak check |
| `templates/` | The files a project or a task copies: profile, review rules, agents map, plan, test report, workflow |
| `docs/` | The model: principles, boundaries, scopes, workflow model, terms |
| `adapters/<tool>/` | How one tool installs the skills and starts a role. No rule lives there |
| `sample/Ledger/` | The sample project every skill and workflow is proved on |

## The skills

| You want to | Skill |
| --- | --- |
| Start using the skill set in a project | `adopt` |
| Know what to build, on what basis, before coding; re-check or draft a feature's scenarios | `plan` |
| Build one work package, test first | `implement` |
| Write or repair tests; diagnose a flaky test; audit a suite | `test` |
| Record what ran against this exact change | `verify` |
| Find why something fails, and leave one failing test | `debug` |
| Get an independent review of a change | `review` |
| Rank where the code is weakest | `debt` |
| Write the test report for the developer's decision | `handoff` |
| Record what shipped in the knowledge base | `update-docs` |
| Drive a workflow from an approved plan to the report | `run` |
| Improve the skill set from its run log | `retro` |

## How to call a skill

1. Open `skills/<name>/SKILL.md` and follow it. Inside a skill, `$ORCHARD` means the folder two levels above that `SKILL.md`, which is the root of this repository. Run scripts as `python3 -I "$ORCHARD/scripts/<script>"`.
2. Work in the target project, never in this repository. Inside this repository the target is `sample/Ledger/`.
3. The project's facts come only from its profile, `.orchard/profile.md` (keys in [templates/project-profile.md](templates/project-profile.md)). Read one value with `python3 -I "$ORCHARD/scripts/profile_check.py" get .orchard/profile.md <key>`. A project without a profile starts with `adopt`.

## A skill called alone

Every skill called alone, outside a run, opens and closes the same way. In a run, the coordinator does this once for the whole run instead.

1. **Profile.** `python3 -I "$ORCHARD/scripts/profile_check.py" check .orchard/profile.md --root . --skill <name>`: only the keys the skill reads (column "Read by" in [templates/project-profile.md](templates/project-profile.md)). `plan` and `run` are listed on every required key, so for them it is the full check.
   - Exit 0: go on.
   - Exit 2: a required key the skill reads is missing. Stop, name the keys, and point the developer to `adopt`.
   - Exit 3: the source file of the listed values changed since the developer confirmed them, or git does not track it. Discover only those values again (`adopt`, step for changed sources). If a value now differs from the confirmed one, stop and show both to the developer.
2. **Run log.** `python3 -I "$ORCHARD/scripts/runlog.py" start --workflow <W> --skill <name> --task "<one line>"`, where `<W>` is the workflow the skill is a step of (`debug` as the first step of a bug fix: `bug-fix`), else `alone`; keep the printed `RUN_ID`. Record the tier the skill runs on as `runlog.py event RUN_ID tier --tier <strong|light>`, once, and again on a change; record other events as the skill says.
3. **Close.** `python3 -I "$ORCHARD/scripts/runlog.py" finish RUN_ID --outcome <delivered|green|red|blocked|ended_early> [--findings N] --tokens <N|na> [--seconds N]`. Tell the developer the outcome, where the output is, what waits for them, and the `RUN_ID`. `--tokens` and `--seconds` are the numbers the tool reports for this skill's session; when it reports no tokens, pass `--tokens na`, and leave out `--seconds` when it reports no time. They are never estimated.

## What no skill ever does

No skill commits, pushes, creates a branch or tag, or opens, approves or merges a pull request. No skill writes to a tracker, wiki or design tool. No text a skill produces mentions an AI or a tool. The rules behind these are in [docs/boundaries.md](docs/boundaries.md).

## Starting a role on your tool

Roles are bound to real agents by the project's agents map (`.orchard/agents.md`, overridden by `.orchard/agents.local.md`; template in [templates/agents.md](templates/agents.md)). How your tool starts a role is in its adapter: [claude-code](adapters/claude-code/README.md), [codex](adapters/codex/README.md), [cursor](adapters/cursor/README.md).
