# Follow-ups from the planning and isolation experiment

Date: 2026-11-26. Every point the agents raised while running the skills on the sample for
[2026-11-26-planning-and-isolation.md](2026-11-26-planning-and-isolation.md), with what was done and where. Script
changes are proved by `scripts/selftest.py` on a copy of `sample/Ledger`; the case names are quoted.

| # | Point raised | What was done | Where |
| --- | --- | --- | --- |
| 1 | `gate_check.py --coverage` failed on a valid compact plan: it has no Requirements and no section 5 | A plan with a `## Compact plan` heading is checked as a compact plan. Every row needs a scenario id matching `--id-pattern`, a reproduction, a cause at `path:line`, owned files, a tier (strong or light) with a reason, and a proof. HTML comments are ignored, so the template's commented example is not read. Selftest: "a compact plan is checked as one", "compact row without id, path:line, tier reason or proof -> exit 1" | `scripts/gate_check.py` (`check_compact`, `table_rows`); `scripts/selftest.py` |
| 1 | A full plan's "Pending or blocked scenarios" sub-table was read as scenario rows | Section 5 is read only up to its first `###` heading. Selftest: "the "###" pending sub-table under section 5 is not read as scenario rows" | `scripts/gate_check.py` (`check_coverage`); `scripts/selftest.py` |
| 1 | `Keep` rows were not counted | The summary line says "N kept". Selftest: "plan file sections 2 and 5" now expects "5 scenario rows, 1 kept" | `scripts/gate_check.py`; `scripts/selftest.py` |
| 2 | The template did not say plainly what a compact plan keeps | The compact-plan note lists what is kept (the header lines, the shortened top part, the Working detail heading and Sources line, Result and Change note) and what is replaced (sections 1–8 only). The stray header comment about compact plans moved into that note | `templates/plan.md` |
| 2 | The "Pending or blocked scenarios" sub-table could be mistaken for scenario changes | It stays under section 5 as a `###` sub-section, with a comment that it is not scenario changes and that the check stops there | `templates/plan.md` |
| 2 | `Keep` was not named as a Change value | The section 5 comment points to the one list of Change values in `references/scenario-gate.md` (Keep included) and says that a kept scenario that gains a test, the usual bug fix, is Keep | `templates/plan.md` |
| 3 | "Approved scenario" was used but not defined | New row: a scenario in the knowledge base; only `update-docs` writes there, after acceptance, so being there is the approval; a blocked or pending scenario is approved but unproved. No standard defines it; nearest are requirements baseline (ISO/IEC/IEEE 29148) and test basis (ISTQB), wording not checked | `docs/terms.md`, "Requirements and scope" |
| 4a | No rule for questions when the developer cannot be reached | The questions go into "What I need from you" with options and a recommendation; no `question` event is logged; the plan stays `draft` | `skills/plan/SKILL.md`, step 11 |
| 4b | Planning tier in bug-fix was unclear | Stance: in `bug-fix`, a full plan runs on strong and a compact plan on light. The bug-fix tier table and the planner role point to it instead of saying it differently | `skills/plan/SKILL.md` (Stance); `workflows/bug-fix.md`; `roles/planner.md` |
| 4c | `--compact` skipped the coverage check | Step 9 runs `gate_check.py --coverage` for `--compact` too; the compact paragraph sends the planner on to steps 9–13 | `skills/plan/SKILL.md` |
| 5 | `runlog.py finish` rejected `--tokens na`, which `AGENTS.md` tells skills to pass | `finish` takes `--tokens N\|na` and `--seconds N`, for the session that closes the run; they count in the report. `AGENTS.md` now shows them in the close command. Selftest: "finish: with the closing session's tokens" (report shows tokens 2000 = 1200 + 800), "finish: --tokens na and --seconds" | `scripts/runlog.py`; `AGENTS.md`, "A skill called alone"; `scripts/selftest.py` |
| 5 | `report` minutes came from finish minus start, which is 0 for records written after the fact | A run's minutes are the sum of its recorded `--seconds` (events other than `approval_wait`, plus finish) when it has any, else finish minus start. The output says which: "from recorded seconds", "from start to finish", or a mix with counts. Selftest: "minutes 7.0 (from recorded seconds)", "minutes 0.0 (from start to finish)" | `scripts/runlog.py` (`recorded_seconds`, `run_seconds`); `scripts/selftest.py` |
| 6 | A passing check's summary showed "Test run with 0 tests in 0 suites passed" (Swift Testing, no tests) instead of the XCTest count | A passing check shows the last XCTest or Swift Testing summary that counts at least one test, then falls back to the last line. Selftest: "a passing check shows the summary that counts tests, not the empty one" | `scripts/evidence.py` (`summary_line`); `scripts/selftest.py` |
| 7 | "Seen failing first with" in the implementer's return was not backed by a record | The rule has one home: run-flow section 3. Each new test's red run is recorded with `evidence.py record --selection red-<test>`, and the coordinator checks the record before `Implement → Verify`; a test without one is reported as not seen failing first. The brief names the evidence file; implement, the implementer role, `run` and both workflows' `Implement → Verify` transition point to section 3. `evidence.py` leaves red runs out of `stale` (they are meant to precede the code) and marks them "before the code" in the table. Selftest: "a red run on an earlier state is not stale", "a red run says "before the code" and shows its failure" | `references/run-flow.md` (sections 2, 3); `skills/implement/SKILL.md`; `roles/implementer.md`; `skills/run/SKILL.md`; `workflows/feature-development.md` and the sample's copy; `workflows/bug-fix.md`; `scripts/evidence.py`; `scripts/selftest.py` |
| 8 | The feature file's header cites a path that does not exist | Left on purpose: it is seeded defect D8 (not graded) | `evals/SEEDED.md`, D8; no change |
| 9 | The sample has no requirements register file | Expected: the profile names the register pattern, and `update-docs` creates the file after the first accepted run | `sample/Ledger/.orchard/profile.md` (`register`); `skills/update-docs/SKILL.md`; no change |
| 10 | A hook blocked the Write tool on a file named `report-writer.md` | Outside the skill set: the hook belongs to the agent tool's local configuration, not to this repository. Nothing in the skill set writes a file by that name during a run | No change |

