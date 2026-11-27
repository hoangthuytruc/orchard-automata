#!/usr/bin/env bash
# The sample as it is.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../fixtures/scaffold-lib.sh"
copy_sample
commit_fixture
echo "scaffolded workflow-bug-fix-refund into $PWD"
