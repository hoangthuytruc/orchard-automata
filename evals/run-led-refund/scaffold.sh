#!/usr/bin/env bash
# Approved led-refund plan on the untouched sample.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../fixtures/scaffold-lib.sh"
copy_sample
put_plan led-refund-plan.md "approved 2026-11-24" led-refund.md
commit_fixture
echo "scaffolded run-led-refund into $PWD"
