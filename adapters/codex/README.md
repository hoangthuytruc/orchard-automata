# Adapter: Codex

How to use the Orchard skills from Codex. No rule lives here.

## Status

**Untested.** Nothing in this file has been run with Codex. Every step below is the intended route, written from how Codex reads instructions; check each one on a real project and record what happened before relying on it.

## Install

Codex reads `AGENTS.md` files from the repository it works in. Point the project's `AGENTS.md` at the skill set:

```markdown
## Orchard skills
The Orchard skill set lives at <path to orchard-automata>. Read <path>/AGENTS.md first.
To call a skill, open <path>/skills/<name>/SKILL.md and follow it. Project facts are in .orchard/profile.md.
```

Keep the path out of a tracked file when teammates keep the skill set elsewhere: put the block in a personal, untracked guide instead, or in the developer's own Codex instructions.

A skill is called by name in the prompt ("use the orchard `plan` skill on LED-7"). Codex then reads the `SKILL.md`; `$ORCHARD` is the folder two levels above it.

## How each role starts

Roles and tiers come from the project's agents map (`.orchard/agents.md`, overridden by `.orchard/agents.local.md`).

| Role | Intended route on Codex |
| --- | --- |
| Coordinator, planner, verifier, documenter | The session the developer started |
| Implementer | A separate non-interactive Codex process per package, started from the coordinator's shell with the brief from `references/run-flow.md` section 2 as its prompt, in the working copy the plan names. Its final message is the return |
| Reviewer | A separate Codex process with a read-only sandbox, prompt `Review <target> in the repository at <root>. Follow <skill set>/roles/reviewer.md.` Its final message is the review |
| Report writer (Strict only) | A separate Codex process with the brief from `roles/report-writer.md` |

What is not known yet:

- Whether a separate process reports tokens. If not, every token field is `na`.
- Whether the read-only sandbox still allows the `gh` and `git fetch` calls the reviewer makes for a pull request.
- How to choose the model per tier for a started process; until checked, the agents map names the setting and the coordinator passes it on the command line.

Because every exchange between roles is a file, roles may also run on different tools: for example implementers on Codex and the reviewer on another tool.
