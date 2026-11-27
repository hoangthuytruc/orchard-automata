# Project profile: Ledger (sample)

Status: confirmed 2026-11-26 by the skill-set owner (sample project)

## Knowledge base

| Key | Value | Source |
| --- | --- | --- |
| knowledge_base | docs/features/*.feature | stated: owner 2026-11-26 |
| knowledge_base_check | `python3 -I "$ORCHARD/scripts/gate_check.py" docs/features/Purchases.feature --id-pattern '@TS_LED_\d{3}'` ($ORCHARD: the skill set root) | stated: owner 2026-11-26 |
| scenario_id_pattern | `@TS_LED_\d{3}` | stated: owner 2026-11-26 |
| register | docs/features/<Feature>.requirements.md | stated: owner 2026-11-26 |

## Task folders

| Key | Value | Source |
| --- | --- | --- |
| plans_dir | .orchard/runs/plans | stated: owner 2026-11-26 |
| reports_dir | .orchard/runs/reports | stated: owner 2026-11-26 |
| locked_globs | `docs/features/*.feature docs/features/*.requirements.md .swiftlint.yml .swiftformat .swift-format .github/workflows/* .gitlab-ci.yml .circleci/* bitrise.yml Jenkinsfile fastlane/Fastfile **/*.xctestplan **/xcshareddata/xcschemes/*.xcscheme codecov.yml .codecov.yml Package.swift Package.resolved **/xcshareddata/swiftpm/Package.resolved Podfile Podfile.lock Cartfile Cartfile.resolved project.yml Project.swift Tuist/Package.swift .orchard/** !.orchard/runs/**` (the core default) | stated: owner 2026-11-26 |

## Commands

| Key | Value | Source |
| --- | --- | --- |
| build | swift build | file:README.md#9640b755 |
| test.unit | swift test --filter <TestClass or TestClass/method> | file:README.md#9640b755 |
| test.behaviour | `xcodebuild test -project App/LedgerApp.xcodeproj -scheme LedgerApp -destination 'platform=iOS Simulator,id=<udid>' -only-testing:LedgerAppUITests/<TestClass or TestClass/method>` (through the UI, on the simulator of `device_policy`); in-process: swift test --filter <TestClass> | file:README.md#9640b755; file:App/LedgerApp.xcodeproj/xcshareddata/xcschemes/LedgerApp.xcscheme#e8a63ab9 |
| test.visual | disabled (no snapshot test; screenshots and recordings of the app are evidence, not a visual test) | stated: sample author 2026-11-26 (owner to confirm) |
| test.integration | none (no test backend) | stated: owner 2026-11-26 |
| lint | none configured | stated: owner 2026-11-26 |
| pr_check | swift build && swift test | stated: owner 2026-11-26 |
| generate | none | file:Package.swift#860470af |
| affected_map | none (one module: every unit test is affected) | stated: owner 2026-11-26 |

## Platform

| Key | Value | Source |
| --- | --- | --- |
| build_system | Xcode project over the SwiftPM package (the app depends on the local package `Ledger`) | file:App/LedgerApp.xcodeproj/project.pbxproj#abaa329e; file:Package.swift#860470af |
| scheme | LedgerApp (builds the app, tests LedgerAppUITests) | file:App/LedgerApp.xcodeproj/xcshareddata/xcschemes/LedgerApp.xcscheme#e8a63ab9 |
| workspace | App/LedgerApp.xcodeproj | file:App/LedgerApp.xcodeproj/project.pbxproj#abaa329e |
| destination | platform=iOS Simulator,name=iPhone 17 Pro,OS=26.1 (any iOS 17.0 or later simulator; deployment target 17.0) | file:App/LedgerApp.xcodeproj/project.pbxproj#abaa329e; stated: sample author 2026-11-26 (owner to confirm) |
| device_policy | each run creates its own simulator, drives it by id and deletes it at the end: xcrun simctl create "Ledger-<run>" "iPhone 17 Pro" com.apple.CoreSimulator.SimRuntime.iOS-26-1; never a simulator another run has booted | stated: sample author 2026-11-26 (owner to confirm) |
| workers | 2 | stated: owner 2026-11-26 |

## Git

| Key | Value | Source |
| --- | --- | --- |
| base_branch | main | stated: owner 2026-11-26 |
| plan_files_excluded | yes: .orchard/runs/ is ignored | stated: owner 2026-11-26 |

## Sources

| Key | Value | Source |
| --- | --- | --- |
| source_ranking | current spec (docs/specs/purchases-v3.md) > design notes > ticket acceptance criteria > ticket comment; purchases-legacy.md is superseded | file:docs/specs/purchases-v3.md#70a2f2a5 |
| design_source | docs/design/figma-LED-7.md (frames 210:14, 210:31, 210:44) | file:docs/design/figma-LED-7.md#cd0393d9 |
| spec_source | docs/specs/ | stated: owner 2026-11-26 |
| tracker | docs/tickets/ (read-only) | stated: owner 2026-11-26 |

## Real backend

| Key | Value | Source |
| --- | --- | --- |
| backend_environments | none | stated: owner 2026-11-26 |
| backend_cleanup | n/a | stated: owner 2026-11-26 |

## Guides

| Key | Value | Source |
| --- | --- | --- |
| guides | README.md | file:README.md#9640b755 |
| review_rules | .orchard/review-rules.md | stated: owner 2026-11-26 |
| pr_template | none | stated: owner 2026-11-26 |
