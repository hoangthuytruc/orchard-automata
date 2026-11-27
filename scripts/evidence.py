#!/usr/bin/env python3
"""Record which check ran, on which state of the change, with what result. The evidence behind `Verify → Review`.

  evidence.py state [--root R]
      print the change state: the first 12 hex of sha256 over the HEAD commit id, `git diff HEAD --binary` and the
      path and content of every untracked file that git does not ignore
  evidence.py record <evidence.jsonl> --check <kind> --selection <text> [--root R] -- <command...>
      run the command in the root, show its output, and append one record: check, selection, command, exit,
      duration_s, summary (last 15 lines of output), failures (up to 10 lines that look like an error or a failed assertion), state, time. One argument after -- runs through the shell
      (for `swift build && swift test`); several run as given
  evidence.py stale <evidence.jsonl> [--root R]
      list the checks whose latest record was made on another state than the current one. A red run (selection
      `red-<test>`: a new test run before its code existed, references/run-flow.md section 3) is left out: it is
      meant to have run on an earlier state
  evidence.py table <evidence.jsonl> [--root R]
      print the "Checks run" table of templates/test-report.md; a stale row says so in "Ran on", a red run says
      "before the code". Summary: a failed
      check's first failure line; a passing check's last XCTest or Swift Testing summary with a non-zero test count,
      else its last line

<kind> is a profile command key: build, test.unit, test.behaviour, test.visual, test.integration, lint, pr_check,
knowledge_base_check, or another short name. The evidence file itself is left out of the state, so it may sit in
the project; keep it in the plan's folder. Root defaults to the git top level of the current directory.

Exit codes:
  record: the command's own exit code (127 when it cannot be started)
  state, table: 0
  stale: 0 when every check's latest record matches the current state, 1 when one does not (listed)
  2   not inside a git repository and no --root given (with --root, the state hashes the files: nogit-)
  64  wrong usage, or the evidence file cannot be read
"""
import argparse
import collections
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SUMMARY_LINES = 15
FAILURE_LINES = 10
RED = 'red-'
FAILURE_PATTERN = re.compile(r'(\berror:|\bfailed\b|\bFAIL(ED)?\b|fatal error|Assertion failed)')
# XCTest: "Executed 3 tests, with 0 failures"; Swift Testing: "Test run with 3 tests in 1 suite passed"
TEST_SUMMARY = re.compile(r'\bExecuted (\d+) tests?\b|\bTest run with (\d+) tests?\b')


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('%s: error: %s' % (self.prog, message), file=sys.stderr)
        sys.exit(64)


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True)


def find_root(given):
    start = Path(given) if given else Path.cwd()
    try:
        done = git(start, 'rev-parse', '--show-toplevel')
    except OSError:
        done = None
    if done is not None and done.returncode == 0:
        return Path(done.stdout.decode().strip())
    if given:
        # git cannot run here, or this is not a work tree: the given root is used and the state hashes files.
        print('git not usable at %s: the state hashes the files themselves (nogit-)' % start, file=sys.stderr)
        return start.resolve()
    print('not inside a git repository: %s (pass --root to hash the files without git)' % start, file=sys.stderr)
    sys.exit(2)


FILES_SKIP_DIRS = {'.git', '.build', '.swiftpm', 'DerivedData', 'build', 'node_modules', 'Pods'}


def git_usable(root):
    """False when git cannot run here (not installed, blocked by a sandbox) or the root is not a work tree."""
    try:
        return git(root, 'rev-parse', '--is-inside-work-tree').returncode == 0
    except OSError:
        return False


def files_state(root, skip):
    """Without git: first 12 hex of sha256 over every file's path and content, build output and run output left out."""
    sha = hashlib.sha256()
    for path in sorted(p for p in root.rglob('*') if p.is_file()):
        rel = path.relative_to(root).as_posix()
        parts = rel.split('/')
        if FILES_SKIP_DIRS & set(parts[:-1]) or rel.startswith('.orchard/runs/') or rel in skip:
            continue
        sha.update(rel.encode() + b'\0')
        try:
            sha.update(path.read_bytes())
        except OSError:
            sha.update(b'<unreadable>')
    return sha.hexdigest()[:12]


def change_state(root, exclude=()):
    """First 12 hex of sha256(HEAD id + diff against HEAD + untracked files), leaving out `exclude` paths.
    Where git cannot run, `nogit-` + a hash of the files themselves (see files_state)."""
    skip = set()
    for path in exclude:
        try:
            skip.add(Path(path).resolve().relative_to(root.resolve()).as_posix())
        except ValueError:
            pass
    if not git_usable(root):
        return 'nogit-' + files_state(root, skip)
    pathspec = ['--', '.'] + [':(exclude)%s' % p for p in sorted(skip)]
    sha = hashlib.sha256()
    head = git(root, 'rev-parse', 'HEAD')
    sha.update(head.stdout.strip() if head.returncode == 0 else b'no-head')
    if head.returncode == 0:
        sha.update(git(root, 'diff', 'HEAD', '--binary', *pathspec).stdout)
    else:
        sha.update(git(root, 'diff', '--cached', '--binary', *pathspec).stdout)
    untracked = git(root, 'ls-files', '--others', '--exclude-standard', '-z').stdout.split(b'\0')
    for name in sorted(n for n in untracked if n):
        if name.decode(errors='replace') in skip:
            continue
        sha.update(b'\0' + name + b'\0')
        try:
            sha.update((root / name.decode(errors='surrogateescape')).read_bytes())
        except OSError:
            sha.update(b'<unreadable>')
    return sha.hexdigest()[:12]


