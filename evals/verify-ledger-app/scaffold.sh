#!/usr/bin/env bash
# The sample with its iOS app, committed and unchanged: verify runs the checks and captures visual evidence.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../fixtures/scaffold-lib.sh"
copy_sample
commit_fixture "chore: ledger sample with its app"
echo "scaffolded verify-ledger-app into $PWD"
