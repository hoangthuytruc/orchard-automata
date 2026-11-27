#!/usr/bin/env bash
# Shared by every case's scaffold.sh (sourced, never run alone). The caller sets HERE to its own case folder.
# Copies the sample project into the eval run's workspace (the current directory) and offers the helpers the
# cases share, so each behaviour is written once. Never writes inside the skill set itself.
set -euo pipefail
: "${HERE:?scaffold.sh must set HERE to its case folder before sourcing scaffold-lib.sh}"
EVALS="$(cd "$HERE/.." && pwd -P)"  # -P: the adapter reaches evals/ through a symlink
ORCHARD="$(cd "$EVALS/.." && pwd -P)"
SAMPLE="$ORCHARD/sample/Ledger"
FIXTURES="$EVALS/fixtures"

case "$PWD" in
  "$ORCHARD"|"$ORCHARD"/*) echo "refusing to scaffold inside the skill set ($PWD)" >&2; exit 1 ;;
esac
[ -f "$SAMPLE/Package.swift" ] || { echo "sample not found at $SAMPLE" >&2; exit 1; }

# Copy the sample with its .orchard/ folder, drop build output and run output, and make the profile's
# knowledge_base_check runnable from the workspace (in the sample it names the script relative to the skill set).
copy_sample() {
  cp -R "$SAMPLE/." "$PWD/"
  rm -rf .build .swiftpm .orchard/runs .orchard/agents.local.md
  mkdir -p .orchard/runs/plans .orchard/runs/reports
  python3 -I - "$ORCHARD/scripts/gate_check.py" <<'PY'
import re, sys
from pathlib import Path
p = Path('.orchard/profile.md')
lines = p.read_text().splitlines(keepends=True)
for i, line in enumerate(lines):
    if line.startswith('| knowledge_base_check'):
        # Any spelling of the script's location ($ORCHARD/…, ../../scripts/…) becomes the resolved path.
        line = re.sub(r'"?(\$ORCHARD|\.\./\.\.)/scripts/gate_check\.py"?', '"%s"' % sys.argv[1], line)
        lines[i] = re.sub(r' \(\$ORCHARD: [^)]*\)', '', line)
p.write_text(''.join(lines))
PY
}

# One commit so git-based scripts (lock check, evidence state, diff) work. The fixture identity is local to the repo.
commit_fixture() {
  git init -q -b main
  git -c user.name=fixture -c user.email=fixture@localhost add -A
  git -c user.name=fixture -c user.email=fixture@localhost commit -qm "${1:-chore: ledger sample}"
}

# The unsourced app rule (140-character note limit): in code and in TS_LED_006 only, in no spec or design.
add_note_rule() {
  cat > Sources/Ledger/NoteRule.swift <<'SWIFT'
import Foundation

public enum NoteRule {
    public static let maxLength = 140

    public static func isValid(_ note: String) -> Bool {
        note.trimmingCharacters(in: .whitespacesAndNewlines).count <= maxLength
    }
}
SWIFT
}

# The delivered change of plan led-refund: balance signs amounts by kind; latest() returns an optional.
apply_refund_fix() {
  python3 -I - <<'PY'
from pathlib import Path
p = Path('Sources/Ledger/TransactionStore.swift')
s = p.read_text()
pairs = [
    ("        transactions.map { $0.amountCents }.reduce(0, +)\n    }\n\n    public func latest",
     "        transactions.map { $0.kind == .refund ? -$0.amountCents : $0.amountCents }.reduce(0, +)\n    }\n\n    public func latest"),
    ("    public func latest() -> Transaction {\n        transactions.sorted { $0.date > $1.date }.first!\n",
     "    public func latest() -> Transaction? {\n        transactions.sorted { $0.date > $1.date }.first\n"),
]
for old, new in pairs:
    assert old in s, 'sample TransactionStore.swift changed; update scaffold-lib.sh'
    s = s.replace(old, new)
p.write_text(s)
PY
}

# Tests for plan led-refund, in the sample's own style (the async add is awaited with sleep, as the existing test does).
add_refund_tests() {
  cat >> Tests/LedgerTests/TransactionStoreTests.swift <<'SWIFT'

extension TransactionStoreTests {
    func testRefundReducesBalance() {
        let store = TransactionStore()
        store.add(Transaction(amountCents: 1000, kind: .purchase))
        store.add(Transaction(amountCents: 400, kind: .refund))
        sleep(1)
        XCTAssertEqual(store.balanceCents(), 600)
    }
}
SWIFT
}

# The contract test of plan led-refund (needs apply_refund_fix: latest() returns an optional).
add_latest_test() {
  cat >> Tests/LedgerTests/TransactionStoreTests.swift <<'SWIFT'

extension TransactionStoreTests {
    func testLatestIsNilWhenEmpty() {
        XCTAssertNil(TransactionStore().latest())
    }
}
SWIFT
}

# The delivered N1 of plan led-7: the limit banner from the server's 409 DAILY_LIMIT reply, with its test.
add_daily_limit() {
  cat > Sources/Ledger/DailyLimit.swift <<'SWIFT'
import Foundation

public struct LimitBanner: Equatable {
    public let message: String
    public let resetsAt: Date
}

public enum DailyLimit {
    public static func banner(status: Int, code: String?, resetsAt: Date?) -> LimitBanner? {
        guard status == 409, code == "DAILY_LIMIT", let resetsAt else { return nil }
        return LimitBanner(message: "You've reached today's limit.", resetsAt: resetsAt)
    }
}
SWIFT
  cat > Tests/LedgerTests/DailyLimitTests.swift <<'SWIFT'
import XCTest
@testable import Ledger

final class DailyLimitTests: XCTestCase {
    func testBannerShowsResetTimeOnDailyLimit() {
        let reset = Date(timeIntervalSince1970: 1_800_000_000)
        let banner = DailyLimit.banner(status: 409, code: "DAILY_LIMIT", resetsAt: reset)
        XCTAssertEqual(banner?.resetsAt, reset)
    }
}
SWIFT
}

# The change under review in workflow-review-only, with the defects listed in evals/SEEDED.md ("Review-only diff").
apply_review_diff() {
  cat > Sources/Ledger/DailyLimit.swift <<'SWIFT'
import Foundation

public struct LimitBanner: Equatable {
    public let message: String
    public let resetsAt: Date
}

public enum DailyLimit {
    static let formatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        return formatter
    }()

    public static func banner(status: Int, body: Data) -> LimitBanner? {
        guard status >= 400 else { return nil }
        let json = try! JSONSerialization.jsonObject(with: body) as! [String: String]
        let resetsAt = formatter.date(from: json["resets_at"]!)!
        return LimitBanner(message: "You've reached today's limit.", resetsAt: resetsAt)
    }
}
SWIFT
  python3 -I - <<'PY2'
from pathlib import Path
p = Path('Sources/Ledger/SyncClient.swift')
s = p.read_text()
old = '        var request = URLRequest(url: baseURL.appendingPathComponent("transactions"))\n'
assert old in s, 'sample SyncClient.swift changed; update scaffold-lib.sh'
p.write_text(s.replace(old, old + '        print("sync: using token \\(authToken ?? "none")")\n'))
PY2
}

# Copy a plan fixture into plans_dir with its status line set and its Result rows filled.
# $1 fixture name, $2 status, $3 target name, $4 Result rows (Markdown table rows; empty before the run).
put_plan() {
  python3 -I - "$FIXTURES/$1" "$2" ".orchard/runs/plans/$3" "${4:-}" <<'PY'
import sys
from pathlib import Path
src, status, out, result = sys.argv[1:]
s = Path(src).read_text()
assert '@STATUS@' in s and '@RESULT@' in s
s = s.replace('@STATUS@', status).replace('@RESULT@\n', result.strip('\n') + '\n' if result.strip() else '')
Path(out).write_text(s)
PY
}

# A lock snapshot of the profile's locked globs, as `run` takes it at approval.
snapshot_locks() {
  python3 -I "$ORCHARD/scripts/lock_check.py" snapshot .orchard/runs/locks.json \
    'docs/features/*.feature' 'docs/features/*.requirements.md' >/dev/null
}

# The change state as scripts/evidence.py computes it (left out: the evidence file).
change_state() {
  python3 -I "$ORCHARD/scripts/evidence.py" state
}