## Not done

- `debug` records its regression test with `--selection regression` and its experiments with `experiment-<n>`. Those
  rows still show as stale in `evidence.py stale` once the fix lands, which `debug` calls expected. Only `red-`
  records are exempt for now; whether `regression` should be is left for the next bug-fix run to show.
- The new rules were proved by the self-tests on a copy of the sample, not yet by a full `run` on the sample.

## P4 adoption gaps

Gaps found when the skill set was adopted in two real projects. Script changes are proved by `scripts/selftest.py`
on a copy of `sample/Ledger` (plus a small Xcode-project fixture it builds for `discover.sh`); the case names are quoted.

| # | Gap | What was done | Where |
| --- | --- | --- | --- |
| 1 | A project with no Gherkin knowledge base: `knowledge_base`, `knowledge_base_check` and `tag_policy_untested` were required with no defined "none", and `verify`/`update-docs` would run "none" as a command | One definition in the template's note under "Knowledge base": Gherkin or a Markdown suite (checked by script), another format (`knowledge_base_check` is `by a person: …`, recorded "not run: checked by a person"), or `none` (then `knowledge_base_check` and `tag_policy_untested` are `n/a`, `register` is `none`, `locked_globs` may be `none`). `profile_check.py check` accepts `none`/`n/a` for those three keys only when `knowledge_base` is `none`, wants `n/a` for the first two then, and exits 2 otherwise. Each skill says what it does: `plan` keeps scenarios only in the plan; `verify` records the scenario check and the lock as not run with the reason; `update-docs` writes nothing and says so; `run` skips `lock_check.py snapshot` and records why (run-flow 1.4); `handoff` lists both under Not run and reads scenarios from the plan; `adopt` proposes the form for the developer to state; `debug` notes "none". Both workflows' `Plan → Implement` accepts a recorded "lock covers nothing". Selftest: "knowledge_base none with n/a and none -> exit 0", "n/a or none while knowledge_base is set -> exit 2", "a command while knowledge_base is none -> exit 2" | `templates/project-profile.md`; `scripts/profile_check.py`; `skills/plan`, `verify`, `update-docs`, `run`, `handoff`, `adopt`, `debug`; `references/run-flow.md`; `workflows/feature-development.md` and the sample's copy; `workflows/bug-fix.md`; `templates/plan.md`; `docs/terms.md` (Knowledge base); `scripts/selftest.py` |
| 1 | Markdown-suite knowledge base | `gate_check.py` reads a `.md` file as a suite: each heading or table row carrying an id that matches `--id-pattern` is a scenario, its tags the @words on the line; fenced code is skipped; a suite with no such line fails. Register and `--report` modes work on it unchanged. Selftest: "a Markdown suite -> scenarios from table rows and headings with an id, code blocks skipped", "a Markdown suite with no id -> exit 1" | `scripts/gate_check.py` (`markdown_scenarios`); `references/scenario-register.md` section 3; `scripts/selftest.py` |
| 2 | `workspace` named as a profile key in both workflows' Inputs, but absent from the template | `workspace` (optional) added under Platform. The sample's `feature-development.md` is again identical to core | `templates/project-profile.md`; `sample/Ledger/.orchard/workflows/feature-development.md` |
| 3a | `discover.sh` suggested the alphabetically first scheme as the test scheme | The test command shows `-scheme <scheme>`; all schemes are listed, with those that look like test schemes (name contains Test) and app schemes (named as the project or workspace); the choice is left to the developer. Selftest: "Xcode project -> lists every scheme, picks none; …" (a stand-in `xcodebuild` on `PATH`) | `scripts/discover.sh`; `scripts/selftest.py` (`discover_fixture`) |
| 3b | Test files counted only in the first test folder | Every folder named `Test` or ending in `Tests` (so `UITests` too), at any depth outside build output, is listed and counted; a file under nested folders counts once. Same selftest case: "Test folders (3)", XCTest 2, Swift Testing 1, UI tests 1 | `scripts/discover.sh` (`count`, Tests section) |
| 3c | An empty "SwiftLint custom rules:" line | The config is listed; the custom-rules line only when there are some. Same selftest case: output has no "SwiftLint custom rules" | `scripts/discover.sh` |
| 3d | Guides an `AGENTS.md` links to under `docs/`, and `.cursor/rules`, were not listed | Both listed under guides; a link to a missing file is not. Same selftest case: "`docs/testing.md` (linked from `AGENTS.md`)", "`.cursor/rules/swift.mdc` (Cursor rule)", no `docs/missing.md` | `scripts/discover.sh` |
| 4 | A source written `(file:x)` read `)` as part of the path | The path stops at whitespace, `#`, `;`, `,`, `|`, a backtick, a bracket, a parenthesis or a quote, and never ends in `.` or `:`. The accepted forms are in the template's header comment. Selftest: "a source in parentheses -> the ")" is not part of the path", "the parenthesised source is stamped and current" | `scripts/profile_check.py` (`SOURCE`); `templates/project-profile.md` |
| 5a | `adopt` did not say the outcome when the check exits 2 with answers pending | Step 6 stops there with the profile `draft`; step 10 finishes with `--outcome blocked` and the pending keys | `skills/adopt/SKILL.md` |
| 5b | Appending to `.git/info/exclude` failed when `.git/info/` was missing | Step 7 resolves the file with `git rev-parse --git-path info/exclude` and runs `mkdir -p` on its folder first; `plan` step 10 points there instead of repeating it | `skills/adopt/SKILL.md`; `skills/plan/SKILL.md` |
| 5c | Review rules without a severity in the guides | The severity is taken from the definitions in `references/review-checklist.md` part D and marked "to confirm" | `skills/adopt/SKILL.md`, step 8 |
| 6 | `profile_check.py get` returned the whole cell, prose included | The template defines a command value as the first code span of its cell when it has one; `get` prints that span, else the cell. The sample's `knowledge_base_check` now puts its command in backticks. Selftest: "a command cell with a note -> its code span only" | `scripts/profile_check.py` (`cmd_get`); `templates/project-profile.md`; `sample/Ledger/.orchard/profile.md`; `scripts/selftest.py` |

