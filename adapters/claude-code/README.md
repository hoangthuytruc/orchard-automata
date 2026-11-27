# Adapter: Claude Code

How Claude Code installs the Orchard skills and starts each role. No rule lives here; the rules are in the skills, roles and docs this adapter links to.

## Status

The plugin layout follows a private plugin whose layout was validated with `claude plugin validate` and whose reviewer agent registered through the default `agents/` scan. Installed with `install.sh` and listed as loaded by `claude plugin list` (12 skills, agent `orchard-reviewer`) on 2026-11-26; no skill has yet been run end to end through it. Check it with the commands under "Check the install" before relying on it, and record the result.

## Layout

`plugin/` is a Claude Code plugin whose folders are relative symlinks into this repository, so there is one copy of every file:

| Path | Points to |
| --- | --- |
| `plugin/.claude-plugin/plugin.json` | The manifest: name `orchard`, skills `./skills` |
| `plugin/skills`, `references`, `scripts`, `roles`, `templates`, `workflows`, `docs`, `AGENTS.md` | The same names at the repository root. `evals` is not linked: the eval harness rejects a linked eval folder, so `eval.sh` stages a copy |
| `plugin/agents/orchard-reviewer.md` | The reviewer agent; its body says "follow `roles/reviewer.md`" |

`plugin.json` has no `agents` key on purpose: the default `agents/` scan registers `orchard-reviewer`, while an explicit `agents` entry registered none on the CLI version tested with the earlier plugin.

A skill's `$ORCHARD` is the folder two levels above its `SKILL.md`. Inside the plugin that is `plugin/`, which carries the same folders as the repository root through the symlinks, so every `$ORCHARD/...` path resolves either way.

## Install

Claude Code refuses a plugin whose folders are links pointing outside it, so a project gets a real copy:

`adapters/claude-code/install.sh <project root>` copies `plugin/` with every link resolved to `<project>/.claude/skills/orchard`, writes `.orchard-install` (source path, commit, time) beside it, and adds the folder to the project's local git exclude when git does not already ignore it. Run it again to update the copy after the skill set changes; it replaces only a folder it made itself.

For one session without installing: `claude --plugin-dir <path to this repository>/adapters/claude-code/plugin` (untested with the links; use the install script when in doubt).

## Check the install

- `claude plugin validate <path>/adapters/claude-code/plugin`
- `claude plugin details orchard`: lists the twelve skills and the agent `orchard-reviewer`.
- In a session, `/reload-plugins` after editing a skill.

## How each role starts

Roles and tiers come from the project's agents map (`.orchard/agents.md`, overridden by `.orchard/agents.local.md`). Its Tiers table says which model each tier means on this tool; pass that as `model` on the Agent call.

| Role | How Claude Code starts it |
| --- | --- |
| Coordinator, planner, verifier, documenter at Shared and Standard | The session the developer started. Nothing is started |
| Implementer | Agent tool, general-purpose subagent. Prompt: "Follow the brief in `<brief file>`", the brief from `references/run-flow.md` section 2 saved as a file, and nothing else. `model`: the package's tier. For "a working copy each", add `isolation: "worktree"`; bring each worktree's change into the main tree as `references/run-flow.md` says |
| Plan verifier (every plan, unless the workflow turns it off) | Agent tool, a general-purpose agent. Prompt: one line, `Check the plan <path> in the repository at <root>. Follow <skill set>/roles/plan-verifier.md.` `model`: strong |
| Reviewer | Agent tool, `subagent_type: "orchard:orchard-reviewer"`. Prompt: one line, `Review <target> in the repository at <root>. Follow <skill set>/roles/reviewer.md.`, plus `Plan: <path>.` when there is one. `model`: strong for a full review, light for a review of fixes |
| Report writer (Strict only) | Agent tool, general-purpose subagent. Prompt: the brief from `roles/report-writer.md` |

Notes on the tool:

- A subagent does not see the conversation or any memory. The brief is all it has.
- An agent definition without a `model` field inherits the session's model. Always pass `model` on the call so the tier is the one the plan names.
- The completion notification of a subagent reports `total_tokens`. Pass it to `runlog.py event … --tokens <n>`; when it is absent, `--tokens na`.
- A worktree starts from the last commit, without the main tree's uncommitted work.

## Evals

`eval.sh` runs the eval cases in `evals/` through `claude plugin eval`, with and without the skills, and scores them with the graders each case defines. `eval.sh smoke` runs each case once; `eval.sh full` three times; `eval.sh case '<glob>'` one case. Each run spawns Claude Code processes on the developer's account; `MAX_COST_USD` caps a run. Results stay in `evals/results/` unless `EVAL_OUT` says otherwise. Format of a case: `evals/README.md`.

Harness limits learned with the earlier plugin: inside the eval sandbox `git` and SwiftPM's own test sandbox are blocked, so a run may fall back to `swiftc` with `xctest`, and the honesty grader accepts a truthfully reported substitute; telling a run to disable SwiftPM's sandbox made both arms hang until the timeout. One run per case is a smoke signal; run `full` before trusting a difference.
