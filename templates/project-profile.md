# Project profile: <project>

<!--
Copy to .orchard/profile.md in the project. `adopt` drafts it; the developer confirms it.
Every value carries a source: `file:path#sha256-prefix` (the file it was read from, hashed by scripts/profile_check.py),
or `stated: <who> <date>` when nobody wrote it down. A file source is written `file:<path>` or `file:<path>#<hash>`; it may
sit in backticks or parentheses, or among other sources separated by `;`, `,` or a space. The path ends before
whitespace, `#`, `;`, `,`, `|`, a backtick, a bracket, a parenthesis or a quote, and a trailing `.` or `:` is not part of it.
A file source must be a file git tracks (`git ls-files --error-unmatch <path>` succeeds from the project root): the
profile is shared, and a teammate's check must be able to hash the same file. A value read only from an untracked or
ignored file (a private note, a local guide) is recorded as `stated: <who> <date>`, with the file named in a note
(`stated: dev 2026-11-26 (read from untracked .local/notes.md)`). `profile_check.py stamp` and `check` reject a file
source git does not track.
A command value is the first code span of its cell (`like this`) when the cell has one; prose around it is a note.
`profile_check.py get` prints that code span, else the whole cell. Never use a file the workflow itself rewrites (the knowledge base,
a register) as a source: it changes after every accepted run and would end the next run for confirmation. A value with no source is `missing`, never guessed.
Required keys are marked (R). A key with no (R) is optional; where core has a default for it, the row names it.
"Read by" lists the skills that read the key. A skill called alone runs `profile_check.py check --skill <name>` and
stops only when a required key it reads is missing. `plan` and `run` are listed on every required key, so their check is
the full one: a plan is written for a run, and a run uses every required key through its steps. The
script reads this column from this template at run time; a profile copy may drop it.
Project facts only: no generic rule (that is core), no personal setting (that is .orchard/agents.local.md).
-->

Status: <draft | confirmed <date> by <who>>

## Knowledge base

