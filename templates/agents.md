# Agents map

<!--
Binds each role to a real agent. Two files:
- .orchard/agents.md        project default; may be tracked; no tokens, no personal paths.
- .orchard/agents.local.md  personal override; never tracked. A row here replaces the same role's row above.
Tiers come from the workflow and the plan (strong / light); this file says what each tier means on each tool.
No rule lives here: only bindings.
-->

## Tiers

| Tier | Agent tool | Model or setting |
| --- | --- | --- |
| strong | <tool> | <model or effort setting> |
| light | <tool> | <model or effort setting> |

## Roles

| Role | Agent tool | How it is started | Isolation | Notes |
| --- | --- | --- | --- | --- |
| Coordinator | <the session the developer starts> | n/a | n/a | Runs `run` |
| Planner | <same session> | n/a | n/a | Runs `plan` |
| Implementer | <tool> | <see adapters/<tool>/README.md> | <shared tree / working copy each> | |
| Reviewer | <tool> | <see adapters/<tool>/README.md> | read-only | Never the implementer's tool session |
| Report writer (Strict only) | <tool> | <see adapters/<tool>/README.md> | read-only except the report | |