def load(path):
    if not Path(path).exists():
        return []
    try:
        with open(path, encoding='utf-8') as handle:
            return [json.loads(line) for line in handle if line.strip()]
    except (OSError, ValueError) as error:
        print('cannot read %s: %s' % (path, error), file=sys.stderr)
        sys.exit(64)


def latest(records):
    by_check = collections.OrderedDict()
    for record in records:
        by_check[(record.get('check'), record.get('selection'))] = record
    return list(by_check.values())


def cmd_state(args):
    print(change_state(find_root(args.root)))
    return 0


def cmd_record(args):
    command = args.command
    if not command:
        print('no command given after --', file=sys.stderr)
        return 64
    root = find_root(args.root)
    state = change_state(root, [args.evidence])
    shell = len(command) == 1
    shown = command[0] if shell else shlex.join(command)
    tail = collections.deque(maxlen=SUMMARY_LINES)
    failures = []
    started = time.monotonic()
    try:
        process = subprocess.Popen(command[0] if shell else command, shell=shell, cwd=str(root),
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as error:
        print('cannot start %s: %s' % (shown, error), file=sys.stderr)
        code, tail = 127, collections.deque(['cannot start: %s' % error])
    else:
        for raw in process.stdout:
            sys.stdout.buffer.write(raw)
            sys.stdout.flush()
            line = raw.decode(errors='replace').rstrip('\n')
            tail.append(line)
            if len(failures) < FAILURE_LINES and FAILURE_PATTERN.search(line):
                failures.append(line.strip())
        code = process.wait()
        if code < 0:
            code = 128 - code  # killed by a signal: report it the way a shell does
    record = {
        'check': args.check,
        'selection': args.selection,
        'command': shown,
        'exit': code,
        'duration_s': round(time.monotonic() - started, 1),
        'summary': '\n'.join(tail),
        'failures': failures,
        'state': state,
        'time': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }
    after = change_state(root, [args.evidence])
    if after != state:
        record['state_after'] = after
        print('note: the command changed the working tree (%s -> %s)' % (state, after), file=sys.stderr)
    Path(args.evidence).parent.mkdir(parents=True, exist_ok=True)
    with open(args.evidence, 'a', encoding='utf-8') as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + '\n')
    print('evidence: %s exit %d on state %s -> %s' % (args.check, code, state, args.evidence))
    return code


def cmd_stale(args):
    current = change_state(find_root(args.root), [args.evidence])
    records = [r for r in latest(load(args.evidence)) if not str(r.get('selection', '')).startswith(RED)]
    stale = [r for r in records if r.get('state') != current]
    for record in stale:
        print('stale: %s [%s] ran on %s, now %s' % (record.get('check'), record.get('selection'), record.get('state'), current))
    print('%d of %d checks stale (current state %s)' % (len(stale), len(records), current))
    return 1 if stale else 0


def cell(text):
    return ' '.join(str(text).split()).replace('|', '\\|')


def summary_line(record, lines):
    """A failed check shows its first failure line (an assertion, a compile error), not the last line. A passing
    check shows the last XCTest or Swift Testing summary that counts at least one test, then the last line."""
    if record.get('exit') not in (0, None) and record.get('failures'):
        return record['failures'][0]
    counted = [line for line in lines if any(int(m.group(1) or m.group(2)) > 0 for m in TEST_SUMMARY.finditer(line))]
    if counted:
        return counted[-1]
    return lines[-1] if lines else ''


def cmd_table(args):
    current = change_state(find_root(args.root), [args.evidence])
    print('| Check | Command | Selection | Ran on | Exit | Summary | Time |')
    print('| --- | --- | --- | --- | --- | --- | --- |')
    for record in load(args.evidence):
        lines = [line for line in record.get('summary', '').splitlines() if line.strip()]
        ran_on = record.get('state', '')
        if str(record.get('selection', '')).startswith(RED):
            ran_on += ' (before the code)'
        elif ran_on != current:
            ran_on += ' (stale)'
        print('| %s | `%s` | %s | %s | %s | %s | %s s |' % (
            cell(record.get('check', '')), cell(record.get('command', '')).replace('`', "'"),
            cell(record.get('selection', '')), ran_on, record.get('exit', ''),
            cell(summary_line(record, lines)), record.get('duration_s', '')))
    return 0


def main():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='cmd', required=True, parser_class=Parser)
    state = sub.add_parser('state')
    state.add_argument('--root')
    state.set_defaults(fn=cmd_state)
    record = sub.add_parser('record', usage='%(prog)s <evidence.jsonl> --check KIND --selection TEXT [--root R] -- <command...>')
    record.add_argument('evidence')
    record.add_argument('--check', required=True, help='kind of check: a profile command key')
    record.add_argument('--selection', required=True, help='what ran: suites, files, "all"')
    record.add_argument('--root')
    record.set_defaults(fn=cmd_record)
    for name, fn in (('stale', cmd_stale), ('table', cmd_table)):
        command = sub.add_parser(name)
        command.add_argument('evidence')
        command.add_argument('--root')
        command.set_defaults(fn=fn)
    argv, command = sys.argv[1:], []
    if argv and argv[0] == 'record' and '--' in argv:
        split = argv.index('--')
        argv, command = argv[:split], argv[split + 1:]
    args = parser.parse_args(argv)
    args.command = command
    return args.fn(args)


if __name__ == '__main__':
    sys.exit(main())
