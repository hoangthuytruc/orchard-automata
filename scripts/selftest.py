#!/usr/bin/env python3
"""Run every script of this folder against a temporary copy of sample/Ledger and check its exit codes.

  selftest.py [--keep]

The copy is made in a new temporary folder, turned into its own git repository with one commit, and removed at the
end (--keep leaves it and prints where). Nothing touches the network: the Figma adapter is only run without a token,
and the review poster only with --dry-run on a saved files reply. Prints one line per check.

Exit codes:
  0   every check passed
  1   at least one check failed (the line starts with FAIL)
  64  wrong usage, or the sample cannot be copied
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORCHARD = HERE.parent
SAMPLE = ORCHARD / 'sample' / 'Ledger'
results = []


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('%s: error: %s' % (self.prog, message), file=sys.stderr)
        sys.exit(64)


def run(args, cwd, env=None, script=True):
    """Run a script of this folder (or a plain command when script is False); return (exit, combined output)."""
    if script:
        name = args[0]
        command = (['bash', str(HERE / name)] if name.endswith('.sh')
                   else [sys.executable, '-I', str(HERE / name)]) + list(args[1:])
    else:
        command = list(args)
    merged = dict(os.environ, **(env or {}))
    for key in [k for k, v in merged.items() if v is None]:
        del merged[key]
    done = subprocess.run(command, cwd=str(cwd), env=merged, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def check(name, args, cwd, want=0, contains=(), env=None, script=True, absent=()):
    code, out = run(args, cwd, env, script)
    missing = [text for text in contains if not re.search(text, out, re.M)]
    present = [text for text in absent if re.search(text, out, re.M)]
    ok = (code in (0, 1) if want is None else code == want) and not missing and not present
    detail = '' if ok else ' (exit %s, wanted %s%s%s)\n%s' % (
        code, want, '; output lacks %s' % missing if missing else '', '; output has %s' % present if present else '',
        '\n'.join('    ' + l for l in out.splitlines()[-12:]))
    print('%s %s%s' % ('PASS' if ok else 'FAIL', name, detail))
    results.append(ok)
    return out


def edit(path, append):
    with open(path, 'a', encoding='utf-8') as handle:
        handle.write(append)


REGISTER = """# Purchases: requirements register

## Scenarios
| Scenario | Basis | Spec clause or evidence | Tests |
| --- | --- | --- | --- |
| @TS_LED_001 | Spec | purchases-v3 2.1 | TransactionStoreTests.testAddIncreasesBalance |
| @TS_LED_002 | Spec | purchases-v3 2.2 | |
| @TS_LED_003 | Design | F/210:31 limit banner | |
| @TS_LED_004 | Spec + Design | purchases-v3 3.1; F/210:44 | |
| @TS_LED_005 | Team decision | export agreed by the team | |
| @TS_LED_006 | Spec · team decision on a detail | purchases-v3 4 | |

## Team decisions
| Scenario | Decision | Date |
| --- | --- | --- |
| @TS_LED_005 | Keep the CSV export | 2026-11-20 |
| @TS_LED_006 | The limit is 140 characters | 2026-11-20 |
"""

PLAN = """# Plan: LED-7 daily limit

## 2. Requirements
| # | Requirement | Source and version | Quote | Scenario, or reason for none |
| --- | --- | --- | --- | --- |
| R1 | Five purchases a day | purchases-v3 3.1 | "at most five" | @TS_LED_004 |
| R2 | The banner offers support | design D/210:31 | "Contact support" | N1 |
| R3 | The limit resets at midnight | purchases-v3 3.2 | "resets daily" | N2 |
| R4 | Copy is localised | purchases-v3 5 | "all copy" | none: covered by the localisation suite |

## 5. Scenario changes
| Change | Scenario | Steps | Basis | Evidence | Kind | Oracle | Test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Keep | @TS_LED_004 | as today | Spec | purchases-v3 3.1 | unit | | LimitTests.testSixthRefused |
| Add | N1 | Given the limit ... | Spec + Design | purchases-v3 3.1; D/210:31 | behaviour | | @blocked:no-ui-host |
| Team decision (decided 2026-11-20) | N2 | Given midnight ... | Team decision (owner 2026-11-20) | team decision in LED-7 | unit | | LimitTests.testReset |
| Remove | @TS_LED_005 | | | | | | |
| Not a gate scenario (to confirm) | N3 | | | | | | |
"""

PENDING_SUBTABLE = """
### Pending or blocked scenarios the change touches
| Scenario | Tag today | Test that will resolve it, or reason it stays |
| --- | --- | --- |
| @TS_LED_003 | @blocked:no-ui-host | stays: no screen in the package |
"""

COMPACT = """# Plan: refund sign
Status: draft
Workflow: bug-fix · Isolation: Standard · Base branch: main

## In short
A refund is added to the balance instead of subtracted.

---

# Working detail (for the agents)
Sources: code at abc1234

