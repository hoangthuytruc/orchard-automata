#!/usr/bin/env python3
"""The run log: what each run did, written by this script and never recalled by an agent. `retro` reads it.

  runlog.py start --workflow W --skill S --task T [--isolation shared|standard|strict]       -> prints RUN_ID
  runlog.py event RUN_ID <type> [--role R] [--round N] [--tier strong|light] [--tokens N|na] [--seconds N] [--note T]
  runlog.py finish RUN_ID --outcome delivered|green|red|blocked|ended_early [--findings N] [--tokens N|na] [--seconds N]
  runlog.py rate RUN_ID [--accepted N] [--rejected N] [--rework-minutes N] [--verify-minutes N]
  runlog.py report [--since 30d] [--group workflow,isolation] [--json]
  runlog.py list [--limit 20]

Event types:
  tier            the tier a package, diagnosis or planning ran on (--role, --tier; --tokens and --seconds for
                  that role and round)
  step_up         a step up to the strong tier; --note names the failure before it
  ended_early     where the run ended early; --note names the conflict
  finding         one reviewer finding; --note gives its category and the rule it cites
  first_try_fail  a check that failed on its first try (--note: which)
  flaky           a flaky test (--note: which)
  wait            time waiting on the simulator, device or backend (--seconds)
  approval_wait   time waiting for the developer's approval (--seconds)
  send_back       what the developer sent back at acceptance, in their words (--note)
  question        a question asked before the run (--note)
  seeded_missed   a seeded defect the reviewer missed on the sample (evals only)

Tokens are never estimated: pass --tokens only when the agent tool reports them, or `na` when it does not; the
report then says "not available". On finish, --tokens and --seconds are those of the session that closes the run (a
skill called alone, or the coordinator), not already given on an event. The isolation level defaults to standard, the default of the workflow model.

File: $ORCHARD_RUNLOG, else ~/.orchard/runlog.jsonl. One JSON line per start, event, finish or rating, folded into
one record per run when read. Nothing leaves the machine. When the file cannot be written, start prints `none` and
the other commands accept `none` and do nothing, so a read-only home never breaks a run.

The report prints, per group (default: workflow and isolation level):
  verification   share of runs that ended early; review findings per run; share of runs sent back at acceptance;
                 minutes spent verifying a run (from rate --verify-minutes)
  cost           tokens and minutes per accepted task (delivered or green), counting every run of the group,
                 failed attempts and send-backs included. A run's minutes are the sum of its recorded --seconds
                 (events other than approval_wait, and finish) when it has any, else finish minus start; the
                 report says which
  quality        seeded defects the reviewer missed
  trend          earlier half against later half once a group has five finished runs; "no baseline yet" before
Findings per run is never read alone: fewer findings can mean better code or a weaker reviewer.

Exit codes:
  0   done
  2   no run with that RUN_ID in the log
  64  wrong usage, or the log cannot be read
"""
import argparse
import json
import os
import re
import statistics
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

FILE = Path(os.environ.get('ORCHARD_RUNLOG') or Path.home() / '.orchard' / 'runlog.jsonl')
OUTCOMES = ('delivered', 'green', 'red', 'blocked', 'ended_early')
ACCEPTED = ('delivered', 'green')
EVENTS = ('tier', 'step_up', 'ended_early', 'finding', 'first_try_fail', 'flaky', 'wait', 'approval_wait',
          'send_back', 'question', 'seeded_missed')
ISOLATION = ('shared', 'standard', 'strict')
GROUP_FIELDS = ('workflow', 'isolation', 'skill')
BASELINE = 5
NA = 'not available'


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('%s: error: %s' % (self.prog, message), file=sys.stderr)
        sys.exit(64)


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def append(line):
    """Append one line; False when the log cannot be written."""
    try:
        FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(FILE, 'a', encoding='utf-8') as handle:
            handle.write(json.dumps(line, ensure_ascii=False) + '\n')
        return True
    except OSError as error:
        print('run log disabled: cannot write %s (%s)' % (FILE, error), file=sys.stderr)
        return False


def lines():
    if not FILE.exists():
        return []
    try:
        with open(FILE, encoding='utf-8') as handle:
            return [json.loads(line) for line in handle if line.strip()]
    except (OSError, ValueError) as error:
        print('cannot read %s: %s' % (FILE, error), file=sys.stderr)
        sys.exit(64)


