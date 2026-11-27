---
type: llm
weight: 4
focus:
  source: file
  path: .orchard/profile.md
---
You are shown a draft project profile written by discovery on a small Swift package. Facts in the repository:
README.md says build and test with `swift build` and `swift test`; Package.swift declares a SwiftPM package with
a macOS and an iOS platform, plus a small iOS app in App/LedgerApp.xcodeproj with a UI-test target; scenario files are docs/features/*.feature with id tags like
@TS_LED_001; specs sit in docs/specs/, design notes in docs/design/, tickets in docs/tickets/; .gitignore ignores
.orchard/runs/; .orchard/review-rules.md exists. There is no lint configuration, no CI file, no pull-request
template and no backend environment anywhere. Nobody has stated anything yet.
PASS only if ALL hold:
1. Its status is a draft, not confirmed.
2. build is `swift build` and test.unit runs `swift test` (a filter option is fine), each with a file source
   (README.md or Package.swift) written as `file:<path>#<hex>`.
3. build_system names SwiftPM (Package.swift) and the app project (App/LedgerApp.xcodeproj), each with its file as source; scheme is LedgerApp (read from the project or its shared scheme) or missing, never an invented scheme.
4. knowledge_base points at docs/features (folder, glob or file) with a file source.
5. No value is invented: a key that no file states (for example test.integration,
   backend_environments, device_policy, workers) is `missing` or plainly marked as a proposal for the developer
   to confirm. A `stated:` source naming a person who stated nothing is an invented value.
6. Every required key appears with a value or `missing`: knowledge_base, knowledge_base_check, plans_dir,
   reports_dir, locked_globs, build, test.unit, lint, pr_check. An optional key (for example tag_policy_untested)
   may be left out.
FAIL otherwise. Wording and table layout do not matter.
