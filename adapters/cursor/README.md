# Adapter: Cursor

How to use the Orchard skills from Cursor. No rule lives here.

## Status

**Untested.** Nothing in this file has been run with Cursor. Every step below is the intended route; check each one on a real project and record what happened before relying on it.

## Install

Cursor's agent reads `AGENTS.md` at the root of the project. Point it at the skill set:

```markdown
## Orchard skills
The Orchard skill set lives at <path to orchard-automata>. Read <path>/AGENTS.md first.
To call a skill, open <path>/skills/<name>/SKILL.md and follow it. Project facts are in .orchard/profile.md.
```

When the skill set sits outside the project folder, add it to the workspace so the agent can read it. Keep the path out of a tracked file when teammates keep the skill set elsewhere.

A skill is called by name in the prompt ("use the orchard `review` skill on the working tree"). `$ORCHARD` is the folder two levels above the `SKILL.md`.

## How each role starts

Roles and tiers come from the project's agents map (`.orchard/agents.md`, overridden by `.orchard/agents.local.md`).

| Role | Intended route on Cursor |
| --- | --- |
| Coordinator, planner, verifier, documenter | The chat the developer started |
| Implementer | A new agent chat, or a background agent, per package, given only the brief from `references/run-flow.md` section 2, with the model the agents map names for the package's tier. Its final message is saved as the return |
| Reviewer | A new agent chat with no history of the work, asked `Review <target> in the repository at <root>. Follow <skill set>/roles/reviewer.md.` Edits must be refused or reverted: the reviewer is read-only |
| Report writer (Strict only) | A new agent chat with the brief from `roles/report-writer.md` |

What is not known yet:

- Whether a coordinator chat can start another agent and read its final message without a person copying it. If not, a run at Standard needs the developer to start each agent, which breaks "the run does not wait". Until a route is found, run implementers in the coordinator chat (the Shared level, logged as Shared) and start the reviewer, which is always separate, on another tool.
- Whether a new chat can be held to read-only tools.
- Whether token counts are reported. If not, every token field is `na`.