def runs():
    """Fold the log lines into one record per run, in start order."""
    folded = {}
    for line in lines():
        run_id, kind = line.get('run_id'), line.get('kind')
        if kind == 'start':
            folded[run_id] = dict(line, events=[])
            continue
        run = folded.get(run_id)
        if run is None:
            continue
        if kind == 'event':
            run['events'].append(line)
        elif kind == 'finish':
            run.update({k: v for k, v in line.items() if k not in ('kind', 'time')}, finished_at=line.get('time'))
        elif kind == 'rate':
            run.update({k: v for k, v in line.items() if k not in ('kind', 'time')}, rated_at=line.get('time'))
    return list(folded.values())


def known(run_id):
    if run_id == 'none':
        return False
    if not any(line.get('run_id') == run_id and line.get('kind') == 'start' for line in lines()):
        print('no run %s in %s' % (run_id, FILE), file=sys.stderr)
        sys.exit(2)
    return True


def cmd_start(args):
    run_id = time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]
    ok = append({'run_id': run_id, 'kind': 'start', 'time': now_iso(), 'started_epoch': time.time(),
                 'workflow': args.workflow, 'skill': args.skill, 'task': args.task, 'isolation': args.isolation})
    print(run_id if ok else 'none')
    return 0


def tokens_value(text):
    if text is None:
        return None
    if text.lower() in ('na', 'n/a', NA):
        return NA
    if not text.isdigit():
        raise argparse.ArgumentTypeError('--tokens takes a whole number or na')
    return int(text)


def cmd_event(args):
    if not known(args.run_id):
        print('no run to log (the run log is disabled)')
        return 0
    line = {'run_id': args.run_id, 'kind': 'event', 'time': now_iso(), 'type': args.type}
    for key in ('role', 'round', 'tier', 'tokens', 'seconds', 'note'):
        value = getattr(args, key)
        if value is not None:
            line[key] = value
    append(line)
    return 0


def cmd_finish(args):
    if not known(args.run_id):
        print('no run to finish (the run log is disabled)')
        return 0
    start = next(r for r in runs() if r['run_id'] == args.run_id)
    line = {'run_id': args.run_id, 'kind': 'finish', 'time': now_iso(), 'outcome': args.outcome,
            'duration_s': round(time.time() - start.get('started_epoch', time.time()), 1)}
    for key in ('findings', 'tokens', 'seconds'):
        value = getattr(args, key)
        if value is not None:
            line[key] = value
    append(line)
    print(json.dumps({k: line[k] for k in ('run_id', 'outcome', 'duration_s')}))
    return 0


def cmd_rate(args):
    if not known(args.run_id):
        print('no run to rate (the run log is disabled)')
        return 0
    line = {'run_id': args.run_id, 'kind': 'rate', 'time': now_iso()}
    for key in ('accepted', 'rejected', 'rework_minutes', 'verify_minutes'):
        value = getattr(args, key)
        if value is not None:
            line[key] = value
    append(line)
    print('rated %s' % args.run_id)
    return 0


def parse_since(text):
    if not text:
        return None
    match = re.fullmatch(r'(\d+)([dwm])', text)
    if not match:
        raise argparse.ArgumentTypeError('--since takes 30d, 8w or 3m')
    return datetime.now(timezone.utc) - timedelta(days={'d': 1, 'w': 7, 'm': 30}[match.group(2)] * int(match.group(1)))


def count(run, kind):
    return sum(1 for e in run['events'] if e.get('type') == kind)


def seconds(run, kind):
    return sum(e.get('seconds') or 0 for e in run['events'] if e.get('type') == kind)


def findings(run):
    return run['findings'] if isinstance(run.get('findings'), int) else count(run, 'finding')


def run_tokens(run):
    """Tokens a run reported, or None when any part of it was not available or nothing was reported."""
    values = [e.get('tokens') for e in run['events'] if 'tokens' in e] + ([run['tokens']] if 'tokens' in run else [])
    if not values or any(not isinstance(v, int) for v in values):
        return None
    return sum(values)


def recorded_seconds(run):
    """Sum of the --seconds recorded on the run's events (approval waits left out) and on finish; None when none."""
    values = [e['seconds'] for e in run['events'] if isinstance(e.get('seconds'), (int, float))
              and e.get('type') != 'approval_wait']
    if isinstance(run.get('seconds'), (int, float)):
        values.append(run['seconds'])
    return sum(values) if values else None