Not done: the `none` and Markdown-suite paths are proved by the self-tests on a copy of the sample and a fixture, not
yet by a full `run` on a project that has no knowledge base.

## Owner decision, 2026-11-26: Gherkin required

The owner decided that Gherkin scenario files are required in every project: they are the single source of truth
between tech and product. A project that keeps its scenarios only in plans, in a Markdown suite or in a format a person
checks has no shared, testable record of agreed behaviour, so the optional forms added by gap 1 of "P4 adoption gaps"
were removed.

- Removed: `knowledge_base: none` with its `n/a` and `none` values for `knowledge_base_check`, `tag_policy_untested`,
  `register` and `locked_globs`; the `by a person: …` form of `knowledge_base_check`; the Markdown-suite reader of
  `gate_check.py` (`markdown_scenarios`); every skill, reference and workflow branch for them, including the
  "lock covers nothing" exit from `Plan → Implement`.
- Now: `knowledge_base` (R) is a folder or glob of Gherkin `.feature` files; `knowledge_base_check` (R) and
  `tag_policy_untested` (R) have no `none`/`n/a` form; `locked_globs` always includes the knowledge base.
  `profile_check.py check` reports `none` or `n/a` in any of these four keys as a missing required key (exit 2).
  A project with no feature files yet names the folder where they will live (it may be empty at adoption); the first
  `plan` drafts scenarios for the feature it touches (`--draft` mode) and `update-docs` writes them after acceptance.
  `adopt` proposes that folder and never offers `none`.
