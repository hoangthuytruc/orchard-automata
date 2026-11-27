# Scope levels: where each thing lives

A scope level is the home of a fact: the narrowest place where it is true for everyone who reads it. "Scope of a change" (what one plan covers) is a different term; both are defined in [terms](terms.md).

| Scope level | Home | Holds | Must not hold |
| --- | --- | --- | --- |
| Model | `orchard-automata/docs/` | States, transitions, evidence, decision points, roles. Platform-neutral | Anything about Xcode or one project |
| Core | `orchard-automata/skills`, `references`, `scripts`, `roles`, `templates`, `workflows`, `evals` | Generic iOS rules, skill procedures, check scripts, role briefs, shipped workflows | Project names, absolute paths, ticket keys, model names, tokens |
| Sample | `orchard-automata/sample/Ledger/` | A small generic Swift package with its own `.orchard/` profile, fake ticket, spec and design, and seeded bugs | Any rule; anything from a real project |
| Project | `.orchard/` in the project repository, linked from its `AGENTS.md` | Project profile, review rules, workflow copies, agents map default | Generic rules already in core; personal settings |
| Task | Folders named in the project profile | Plan file, lock snapshot, test report, screenshots | Rules of any kind |
| Personal | The developer's machine | Personal agents map, model choice, tokens, run log | Anything a teammate needs |
| External | Tracker, wiki, design tool | Specs and designs. Read-only sources | Agent writes |

**Routing rule.** A fact true for every iOS project goes to core; a fact true for one project goes to its profile; a fact true for one task goes to its plan; a preference goes to personal. The team chooses whether `.orchard/` is tracked or locally excluded; the skill set works either way.

**Leak check.** `scripts/leak_check.py` fails when core holds what only a narrower level may hold: absolute home paths, a project name, a ticket key, a model name. It runs before any change to core is accepted.

## The project profile

`.orchard/profile.md`, from [`templates/project-profile.md`](../templates/project-profile.md). Its required keys, and the skills that read each key, are listed there. A skill stops when a required key it reads is missing.

Each value carries its source: the file it was read from and that file's hash, or "stated by the developer". A file source is a file git tracks, so every teammate's check hashes the same file; a value found only in an untracked or ignored file is recorded as stated, with the file named in a note. `scripts/profile_check.py` re-hashes the sources at the start of a run or of a skill called alone. Only a value whose source changed is discovered again, and a value that then differs from the confirmed one ends the run for the developer to confirm.

## The agents map

Roles are bound to real agents in two files: `.orchard/agents.md` (the project default, may be tracked) and `.orchard/agents.local.md` (the personal override, never tracked). A row in the personal file replaces the same role's row in the project file. Template: [`templates/agents.md`](../templates/agents.md).
