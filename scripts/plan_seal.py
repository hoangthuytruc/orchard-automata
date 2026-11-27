#!/usr/bin/env python3
"""Bind a plan's approval to the text that was approved.

  plan_seal.py seal <plan.md>     record the hash of the plan's approved text in <plan.md>.seal.json
  plan_seal.py check <plan.md>    say whether the plan still has the text that was sealed
  plan_seal.py hash <plan.md>     print the hash of the plan's approved text as it stands, writing nothing (a plan
                                  verifier quotes it, so its result is tied to the text it read)

The approved text is the plan file without the parts later steps are meant to write: the `Status:` line, the
`## Result` section (written by run) and the `## Change note` section (written by update-docs). Everything else
(scope, requirements, design change, scenario changes, work packages, rounds and locks, the compact table) is what
the developer approved. `plan` seals when the developer approves; `run` checks before round 1 and before the
report. An edit after approval breaks the seal: the plan goes back to the developer, who approves the new text
(a new seal) or restores the old one. Line endings and trailing spaces do not count.

Exit codes:
  0   seal written; hash printed; or check: the text is the sealed one
  1   check: the text changed since the seal (the first differing section is named)
  2   check: no seal for this plan
  64  wrong usage, or a file cannot be read
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

UNSEALED = re.compile(r'^##\s+(Result|Change note)\b', re.I)
HEADING = re.compile(r'^#{1,2}\s')


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('%s: error: %s' % (self.prog, message), file=sys.stderr)
        sys.exit(64)


def sections(path):
    """The approved text as {heading: hash}, in order; the text before the first heading is under ''."""
    try:
        text = Path(path).read_text(encoding='utf-8')
    except OSError as error:
        print('cannot read %s: %s' % (path, error), file=sys.stderr)
        sys.exit(64)
    parts, name, skip = {'': []}, '', False
    for line in text.splitlines():
        line = line.rstrip()
        if HEADING.match(line):
            skip = bool(UNSEALED.match(line))
            name = line
            if not skip:
                while name in parts:
                    name += ' (again)'
                parts[name] = []
            continue
        if skip or line.startswith('Status:'):
            continue
        parts[name].append(line)
    return {name: hashlib.sha256('\n'.join(lines).strip().encode()).hexdigest()[:12] for name, lines in parts.items()}


def whole(parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=False).encode()).hexdigest()[:12]


def seal_path(plan):
    return Path(str(plan) + '.seal.json')


def cmd_seal(args):
    parts = sections(args.plan)
    seal = {'hash': whole(parts), 'sections': parts, 'time': datetime.now(timezone.utc).isoformat(timespec='seconds')}
    seal_path(args.plan).write_text(json.dumps(seal, indent=2) + '\n', encoding='utf-8')
    print('plan seal: %s -> %s' % (seal['hash'], seal_path(args.plan)))
    return 0


def cmd_hash(args):
    print(whole(sections(args.plan)))
    return 0


def cmd_check(args):
    if not seal_path(args.plan).exists():
        print('plan seal: none for %s' % args.plan)
        return 2
    try:
        seal = json.loads(seal_path(args.plan).read_text(encoding='utf-8'))
        sealed = seal['sections']
    except (OSError, ValueError, KeyError) as error:
        print('cannot read %s: %s' % (seal_path(args.plan), error), file=sys.stderr)
        return 64
    now = sections(args.plan)
    if whole(now) == seal.get('hash'):
        print('plan seal: holds (%s, sealed %s)' % (seal['hash'], seal.get('time', '?')))
        return 0
    for name in list(sealed) + [n for n in now if n not in sealed]:
        if sealed.get(name) != now.get(name):
            what = 'added' if name not in sealed else 'removed' if name not in now else 'changed'
            print('plan seal: broken, %s since approval: %s' % (what, name or 'the header'))
    return 1


def main():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='cmd', required=True, parser_class=Parser)
    for name, fn in (('seal', cmd_seal), ('check', cmd_check), ('hash', cmd_hash)):
        command = sub.add_parser(name)
        command.add_argument('plan')
        command.set_defaults(fn=fn)
    args = parser.parse_args()
    return args.fn(args)


if __name__ == '__main__':
    sys.exit(main())
