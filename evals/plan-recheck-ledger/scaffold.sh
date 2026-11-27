#!/usr/bin/env bash
# Sample plus one unsourced app rule (NoteRule) in code.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../fixtures/scaffold-lib.sh"
copy_sample
add_note_rule
commit_fixture "chore: ledger sample with an unsourced note rule"
echo "scaffolded plan-recheck-ledger into $PWD"