def run_seconds(finished):
    """(total seconds, runs timed from recorded seconds) over finished runs; finish minus start where none."""
    total, recorded = 0.0, 0
    for run in finished:
        value = recorded_seconds(run)
        if value is None:
            total += run.get('duration_s', 0) or 0
        else:
            total, recorded = total + value, recorded + 1
    return total, recorded


def minutes_source(recorded, finished):
    if not finished:
        return NA
    if recorded == finished:
        return 'from recorded seconds'
    if recorded == 0:
        return 'from start to finish'
    return 'recorded seconds for %d of %d runs, start to finish for the rest' % (recorded, finished)


def share(part, whole):
    return round(100.0 * part / whole) if whole else None


def verification(finished):
    """The four verification figures for a list of finished runs."""
    n = len(finished)
    verify = [r['verify_minutes'] for r in finished if isinstance(r.get('verify_minutes'), (int, float))]
    return {
        'ended_early_pct': share(sum(1 for r in finished if r.get('outcome') == 'ended_early' or count(r, 'ended_early')), n),
        'findings_per_run': round(statistics.mean(findings(r) for r in finished), 1) if n else None,
        'sent_back_pct': share(sum(1 for r in finished if count(r, 'send_back')), n),
        'verify_minutes_median': round(statistics.median(verify), 1) if verify else None,
    }


def figures(group_runs):
    finished = [r for r in group_runs if 'outcome' in r]
    accepted = [r for r in finished if r['outcome'] in ACCEPTED]
    tokens = [run_tokens(r) for r in group_runs]
    with_tokens = sum(1 for t in tokens if t is not None)
    rated = [r for r in group_runs if 'accepted' in r or 'rejected' in r]
    acc, rej = sum(r.get('accepted', 0) for r in rated), sum(r.get('rejected', 0) for r in rated)
    rework = [r['rework_minutes'] for r in rated if isinstance(r.get('rework_minutes'), (int, float))]
    total_seconds, timed = run_seconds(finished)
    result = {
        'runs': len(group_runs),
        'finished': len(finished),
        'accepted_tasks': len(accepted),
        **verification(finished),
        'tokens_per_accepted_task': (round(sum(tokens) / len(accepted)) if accepted and with_tokens == len(group_runs)
                                     else NA),
        'tokens_reported_runs': with_tokens,
        'minutes_per_accepted_task': round(total_seconds / 60 / len(accepted), 1) if accepted else None,
        'minutes_source': minutes_source(timed, len(finished)),
        'seeded_missed': sum(count(r, 'seeded_missed') for r in group_runs),
        'first_try_fails': sum(count(r, 'first_try_fail') for r in group_runs),
        'flaky_tests': sum(count(r, 'flaky') for r in group_runs),
        'step_ups': sum(count(r, 'step_up') for r in group_runs),
        'questions': sum(count(r, 'question') for r in group_runs),
        'device_or_backend_wait_minutes': round(sum(seconds(r, 'wait') for r in group_runs) / 60, 1),
        'approval_wait_minutes': round(sum(seconds(r, 'approval_wait') for r in group_runs) / 60, 1),
        'finding_acceptance_pct': share(acc, acc + rej),
        'rework_minutes_median': round(statistics.median(rework), 1) if rework else None,
    }
    if len(finished) >= BASELINE:
        ordered = sorted(finished, key=lambda r: r.get('started_epoch', 0))
        half = len(ordered) // 2
        result['trend'] = {'earlier': verification(ordered[:half]), 'later': verification(ordered[half:])}
    else:
        result['trend'] = 'no baseline yet (%d of %d finished runs)' % (len(finished), BASELINE)
    return result


def show(value, unit=''):
    if value is None:
        return NA
    return '%s%s' % (value, unit) if not isinstance(value, str) else value