## Compact plan
| Scenario id | Reproduction | Cause (path:line) | Files the fix owns | Tier and reason | Proof |
| --- | --- | --- | --- | --- | --- |
| @TS_LED_002 | purchase 10.00, refund 4.00 -> 14.00 | `Sources/Ledger/TransactionStore.swift:18` ignores kind | Sources/Ledger/TransactionStore.swift | light: one line, reproduced | testRefundIsSubtractedFromBalance_TS_LED_002 passes |
"""


def test_profile(root):
    profile = root / '.orchard' / 'profile.md'
    check('profile_check check: sample profile is complete and current', ['profile_check.py', 'check', str(profile)],
          root, 0, ['profile check: OK'])
    check('profile_check get: scenario_id_pattern', ['profile_check.py', 'get', str(profile), 'scenario_id_pattern'],
          root, 0, [r'^@TS_LED_\\d\{3\}$'])
    edit(root / 'README.md', '\nOne more line.\n')
    check('profile_check check: changed README.md -> exit 3 naming its keys', ['profile_check.py', 'check', str(profile)],
          root, 3, [r'build: README\.md \(recorded [0-9a-f]{8}, now ', r'guides: README\.md'])
    check('profile_check stamp: rehash every file source', ['profile_check.py', 'stamp', str(profile)],
          root, 0, [r'stamped \d+ file source'])
    check('profile_check check: after stamp -> exit 0', ['profile_check.py', 'check', str(profile)],
          root, 0, ['profile check: OK'])
    check('profile_check get: a command cell with a note -> its code span only', ['profile_check.py', 'get',
          str(profile), 'knowledge_base_check'], root, 0,
          [r'^python3 -I "\$ORCHARD/scripts/gate_check\.py" docs/features/Purchases\.feature --id-pattern \S+\s*\Z'],
          absent=[r'the skill set root'])
    text = profile.read_text(encoding='utf-8')
    profile.write_text(text.replace('| generate | none | file:Package.swift#860470af |',
                                    '| generate | none | (file:Package.swift) |'), encoding='utf-8')
    check('profile_check stamp: a source in parentheses -> the ")" is not part of the path', ['profile_check.py',
          'stamp', str(profile)], root, 0, [r'stamped \d+ file source'], absent=[r'cannot read'])
    check('profile_check check: the parenthesised source is stamped and current', ['profile_check.py', 'check',
          str(profile)], root, 0, ['profile check: OK'])
    test_profile_none(root, profile.read_text(encoding='utf-8'))
    test_profile_skill(root, profile.read_text(encoding='utf-8'))
    test_profile_untracked(root, profile.read_text(encoding='utf-8'))
    text = profile.read_text(encoding='utf-8')
    text = text.replace('| base_branch | main |', '| base_branch | missing |')
    text = '\n'.join(l for l in text.split('\n') if not l.startswith('| knowledge_base_check |'))
    profile.write_text(text, encoding='utf-8')
    check('profile_check check: missing required keys -> exit 2', ['profile_check.py', 'check', str(profile)],
          root, 2, [r'- knowledge_base_check', r'- base_branch'])
    check('profile_check get: missing key -> exit 2', ['profile_check.py', 'get', str(profile), 'base_branch'], root, 2)


def set_row(text, key, value):
    return re.sub(r'^\| %s \|[^|]*\|' % re.escape(key), '| %s | %s |' % (key, value), text, flags=re.M)


def test_profile_none(root, text):
    """The knowledge base is required: `none` is not a value (templates/project-profile.md, Knowledge base)."""
    none = root / '.orchard' / 'profile-none.md'
    none.write_text(set_row(text, 'knowledge_base', 'none'), encoding='utf-8')
    check('profile_check check: knowledge_base none -> exit 2, reported as a missing required key', ['profile_check.py',
          'check', str(none)], root, 2, ['missing required keys', r'- knowledge_base\s*$'])
    none.unlink()


def test_profile_skill(root, text):
    """A skill called alone stops only on the keys it reads (column "Read by" in templates/project-profile.md)."""
    nobuild = root / '.orchard' / 'profile-nobuild.md'
    nobuild.write_text(set_row(text, 'build', 'missing'), encoding='utf-8')
    check('profile_check check --skill review: build missing, review does not read it -> exit 0', ['profile_check.py',
          'check', str(nobuild), '--skill', 'review'], root, 0, ['checked for review', 'profile check: OK'])
    check('profile_check check --skill run: build missing -> exit 2 naming it', ['profile_check.py', 'check',
          str(nobuild), '--skill', 'run'], root, 2, [r'- build\s*$'])
    check('profile_check check: build missing, full check -> exit 2', ['profile_check.py', 'check', str(nobuild)],
          root, 2, [r'- build\s*$'])
    check('profile_check check --skill: a skill this skill set does not have -> exit 64', ['profile_check.py',
          'check', str(nobuild), '--skill', 'nosuchskill'], root, 64, ['unknown skill'])
    nobuild.unlink()


def test_profile_untracked(root, text):
    """A file source must be tracked by git; a value from an untracked file is `stated:` (templates/project-profile.md)."""
    (root / 'notes.local.md').write_text('build: swift build\n', encoding='utf-8')
    local = root / '.orchard' / 'profile-untracked.md'
    local.write_text(re.sub(r'^(\| build \|[^|]*\|)[^|]*\|', r'\1 file:notes.local.md |', text, flags=re.M),
                     encoding='utf-8')
    check('profile_check stamp: an untracked file source -> exit 3, not stamped', ['profile_check.py', 'stamp',
          str(local)], root, 3, [r'not tracked by git, not stamped: notes\.local\.md'])
    check('profile_check check: an untracked file source -> exit 3 naming it', ['profile_check.py', 'check',
          str(local)], root, 3, [r'build: notes\.local\.md \(not tracked by git'])
    local.unlink()
    (root / 'notes.local.md').unlink()


def test_lock_and_gate(root):
    snap = '.orchard/runs/lock.json'
    (root / '.orchard' / 'runs').mkdir(parents=True, exist_ok=True)
    check('lock_check snapshot: docs/features/*.feature', ['lock_check.py', 'snapshot', snap, 'docs/features/*.feature'],
          root, 0, ['locked 1 files'])
    check('lock_check verify: unchanged -> exit 0', ['lock_check.py', 'verify', snap], root, 0, ['lock holds'])
    check("lock_check snapshot: no glob's folder exists -> exit 2", ['lock_check.py', 'snapshot', snap + '.x',
          'nothing/*.feature', 'nowhere/**/*.yml'], root, 2)
    empty = '.orchard/runs/lock-empty.json'
    check('lock_check snapshot: a folder that exists but matches nothing -> exit 0, an empty set', ['lock_check.py',
          'snapshot', empty, 'docs/features/*.feature', 'docs/features/*.lintrc', 'nothing/*.yml'], root, 0,
          [r'locked as empty.*docs/features/\*\.lintrc', r'no folder yet.*nothing/\*\.yml'])
    check('lock_check verify: the empty glob still empty -> exit 0', ['lock_check.py', 'verify', empty], root, 0,
          ['lock holds'])
    (root / 'docs' / 'features' / 'new.lintrc').write_text('x\n', encoding='utf-8')
    check('lock_check verify: a file appears under the empty glob -> exit 1', ['lock_check.py', 'verify', empty],
          root, 1, [r'added: +docs/features/new\.lintrc'])
    (root / 'docs' / 'features' / 'new.lintrc').unlink()
    orchard = '.orchard/runs/lock-orchard.json'
    check("lock_check snapshot: '.orchard/**' without '.orchard/runs/**'", ['lock_check.py', 'snapshot', orchard,
          '.orchard/**', '!.orchard/runs/**'], root, 0, [r'locked \d+ files'])
    (root / '.orchard' / 'runs' / 'plan.md').write_text('a plan\n', encoding='utf-8')
    check('lock_check verify: a new file under the removed .orchard/runs/ -> exit 0', ['lock_check.py', 'verify',
          orchard], root, 0, ['lock holds'])
    (root / '.orchard' / 'review-rules.md').write_text('changed\n', encoding='utf-8')
    check('lock_check verify: a changed .orchard file -> exit 1', ['lock_check.py', 'verify', orchard], root, 1,
          [r'changed: \.orchard/review-rules\.md'])

    feature = 'docs/features/Purchases.feature'
    check('gate_check: every scenario of Purchases.feature has an id', ['gate_check.py', feature],
          root, 0, ['6 scenarios, 6 with an id', 'gate check: OK'])
    register = root / 'docs' / 'features' / 'Purchases.requirements.md'
    register.write_text(REGISTER, encoding='utf-8')
    check('gate_check: register with Spec, Design, Spec + Design, Team decision bases', ['gate_check.py', feature,
          str(register), '--id-pattern', r'@TS_LED_\d{3}'], root, 0, ['2 cite a frame', 'gate check: OK'])
    register.write_text(REGISTER.replace('| Design | F/210:31', '| Figma | F/210:31'), encoding='utf-8')
    check('gate_check: an old basis name (Figma) -> exit 1', ['gate_check.py', feature, str(register)],
          root, 1, [r"TS_LED_003: basis 'Figma' is not"])
    register.write_text(REGISTER.replace('| Design | F/210:31 limit banner', '| Design | limit banner'), encoding='utf-8')
    check('gate_check: Design basis without a frame -> exit 1', ['gate_check.py', feature, str(register)],
          root, 1, ['TS_LED_003: basis names Design but no frame'])
    register.unlink()
    report = root / '.orchard' / 'runs' / 'report.md'
    report.write_text('TS_LED_001 TS_LED_002 TS_LED_003 TS_LED_004 TS_LED_005\n', encoding='utf-8')
    check('gate_check --report: a scenario missing from the report -> exit 1', ['gate_check.py', feature, '--report',
          str(report)], root, 1, ['TS_LED_006: missing from report.md'])

    plan = root / '.orchard' / 'runs' / 'plan.md'
    plan.write_text(PLAN, encoding='utf-8')
    check('gate_check --coverage: plan file sections 2 and 5', ['gate_check.py', '--coverage', str(plan)], root, 0,
          ['4 requirements, 3 covered, 1 left out with a reason; 5 scenario rows, 1 kept, 0 team decisions to confirm',
           'gate check: OK'])
    plan.write_text(PLAN + PENDING_SUBTABLE, encoding='utf-8')
    check('gate_check --coverage: the "###" pending sub-table under section 5 is not read as scenario rows',
          ['gate_check.py', '--coverage', str(plan)], root, 0, ['5 scenario rows, 1 kept', 'gate check: OK'])
    plan.write_text(COMPACT, encoding='utf-8')
    check('gate_check --coverage: a compact plan is checked as one (no Requirements needed)',
          ['gate_check.py', '--coverage', str(plan), '--id-pattern', r'@TS_LED_\d{3}'], root, 0,
          ['compact plan, 1 scenario rows', 'gate check: OK'])
    plan.write_text(COMPACT.replace('@TS_LED_002 |', 'refund |').replace(
        '`Sources/Ledger/TransactionStore.swift:18` ignores kind', 'the balance sum').replace(
        'light: one line, reproduced', 'light').replace(' testRefundIsSubtractedFromBalance_TS_LED_002 passes ', ' '),
        encoding='utf-8')
    check('gate_check --coverage: compact row without id, path:line, tier reason or proof -> exit 1',
          ['gate_check.py', '--coverage', str(plan), '--id-pattern', r'@TS_LED_\d{3}'], root, 1,
          ['compact row 1: no scenario id', 'the cause names no path:line', 'tier is not strong or light with a reason',
           'no proof'])
    plan.write_text(PLAN, encoding='utf-8')
    plan.write_text(PLAN.replace('purchases-v3 3.1; D/210:31', 'purchases-v3 3.1').replace(
        '| R3 | The limit resets at midnight | purchases-v3 3.2 | "resets daily" | N2 |',
        '| R3 | The limit resets at midnight | purchases-v3 3.2 | "resets daily" | |').replace(
        'LimitTests.testSixthRefused', ''), encoding='utf-8')
    check('gate_check --coverage: no frame, no test, requirement without scenario -> exit 1',
          ['gate_check.py', '--coverage', str(plan)], root, 1,
          ['N1: basis names Design but no frame', 'TS_LED_004: no test', 'requirement R3: no scenario',
           'N2: in the scenario changes but in no requirement row'])

    edit(root / feature, '\n  Scenario: A scenario nobody tagged\n    Given nothing\n')
    check('gate_check: a scenario without an id -> exit 1', ['gate_check.py', feature], root, 1, ['no id'])
    check('lock_check verify: edited feature file -> exit 1', ['lock_check.py', 'verify', snap], root, 1,
          [r'changed: docs/features/Purchases\.feature'])


def test_evidence(root):
    ev = '.orchard/runs/evidence.jsonl'
    out = check('evidence state: 12 hex', ['evidence.py', 'state'], root, 0, [r'^[0-9a-f]{12}\s*$'])
    state = out.strip()
    nogit = Path(tempfile.mkdtemp(prefix='orchard-nogit-'))
    (nogit / 'a.swift').write_text('let a = 1\n')
    first = check('evidence state: no git, --root -> nogit- file hash', ['evidence.py', 'state', '--root', str(nogit)],
                  root, 0, [r'nogit-[0-9a-f]{12}'])
    (nogit / 'a.swift').write_text('let a = 2\n')
    second = check('evidence state: no git, edited file -> a new state', ['evidence.py', 'state', '--root', str(nogit)],
                   root, 0, [r'nogit-[0-9a-f]{12}'])
    changed = first.strip() != second.strip()
    print('%s evidence state: no git, the two states differ' % ('PASS' if changed else 'FAIL'))
    results.append(changed)
    shutil.rmtree(nogit, ignore_errors=True)
    check('evidence record: `true` -> exit 0', ['evidence.py', 'record', ev, '--check', 'build', '--selection', 'all',
          '--', 'true'], root, 0, ['evidence: build exit 0 on state ' + state])
    check('evidence record: shell command, failing -> its exit code passes through', ['evidence.py', 'record', ev,
          '--check', 'lint', '--selection', 'all', '--', 'echo checking && exit 3'], root, 3, ['checking', 'exit 3'])
    check('evidence state: recording does not change the state', ['evidence.py', 'state'], root, 0, ['^' + state])
    check('evidence stale: nothing changed -> exit 0', ['evidence.py', 'stale', ev], root, 0, ['0 of 2 checks stale'])
    check('evidence table: Checks run table', ['evidence.py', 'table', ev], root, 0,
          [r'\| Check \| Command \| Selection \| Ran on \| Exit \| Summary \| Time \|', r'\| lint \| `echo checking'])
    edit(root / 'Sources' / 'Ledger' / 'Transaction.swift', '\n// edited after the checks ran\n')
    check('evidence stale: source edited -> exit 1', ['evidence.py', 'stale', ev], root, 1, ['2 of 2 checks stale'])
    check('evidence table: stale rows say so', ['evidence.py', 'table', ev], root, 0, [r'\(stale\)'])
    check('evidence record: newer record clears staleness for that check', ['evidence.py', 'record', ev, '--check',
          'build', '--selection', 'all', '--', 'true'], root, 0)
    check('evidence stale: only the lint check is still stale', ['evidence.py', 'stale', ev], root, 1,
          ['1 of 2 checks stale', 'stale: lint'])
    check('evidence record: passing test run with an XCTest and an empty Swift Testing summary', ['evidence.py',
          'record', ev, '--check', 'test.unit', '--selection', 'all', '--',
          "echo 'Executed 3 tests, with 0 failures (0 unexpected) in 0.01 seconds'; "
          "echo 'Test run with 0 tests in 0 suites passed after 0.001 seconds.'"], root, 0)
    check('evidence table: a passing check shows the summary that counts tests, not the empty one',
          ['evidence.py', 'table', ev], root, 0, [r'\| test\.unit \|.*\| Executed 3 tests, with 0 failures'])
    check('evidence record: a red run of a new test, before its code', ['evidence.py', 'record', ev, '--check',
          'test.unit', '--selection', 'red-LimitTests.testSixthRefused', '--',
          "echo 'error: XCTAssertEqual failed: (\"6\") is not equal to (\"5\")'; exit 1"], root, 1)
    edit(root / 'Sources' / 'Ledger' / 'Transaction.swift', '\n// the code that makes it pass\n')
    check('evidence stale: a red run on an earlier state is not stale', ['evidence.py', 'stale', ev], root, 1,
          ['3 of 3 checks stale'])
    check('evidence table: a red run says "before the code" and shows its failure', ['evidence.py', 'table', ev], root,
          0, [r'red-LimitTests\.testSixthRefused \| [0-9a-f]{12} \(before the code\) \| 1 \| error: XCTAssertEqual'])
    test_file = 'Tests/LedgerTests/TransactionStoreTests.swift'
    check('evidence record: a red run that names its test file', ['evidence.py', 'record', ev, '--check', 'test.unit',
          '--selection', 'red-TransactionStoreTests.testRefund', '--files', test_file, '--',
          "echo 'error: XCTAssertEqual failed'; exit 1"], root, 1)
    check('evidence held: test file untouched since its red run -> exit 0', ['evidence.py', 'held', ev], root, 0,
          [r'0 of 1 test files named by red runs changed since \(1 red runs name no file\)'])
    edit(root / 'Sources' / 'Ledger' / 'Transaction.swift', '\n// production code may change after red\n')
    check('evidence held: a source edit does not break it', ['evidence.py', 'held', ev], root, 0)
    edit(root / test_file, '\n// assertion loosened after red\n')
    check('evidence held: test file edited after its red run -> exit 1, named', ['evidence.py', 'held', ev], root, 1,
          [r'changed after red: Tests/LedgerTests/TransactionStoreTests\.swift \[red-TransactionStoreTests\.testRefund\]',
           '1 of 1 test files'])
    check('evidence table: the red row says the test changed since', ['evidence.py', 'table', ev], root, 0,
          [r'red-TransactionStoreTests\.testRefund \| [0-9a-f]{12} \(before the code; test changed since\)'])
    check('evidence record: a new red run of the edited test restores it', ['evidence.py', 'record', ev, '--check',
          'test.unit', '--selection', 'red-TransactionStoreTests.testRefund', '--files', test_file, '--',
          "echo 'error: XCTAssertEqual failed'; exit 1"], root, 1)
    check('evidence held: holds again after the new red run', ['evidence.py', 'held', ev], root, 0)
    edit(root / test_file, '\n// a fix round adds a second test to the same file\n')
    check('evidence record: a red run of the added test names the same file', ['evidence.py', 'record', ev, '--check',
          'test.unit', '--selection', 'red-TransactionStoreTests.testAdded', '--files', test_file, '--',
          "echo 'error: XCTAssertEqual failed'; exit 1"], root, 1)
    check('evidence held: the latest red run per file counts -> holds', ['evidence.py', 'held', ev], root, 0,
          ['0 of 1 test files'])
    os.rename(root / test_file, root / (test_file + '.gone'))
    check('evidence held: test file removed -> exit 1', ['evidence.py', 'held', ev], root, 1, ['removed after red'])
    os.rename(root / (test_file + '.gone'), root / test_file)


def test_plan_seal(work):
    plan = work / 'seal-plan.md'
    plan.write_text('# Plan: seal\nStatus: draft\nWorkflow: bug-fix · Isolation: Standard · Base branch: main\n\n'
                    '## In short\nFix the refund.\n\n## 7. Work packages\n| 1 | store | Sources/a.swift |\n\n'
                    '## Result (written by run)\n| Scenario | Delivered |\n\n## Change note (written by update-docs)\n',
                    encoding='utf-8')
    check('plan seal: check before any seal -> exit 2', ['plan_seal.py', 'check', str(plan)], work, 2, ['none for'])
    check('plan seal: seal', ['plan_seal.py', 'seal', str(plan)], work, 0, [r'plan seal: [0-9a-f]{12} -> '])
    check('plan seal: untouched -> holds', ['plan_seal.py', 'check', str(plan)], work, 0, ['holds'])
    sealed = json.loads((work / 'seal-plan.md.seal.json').read_text(encoding='utf-8'))['hash']
    check('plan seal: hash prints the sealed hash and writes nothing', ['plan_seal.py', 'hash', str(plan)], work, 0,
          ['^%s$' % sealed])
    text = plan.read_text(encoding='utf-8')
    plan.write_text(text.replace('Status: draft', 'Status: executed').replace(
        '| Scenario | Delivered |', '| Scenario | Delivered |\n| TS_1 | yes |') + 'Scenarios changed: none\n',
        encoding='utf-8')
    check('plan seal: status, Result and Change note written by later steps -> still holds',
          ['plan_seal.py', 'check', str(plan)], work, 0, ['holds'])
    plan.write_text(plan.read_text(encoding='utf-8').replace('Sources/a.swift', 'Sources/a.swift, Sources/b.swift'),
                    encoding='utf-8')
    check('plan seal: a work package edited after approval -> exit 1, section named',
          ['plan_seal.py', 'check', str(plan)], work, 1, [r'broken, changed since approval: ## 7\. Work packages'])
    check('plan seal: sealing again (a new approval) holds', ['plan_seal.py', 'seal', str(plan)], work, 0)
    check('plan seal: holds after the new seal', ['plan_seal.py', 'check', str(plan)], work, 0, ['holds'])
    check('plan seal: a plan with no seal file -> exit 2', ['plan_seal.py', 'check', str(work / 'no-plan.md')], work, 2)


def test_runlog(work):
    env = {'ORCHARD_RUNLOG': str(work / 'runlog.jsonl')}
    out = check('runlog start', ['runlog.py', 'start', '--workflow', 'feature-development', '--skill', 'run',
                '--task', 'LED-7 daily limit', '--isolation', 'standard'], work, 0, [r'^\d{8}-\d{6}-[0-9a-f]{6}'], env)
    run_id = out.split()[0]
    for args in (['tier', '--role', 'implementer', '--round', '1', '--tier', 'light', '--tokens', '1200', '--seconds', '300'],
                 ['finding', '--note', 'concurrency: R-3'], ['send_back', '--note', 'banner copy wrong'],
                 ['wait', '--seconds', '120'],
                 ['loop_failed', '--cause', 'plan_gap', '--round', '1', '--note', 'package 1: interface not in the plan'],
                 ['loop_failed', '--cause', 'executor', '--round', '2', '--note', 'package 1']):
        check('runlog event %s' % args[0], ['runlog.py', 'event', run_id] + args, work, 0, [], env)
    check('runlog finish: with the closing session\'s tokens', ['runlog.py', 'finish', run_id, '--outcome', 'delivered',
          '--findings', '1', '--tokens', '800'], work, 0, ['"outcome": "delivered"'], env)
    check('runlog rate', ['runlog.py', 'rate', run_id, '--accepted', '1', '--rejected', '0', '--rework-minutes', '4',
          '--verify-minutes', '6'], work, 0, ['rated'], env)
    check('runlog event: loop_failed without --cause -> exit 64', ['runlog.py', 'event', run_id, 'loop_failed'], work,
          64, ['--cause is required'], env)
    check('runlog event: --cause on another event -> exit 64', ['runlog.py', 'event', run_id, 'flaky', '--cause',
          'flaky'], work, 64, [], env)
    check('runlog report: one run -> no baseline yet', ['runlog.py', 'report'], work, 0,
          ['failed loops by cause: plan_gap 1, executor 1', 'feature-development / standard', 'sent back 100%', 'tokens 2000', r'minutes 7\.0 \(from recorded seconds\)',
           'no baseline yet'], env)
    other = check('runlog start: second run', ['runlog.py', 'start', '--workflow', 'feature-development', '--skill',
                  'run', '--task', 'LED-8'], work, 0, [], env).split()[0]
    check('runlog event: tokens na', ['runlog.py', 'event', other, 'tier', '--role', 'reviewer', '--tier', 'strong',
          '--tokens', 'na'], work, 0, [], env)
    check('runlog finish: --tokens na and --seconds', ['runlog.py', 'finish', other, '--outcome', 'green', '--tokens',
          'na', '--seconds', '60'], work, 0, [], env)
    check('runlog report: a run without tokens -> not available; minutes from recorded seconds', ['runlog.py', 'report'],
          work, 0, [r'tokens not available \(1 of 2 runs report tokens\); minutes 4\.0 \(from recorded seconds\)'], env)
    for n in range(5):
        rid = check('runlog bug-fix run %d' % (n + 1), ['runlog.py', 'start', '--workflow', 'bug-fix', '--skill', 'run',
                    '--task', 'bug %d' % n, '--isolation', 'shared'], work, 0, [], env).split()[0]
        if n == 0:
            run(['runlog.py', 'event', rid, 'ended_early', '--note', 'sources conflict'], work, env)
        if n == 4:
            run(['runlog.py', 'event', rid, 'seeded_missed', '--note', 'S1'], work, env)
        run(['runlog.py', 'finish', rid, '--outcome', 'ended_early' if n == 0 else 'green'], work, env)
    check('runlog report: five runs -> trend, seeded defects missed', ['runlog.py', 'report', '--since', '30d'], work, 0,
          ['bug-fix / shared', r'minutes 0\.0 \(from start to finish\)', 'trend ended early %',
           'seeded defects missed 1'], env)
    check('runlog report --json', ['runlog.py', 'report', '--json', '--group', 'workflow'], work, 0,
          ['"bug-fix"', '"ended_early_pct"'], env)
    check('runlog event: unknown run -> exit 2', ['runlog.py', 'event', 'nope', 'flaky'], work, 2, [], env)
    blocked = {'ORCHARD_RUNLOG': str(work / 'runlog.jsonl' / 'cannot' / 'be' / 'here.jsonl')}
    check('runlog start: unwritable log -> prints none, exit 0', ['runlog.py', 'start', '--workflow', 'w', '--skill',
          's', '--task', 't'], work, 0, ['^none'], blocked)
    check('runlog finish none: does nothing, exit 0', ['runlog.py', 'finish', 'none', '--outcome', 'red'], work, 0,
          [], blocked)


def test_leaks(work):
    dirty = work / 'dirty.md'
    dirty.write_text('Read the plan in /Users/x/notes.\n', encoding='utf-8')  # leak-check: allow
    check('leak_check: planted home path -> exit 1', ['leak_check.py', str(dirty)], work, 1, ['dirty.md:1: home path'])
    clean = work / 'clean.md'
    clean.write_text('Run `swift test` from the project root.\nA path like $ORCHARD/scripts is fine.\n', encoding='utf-8')
    check('leak_check: clean file -> exit 0', ['leak_check.py', str(clean)], work, 0, ['clean'])
    allowed = work / 'allowed.md'
    allowed.write_text('/Users/x is an example. <!-- leak-check: allow -->\n', encoding='utf-8')  # leak-check: allow
    check('leak_check: allow-listed line -> exit 0', ['leak_check.py', str(allowed)], work, 0, ['clean'])
    check('leak_check: default folders scan runs', ['leak_check.py'], work, None, [r'leak check: \d+ file'])
    patterns = work / 'leak-patterns'
    patterns.write_text('# private names stay out of git\nproject name: \\bacmebank\\b\nticket key: \\bACME-\\d+\n',
                        encoding='utf-8')
    named = work / 'named.md'
    named.write_text('Copied from the AcmeBank app, ticket ACME-12.\n', encoding='utf-8')
    check('leak_check: without a local pattern file, a private name passes and the output says so',
          ['leak_check.py', str(named)], work, 0, ['clean', 'no local pattern file'],
          {'ORCHARD_LEAK_PATTERNS': str(work / 'none')})
    check('leak_check: local patterns catch a project name and a ticket key', ['leak_check.py', str(named)], work, 1,
          ['named.md:1: project name', 'named.md:1: ticket key', r'2 local pattern\(s\)'],
          {'ORCHARD_LEAK_PATTERNS': str(patterns)})
    patterns.write_text('project name \\bacmebank\\b\n', encoding='utf-8')
    check('leak_check: a malformed local pattern line -> exit 64', ['leak_check.py', str(named)], work, 64,
          ['expected `<name>: <regular expression>`'], {'ORCHARD_LEAK_PATTERNS': str(patterns)})


def test_adapters(root, work):
    payload = work / 'payload.json'
    payload.write_text(json.dumps({'body': 'Review of the change.', 'comments': [
        {'path': 'Sources/Ledger/TransactionStore.swift', 'line': 2, 'body': 'Blocker · High: balance ignores refunds'},
        {'path': 'Sources/Ledger/TransactionStore.swift', 'line': 90, 'body': 'NOTE · Low: outside the hunk'}]}))
    files = work / 'files.json'
    files.write_text(json.dumps([{'filename': 'Sources/Ledger/TransactionStore.swift',
                                  'patch': '@@ -1,2 +1,3 @@\n line one\n+line two\n line three'}]))
    check('post_review --dry-run: anchors one comment, moves one, counts the blocker', ['post_review.py', '1',
          str(payload), '--dry-run', '--files-json', str(files)], work, 0,
          ['1 inline, 1 moved to the summary, 1 blocking', 'Outside the diff'])
    check('sources/figma_frames: no token -> exit 2, no request', ['sources/figma_frames.py', '--file', 'KEY',
          'exists', '1:2'], work, 2, ['FIGMA_TOKEN'], {'FIGMA_TOKEN': None})
    check('discover.sh: lists the .orchard files', ['discover.sh', str(root)], work, 0,
          [r'## Orchard files', r'\.orchard/profile\.md', r'Profile status: confirmed', r'SwiftPM\(Package\.swift\)'])
    app, env = discover_fixture(work)
    check('discover.sh: Xcode project -> lists every scheme, picks none; counts every test folder; linked and '
          'Cursor guides; no empty SwiftLint line', ['discover.sh', str(app)], work, 0,
          [r'Schemes \(project App\): `Analytics` `App` `AppTests` `AppUITests`',
           r'look like test schemes \(name contains Test\): `AppTests` `AppUITests`',
           r'look like app schemes \(named as the project\): `App`$', r'-scheme <scheme>',
           r'Test folders \(3\)', r'Files importing XCTest: 2$', r'Swift Testing\): 1$', r'UI tests\): 1$',
           r'`docs/testing\.md` \(linked from `AGENTS\.md`\)', r'`\.cursor/rules/swift\.mdc` \(Cursor rule\)',
           r'SwiftLint config'],
          env, absent=[r'SwiftLint custom rules', r'-scheme Analytics', r'docs/missing\.md'])


def discover_fixture(work):
    """An Xcode-project layout with three test folders and a stand-in xcodebuild on PATH (no Xcode needed)."""
    app = work / 'App'
    files = {
        'App.xcodeproj/project.pbxproj': '',
        'AppTests/AppTests.swift': 'import XCTest\n',
        'AppUITests/AppUITests.swift': 'import XCTest\nlet app = XCUIApplication()\n',
        'Modules/Feature/FeatureTests/FeatureTests.swift': 'import Testing\n',
        '.swiftlint.yml': 'disabled_rules:\n  - line_length\n',
        'AGENTS.md': 'Read [testing](docs/testing.md) and [old](docs/missing.md).\n',
        'docs/testing.md': '# Testing\n',
        '.cursor/rules/swift.mdc': 'Use Swift Testing.\n',
        '../bin/xcodebuild': '#!/bin/sh\ncase "$1" in\n  -version) echo "Xcode 0.0";;\n'
                             '  -list) echo \'{"project": {"name": "App", "schemes": '
                             '["Analytics", "App", "AppTests", "AppUITests"]}}\';;\nesac\n',
    }
    for name, body in files.items():
        path = app / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding='utf-8')
    (work / 'bin' / 'xcodebuild').chmod(0o755)
    return app, {'PATH': '%s:%s' % (work / 'bin', os.environ.get('PATH', ''))}


VERDICT_PLAN = """# Plan: sample
Workflow: feature-development · Isolation: Standard

