#!/usr/bin/env bash
# Accepted led-7 run: delivered code and tests uncommitted, plan accepted, report written.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../fixtures/scaffold-lib.sh"
copy_sample
put_plan led-7-plan.md "accepted 2026-11-25" led-7.md "$(printf '%s\n' \
  '| TS_LED_002 | yes | TransactionStoreTests.testRefundReducesBalance | green |' \
  '| N1 | yes | DailyLimitTests.testBannerShowsResetTimeOnDailyLimit | green |' \
  '| N2 | no | none | offline queue not built in this change; its code and tests were removed |' \
  '| TS_LED_004 removal | yes | none | the app never counted purchases; nothing to remove in code |')"
commit_fixture
snapshot_locks
cp "$FIXTURES/led-7-test-report.md" .orchard/runs/reports/led-7-test-report.md
apply_refund_fix
add_refund_tests
add_daily_limit
echo "scaffolded update-docs-led into $PWD"
