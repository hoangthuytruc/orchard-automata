#!/usr/bin/env python3
"""Prove that locked files did not change while a plan was being carried out.

  lock_check.py snapshot <snapshot.json> <glob>... [--root R]   record the content hash of every file the globs match
  lock_check.py verify <snapshot.json>                         list every locked file changed, added or removed

Globs are relative to the root (default: the current directory) and may use ** (for example 'docs/**/*.feature').
A glob starting with ! removes what it matches from the others (for example '.orchard/**' '!.orchard/runs/**').
The profile key `locked_globs` names them (default in templates/project-profile.md). The snapshot keeps the globs,
so verify also catches a new file that matches one. A glob whose folder (the part before the first wildcard) exists
but matches no file is valid and locks an empty set: a file that appears there later breaks the lock. A glob whose
folder does not exist is listed; it too breaks the lock if a matching file appears. Content hashes are used rather than git status, because a locked file
may already carry uncommitted changes when the work starts. Keep the snapshot outside the locked globs, in the
plan's folder.

Exit codes:
  0   snapshot written; or verify: the lock holds
  1   verify: a locked file changed, was added or was removed (listed)
  2   snapshot: no glob's folder exists
  64  wrong usage, or the snapshot cannot be read
"""
import argparse
import glob
import hashlib
import json
import os
import sys


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('%s: error: %s' % (self.prog, message), file=sys.stderr)
        sys.exit(64)


def files_of(pattern):
    return {os.path.normpath(path) for path in glob.glob(pattern, recursive=True) if os.path.isfile(path)}


def matched(patterns):
    paths, removed = set(), set()
    for pattern in patterns:
        if pattern.startswith('!'):
            removed |= files_of(pattern[1:])
        else:
            paths |= files_of(pattern)
    return sorted(paths - removed)


def folder(pattern):
    """The folder a glob looks in: its path up to the first part with a wildcard."""
    parts = []
    for part in pattern.split('/')[:-1]:
        if glob.has_magic(part):
            break
        parts.append(part)
    return os.path.join(*parts) if parts else '.'


def digest(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def snapshot(args):
    out = os.path.abspath(args.snapshot)
    os.chdir(args.root)
    adding = [g for g in args.globs if not g.startswith('!')]
    absent = [g for g in adding if not os.path.isdir(folder(g))]
    if len(absent) == len(adding):
        print('no folder of these globs exists: %s' % ' '.join(adding), file=sys.stderr)
        return 2
    files = {path: digest(path) for path in matched(args.globs)}
    empty = [g for g in adding if g not in absent and not (files_of(g) & set(files))]
    with open(out, 'w', encoding='utf-8') as handle:
        json.dump({'root': os.getcwd(), 'globs': args.globs, 'files': files, 'empty': empty, 'no_folder': absent},
                  handle, indent=2)
    print('locked %d files -> %s' % (len(files), args.snapshot))
    if empty:
        print('locked as empty (a file appearing breaks the lock): %s' % ' '.join(empty))
    if absent:
        print('no folder yet (a file appearing breaks the lock): %s' % ' '.join(absent))
    return 0


def verify(args):
    try:
        with open(args.snapshot, encoding='utf-8') as handle:
            data = json.load(handle)
        os.chdir(data['root'])
    except (OSError, ValueError, KeyError) as error:
        print('cannot read snapshot %s: %s' % (args.snapshot, error), file=sys.stderr)
        return 64
    before, now = data['files'], matched(data['globs'])
    problems = ['changed: %s' % name for name in before if name in now and digest(name) != before[name]]
    problems += ['removed: %s' % name for name in before if name not in now]
    problems += ['added:   %s' % name for name in now if name not in before]
    if problems:
        print('LOCK BROKEN (%d)' % len(problems))
        print('\n'.join(sorted(problems)))
        return 1
    print('lock holds: %d files unchanged' % len(before))
    return 0


def main():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True, parser_class=Parser)
    snap = sub.add_parser('snapshot')
    snap.add_argument('snapshot')
    snap.add_argument('globs', nargs='+')
    snap.add_argument('--root', default='.', help='folder the globs are relative to (default: current directory)')
    snap.set_defaults(fn=snapshot)
    check = sub.add_parser('verify')
    check.add_argument('snapshot')
    check.set_defaults(fn=verify)
    args = parser.parse_args()
    return args.fn(args)


if __name__ == '__main__':
    sys.exit(main())
