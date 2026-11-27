# Agents map: Ledger (sample)

Project default. A personal override goes in `.orchard/agents.local.md` (never tracked).

## Tiers

| Tier | Agent tool | Model or setting |
| --- | --- | --- |
| strong | claude-code | the strongest model available to the developer |
| light | claude-code | a lighter model |

## Roles

| Role | Agent tool | How it is started | Isolation | Notes |
| --- | --- | --- | --- | --- |
| Coordinator | the developer's session | n/a | n/a | Runs `run` |
| Planner | the developer's session | n/a | n/a | Runs `plan` |
| Implementer | claude-code | adapters/claude-code: subagent with the implementer brief | shared tree | |
| Reviewer | claude-code | adapters/claude-code: subagent `orchard-reviewer` | read-only | |
| Report writer (Strict only) | claude-code | adapters/claude-code: subagent with the report-writer brief | read-only except the report | |
