#!/usr/bin/env python3
"""Find text that must not ship in the core skill set: private paths, project names, ticket keys, model names, emails.

  leak_check.py [path ...]

With no path, scans these folders of the skill set: skills, references, scripts, roles, workflows, templates,
adapters, evals. Folders are walked; sample/, docs/skill-set-plan.md and THIRD_PARTY_NOTICES.md are always left out
of a walk, as are .git and build folders. A file named on the command line is scanned as given. A line that carries
the comment `leak-check: allow` is skipped. Binary files are skipped.

Prints one line per hit: `path:line: pattern: text`.

Exit codes:
  0   no hit
  1   at least one hit
  64  wrong usage, or a named path does not exist
"""
import argparse
import os
import re
import sys
from pathlib import Path

ORCHARD = Path(__file__).resolve().parents[1]
DEFAULT_DIRS = ('skills', 'references', 'scripts', 'roles', 'workflows', 'templates', 'adapters', 'evals')
EXCLUDED = {'sample', 'docs/skill-set-plan.md', 'THIRD_PARTY_NOTICES.md'}
SKIP_DIRS = {'.git', '.build', 'build', 'DerivedData', 'node_modules', '__pycache__', 'results'}
ALLOW = 'leak-check: allow'
PATTERNS = [  # leak-check: allow (the patterns name what they look for)
    ('home path', re.compile(r'/Users/')),  # leak-check: allow
    ('tool home', re.compile(r'~/\.claude')),  # leak-check: allow
    ('model name', re.compile(r'\b(?:sonnet|opus|haiku|fable)\b|\bgpt-\d|\bclaude-[a-z]+-\d', re.I)),  # leak-check: allow
    ('email', re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b')),
]


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('%s: error: %s' % (self.prog, message), file=sys.stderr)
        sys.exit(64)


def excluded(path):
    try:
        relative = path.resolve().relative_to(ORCHARD).as_posix()
    except ValueError:
        return False
    return any(relative == e or relative.startswith(e + '/') for e in EXCLUDED)


def walk(root):
    if root.is_file():
        yield root
        return
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not excluded(Path(folder) / d))
        for name in sorted(files):
            path = Path(folder) / name
            if not excluded(path):
                yield path


def scan(path):
    try:
        data = path.read_bytes()
    except OSError:
        return []
    if b'\0' in data[:4096]:
        return []
    hits = []
    for number, line in enumerate(data.decode('utf-8', errors='replace').splitlines(), 1):
        if ALLOW in line:
            continue
        for name, pattern in PATTERNS:
            if pattern.search(line):
                hits.append('%s:%d: %s: %s' % (path, number, name, line.strip()[:160]))
    return hits


def main():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('paths', nargs='*', type=Path)
    args = parser.parse_args()
    if args.paths:
        missing = [str(p) for p in args.paths if not p.exists()]
        if missing:
            parser.error('no such path: %s' % ', '.join(missing))
        targets = [(p, p.is_file()) for p in args.paths]
    else:
        targets = [(ORCHARD / d, False) for d in DEFAULT_DIRS if (ORCHARD / d).exists()]
    hits, files = [], 0
    for target, named in targets:
        for path in ([target] if named else walk(target)):
            files += 1
            found = scan(path)
            hits += [h.replace(str(ORCHARD) + os.sep, '', 1) for h in found]
    for hit in hits:
        print(hit)
    print('leak check: %d file(s), %s' % (files, '%d hit(s)' % len(hits) if hits else 'clean'))
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(main())
