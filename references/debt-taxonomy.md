# Technical debt taxonomy and scoring

Used by the `debt` skill. Technical debt is defined in `$ORCHARD/docs/terms.md`. The report is the deliverable:
`debt` measures and ranks; it fixes nothing.

## Categories and how to find each (cheapest signal first)

| Category | Signals | Command or check |
| --- | --- | --- |
| Hotspots | files changed often and large | `git log --since=<window> --name-only --pretty=format: -- '*.swift' \| sort \| uniq -c \| sort -rn \| head -30`, joined with line counts |
| Complexity | long files and functions, deep nesting, many parameters | `swiftlint lint --reporter json` when a config exists (file_length, function_body_length, cyclomatic_complexity, type_body_length); otherwise `awk 'END{print NR, FILENAME}'` over Swift files |
| Crash risk | `!`, `try!`, `as!`, `.first!`, `fatalError` on data paths, `[0]` on possibly empty arrays | grep over the source folders, excluding tests |
| Concurrency debt | Swift 5 language mode, `@unchecked Sendable`, `nonisolated(unsafe)`, `DispatchQueue`, `DispatchSemaphore`, completion-handler APIs with an async alternative, `Task.detached`, `MainActor.assumeIsolated` | grep; language mode from the package manifest or project files |
| Deprecated or legacy API | `UIScreen.main`, `UIApplication.shared.windows`/`keyWindow`, `NavigationView`, `ObservableObject` where `@Observable` is available, `NSKeyedUnarchiver.unarchiveObject`, `URLSession` completion `dataTask`, `UIWebView`, `Result`-callback APIs, `@available(*, deprecated)` in own code | grep; check the deployment target before calling `@Observable` adoption debt |
| Dead code | unreferenced types, functions, resources, feature flags that are always on | `periphery scan` when installed; a code index's callers query when the project has one; otherwise `git grep -c <TypeName>` sampling of `public`/`internal` types with one hit |
| Test gaps | source types without a test naming them; tests with sleeps or no assertions; disabled or skipped tests; thresholds as warnings | the suite audit signals in `$ORCHARD/references/test-strategy.md`, section 15 |
| Duplication | same helper twice (formatters, parsers, empty-state views, buttons), same rule in two enums | grep for sibling names; compare bodies of similarly named types |
| Dependency debt | pinned old packages, abandoned forks, two libraries for one job, two package managers together | `Package.resolved` versions and dates (`git log -1 --format=%cs -- Package.resolved`); list only, no network needed |
| Build and tooling | warnings count, scripts not covered by the project's task runner, generated files in the repository, README commands that do not exist | compare README and task runner with the profile's commands; `grep -c warning:` in the last build log if present |
| Documentation drift | decision records marked proposed for months, docs describing removed behaviour, scenarios the app no longer satisfies | `git log -1 --format=%cs -- <decision folder>`; grep docs for identifiers that no longer exist; the knowledge base check (`knowledge_base_check`) |
| Intentional debt | TODO, FIXME, HACK with age and owner | `grep -rn 'TODO\|FIXME\|HACK'` then `git blame -L <n>,<n> --porcelain <file>` for author time |

## Scoring

For each item:

- **Impact (1–5):** what it costs when it bites: 5 = crash, data loss or security exposure in production; 4 = wrong
  behaviour users see; 3 = blocks or slows every change in the area; 2 = slows some changes; 1 = cosmetic.
- **Likelihood (1–5):** how often the area is touched or the failure path is hit: use churn (hotspot rank) and
  whether the path is on a main journey.
- **Effort (S/M/L):** S = under half a day, one pull request, no migration; M = one to three days or a small
  migration; L = more than three days, cross-cutting, needs its own plan.

Priority = Impact × Likelihood, then smaller Effort first. Items with Impact 5 are listed first regardless of
effort. Say when a score is a judgement call and what would change it.

## Rules

- Evidence per item: at least one `path:line` and the command or signal that produced it. No item without evidence.
- No fixes, no refactors, no tickets: the report is the deliverable. A "first step" per item is one move the size of
  one pull request.
- Keep a "deliberate debt, keep for now" section for items with a documented reason (a decision record, a comment,
  a product decision), so the next person does not re-argue them.
- Count what the automated gates already enforce (lint rules, pre-pull-request checks) only when something works
  around them.
- Numbers are triage, not verdicts: a 600-line file with one responsibility is not debt; ten `!` in a test target
  are not crash risk.

## Report template

Written to `reports_dir`, or the path the developer names.

```markdown
# Technical debt: <scope> — YYYY-MM-DD

Scope: <paths>. Window for churn: <since>. Tools: <what ran>. Baseline numbers: <counts>.

## Top items (ranked)

| # | Item | Category | Impact | Likelihood | Effort | Evidence | First step |
|---|---|---|---|---|---|---|---|
| 1 | <one line> | Concurrency | 5 | 4 | M | `Sources/…/File.swift:42`, `git log` churn 17/90d | <one move the size of a pull request> |

## By category
<one short paragraph or bullets per category with the counts and the notable cases>

## Deliberate debt, keep for now
- <item, reason, where the reason is recorded>

## Suggested order of work
1. <item #> because <impact or unblocks>
2. …

## Method and limits
What was scanned, what was not (no network, no build), tools missing on this machine.
```
