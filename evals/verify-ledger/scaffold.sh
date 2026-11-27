#!/usr/bin/env bash
# Implemented led-refund change, uncommitted, with a locked register edited after the snapshot.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../fixtures/scaffold-lib.sh"
copy_sample
cat > docs/features/Purchases.requirements.md <<'MD'
# Purchases: requirements register

| Scenario | Basis | Evidence | Test |
| --- | --- | --- | --- |
| TS_LED_001 | Spec | v3 §1: "The balance is the sum of all purchases minus all refunds." | TransactionStoreTests.testAddIncreasesBalance |
| TS_LED_002 | Spec | v3 §2: "A refund is added back to the balance at once." | pending |
MD
put_plan led-refund-plan.md "approved 2026-11-24" led-refund.md
commit_fixture "chore: ledger sample with a register"
snapshot_locks
apply_refund_fix
add_refund_tests
add_latest_test
# The breach: an implementer wrote into the locked register after approval.
sed -i.bak 's/| pending |/| TransactionStoreTests.testRefundReducesBalance |/' docs/features/Purchases.requirements.md
rm -f docs/features/Purchases.requirements.md.bak
echo "scaffolded verify-ledger into $PWD"