- Kept from the P4 change: the `workspace` key, the `discover.sh` fixes (3a-3d), source parsing (4), the `get` code
  span (6), and `adopt`'s outcome, exclude-file and severity steps (5a-5c).
- Selftest: removed "knowledge_base none with n/a and none -> exit 0", "n/a or none while knowledge_base is set ->
  exit 2", "a command while knowledge_base is none -> exit 2", "a Markdown suite -> …" and "a Markdown suite with no
  id -> exit 1"; added "knowledge_base none -> exit 2, reported as a missing required key".

Files changed: `templates/project-profile.md`; `templates/plan.md`; `scripts/profile_check.py`;
`scripts/gate_check.py`; `scripts/selftest.py`; `skills/adopt`, `plan`, `update-docs`, `verify`, `handoff`, `run`,
`debug` (`SKILL.md`); `references/run-flow.md`; `references/scenario-register.md`; `workflows/feature-development.md`
and `sample/Ledger/.orchard/workflows/feature-development.md` (identical); `workflows/bug-fix.md`; `docs/terms.md`
(Knowledge base).

Not done: `lock_check.py snapshot` exits 2 when no file matches the globs, so a first run whose knowledge-base folder
is still empty stops at the lock step (run-flow 1.4). Deciding whether an empty folder is a valid lock (verify would
still catch a file added to it) is left to the owner.

## Audit changes applied (report and evals)

Owner-approved rows 7, 8 and 11 of the plan audit, plus the owner's answer on the pull-request body.