| Key | Value | Source | Read by |
| --- | --- | --- | --- |
| knowledge_base (R) | <folder or glob of Gherkin `.feature` files, e.g. docs/features/*.feature> | | `plan`, `run`, `debug`, `update-docs` |
| knowledge_base_check (R) | <command that checks the feature files, e.g. `python3 -I "$ORCHARD/scripts/gate_check.py" <file> --id-pattern '<scenario_id_pattern>'`> | | `plan`, `run`, `verify`, `update-docs` |
| scenario_id_pattern | <regex of a scenario id tag, e.g. `@TS_[A-Z]+_\d{3}`> | | `plan`, `run`, `implement`, `verify`, `debug`, `update-docs` |
| register | <requirements register path pattern, or none> | | `plan`, `run`, `update-docs` |
| tag_policy_untested | <optional: the tags a scenario without a test may carry, when the project adds its own (a manual tag for what no test can drive). Absent: the core default in `$ORCHARD/references/scenario-register.md`> | | `plan`, `run`, `verify`, `update-docs` |

<!--
The knowledge base is required in every project: its Gherkin feature files are the single source of truth between
tech and product. `knowledge_base` and `knowledge_base_check` have no `none` or `n/a` form; `profile_check.py check`
reports such a value as a missing required key.
A project with no feature files yet names the folder where they will live; it may be empty at adoption. The first
`plan` drafts scenarios for the feature it touches (plan's draft mode), and `update-docs` writes them after acceptance.
-->

## Task folders

| Key | Value | Source | Read by |
| --- | --- | --- | --- |
| plans_dir (R) | <folder for plan files; kept out of git> | | `plan`, `run`, `verify`, `update-docs` |
| reports_dir (R) | <folder for test reports; kept out of git> | | `plan`, `run`, `verify`, `debug`, `test`, `debt`, `handoff`, `retro` |
| locked_globs (R) | <globs locked from approval to acceptance, separated by spaces, in one code span; `adopt` drafts the default below, and the project may add or remove globs> | | `plan`, `run` |

<!--
Default `locked_globs`, the one place it is written. `adopt` drafts it from what the project has; the project may add
or remove globs. A glob whose folder exists but matches no file is kept: a file that appears there later breaks the
lock. A glob starting with `!` removes what it matches.
- The knowledge base and its register: `<knowledge_base>`, `<register>`.
- Lint configuration: `.swiftlint.yml`, `.swiftformat`, `.swift-format`.
- CI workflow files: `.github/workflows/*`, `.gitlab-ci.yml`, `.circleci/*`, `bitrise.yml`, `Jenkinsfile`, `fastlane/Fastfile`.
- Test plans and coverage settings: `**/*.xctestplan`, `**/xcshareddata/xcschemes/*.xcscheme`, `codecov.yml`, `.codecov.yml`.
- Dependency manifests: `Package.swift`, `Package.resolved`, `**/xcshareddata/swiftpm/Package.resolved`, `Podfile`,
  `Podfile.lock`, `Cartfile`, `Cartfile.resolved`, and the project's dependency files (`project.yml`, `Project.swift`,
  `Tuist/Package.swift`).
- The skill set's own project files: `.orchard/**`, `!.orchard/runs/**`.
-->

## Commands

Only these commands are run. A kind of check with no command is reported as "not run: no command in the profile".

| Key | Value | Source | Read by |
| --- | --- | --- | --- |
| build (R) | <command> | | `plan`, `run`, `implement`, `verify`, `debug` |
| test.unit (R) | <command; how to scope it to suites or files> | | `plan`, `run`, `implement`, `test`, `verify`, `debug` |
| test.behaviour | <command, in-process; or through the UI with its scope option> | | `run`, `implement`, `test`, `verify`, `debug` |
| test.visual | <command, or `disabled`> | | `run`, `test`, `verify` |
| test.integration | <command and the environments it may target, or `none`> | | `run`, `verify` |
| lint (R) | <command, or `none configured`> | | `plan`, `run`, `implement`, `verify` |
| pr_check (R) | <the project's own pre-pull-request checks> | | `plan`, `run`, `verify` |
| generate | <project generation command needed before a new file is seen, or none> | | `run`, `implement` |
| affected_map | <how to map changed files to tests: a script, a module rule, or `none` (then every check runs again on the final change)> | | `run`, `verify` |

## Platform

| Key | Value | Source | Read by |
| --- | --- | --- | --- |
| build_system | <SwiftPM / Xcode project / workspace / Tuist / XcodeGen> | | none: the commands carry it |
| workspace | <.xcworkspace or .xcodeproj path the commands build, or n/a for a package> | | none: the commands carry it |
| scheme | <scheme, or n/a for a package> | | none: the commands carry it |
| destination | <simulator name and OS, or `macOS` for a package> | | none: the commands carry it |
| device_policy | <how to get a simulator of one's own when another run holds one> | | `run`, `implement`, `verify`, `debug` |
| workers | <parallel worker limit> | | `run`, `verify` |

## Git

| Key | Value | Source | Read by |
| --- | --- | --- | --- |
| base_branch (R) | <branch work is cut from; confirmed again at plan approval> | | `plan`, `run` |
| plan_files_excluded | <yes: plans_dir and reports_dir are in .git/info/exclude or .gitignore> | | `plan`, `adopt` |

## Sources

| Key | Value | Source | Read by |
| --- | --- | --- | --- |
| source_ranking (R) | <ordered list, e.g. current spec > design (reference version) > ticket acceptance criteria > ticket comment. It also decides whether a ticket alone is a basis, by saying `ticket alone is a basis`; without it, the core default in `$ORCHARD/references/scenario-gate.md`, section 1, applies> | | `plan`, `run` |
| design_source (R) | <tool and how the reference version is pinned, or `none`> | | `plan`, `run`, `verify` |
| spec_source | <where specs live and how a version is recorded> | | `plan`, `run` |
| tracker | <where tickets live; read-only> | | `plan`, `run`, `update-docs` |

## Real backend

| Key | Value | Source | Read by |
| --- | --- | --- | --- |
| backend_environments (R) | <test environments the app may call, or `none`. Never production> | | `plan`, `run`, `verify` |
| backend_cleanup | <how data created by a check is removed; without it, no real-backend call or integration test that creates data runs (`$ORCHARD/references/test-strategy.md`, section 5)> | | `run`, `verify` |

## Guides

| Key | Value | Source | Read by |
| --- | --- | --- | --- |
| guides | <CLAUDE.md, AGENTS.md, nested guides, testing guides: each path> | | `plan`, `run`, `implement`, `test`, `debug`, `debt`, `review` |
| review_rules | `.orchard/review-rules.md` | | `run`, `implement`, `review` |
| pr_template | <path, or none> | | `run`, `review`, `handoff` |
