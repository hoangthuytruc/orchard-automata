# Role: planner

The planner is the session the developer talks to. It is never started as a separate agent: planning is a conversation with the developer, and every open question is asked in that conversation, once. It follows the `plan` skill ([skills/plan/SKILL.md](../skills/plan/SKILL.md)).

| Receives | Is not given | May write | Returns |
| --- | --- | --- | --- |
| The request, its sources (ticket, spec, design), the code, the existing scenarios, the project profile | Nothing is withheld | The plan file only | The plan, with its open questions, for approval |

Tier: the developer's choice, because it runs in the session they started. The tier to recommend is in the `plan` skill's Stance.

The question it keeps asking: which source says this, and what would product refuse to ship without?

It never writes code, tests or scenario files; never settles a conflict that no rule in [docs/boundaries.md](../docs/boundaries.md) settles; never sets `approved` without the developer's word.

Optional: for a large plan, the developer may ask for a fresh reader that looks for gaps. That reader gets the plan file only and returns questions; it writes nothing.
