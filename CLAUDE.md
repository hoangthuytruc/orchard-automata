# CLAUDE.md

Guidance for agents working on this repository.

## What this repository is

Orchard Automata is a portable, tool-agnostic skill set for iOS development with agents. It holds a platform-neutral workflow model, core skills, references, check scripts, role briefs, workflows, templates, per-tool adapters, an eval suite, and one sample project. The approved design is [docs/skill-set-plan.md](docs/skill-set-plan.md).

This repository is the product. It is never the target of its own workflows: a plan, a run or a review acts on a target project, and inside this repository that target is `sample/Ledger/`. Editing this repository (docs, skills, templates, scripts) is ordinary authoring.

## Structure

| Path | Scope level | Holds |
| --- | --- | --- |
| `docs/` | Model | Principles, boundaries, scopes, workflow model, terms. Platform-neutral |
| `skills/<name>/SKILL.md` | Core | Twelve skills |
| `references/` | Core | Generic iOS rules the skills cite |
| `scripts/` | Core | Check and record scripts (Python 3 standard library, Bash) |
| `roles/` | Core | Role briefs (implementer, reviewer, report writer) |
| `workflows/` | Core | `feature-development`, `bug-fix`, `review-only` |
| `templates/` | Core | Profile, review rules, agents map, plan, test report, workflow |
| `adapters/<tool>/` | Core | Installation and how a tool starts a role. No rules |
| `evals/` | Core | One case per skill, run on the sample |
| `sample/Ledger/` | Sample | A Swift package with seeded bugs and its own `.orchard/` |

## Rules for changes

- Keep the model, the templates and the workflows consistent: a change to the model's required fields or state contract is made in `templates/workflow.md` and every file in `workflows/` in the same change.
- Core holds nothing project-specific. Run `python3 -I scripts/leak_check.py` after any change to core; it must report "clean" and exit 0.
- One home per rule. Before adding a rule, search for it; sharpen the existing text instead of adding a copy. A skill points to a reference; it does not restate it.
- Every term is used as defined in `docs/terms.md`; a new term gets a row there with its official definition and source, or a statement that no standard defines it.
- A change to a skill, reference, script or workflow is accepted only after it has been applied to `sample/Ledger/` and the evidence is recorded.
- Transitions are written as `` `From → To` when <observable condition>. ``
- Apple-specific values (scheme, workspace, destination) belong in a project profile, never in the model.
- No skill commits, pushes, or opens, approves or merges a pull request. Publishing and distribution need a person.

## Commands

| Purpose | Command |
| --- | --- |
| Leak check over core | `python3 -I scripts/leak_check.py` |
| Script self-tests | `python3 -I scripts/selftest.py` |
| Sample builds and tests | `cd sample/Ledger && swift build && swift test` |
| Eval suite | `scripts/eval.sh smoke` (spawns agent runs on the developer's account) |