- **Row 7, one route for a ticket criterion.** The separate "Acceptance criteria" table is gone from
  `templates/test-report.md` and from `handoff`. A ticket criterion reaches the report only through a scenario (and
  so that scenario's evidence) or through the plan's stated reason for none. The `led-7` test report fixture already
  had no criteria table; the `handoff-ledger` quality grader now fails a report that adds one.
- **Row 8, a script computes the verdict.** New `scripts/verdict.py <evidence.jsonl> <plan> [--reviews <dir or
  file>] [--ended-early <reason>] [--root R]` prints `Ready to accept`, `Not ready` or `Blocked`, the reasons and the
  gaps. Ready needs a passing record on the current state for every delivered scenario, no required check failed or
  stale, and no open Blocker, Risk, High or Medium finding in the latest review (labels from
  `references/review-checklist.md` part D, read from the findings table or the part E headings). A required check
  still failing once the plan's rounds are used up gives Blocked. A missing screenshot or recording is a gap and
  never changes the verdict. Exit codes: 0 Ready, 1 Not ready, 3 Blocked, 2 no git and no `--root`, 64 usage.
  `handoff` quotes it and never writes its own; `roles/report-writer.md` and the Strict row of
  `docs/workflow-model.md` now say Strict is for risk and long runs, and the verdict does not depend on who writes
  the report. Ten selftest cases cover it.
- **Owner answer, the pull-request body carries the evidence.** `handoff` drafts the body from the profile's PR
  template, with the report's top part, the verdict and links to or embeds of every screenshot and recording; the
  plan, report and evidence files stay out of git.
- **Row 11, evals gate on their own graders.** `adapters/claude-code/eval.sh` prints and saves `summary.txt`: per
  case passed, failed or "not run (environment)", with the with/without delta as a signal only. Exit 0 when no case
  failed. Replayed on the first smoke results (no new run): 6 passed, 7 failed, 3 not run (environment)
  (`debug-ledger-latest-crash`, `run-led-refund`, `workflow-bug-fix-refund`). `evals/README.md` states the bar.

Evidence: `python3 -I scripts/selftest.py` all passing with the verdict cases; `python3 -I scripts/leak_check.py`
clean; `verdict.py` run on the `handoff-ledger` fixture gives Not ready (the Risk finding at
`TransactionStoreTests.swift:18` is open; Risk blocks whatever its severity). The eval suite was not run (cost).

Left for other owners (outside this change's files): `references/run-flow.md` section 9 should name `verdict.py`
for the report's verdict; `docs/skill-set-plan.md` sections 6, 7 and 11 still describe the criteria table, the
Strict level as the verdict's guard and the with/without bar; the "Documenter" row of `docs/workflow-model.md` still
reads "Only at Strict, for the report" (true, but no longer tied to the verdict). The `led-refund` review fixture
labels finding 2 "Risk · Low" with state "open, for the developer", which part D counts as blocking.

## Audit changes applied (profile and rules)

Owner decisions applied: Gherkin `.feature` files stay required in every project; `retro` stays per developer (one
run log, never pooled). Rows refer to the plan audit.

| # | Item | What changed | Where |
| --- | --- | --- | --- |
| 1 | Skills stop only on keys they read (row 1) | Each profile key has a "Read by" cell naming the skills that read it, the one home of that mapping. `profile_check.py check --skill <name>` reads it from the template at run time and reports only that skill's keys: exit 2 for a missing required key it reads, exit 3 for a changed or untracked source of a key it reads; an unknown skill exits 64. Without `--skill` every key is checked. `plan` and `run` are listed on every required key, so theirs is the full check. A skill called alone opens with `check --skill <name>`; `adopt` runs the full check | `templates/project-profile.md`; `scripts/profile_check.py`; `AGENTS.md` "A skill called alone"; `skills/adopt`; `docs/scopes.md` |
| 2 | Core defaults (row 2) | `tag_policy_untested` is optional; the core default, `@blocked:<reason>` only, lives in `references/scenario-register.md` ("Untested tags"), and a project may override it. `ticket_is_basis` is gone: `source_ranking` decides whether a ticket alone is a basis (`ticket alone is a basis`); the default (not a basis) lives in `references/scenario-gate.md` section 1 | `templates/project-profile.md`; `references/scenario-register.md`; `references/scenario-gate.md`; `skills/plan`; `skills/update-docs`; `scripts/profile_check.py` docstring; `sample/Ledger/.orchard/profile.md` (row removed) |
| 3 | Wider default lock (row 4), empty-folder lock | Default `locked_globs`, written once in the template: knowledge base and register, lint configuration, CI workflow files, test plans and coverage settings, dependency manifests, `.orchard/**` without `.orchard/runs/**`. `lock_check.py snapshot`: a glob starting with `!` removes what it matches; a glob whose folder exists but matches nothing locks an empty set (a file appearing later breaks the lock); a glob whose folder is missing is listed; exit 2 only when no glob's folder exists. The run quotes each glob. The sample's `locked_globs` is the default, in one code span | `templates/project-profile.md`; `scripts/lock_check.py`; `references/run-flow.md` step 4; `docs/boundaries.md` "Locked files"; `skills/adopt` step 3; `sample/Ledger/.orchard/profile.md` |
| 4 | Tracked sources only (row 5) | A `file:` source must be a file git tracks (`git ls-files --error-unmatch`); a value read from an untracked or ignored file is `stated: <who> <date>` with the file named in a note. `profile_check.py stamp` leaves such a source unstamped and exits 3; `check` lists it and exits 3 | `templates/project-profile.md`; `scripts/profile_check.py`; `skills/adopt` steps 3 and 5; `docs/scopes.md`; `AGENTS.md` |
| 5 | Ask once (row 6) | "Revise until no hidden assumption is left" removed. Questions are asked once, together, each with options and one recommended; a second round only for a question that depends on a first-round answer | `skills/plan` step 11 |
| 6 | Isolation figures (row 9) | No core file claimed Shared is cheapest outright; the isolation table now has a "Tokens and time: Not measured" row and points to the one-bug result. The terms row no longer says the table gives the level's cost | `docs/workflow-model.md` "Isolation levels"; `docs/terms.md` "Isolation level" |
| 7 | Backend without clean-up (owner answer) | Without `backend_cleanup`, no real-backend call or integration test that creates data runs; it is recorded "not run: no clean-up method in the profile". Home: rule 3 of the four real-backend rules. `verify` points there instead of restating the rules | `references/test-strategy.md` section 5; `skills/verify` steps 8 and 10; `templates/project-profile.md` (`backend_cleanup` row) |
| 8 | Integration tests not a default every run (owner answer) | Integration tests run once per run only on the endpoints the plan names, never as a blanket default. The plan template has an "Integration tests" line; `plan` step 8 names the endpoints | `references/test-strategy.md` section 1; `skills/verify` step 8; `references/run-flow.md` step 6 of the rounds; `templates/plan.md` section 8; `skills/plan` step 8 |
| 9 | Codex and Cursor adapters | Nothing changed; they stay "untested" | none |

Evidence: `python3 -I scripts/selftest.py` all passing, with new cases: a profile missing `build` passes
`check --skill review` and fails `check --skill run` (and the full check); an unknown skill exits 64; an untracked
`file:` source makes `stamp` and `check` exit 3; a glob whose folder exists but matches nothing snapshots as an empty
set and a file appearing there breaks the lock; `.orchard/**` with `!.orchard/runs/**` ignores a new run file and
catches a changed `.orchard` file; no glob's folder existing exits 2. `python3 -I scripts/leak_check.py` clean. The
selftest's README hash is no longer hard-coded, since the sample README changed in a parallel change.

Not done here: `profile_check.py check sample/Ledger/.orchard/profile.md` in this repository exits 3 until the
sample's files are tracked by git (the repository has one commit and `sample/` is untracked); inside the selftest's
git copy it passes. `evals/adopt-ledger/graders/profile-quality.md` still lists `tag_policy_untested` among the
required keys, and `docs/skill-set-plan.md` sections 4, 5, 6 and 7 still carry the old wording (both outside this
change's files). `pr_check` is required, but no skill reads it; it is listed only under `plan` and `run`.

## Cleanup after audit changes

Small consistency fixes left over from the two sections above.

- **`handoff-ledger` fixture.** Finding 2 of `evals/fixtures/led-refund-review.md` (the `sleep(1)` in the new test)
  is now a `NOTE` with no severity: part D gives a NOTE no severity, and a Risk blocks whatever its severity. The
  quality grader and the case's expected outcome now carry two NOTEs for the developer, and item 7 reads the verdict
  as Not ready because the unit tests are stale on the final change. `verdict.py` on the scaffolded fixture prints
  Not ready, exit 1, with the three stale reasons and no finding reason.
- **`verify`.** The "sample has no app target" gotcha is gone (the sample has `App/LedgerApp.xcodeproj` with a
  UI-test target). `--final` now records `pr_check` once, last, through `evidence.py` (check `pr_check`, selection
  `all`). `templates/project-profile.md` lists `verify` under "Read by" for `pr_check`.
- **Sample profile.** The `tag_policy_untested` row only restated the core default, so it is removed.
- **Verdict source.** `references/run-flow.md` section 9 names `scripts/verdict.py` as the verdict's source; the
  Documenter row of `docs/workflow-model.md` says the report quotes that verdict at every level.
- **`adopt-ledger` grader.** `tag_policy_untested` is no longer listed among the required keys (it is optional).
- **Straggler grep** over the repository (without `docs/skill-set-plan.md`): `ticket_is_basis` appears only in this
  log; "acceptance criteria" only in term definitions, the source ranking, the sample ticket and statements that
  there is no criteria table; no "Ready to accept" rule requires a picture; "by a person" only in the Validation
  term and this log.

Evidence: `python3 -I scripts/selftest.py` all passing (106 checks); `python3 -I scripts/leak_check.py` clean.

Not done here: part D of `references/review-checklist.md` marks Low and NIT "Blocks: No", yet every typed finding
that can carry a severity (Blocker, Risk) blocks, so a non-blocking Low finding cannot be written; the test-report
template and `handoff` still name "Low finding" among the items for the developer. `evals/fixtures/led-7-test-report.md`
still says "a package has no app target", and `evals/adopt-ledger/graders/profile-quality.md` still states "no app
target" and wants `scheme` n/a, although the scaffold now copies `App/LedgerApp.xcodeproj`. The eval suite was not
run.
