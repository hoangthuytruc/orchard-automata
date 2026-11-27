#!/usr/bin/env bash
# Sample committed, then an uncommitted change with seeded defects (see evals/SEEDED.md).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../fixtures/scaffold-lib.sh"
copy_sample
commit_fixture
apply_review_diff
echo "scaffolded workflow-review-only into $PWD"
