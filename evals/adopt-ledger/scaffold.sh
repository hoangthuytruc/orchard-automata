#!/usr/bin/env bash
# Sample without its profile: adopt has to discover it.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../fixtures/scaffold-lib.sh"
copy_sample
rm -f .orchard/profile.md
commit_fixture "chore: ledger sample without a profile"
echo "scaffolded adopt-ledger into $PWD"