## 5. Scenario changes
| Change | Scenario | Steps | Basis | Evidence | Kind | Oracle | Test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| change | S1 — A refund lowers the balance | unchanged | Spec | v3 | unit | | StoreTests.testRefund |
| add | S2 — The banner shows | Given · When · Then | Spec | v3 | unit | | BannerTests.testBanner |
| remove | S3 — Old rule | | | contradicts v3 | | | |

### Pending or blocked scenarios the change touches
| Scenario | Tag today | Test that will resolve it, or reason it stays |
| --- | --- | --- |
| S9 | @blocked | none |

## 8. Rounds and locks
Rounds: at most three.
"""

VERDICT_REVIEW_CLEAN = """# Review: sample

## Round 1: full review

| # | Type | Severity | Where | Finding | Fix | State |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Risk | Medium | a.swift:3 | no test | add one | fixed in round 2 |
| 2 | NOTE | | a.swift:9 | out of scope | later | for the developer |
| 3 | Risk | NIT | a.swift:4 | naming | rename | fixed in round 2 |

## Round 2: review of the fixes

No new findings.
"""


def test_verdict(root):
    reviews = root / '.orchard' / 'runs' / 'verdict-reviews'
    reviews.mkdir(parents=True, exist_ok=True)
    plan = root / '.orchard' / 'runs' / 'verdict-plan.md'
    plan.write_text(VERDICT_PLAN, encoding='utf-8')
    ev = root / '.orchard' / 'runs' / 'verdict-evidence.jsonl'
    (reviews / 'review-round-1.md').write_text(VERDICT_REVIEW_CLEAN, encoding='utf-8')
    state = run(['evidence.py', 'state'], root)[1].strip()

    def records(*rows):
        ev.write_text(''.join(json.dumps(dict(r, state=r.get('state', state))) + '\n' for r in rows), encoding='utf-8')

    base = [{'check': 'build', 'selection': 'all', 'command': 'swift build', 'exit': 0},
            {'check': 'test.unit', 'selection': 'StoreTests', 'command': 'swift test --filter StoreTests', 'exit': 0},
            {'check': 'test.unit', 'selection': 'BannerTests.testBanner', 'command': 'swift test --filter BannerTests',
             'exit': 0}]
    args = ['verdict.py', str(ev), str(plan), '--reviews', str(reviews)]
    records(*base)
    check('verdict: every scenario proven, fixed findings only -> Ready to accept, exit 0', args, root, 0,
          [r'^Ready to accept$', 'S1: no screenshot or recording', 'Rounds: 2 of 3'], absent=['S3', 'S9:.*no evidence'])
    records(*(base + [{'check': 'screenshot', 'selection': 'S1', 'command': 'simctl screenshot screens/S1.png',
                       'exit': 0}]))
    check('verdict: a screenshot for S1 -> S1 leaves the gaps, verdict unchanged', args, root, 0,
          [r'^Ready to accept$', 'S2: no screenshot'], absent=['S1: no screenshot'])
    records(base[0], base[1], dict(base[2], selection='red-BannerTests.testBanner', exit=1))
    check('verdict: only a red run for S2 -> Not ready, exit 1', args, root, 1, [r'^Not ready$', 'S2: no evidence record'])
    records(base[0], base[1], dict(base[2], state='0123456789ab'))
    check('verdict: S2 proven on an earlier state -> Not ready, stale', args, root, 1,
          [r'^Not ready$', r'S2: its evidence ran on an earlier version \(stale\)', r'check test.unit \[BannerTests'])
    records(*(base + [{'check': 'lint', 'selection': 'all', 'command': 'lint', 'exit': 2}]))
    check('verdict: a required check fails, rounds left -> Not ready', args, root, 1,
          [r'^Not ready$', r'check lint \[all\] fails on the current state \(exit 2\)'])
    (reviews / 'review-round-3.md').write_text('# Review of fixes, round 3\n\nNo new findings.\n', encoding='utf-8')
    check('verdict: a required check still fails after round 3 of 3 -> Blocked, exit 3', args, root, 3,
          [r'^Blocked$', 'after round 3 of 3', 'check lint'])
    records(*base)
    (reviews / 'review-round-3.md').write_text(
        '# Review of fixes, round 3\n\nFinding 1 is not fixed.\n\n## Inline comments\n\n'
        '### `Sources/a.swift:7` · Risk · Medium\n**Claim.** Detail.\n\n### `Sources/b.swift:2` · NOTE\nNote.\n',
        encoding='utf-8')
    check('verdict: an open Risk heading and a "not fixed" line in the latest review -> Not ready', args, root, 1,
          [r'^Not ready$', r'open blocking finding in review-round-3.md: Risk · Medium at Sources/a.swift:7',
           'says a finding is not fixed'], absent=['b.swift'])
    (reviews / 'review-round-3.md').unlink()
    check('verdict: no --reviews -> Not ready, findings unknown', args[:3], root, 1, ['no review read'])
    check('verdict: --ended-early quotes the reason -> Not ready', args + ['--ended-early', 'spec and design differ'],
          root, 1, [r'^Not ready$', 'the run ended early: "spec and design differ"'])
    records(*base)
    (reviews / 'review-round-1.md').write_text(VERDICT_REVIEW_CLEAN, encoding='utf-8')
    check('verdict: an unsealed plan is a gap, not a reason', args, root, 0, [r'^Ready to accept$', 'the plan has no seal'])
    run(['plan_seal.py', 'seal', str(plan)], root)
    check('verdict: a sealed, unchanged plan -> Ready, no seal gap', args, root, 0, [r'^Ready to accept$'],
          absent=['no seal', 'changed after approval'])
    held = root / 'Tests' / 'LedgerTests' / 'TransactionStoreTests.swift'
    kept = held.read_text(encoding='utf-8')
    records(*(base + [{'check': 'test.unit', 'selection': 'red-StoreTests.testOne', 'command': 'swift test', 'exit': 1,
                       'files': {'Tests/LedgerTests/TransactionStoreTests.swift': '000000000000'}}]))
    check('verdict: a test file changed after its red run -> Not ready', args, root, 1,
          [r'^Not ready$', 'test file changed after it was seen failing: Tests/LedgerTests/TransactionStoreTests.swift'])
    records(*base)
    edit(plan, '\nAn extra package slipped in after approval.\n')
    check('verdict: the plan edited after its seal -> Not ready', args, root, 1,
          [r'^Not ready$', 'the plan changed after approval'])
    plan.write_text(VERDICT_PLAN, encoding='utf-8')
    held.write_text(kept, encoding='utf-8')
    check('verdict: missing plan file -> exit 64', ['verdict.py', str(ev), str(plan) + '.missing'], root, 64)


def main():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--keep', action='store_true', help='keep the temporary copy')
    args = parser.parse_args()
    work = Path(tempfile.mkdtemp(prefix='orchard-selftest-'))
    root = work / 'Ledger'
    try:
        shutil.copytree(SAMPLE, root, ignore=shutil.ignore_patterns('.build', '.swiftpm', 'runs', 'agents.local.md'))
    except OSError as error:
        print('cannot copy %s: %s' % (SAMPLE, error), file=sys.stderr)
        return 64
    git = ['git', '-c', 'user.name=selftest', '-c', 'user.email=selftest@localhost', '-c', 'commit.gpgsign=false']
    for command in (['git', 'init', '-q'], ['git', 'add', '-A'], git + ['commit', '-q', '--no-verify', '-m', 'fixture']):
        code, out = run(command, root, script=False)
        if code != 0:
            print('cannot set up the git fixture: %s' % out.strip(), file=sys.stderr)
            return 64
    for name in sorted([p.name for p in HERE.glob('*.py')] + ['sources/figma_frames.py']):
        check('%s --help' % name, [name, '--help'], work, 0)
    try:
        test_profile(root)
        test_lock_and_gate(root)
        test_evidence(root)
        test_runlog(work)
        test_plan_seal(work)
        test_leaks(work)
        test_adapters(root, work)
        test_verdict(root)
    finally:
        if args.keep:
            print('kept: %s' % work)
        else:
            shutil.rmtree(work, ignore_errors=True)
    failed = results.count(False)
    print('selftest: %d checks, %s' % (len(results), '%d failed' % failed if failed else 'all passed'))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
