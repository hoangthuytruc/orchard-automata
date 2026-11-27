#!/usr/bin/env bash
# Runs the skill set's eval suite on the sample through `claude plugin eval`, with the no-skill baseline arm, and
# keeps the results local.
#
#   eval.sh smoke [extra flags]    one run per case
#   eval.sh full  [extra flags]    three runs per case
#   eval.sh case <glob> [flags]    one run of the matching case(s)
#
# Environment: JOBS (parallel runs, default 3), MAX_COST_USD (default 25), JUDGE_MODEL (the judge for llm graders;
# when unset the tool's default judge is used; a lighter judge has voted FAIL on reports that met every rubric line,
# so prefer a strong one), EVAL_OUT (results folder, default <skill set>/evals/results), ENV_BLOCK_PATTERN (a
# regular expression for an environment that blocked the build; default below).
#
# Gate: a case passes when every run with the skill set passes all of its own graders. The with/without delta is
# printed as a signal only and never decides a pass. A case whose with-skill run failed while its final message or
# graded files quote an environment block (default pattern: a sandbox refusing SwiftPM or git) is reported
# "not run (environment)", not failed. The summary is printed and saved as summary.txt beside the results.
# Exit: 0 when no case failed, 1 when a case failed or none ran, the harness's own status when it left no results.
# Tool grants: the skills need Bash (swift test, git), Write and Edit inside the scaffolded temporary directory.
set -uo pipefail
# Eval runs never write to the developer's real run log.
export ORCHARD_RUNLOG="${ORCHARD_RUNLOG_EVAL:-${TMPDIR:-/tmp}/orchard-eval-runlog.jsonl}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN="$HERE/plugin"
ORCHARD="$(cd "$HERE/../.." && pwd)"
MODE="${1:-smoke}"; shift || true
RUNS=1; CASE=(); JUDGE=()
case "$MODE" in
  smoke) ;;
  full) RUNS=3 ;;
  case) CASE=(--case "${1:?case glob}"); shift ;;
  *) echo "usage: eval.sh smoke|full|case <glob> [claude plugin eval flags]" >&2; exit 64 ;;
esac
[ -n "${JUDGE_MODEL:-}" ] && JUDGE=(--judge-model "$JUDGE_MODEL")
# The harness accepts only an eval folder that really sits inside the plugin, so the run uses a staged copy:
# the plugin with its links resolved, the eval cases, and the sample the scaffolds copy from.
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/orchard-eval.XXXXXX")"
cp -RL "$PLUGIN" "$STAGE/plugin"
cp -R "$ORCHARD/evals" "$STAGE/plugin/evals"
rm -rf "$STAGE/plugin/evals/results"
mkdir -p "$STAGE/plugin/sample"
cp -R "$ORCHARD/sample/Ledger" "$STAGE/plugin/sample/Ledger"
PLUGIN="$STAGE/plugin"
OUT="${EVAL_OUT:-$ORCHARD/evals/results}/$(date +%Y%m%d-%H%M%S)-$MODE"
mkdir -p "$OUT"
cd "$PLUGIN"
claude plugin eval "$PLUGIN" \
  --scaffold --trust-plugin --no-publish \
  --runs "$RUNS" -j "${JOBS:-3}" \
  --allow-tools Bash Write Edit \
  ${JUDGE[@]+"${JUDGE[@]}"} \
  --threshold 0.6 \
  --max-cost-usd "${MAX_COST_USD:-25}" \
  --output-dir "$OUT" \
  --json "$OUT/aggregate-result.json" \
  --report "$OUT/report.html" \
  ${CASE[@]+"${CASE[@]}"} "$@"
status=$?
if [ -s "$OUT/aggregate-result.json" ]; then
  total=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1])).get("aggregates",{}).get("casesTotal",0))' "$OUT/aggregate-result.json")
  if [ "$total" = "0" ]; then
    echo "no case ran (load error above)" >&2
    rm -rf "$OUT"
    exit 1
  fi
  python3 -I - "$OUT/aggregate-result.json" "${ENV_BLOCK_PATTERN:-}" > "$OUT/summary.txt" <<'SUMMARY'
import json, re, sys
data = json.load(open(sys.argv[1]))
# The build was blocked by the environment: a sandbox error, or the profile's build or test command named on the
# same line as the sandbox that stopped it.
pattern = re.compile(sys.argv[2] or
                     r"sandbox_apply|(swift (build|test)|SwiftPM|xcodebuild)[^\n]{0,120}(sandbox|Operation not permitted"
                     r"|blocked|can't (build|run)|cannot (build|run)|could not (build|run))"
                     r"|(sandbox|Operation not permitted)[^\n]{0,120}(swift (build|test)|SwiftPM|xcodebuild|build or test)",
                     re.I)


def text(run):
    parts = [run.get('error') or '']
    for grader in run.get('graders') or []:
        parts += [str(grader.get('evidence') or ''), str(grader.get('explanation') or '')]
    return '\n'.join(parts)


counts = {'passed': 0, 'failed': 0, 'not run (environment)': 0}
print('%-28s %-22s %-40s %s' % ('Case', 'Result (gate)', 'Graders failed with the skill set', 'Delta (signal only)'))
for case in data.get('cases', []):
    runs = (case.get('arms') or {}).get('with') or []
    failed = sorted({g['name'] for r in runs for g in r.get('graders') or [] if not g.get('passed')})
    if runs and all(r.get('passed') for r in runs):
        result = 'passed'
    elif any(not r.get('passed') and pattern.search(text(r)) for r in runs):
        result = 'not run (environment)'
    else:
        result = 'failed'
    counts[result] += 1
    agg = case.get('aggregates') or {}
    delta = agg.get('delta')
    signal = ('%+.2f (%.2f with, %.2f without)' % (delta, agg.get('score') or 0, agg.get('scoreWithout') or 0)
              if delta is not None else 'n/a')
    print('%-28s %-22s %-40s %s' % (case.get('name'), result, ', '.join(failed) or '-', signal))
print('cases: %d passed, %d failed, %d not run (environment). The delta is a signal, not a gate.' % (
    counts['passed'], counts['failed'], counts['not run (environment)']))
sys.exit(1 if counts['failed'] or not sum(counts.values()) else 0)
SUMMARY
  status=$?
  cat "$OUT/summary.txt"
fi
echo "results: $OUT"
echo "report:  $OUT/report.html"
exit $status
