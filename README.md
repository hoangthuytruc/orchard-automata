# Orchard Automata

A portable skill set for iOS development with agents, built so a person can verify a finished run in minutes.

An agent's statement is a claim, never a result. Agents run from an approved plan to a finished result without waiting on a person; every transition rests on recorded evidence, and the person decides only at the two ends: approving the plan and accepting the result.

## Start here

1. Read the [principles](docs/principles.md), [boundaries](docs/boundaries.md), [scope levels](docs/scopes.md) and [workflow model](docs/workflow-model.md). Words are defined in [terms](docs/terms.md).
2. Adopt it in a project: call the `adopt` skill, or copy [the profile template](templates/project-profile.md) to `.orchard/profile.md` and fill it by hand.
3. Plan a change with `plan`, approve it, build it with `run`, accept the test report.
4. To see every skill work end to end, use the [sample project](sample/Ledger/).

The approved design, with its reasoning, is [docs/skill-set-plan.md](docs/skill-set-plan.md).

## The twelve skills

| You want to | Skill |
| --- | --- |
| Start using it in a project | `adopt` |
| Know what to build, and how it will be proved | `plan` |
| Build an approved plan, end to end | `run` |
| Build one package test-first | `implement` |
| Write or repair tests | `test` |
| Record what ran on the final change | `verify` |
| Find why something fails | `debug` |
| Get an independent review | `review` |
| Know where the code is weakest | `debt` |
| Get a report you can accept from | `handoff` |
| Record what shipped | `update-docs` |
| Make the skill set better from its runs | `retro` |

## Repository map

```text
docs/          Model: principles, boundaries, scopes, workflow model, terms (platform-neutral)
skills/        The twelve skills (SKILL.md each)
references/    Generic iOS rules the skills cite
scripts/       Checks and records: profile, locks, scenarios, evidence, run log, leaks
roles/         Briefs for coordinator, planner, implementer, verifier, reviewer, documenter
workflows/     feature-development, bug-fix, review-only
templates/     Profile, review rules, agents map, plan, test report, workflow
adapters/      How each agent tool installs the set and starts a role (no rules)
evals/         One case per skill, run on the sample
sample/Ledger  The only target of workflows inside this repository
```

## Status

Version 1, in progress. See the roadmap in [the plan](docs/skill-set-plan.md#12-roadmap).
