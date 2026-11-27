#!/usr/bin/env python3
"""Check a project profile (.orchard/profile.md): required keys have a value, and file sources have not changed.

  profile_check.py stamp <profile> [--root R]   rewrite every `file:<path>` or `file:<path>#<old>` source to
                                                `file:<path>#<first 8 hex of sha256>`
  profile_check.py check <profile> [--root R] [--skill S]
                                                are the required keys filled, and do the file sources still hash the
                                                same? With --skill, only the keys that skill reads (column "Read by")
  profile_check.py get <profile> <key>          print the value of one key: its first code span (`...`) when the
                                                cell has one, else the whole cell

The profile is made of Markdown tables with the columns Key | Value | Source. The required keys are the ones marked
(R) in templates/project-profile.md of this skill set, and the skills that read each key are the code spans of its
"Read by" cell there (both read at run time; --template points elsewhere). `check --skill <name>` reports only the
keys that skill reads: a missing required key it reads (exit 2), a changed or untracked source of a key it reads
(exit 3). Without --skill every key is checked; `plan` and `run` read every required key, so theirs is the full check. A value is missing when the row
is absent, the cell is empty, it says `missing`, or it is still a `<placeholder>`. The knowledge base keys
(`knowledge_base`, `knowledge_base_check`, `locked_globs`) are also missing when they say `none` or `n/a`: every
project keeps Gherkin feature files (templates/project-profile.md, section Knowledge base). The optional
`tag_policy_untested` saying `none` or `n/a` counts as absent, so the core default applies.
File source paths are relative to the project root: by default the folder that holds `.orchard/`. A source may sit in
backticks or parentheses, or among other sources: the path stops at whitespace, #, ;, ,, |, a backtick, a bracket, a
parenthesis or a quote, and never ends in . or : (the forms are listed in templates/project-profile.md). A file
source must be a file git tracks from the project root (`git ls-files --error-unmatch`); a value read from an
untracked or ignored file is recorded as `stated: <who> <date>` instead.

Exit codes:
  0   check: every required key has a value and every file source hashes the same. stamp, get: done
  1   stamp: a source file could not be read (the others are stamped)
  2   check: a required key is missing (listed).
      get: the key is absent or missing
  3   check: a file source changed, is gone, was never stamped, or is not tracked by git (listed with its key).
      stamp: a file source is not tracked by git (listed, not stamped; the others are stamped)
  64  wrong usage, the profile or template cannot be read, or --skill names a skill this skill set does not have
"""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ORCHARD = Path(__file__).resolve().parents[1]
TEMPLATE = ORCHARD / 'templates' / 'project-profile.md'
SOURCE = re.compile(r'''file:([^\s#;,|`()\[\]<>"']*[^\s#;,|`()\[\]<>"'.:])(?:#([0-9a-fA-F]*))?''')
CODE_SPAN = re.compile(r'`([^`]+)`')
REQUIRED = re.compile(r'^(\S+)\s+\(R\)$')
SKILLS = ORCHARD / 'skills'
NO_NONE = ('knowledge_base', 'knowledge_base_check', 'tag_policy_untested', 'locked_globs')
NONE_VALUE = re.compile(r'(none|n/a)(?![\w/])', re.I)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('%s: error: %s' % (self.prog, message), file=sys.stderr)
        sys.exit(64)


def cells(line):
    return [c.strip() for c in re.split(r'(?<!\\)\|', line.strip().strip('|'))]


def rows(path, column='source'):
    """Yield (line index, key, value, <column>) for every row of a Key | Value | Source table."""
    header = None
    for index, raw in enumerate(path.read_text(encoding='utf-8').splitlines()):
        line = raw.strip()
        if not line.startswith('|'):
            header = None
            continue
        row = cells(line)
        if all(re.fullmatch(r':?-{3,}:?', c) for c in row):
            continue
        if header is None:
            header = [c.lower() for c in row]
            continue
        if not header or header[0] != 'key':
            continue
        named = dict(zip(header, row))
        yield index, named.get('key', '').strip('`'), named.get('value', ''), named.get(column, '')


def required_keys(template):
    keys = []
    for _, key, _, _ in rows(template):
        match = REQUIRED.match(key)
        if match:
            keys.append(match.group(1).strip('`'))
    return keys


def read_by(template):
    """key -> set of skill names in its "Read by" cell."""
    found = {}
    for _, key, _, cell in rows(template, 'read by'):
        match = REQUIRED.match(key)
        found[match.group(1) if match else key] = set(CODE_SPAN.findall(cell))
    return found


def untracked(root, paths):
    """The paths, relative to root, that git does not track (all of them when root is not in a git work tree)."""
    out = []
    for path in paths:
        try:
            done = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', path], cwd=str(root),
                                  capture_output=True, text=True)
            tracked = done.returncode == 0
        except OSError:
            tracked = False
        if not tracked:
            out.append(path)
    return out


def profile_values(profile):
    """key -> (value, source); the (R) mark is dropped if a profile kept it."""
    found = {}
    for _, key, value, source in rows(profile):
        match = REQUIRED.match(key)
        found[match.group(1) if match else key] = (value, source)
    return found


