---
name: debt
description: Inventory, score and rank technical debt in an iOS or Swift codebase or one module - hotspots by churn and complexity, crash risk, Swift concurrency debt, deprecated APIs, dead code, test gaps, duplication, dependency and documentation drift - into a ranked report with evidence, impact times likelihood over effort, and a first step per item. Fixes nothing. Use for "tech debt", "technical debt", "what should we clean up", "code health", "hotspots", "dead code", "deprecated APIs", "refactor backlog", "where is the risk in this codebase".
argument-hint: "[path or module] [--since 90d]"
---

# debt

A ranked, evidence-backed debt report the team can turn into a backlog. Read-only on the code: the only file written is the report. `$ORCHARD` is the folder two levels above this file.

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| The codebase and its history; [references/debt-taxonomy.md](../../references/debt-taxonomy.md) (read first); [references/standards.md](../../references/standards.md); the guides, for debt the project already tracks or accepts | One report at the path the developer names, else `<reports_dir>/debt-<date>-<scope>.md` | Fixes, refactors, creates tickets, commits | Nothing; they decide what goes on the backlog | Every item: `path:line` plus the signal and the command that produced it |

## Why

Internal quality decays unseen, and unranked cleanup is a matter of taste. It rests on technical debt, hotspot analysis and maintainability as ISO/IEC 25010 defines it.

## Stance

Surveyor. What does the measurement show, and what does it cost when it bites? Tier: light, recommended.

## General steps

1. Choose the scope and what to measure. 2. Measure with the cheapest signal first. 3. Score each item: what it costs when it bites, how often, and the effort to fix. 4. Rank. 5. Report with evidence and a first step; change nothing.

## Method

1. **Open** as in [AGENTS.md](../../AGENTS.md#a-skill-called-alone), with `--skill debt --task "debt <scope>"`.
2. **Discover.** `bash "$ORCHARD/scripts/discover.sh" .` gives the layout, language mode, lint rules, gates and hygiene counts. Read the guides it lists for debt already tracked or accepted (decision records, status docs, `TODO` conventions).
3. **Scope.** The path from the argument or the whole source tree; churn window from `--since` (default 90 days). Exclude build output, generated code, vendored packages and test targets from crash-risk counts; tests are assessed as test gaps.
4. **Collect signals** per category with the commands the taxonomy lists. Use what is installed (`swiftlint`, `periphery`, a code index) and say what is missing. For a large repository, the categories may be collected side by side, each returning `path:line` evidence and counts, never conclusions without evidence.
5. **Score and rank** with the taxonomy's impact × likelihood / effort. Merge duplicates. Set apart deliberate debt that has a recorded reason. Give each item one first step the size of one pull request.
6. **Write the report** from the taxonomy's template, including the method and its limits.
7. **Close.** The top five in chat with their scores and the report path. `runlog.py finish RUN_ID --outcome delivered --findings <items>`; later, `runlog.py rate RUN_ID --accepted <acted on> --rejected <dismissed>`.

## Rule that always holds

Measurements, not opinions; it fixes nothing. No evidence, no item.

## Gotchas

- **Do not count what the automated gates already enforce**, unless something works around them.
- **Numbers are triage, not verdicts.** Say when a score is a judgement call.
