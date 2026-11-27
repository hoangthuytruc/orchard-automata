#!/usr/bin/env python3
"""Compute the test report's verdict from the evidence file, the plan and the latest review. `handoff` quotes it.

  verdict.py <evidence.jsonl> <plan file> [--reviews <dir or file>] [--ended-early <reason>] [--root R]

Prints the verdict on the first line (`Ready to accept`, `Not ready` or `Blocked`), then its reasons, then the gaps
that do not change it.

Ready to accept, when all hold:
  - every delivered scenario has at least one passing evidence record made on the current state of the change. The
    delivered scenarios are the rows of the plan's "Result" table marked yes; while that table is empty, every row of
    "Scenario changes" except removed, "not a gate scenario" and pending-tagged ones, or every row of a "Compact
    plan". A record supports a scenario when its selection or command names the scenario id, its test, the test's
    type or the test's method, or when a test check ran with selection `all`. Red runs (`red-<test>`) never count
  - no required check failed or is stale: the latest record of each check and selection, red runs, screenshots and
    recordings left out
  - no blocking finding is open in the latest review file: a Blocker or a Risk, or High or Medium
    (references/review-checklist.md part D), read from the findings table (Type, Severity, State columns) or from
    the `### <where> · <Type> · <Severity>` headings of part E. A finding is closed only when its state starts with
    "fixed"; a line saying a finding is "not fixed" keeps the verdict at Not ready
  - no test file changed after the red run that named it (`evidence.py held`): a test edited after it was seen
    failing has to be seen failing again
  - the plan still has the text that was approved, when it was sealed (`plan_seal.py check`)
Blocked: a required check fails on the current state and the review rounds are used up (the plan's "Rounds: at
  most <n>", default three; the rounds used are the highest round number in the review file names or their
  "## Round <n>" headings).
Not ready: otherwise, or when the run ended early (--ended-early, quoted), or when no review was read.

Gaps (never change the verdict): a delivered scenario with no screenshot or recording record (check `screenshot` or
`recording`, selection naming the scenario) on the current state; a plan with no seal. The report names each with
its reason.

Exit codes:
  0   Ready to accept
  1   Not ready
  2   not inside a git repository and no --root given
  3   Blocked
  64  wrong usage, or a file cannot be read
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evidence  # noqa: E402  (a sibling script: the change state and the evidence file are read the same way)

READY, NOT_READY, BLOCKED = 'Ready to accept', 'Not ready', 'Blocked'
EXIT = {READY: 0, NOT_READY: 1, BLOCKED: 3}
PICTURES = ('screenshot', 'recording')
BLOCKING_TYPES = {'blocker', 'risk'}
BLOCKING_SEVERITIES = {'high', 'medium'}
TYPES = {'blocker', 'risk', 'note'}
SEVERITIES = {'high', 'medium', 'low', 'nit'}
WORDS = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
COMMENT = re.compile(r'<!--.*?-->', re.S)
NAME = re.compile(r'[A-Za-z_][\w.]*')


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('%s: error: %s' % (self.prog, message), file=sys.stderr)
        sys.exit(64)


def read(path):
    try:
        return Path(path).read_text(encoding='utf-8')
    except OSError as error:
        print('cannot read %s: %s' % (path, error), file=sys.stderr)
        sys.exit(64)


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def tables(text):
    """[(h2, h3, header, rows)] with header cells lower-cased; HTML comments ignored."""
    found, h2, h3, block = [], '', '', []

    def close():
        if len(block) >= 2 and re.fullmatch(r'[\s|:-]+', block[1]):
            header = [c.lower() for c in cells(block[0])]
            rows = [cells(line) for line in block[2:]]
            found.append((h2, h3, header, [r + [''] * (len(header) - len(r)) for r in rows]))
        del block[:]

    for line in COMMENT.sub('', text).splitlines():
        if line.lstrip().startswith('|'):
            block.append(line)
            continue
        close()
        if line.startswith('## '):
            h2, h3 = line[3:].strip().lower(), ''
        elif line.startswith('### '):
            h3 = line[4:].strip().lower()
    close()
    return found


def column(header, row, *names):
    for name in names:
        for i, cell in enumerate(header):
            if name in cell:
                return row[i]
    return ''


def scenario_id(cell):
    first = re.split(r'\s+[—–-]\s+', cell.strip(), maxsplit=1)[0]
    return first.strip('`* ').lstrip('@')


def delivered_scenarios(plan_text):
    """[(id, [test names])], [notes]: from Result, else Compact plan, else Scenario changes."""
    all_tables = tables(plan_text)
    notes = []
    for h2, _, header, rows in all_tables:
        if 'result' in h2 and any('delivered' in c for c in header):
            picked = [r for r in rows if column(header, r, 'delivered').lower().startswith('yes')]
            if rows:
                return [(scenario_id(column(header, r, 'scenario')), tests_in(column(header, r, 'test'))) for r in picked], notes
    for h2, _, header, rows in all_tables:
        if 'compact plan' in h2 and any('scenario' in c for c in header):
            return [(scenario_id(column(header, r, 'scenario')), tests_in(column(header, r, 'test', 'proof')))
                    for r in rows], notes
    found = []
    for h2, h3, header, rows in all_tables:
        if 'scenario changes' not in h2 or h3 or 'change' not in header:
            continue
        for row in rows:
            change = column(header, row, 'change').lower()
            test = column(header, row, 'test')
            sid = scenario_id(column(header, row, 'scenario'))
            if change.startswith('remove') or change.startswith('not a gate scenario'):
                continue
            if test.strip().startswith('@'):
                notes.append('%s: not delivered by the plan (%s)' % (sid, test.strip()))
                continue
            found.append((sid, tests_in(test)))
    if found:
        notes.append('the plan\'s "Result" is not filled yet: every planned scenario is taken as delivered')
    return found, notes


def tests_in(cell):
    """Test names in a cell: identifiers with a dot, an underscore or a camelCase hump; plain words are prose."""
    names = [m.group(0).strip('.') for m in NAME.finditer(cell.replace('`', ' '))]
    return [n for n in names if '.' in n or '_' in n or re.search(r'[a-z][A-Z]', n)]


def mentions(text, word):
    return bool(word) and re.search(r'(?<![\w])%s(?![\w])' % re.escape(word), text) is not None


def supports(record, sid, tests):
    if str(record.get('selection', '')).startswith(evidence.RED):
        return False
    text = '%s %s' % (record.get('selection', ''), record.get('command', ''))
    if mentions(text, sid):
        return True
    for test in tests:
        parts = test.rsplit('.', 1)
        if any(mentions(text, name) for name in [test] + parts):
            return True
    check = str(record.get('check', ''))
    return check.startswith('test') and str(record.get('selection', '')).strip().lower() == 'all'


def rounds_limit(plan_text):
    match = re.search(r'Rounds:\s*at most\s+(\w+)|[Uu]p to\s+(\w+)\s+rounds', plan_text)
    word = (match.group(1) or match.group(2)).lower() if match else 'three'
    return int(word) if word.isdigit() else WORDS.get(word, 3)


def latest_review(path):
    target = Path(path)
    if target.is_file():
        return target
    if not target.is_dir():
        print('cannot read %s: no such file or folder' % target, file=sys.stderr)
        sys.exit(64)
    files = [p for p in target.glob('*.md') if 'review' in p.name.lower()]
    if not files:
        return None

    def key(p):
        numbers = [int(n) for n in re.findall(r'round-?(\d+)', p.name.lower())]
        return (max(numbers) if numbers else -1, p.stat().st_mtime, p.name)
    return max(files, key=key)


def findings(text):
    """[(label, where, state)] of every labelled finding, and the lines that say a finding is not fixed."""
    found = []
    for _, _, header, rows in tables(text):
        if not any('type' in c for c in header) or not any('severity' in c for c in header):
            continue
        for row in rows:
            kind = column(header, row, 'type')
            if kind.lower() not in TYPES:
                continue
            found.append(((kind, column(header, row, 'severity')), column(header, row, 'where') or row[0],
                          column(header, row, 'state')))
    lines = COMMENT.sub('', text).splitlines()
    for i, line in enumerate(lines):
        if not line.startswith('### '):
            continue
        parts = [p.strip().strip('*') for p in line[4:].split('·')]
        kind = next((p for p in parts if p.lower() in TYPES), '')
        if not kind:
            continue
        severity = next((p for p in parts if p.lower() in SEVERITIES), '')
        state = ''
        for body in lines[i + 1:]:
            if body.startswith('#'):
                break
            match = re.match(r'\s*\**\s*(?:final\s+)?state\s*\**\s*:\s*\**\s*(.*)', body, re.I)
            if match:
                state = match.group(1)
                break
        found.append(((kind, severity), parts[0].strip('` '), state))
    not_fixed = [l.strip() for l in lines if not l.lstrip().startswith('|') and re.search(r'\bnot fixed\b', l, re.I)]
    return found, not_fixed


def rounds_used(review, text):
    numbers = [int(n) for n in re.findall(r'round-?(\d+)', review.name.lower())]
    numbers += [int(n) for n in re.findall(r'^##\s+Round\s+(\d+)', text, re.M | re.I)]
    return max(numbers) if numbers else 1


def main():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('evidence')
    parser.add_argument('plan')
    parser.add_argument('--reviews', help='the folder of review files (the latest is read), or one review file')
    parser.add_argument('--ended-early', help='the reason the run ended early, quoted into the verdict')
    parser.add_argument('--root')
    args = parser.parse_args()

    plan_text = read(args.plan)
    records = evidence.load(args.evidence)
    current = evidence.change_state(evidence.find_root(args.root), [args.evidence])
    reasons, gaps, failing = [], [], []

    scenarios, notes = delivered_scenarios(plan_text)
    gaps += notes
    if not scenarios:
        reasons.append('the plan names no delivered scenario')
    for sid, tests in scenarios:
        own = [r for r in records if supports(r, sid, tests)]
        fresh = [r for r in own if r.get('state') == current]
        if any(r.get('exit') == 0 for r in fresh):
            pass
        elif fresh:
            reasons.append('%s: its evidence failed on the current state' % sid)
        elif own:
            reasons.append('%s: its evidence ran on an earlier version (stale), none on the current state' % sid)
        else:
            reasons.append('%s: no evidence record' % sid)
        pictures = [r for r in records if r.get('check') in PICTURES and r.get('exit') == 0
                    and r.get('state') == current and mentions('%s %s' % (r.get('selection', ''), r.get('command', '')), sid)]
        if not pictures:
            gaps.append('%s: no screenshot or recording on the current state' % sid)

    for record in evidence.latest(records):
        name = '%s [%s]' % (record.get('check'), record.get('selection'))
        if str(record.get('selection', '')).startswith(evidence.RED) or record.get('check') in PICTURES:
            continue
        if record.get('state') != current:
            reasons.append('check %s ran on an earlier version (stale)' % name)
        elif record.get('exit') != 0:
            reasons.append('check %s fails on the current state (exit %s)' % (name, record.get('exit')))
            failing.append(name)

    root = evidence.find_root(args.root)
    for selection, path, what in evidence.changed_since_red(root, records):
        reasons.append('test file %s after it was seen failing: %s [%s]; not seen failing in its current form' % (
            what, path, selection))
    import plan_seal  # a sibling script, read the same way the plan skill writes it
    if not plan_seal.seal_path(args.plan).exists():
        gaps.append('the plan has no seal: its text cannot be compared with what was approved')
    else:
        import json
        sealed = json.loads(plan_seal.seal_path(args.plan).read_text(encoding='utf-8'))
        now = plan_seal.sections(args.plan)
        if plan_seal.whole(now) != sealed.get('hash'):
            names = [n or 'the header' for n in list(sealed.get('sections', {})) + [k for k in now if k not in sealed.get('sections', {})]
                     if sealed.get('sections', {}).get(n) != now.get(n)]
            reasons.append('the plan changed after approval: %s' % '; '.join(names))

    used, limit = None, rounds_limit(plan_text)
    if not args.reviews:
        reasons.append('no review read (--reviews): open findings unknown')
    else:
        review = latest_review(args.reviews)
        if review is None:
            reasons.append('no review file in %s' % args.reviews)
        else:
            text = read(review)
            used = rounds_used(review, text)
            found, not_fixed = findings(text)
            for (kind, severity), where, state in found:
                blocking = kind.lower() in BLOCKING_TYPES or severity.lower() in BLOCKING_SEVERITIES
                if blocking and not re.match(r'\s*fixed\b', state, re.I):
                    label = ' · '.join(p for p in (kind, severity) if p)
                    reasons.append('open blocking finding in %s: %s at %s (state: %s)' % (
                        review.name, label, where, state or 'open'))
            for line in not_fixed:
                reasons.append('%s says a finding is not fixed: "%s"' % (review.name, line))

    if args.ended_early:
        reasons.insert(0, 'the run ended early: "%s"' % args.ended_early)
        verdict = NOT_READY
    elif failing and used is not None and used >= limit:
        verdict = BLOCKED
        reasons.insert(0, 'a required check still fails after round %d of %d' % (used, limit))
    elif reasons:
        verdict = NOT_READY
    else:
        verdict = READY
        reasons = ['every delivered scenario (%d) has a passing record on the current state' % len(scenarios),
                   'no required check failed or is stale',
                   'no blocking finding is open in the latest review']

    print(verdict)
    print('Reasons:')
    for reason in reasons:
        print('- ' + reason)
    print('Gaps (do not change the verdict):')
    for gap in gaps or ['none']:
        print('- ' + gap)
    print('Current state: %s · Records: %d · Rounds: %s of %d' % (
        current, len(records), used if used is not None else 'unknown', limit))
    return EXIT[verdict]


if __name__ == '__main__':
    sys.exit(main())