def cmd_report(args):
    fields = [f.strip() for f in args.group.split(',') if f.strip()]
    if any(f not in GROUP_FIELDS for f in fields):
        print('--group takes a comma-separated list of: %s' % ', '.join(GROUP_FIELDS), file=sys.stderr)
        return 64
    selected = runs()
    if args.since:
        selected = [r for r in selected if datetime.fromisoformat(r['time']) >= args.since]
    groups = {}
    for run in selected:
        groups.setdefault(tuple(str(run.get(f, '?')) for f in fields), []).append(run)
    report = {' / '.join(key): figures(group) for key, group in sorted(groups.items())}
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    if not report:
        print('no runs recorded in %s' % FILE)
        return 0
    for name, f in report.items():
        print('## %s (%s)' % (name, ' / '.join(fields)))
        print('- runs: %d started, %d finished, %d accepted tasks' % (f['runs'], f['finished'], f['accepted_tasks']))
        print('- verification: ended early %s; findings per run %s; sent back %s; minutes verifying a run %s'
              % (show(f['ended_early_pct'], '%'), show(f['findings_per_run']), show(f['sent_back_pct'], '%'),
                 show(f['verify_minutes_median'])))
        tokens = f['tokens_per_accepted_task']
        if tokens == NA:
            tokens = '%s (%d of %d runs report tokens)' % (NA, f['tokens_reported_runs'], f['runs'])
        print('- cost per accepted task: tokens %s; minutes %s (%s)'
              % (tokens, show(f['minutes_per_accepted_task']), f['minutes_source']))
        print('- quality: seeded defects missed %d' % f['seeded_missed'])
        print('- signals: first-try fails %d; flaky tests %d; steps up to strong %d; questions %d; '
              'device or backend wait %s min; approval wait %s min; findings accepted %s; rework minutes %s'
              % (f['first_try_fails'], f['flaky_tests'], f['step_ups'], f['questions'],
                 f['device_or_backend_wait_minutes'], f['approval_wait_minutes'],
                 show(f['finding_acceptance_pct'], '%'), show(f['rework_minutes_median'])))
        trend = f['trend']
        if isinstance(trend, str):
            print('- trend: %s' % trend)
        else:
            for key, label in (('ended_early_pct', 'ended early %'), ('findings_per_run', 'findings per run'),
                               ('sent_back_pct', 'sent back %'), ('verify_minutes_median', 'minutes verifying')):
                print('- trend %s: %s -> %s' % (label, show(trend['earlier'][key]), show(trend['later'][key])))
        print()
    print('file: %s' % FILE)
    return 0


def cmd_list(args):
    for run in runs()[-args.limit:]:
        print('%s  %-20s %-9s %-12s %6s  %s' % (
            run['run_id'], run.get('workflow', '?'), run.get('isolation', '?'), run.get('outcome', 'open'),
            ('%.0fm' % (run['duration_s'] / 60)) if isinstance(run.get('duration_s'), (int, float)) else '',
            (run.get('task') or '')[:60]))
    return 0


def main():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='cmd', required=True, parser_class=Parser)

    start = sub.add_parser('start')
    start.add_argument('--workflow', required=True)
    start.add_argument('--skill', required=True)
    start.add_argument('--task', required=True)
    start.add_argument('--isolation', choices=ISOLATION, default='standard')
    start.set_defaults(fn=cmd_start)

    event = sub.add_parser('event')
    event.add_argument('run_id')
    event.add_argument('type', choices=EVENTS)
    event.add_argument('--role')
    event.add_argument('--round', type=int)
    event.add_argument('--tier', choices=('strong', 'light'))
    event.add_argument('--tokens', type=tokens_value, help='a whole number reported by the agent tool, or na')
    event.add_argument('--seconds', type=float)
    event.add_argument('--note')
    event.set_defaults(fn=cmd_event)

    finish = sub.add_parser('finish')
    finish.add_argument('run_id')
    finish.add_argument('--outcome', required=True, choices=OUTCOMES)
    finish.add_argument('--findings', type=int)
    finish.add_argument('--tokens', type=tokens_value, help='a whole number reported by the agent tool, or na')
    finish.add_argument('--seconds', type=float)
    finish.set_defaults(fn=cmd_finish)

    rate = sub.add_parser('rate')
    rate.add_argument('run_id')
    rate.add_argument('--accepted', type=int, help='findings or items the developer accepted')
    rate.add_argument('--rejected', type=int, help='findings or items the developer rejected')
    rate.add_argument('--rework-minutes', type=float, help='minutes the developer spent fixing the output')
    rate.add_argument('--verify-minutes', type=float, help='minutes the developer spent verifying the run')
    rate.set_defaults(fn=cmd_rate)

    report = sub.add_parser('report')
    report.add_argument('--since', type=parse_since, help='30d, 8w or 3m')
    report.add_argument('--group', default='workflow,isolation', help='fields to group by: workflow, isolation, skill')
    report.add_argument('--json', action='store_true')
    report.set_defaults(fn=cmd_report)

    listing = sub.add_parser('list')
    listing.add_argument('--limit', type=int, default=20)
    listing.set_defaults(fn=cmd_list)

    args = parser.parse_args()
    return args.fn(args)


if __name__ == '__main__':
    sys.exit(main())
