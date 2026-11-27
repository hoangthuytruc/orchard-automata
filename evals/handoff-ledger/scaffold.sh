#!/usr/bin/env bash
# Finished led-refund run: change, evidence (unit tests stale), review findings.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../fixtures/scaffold-lib.sh"
copy_sample
put_plan led-refund-plan.md executed led-refund.md "$(printf '%s\n' \
  '| TS_LED_002 | yes | TransactionStoreTests.testRefundReducesBalance | |' \
  '| latest() nil on an empty store (contract) | yes | TransactionStoreTests.testLatestIsNilWhenEmpty | added in fix round 2 |')"
commit_fixture
snapshot_locks
apply_refund_fix
add_refund_tests
STATE_ROUND1="$(change_state)"
add_latest_test
STATE_FINAL="$(change_state)"
cp "$FIXTURES/led-refund-review.md" .orchard/runs/reports/led-refund-review.md
python3 -I - "$STATE_ROUND1" "$STATE_FINAL" <<'PY'
import json, sys
old, final = sys.argv[1:]
rows = [
    {'check': 'test.unit', 'selection': 'TransactionStoreTests', 'command': 'swift test --filter TransactionStoreTests',
     'exit': 0, 'duration_s': 14.2, 'summary': 'Executed 2 tests, with 0 failures (0 unexpected) in 2.004 seconds',
     'state': old, 'time': '2026-11-25T10:02:11+00:00'},
    {'check': 'build', 'selection': 'all', 'command': 'swift build', 'exit': 0, 'duration_s': 6.1,
     'summary': 'Build complete!', 'state': final, 'time': '2026-11-25T10:31:40+00:00'},
    {'check': 'lock', 'selection': 'docs/features/*', 'command': 'lock_check.py verify .orchard/runs/locks.json',
     'exit': 0, 'duration_s': 0.1, 'summary': 'locked files unchanged (1)', 'state': final,
     'time': '2026-11-25T10:31:52+00:00'},
]
with open('.orchard/runs/reports/led-refund-evidence.jsonl', 'w') as out:
    for row in rows:
        out.write(json.dumps(row) + '\n')
PY
echo "scaffolded handoff-ledger into $PWD"
