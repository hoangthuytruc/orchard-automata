#!/usr/bin/env bash
# Prints what an iOS repository looks like, so `adopt` can draft the project profile and a skill can adapt to it:
# Orchard files, build system, test and lint commands, agent guides, Swift settings, test frameworks, CI, PR template.
# Read-only; no network. Output is Markdown; every line is a lead to confirm, not a profile value.
#
#   discover.sh [repo-root]        defaults to the git root of the current directory
#
# Exit codes: 0 printed; 64 the root cannot be entered.
set -u

ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$ROOT" || { echo "cannot cd to $ROOT" >&2; exit 64; }

have() { [ -e "$1" ]; }
first() { for f in "$@"; do [ -e "$f" ] && { echo "$f"; return; }; done; }
# count PATTERN [PATH...]: Swift files under the paths that match; a file under two given paths counts once.
count() { local pattern="$1"; shift; [ $# -eq 0 ] && set -- .; grep -rl --exclude-dir={build,Derived,.build,node_modules,.git,DerivedData,Pods,Carthage,.claude,reports} --include='*.swift' -e "$pattern" "$@" 2>/dev/null | sed 's|//*|/|g' | grep -v -E '/(\.build|build|Derived|DerivedData|Pods|Carthage|node_modules|\.claude/worktrees)/' | sort -u | wc -l | tr -d ' '; }

echo "# Project discovery"
echo
echo "- Root: \`$ROOT\`"
default_branch=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|origin/||')
xcode=$(xcodebuild -version 2>/dev/null | head -1)
echo "- Default branch: \`${default_branch:-unknown}\`"
echo "- Current branch: \`$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)\`"
echo "- Xcode: \`${xcode:-not found}\`"
echo

echo "## Orchard files"
if [ -d .orchard ]; then
  while IFS= read -r f; do echo "- \`$f\`"; done < <(find .orchard -type f -not -path '.orchard/runs/*' 2>/dev/null | sort)
  have .orchard/profile.md && echo "- Profile status: $(grep -m1 -E '^Status:' .orchard/profile.md | sed 's/^Status: *//')"
  have .orchard/agents.local.md && echo "- Personal settings present (\`.orchard/agents.local.md\`): keep them out of git"
else
  echo "- none: no \`.orchard/\` folder yet (\`adopt\` drafts \`.orchard/profile.md\`)"
fi
echo

echo "## Agent and contributor guides (read these before acting; they override core defaults)"
found=0
for f in CLAUDE.md AGENTS.md .claude/CLAUDE.md CONTRIBUTING.md README.md; do have "$f" && { echo "- \`$f\`"; found=1; }; done
while IFS= read -r f; do echo "- \`$f\`"; found=1; done < <(find . -mindepth 2 -maxdepth 3 \( -name AGENTS.md -o -name CLAUDE.md \) -not -path '*/node_modules/*' -not -path '*/.claude/worktrees/*' 2>/dev/null | sed 's|^\./||' | sort)
# Guides under docs/ that an AGENTS.md links to, read relative to that AGENTS.md's folder.
linked=$(find . -maxdepth 3 -name AGENTS.md -not -path '*/node_modules/*' -not -path '*/.claude/worktrees/*' 2>/dev/null | sed 's|^\./||' | sort | while IFS= read -r agents; do
  dir=$(dirname "$agents")
  grep -oE '\]\((\./)?docs/[^)# ]+' "$agents" 2>/dev/null | sed -E 's/^\]\((\.\/)?//' | while IFS= read -r link; do
    target="$dir/$link"; target="${target#./}"
    [ -e "$target" ] && echo "- \`$target\` (linked from \`$agents\`)"
  done
done | sort -u)
[ -n "$linked" ] && { echo "$linked"; found=1; }
if [ -d .cursor/rules ]; then
  while IFS= read -r f; do echo "- \`$f\` (Cursor rule)"; found=1; done < <(find .cursor/rules -type f 2>/dev/null | sort)
fi
[ $found = 0 ] && echo "- none"
echo

echo "## Build system"
bs=""
have Project.swift && bs="$bs Tuist(Project.swift)"
have Tuist.swift && bs="$bs Tuist.swift"
have Workspace.swift && bs="$bs Tuist(Workspace.swift)"
have project.yml && bs="$bs XcodeGen(project.yml)"
have Package.swift && bs="$bs SwiftPM(Package.swift)"
ls -d *.xcworkspace >/dev/null 2>&1 && bs="$bs $(ls -d *.xcworkspace | head -1)"
ls -d *.xcodeproj >/dev/null 2>&1 && bs="$bs $(ls -d *.xcodeproj | head -1)"
have Podfile && bs="$bs CocoaPods"
have Cartfile && bs="$bs Carthage"
have mise.toml && bs="$bs mise.toml"
have .tool-versions && bs="$bs .tool-versions"
echo "- Detected:${bs:- none}"
if have Makefile; then
  echo "- Makefile targets: $(grep -E '^[a-zA-Z0-9_.-]+:' Makefile | cut -d: -f1 | grep -v -E '^\.PHONY' | sort -u | tr '\n' ' ')"
fi
have fastlane/Fastfile && echo "- fastlane lanes: $(grep -E '^\s*lane :' fastlane/Fastfile | sed -E 's/.*lane :([a-z_]+).*/\1/' | tr '\n' ' ')"
echo

echo "## Commands to use (in this order of preference)"
if have Makefile && grep -qE '^test:' Makefile; then
  echo "- Tests: \`make test\` (plus the parameters the Makefile or an AGENTS.md documents). Never hand-roll xcodebuild when a make target exists."
elif have Package.swift && ! ls -d *.xcodeproj >/dev/null 2>&1; then
  echo "- Tests: \`swift test\`"
else
  echo "- Tests: \`xcodebuild test -scheme <scheme> -destination 'platform=iOS Simulator,name=<device>'\` (no make target found; the developer chooses the scheme from the list below)"
fi
if ls -d *.xcworkspace >/dev/null 2>&1 || ls -d *.xcodeproj >/dev/null 2>&1; then
  xcodebuild -list -json 2>/dev/null | python3 -I -c '
import json, sys
try:
    data = json.load(sys.stdin)
except ValueError:
    sys.exit(0)
kind = "workspace" if "workspace" in data else "project"
info = data.get(kind) or {}
schemes = info.get("schemes") or []
name = info.get("name", "")
if not schemes:
    sys.exit(0)
tests = [s for s in schemes if "test" in s.lower()]
apps = [s for s in schemes if s not in tests and s == name]
quote = lambda names: " ".join("`%s`" % s for s in names) or "none"
print("- Schemes (%s %s): %s" % (kind, name or "?", quote(schemes)))
print("  - look like test schemes (name contains Test): %s" % quote(tests))
print("  - look like app schemes (named as the %s): %s" % (kind, quote(apps)))
print("  - which one runs the tests is the developer\x27s choice; nothing here picks one")
'
fi
if have Makefile && grep -qE '^lint:' Makefile; then echo "- Lint: \`make lint\`"; elif have .swiftlint.yml; then echo "- Lint: \`swiftlint\` (config .swiftlint.yml)"; else echo "- Lint: none configured"; fi
have .swiftformat && echo "- Format: \`swiftformat\` (config .swiftformat)"
if have Makefile && grep -qE '^generate:' Makefile; then echo "- Project generation: \`make generate\`"; elif have Project.swift; then echo "- Project generation: \`tuist generate\`"; elif have project.yml; then echo "- Project generation: \`xcodegen generate\`"; fi
echo

echo "## Swift settings"
tools=$(grep -h -m1 -E '^// swift-tools-version' Package.swift 2>/dev/null | sed -E 's|// swift-tools-version: *||')
[ -n "$tools" ] && echo "- swift-tools-version: $tools"
sv=$(grep -rh --exclude-dir={build,Derived,.build,node_modules,.git,DerivedData,Pods,Carthage,.claude,reports} -E 'SWIFT_VERSION|swiftVersion|swiftLanguageVersion|swiftLanguageMode' --include='*.xcconfig' --include='*.swift' --include='*.yml' --include='*.pbxproj' . 2>/dev/null | grep -v -E '/(build|Derived|\.build)/' | head -3 | sed 's/^[[:space:]]*//' | sort -u)
[ -n "$sv" ] && echo "- Swift version settings:" && echo "$sv" | sed 's/^/  - `/; s/$/`/'
sc=$(grep -rh --exclude-dir={build,Derived,.build,node_modules,.git,DerivedData,Pods,Carthage,.claude,reports} -E 'SWIFT_STRICT_CONCURRENCY|StrictConcurrency|swiftSettings' --include='*.xcconfig' --include='*.swift' --include='*.pbxproj' . 2>/dev/null | grep -v -E '/(build|Derived|\.build)/' | head -3 | sed 's/^[[:space:]]*//' | sort -u)
[ -n "$sc" ] && echo "- Strict concurrency settings:" && echo "$sc" | sed 's/^/  - `/; s/$/`/'
dt=$(grep -rh --exclude-dir={build,Derived,.build,node_modules,.git,DerivedData,Pods,Carthage,.claude,reports} -E 'IPHONEOS_DEPLOYMENT_TARGET|deploymentTargets|\.iOS\(' --include='*.xcconfig' --include='Project.swift' --include='Package.swift' --include='project.yml' . 2>/dev/null | grep -v -E '/(build|Derived|\.build)/' | head -2 | sed 's/^[[:space:]]*//')
[ -n "$dt" ] && echo "- Deployment target:" && echo "$dt" | sed 's/^/  - `/; s/$/`/'
echo

echo "## Source layout (top two levels)"
for d in Sources Source App Modules Packages Features Targets; do
  [ -d "$d" ] && find "$d" -maxdepth 2 -type d -not -path '*/.*' | sort | sed 's/^/- /' | head -60
done
echo

echo "## Tests"
# Every folder named Test, or ending in Tests (UITests included), at any depth outside build output.
testdirs=()
while IFS= read -r d; do testdirs+=("$d"); done < <(find . -type d \( -name Test -o -name '*Tests' \) -not -path '*/.*' -not -path '*/build/*' -not -path '*/Derived*' -not -path '*/Pods/*' -not -path '*/Carthage/*' -not -path '*/node_modules/*' 2>/dev/null | sed 's|^\./||' | sort)
if [ ${#testdirs[@]} -eq 0 ]; then
  echo "- Test folders: none found; the counts below are over the whole repository"
  testdirs=(.)
else
  echo "- Test folders (${#testdirs[@]}): $(printf '%s ' "${testdirs[@]}")"
fi
echo "- Files importing Testing (Swift Testing): $(count '^import Testing' "${testdirs[@]}")"
echo "- Files importing XCTest: $(count '^import XCTest' "${testdirs[@]}")"
echo "- Files using XCUIApplication (UI tests): $(count 'XCUIApplication' "${testdirs[@]}")"
echo "- Snapshot testing files (assertSnapshot/SnapshotTesting): $(count 'assertSnapshot\|SnapshotTesting' "${testdirs[@]}")"
echo "- Files with sleep in tests (Task.sleep/usleep/sleep(): $(count 'Task.sleep\|usleep(\| sleep(' "${testdirs[@]}")"
have Tests/scope.yml && echo "- Change-to-test map: \`Tests/scope.yml\`"
ls TestPlans/*.xctestplan >/dev/null 2>&1 && echo "- Test plans: $(ls TestPlans/*.xctestplan | tr '\n' ' ')"
ls *.xctestplan **/*.xctestplan >/dev/null 2>&1 && echo "- Test plans: $(ls *.xctestplan **/*.xctestplan 2>/dev/null | tr '\n' ' ')"
echo

echo "## Quality gates and CI"
if have .swiftlint.yml; then
  echo "- SwiftLint config: \`.swiftlint.yml\`"
  rules=$(awk '/^custom_rules:/{f=1;next} f&&/^[^ ]/{f=0} f&&/^  [a-z_]+:$/{gsub(/[: ]/,"");printf "%s ",$0}' .swiftlint.yml)
  [ -n "$rules" ] && echo "- SwiftLint custom rules: $rules"
fi
ls .github/workflows/*.yml >/dev/null 2>&1 && echo "- GitHub workflows: $(ls .github/workflows/*.yml | xargs -n1 basename | tr '\n' ' ')"
have .github/pull_request_template.md && echo "- PR template: \`.github/pull_request_template.md\`"
have commitlint.config.js && echo "- Commit convention: commitlint (Conventional Commits)"
have .husky && echo "- Git hooks: husky ($(ls .husky | grep -v '^_$' | tr '\n' ' '))"
have sonar-project.properties && echo "- SonarQube configured"
have .periphery.yml && echo "- Periphery (dead code) configured"
echo

echo "## Source hygiene counters (whole repo, Swift files; for triage, not verdicts)"
src=$(first Sources Source App .)
echo "- Force unwrap or try!: $(grep -rn --exclude-dir={build,Derived,.build,node_modules,.git,DerivedData,Pods,Carthage,.claude,reports} --include='*.swift' -E '[a-zA-Z0-9_)\]]![^=]|try!' "$src" 2>/dev/null | grep -v -E '/(build|Derived|\.build|Tests?)/|!= ' | wc -l | tr -d ' ') lines"
echo "- TODO/FIXME/HACK: $(grep -rn --exclude-dir={build,Derived,.build,node_modules,.git,DerivedData,Pods,Carthage,.claude,reports} --include='*.swift' -E 'TODO|FIXME|HACK' "$src" 2>/dev/null | grep -v -E '/(build|Derived|\.build)/' | wc -l | tr -d ' ') lines"
echo "- @available deprecated markers: $(grep -rn --exclude-dir={build,Derived,.build,node_modules,.git,DerivedData,Pods,Carthage,.claude,reports} --include='*.swift' -E 'deprecated' "$src" 2>/dev/null | grep -v -E '/(build|Derived|\.build)/' | wc -l | tr -d ' ') lines"
echo "- DispatchQueue usage: $(count 'DispatchQueue' "$src") files; @unchecked Sendable: $(count '@unchecked Sendable' "$src") files; nonisolated(unsafe): $(count 'nonisolated(unsafe)' "$src") files"
echo "- Swift files over 400 lines: $(find "$src" -name '*.swift' -not -path '*/build/*' -not -path '*/Derived/*' -not -path '*/.build/*' -not -path '*/node_modules/*' -not -path '*/.claude/*' -exec awk 'END{if(NR>400)print FILENAME}' {} \; 2>/dev/null | wc -l | tr -d ' ')"
