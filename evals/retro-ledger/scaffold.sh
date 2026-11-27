#!/usr/bin/env bash
# Sample with a fixture run log: one repeated signal, two single events.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../fixtures/scaffold-lib.sh"
copy_sample
cp "$FIXTURES/runlog.jsonl" .orchard/runs/runlog.jsonl
commit_fixture
echo "scaffolded retro-ledger into $PWD"