def is_missing(value, key=None):
    text = value.strip().strip('`').strip()
    if key in NO_NONE and NONE_VALUE.match(text):
        return True
    return not text or text.lower() == 'missing' or (text.startswith('<') and text.endswith('>'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def default_root(profile):
    parent = profile.resolve().parent
    return parent.parent if parent.name == '.orchard' else Path.cwd()


def read_or_exit(path):
    if not path.is_file():
        print('cannot read %s' % path, file=sys.stderr)
        sys.exit(64)


def cmd_check(args):
    read_or_exit(args.profile)
    read_or_exit(args.template)
    root = args.root or default_root(args.profile)
    values = profile_values(args.profile)
    required = required_keys(args.template)
    scope = None
    if args.skill:
        if not (SKILLS / args.skill / 'SKILL.md').is_file():
            print('unknown skill: %s' % args.skill, file=sys.stderr)
            return 64
        scope = {key for key, skills in read_by(args.template).items() if args.skill in skills}
        required = [key for key in required if key in scope]
    missing = [key for key in required if key not in values or is_missing(values[key][0], key)]
    changed = []
    sources = [(key, path, recorded) for key, (_, source) in values.items() if scope is None or key in scope
               for path, recorded in SOURCE.findall(source)]
    not_tracked = set(untracked(root, sorted({path for _, path, _ in sources})))
    for key, path, recorded in sources:
        target = root / path
        if not target.is_file():
            changed.append('%s: %s (recorded %s, file not found)' % (key, path, recorded or 'no hash'))
        elif path in not_tracked:
            changed.append('%s: %s (not tracked by git; record the value as stated: <who> <date>)' % (key, path))
        elif not recorded:
            changed.append('%s: %s (not stamped; run stamp)' % (key, path))
        elif digest(target) != recorded.lower():
            changed.append('%s: %s (recorded %s, now %s)' % (key, path, recorded, digest(target)))
    print('profile: %s (%d keys%s)' % (args.profile, len(values),
                                      '; checked for %s: %d' % (args.skill, len(scope)) if scope is not None else ''))
    if missing:
        print('missing required keys (%d):' % len(missing))
        print('\n'.join('  - ' + key for key in missing))
    if changed:
        print('changed sources (%d): discover these keys again, and confirm any value that differs' % len(changed))
        print('\n'.join('  - ' + line for line in changed))
    if missing:
        return 2
    if changed:
        return 3
    print('profile check: OK')
    return 0


def cmd_stamp(args):
    read_or_exit(args.profile)
    root = args.root or default_root(args.profile)
    lines = args.profile.read_text(encoding='utf-8').split('\n')
    failed, stamped = [], 0
    not_tracked = set(untracked(root, sorted({m.group(1) for _, _, _, source in rows(args.profile)
                                               for m in SOURCE.finditer(source)})))
    rejected = []

    def replace(match):
        nonlocal stamped
        target = root / match.group(1)
        if not target.is_file():
            failed.append(match.group(1))
            return match.group(0)
        if match.group(1) in not_tracked:
            rejected.append(match.group(1))
            return match.group(0)
        stamped += 1
        return 'file:%s#%s' % (match.group(1), digest(target))

    for index, _, _, _ in rows(args.profile):
        line = lines[index]
        pipes = [m.start() for m in re.finditer(r'(?<!\\)\|', line)]
        if len(pipes) < 2:
            continue
        start, end = (pipes[-2], pipes[-1]) if line.rstrip().endswith('|') else (pipes[-1], len(line))
        lines[index] = line[:start] + SOURCE.sub(replace, line[start:end]) + line[end:]
    args.profile.write_text('\n'.join(lines), encoding='utf-8')
    print('stamped %d file source(s) in %s' % (stamped, args.profile))
    for path in failed:
        print('cannot read source file: %s' % path, file=sys.stderr)
    for path in sorted(set(rejected)):
        print('not tracked by git, not stamped: %s (record the value as stated: <who> <date>)' % path,
              file=sys.stderr)
    if rejected:
        return 3
    return 1 if failed else 0


def cmd_get(args):
    read_or_exit(args.profile)
    values = profile_values(args.profile)
    if args.key not in values or is_missing(values[args.key][0], args.key):
        print('%s: missing' % args.key, file=sys.stderr)
        return 2
    value = values[args.key][0].strip()
    span = CODE_SPAN.search(value)
    print(span.group(1) if span else value)
    return 0


def main():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True, parser_class=Parser)
    for name, fn in (('stamp', cmd_stamp), ('check', cmd_check)):
        command = sub.add_parser(name)
        command.add_argument('profile', type=Path)
        command.add_argument('--root', type=Path, help='project root (default: the folder that holds .orchard/)')
        command.add_argument('--template', type=Path, default=TEMPLATE, help='profile template with (R) marks')
        command.set_defaults(fn=fn, skill=None)
        if name == 'check':
            command.add_argument('--skill', help='check only the keys this skill reads (column "Read by")')
    get = sub.add_parser('get')
    get.add_argument('profile', type=Path)
    get.add_argument('key')
    get.set_defaults(fn=cmd_get)
    args = parser.parse_args()
    return args.fn(args)


if __name__ == '__main__':
    sys.exit(main())
