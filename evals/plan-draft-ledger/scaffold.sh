#!/usr/bin/env bash
# Sample without its feature file, plus one unsourced app rule in code.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../fixtures/scaffold-lib.sh"
copy_sample
rm -f docs/features/Purchases.feature
add_note_rule
# The feature file was a file source in the profile; without it the owner states the knowledge-base keys.
python3 -I - <<'PY'
import re
from pathlib import Path
p = Path('.orchard/profile.md')
s = re.sub(r'file:docs/features/Purchases\.feature#[0-9a-f]+', 'stated: owner 2026-11-26', p.read_text())
p.write_text(s)
PY
commit_fixture "chore: ledger sample without scenarios"
echo "scaffolded plan-draft-ledger into $PWD"
