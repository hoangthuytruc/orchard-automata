#!/usr/bin/env python3
"""Check that every scenario of a feature file has an id, a basis and evidence in its requirements register.

  gate_check.py <feature file>                               every scenario carries an id tag
  gate_check.py <feature file> <register.md> [--report R]    every scenario has exactly one register row with a basis
  gate_check.py <feature file> --report <report.md>          every scenario id is in the report
  gate_check.py --coverage <plan.md>                         plan phase: every requirement (plan section 2) has a
                                                             scenario or "none: <reason>"; every scenario change
                                                             (section 5, up to its first ### sub-section) has a
                                                             basis, evidence, a test or @blocked:<reason>, and a
                                                             requirement. A compact plan (a "## Compact plan" table)
                                                             is checked instead: every row has a scenario id, a
                                                             reproduction, a cause at path:line, owned files, a tier
                                                             with its reason, and a proof

The feature file is Gherkin (`*.feature`): ids are tags on the lines above each Scenario.

A scenario passes when exactly one register row carries it with a Basis of Spec, Design, Spec + Design or
Team decision (optionally "· team decision on a detail"), evidence, and a test or a pending tag. A Design basis
cites a frame reference (D/<frame id>, F/<frame id>, or <n>:<n>). A team decision has a dated row under "Team decisions".
The scenario id pattern comes from the profile key `scenario_id_pattern` (--id-pattern); the leading @ is optional
wherever an id is read. Prints the counts for the register's "At a glance" table. Rules: references/scenario-gate.md.

Exit codes:
  0   clean
  1   one line per problem on stderr
  64  wrong usage, or a file cannot be read
"""
import argparse
import collections
import re
import sys
from pathlib import Path

BASES = {'spec', 'design', 'spec + design', 'team decision'}
DETAIL = 'team decision on a detail'
PENDING = ('@manual', '@blocked', '@gap', '@automation-pending', '@pending')
FRAME = re.compile(r'[DF]/\S+|\b\d+:\d+\b')
DATE = re.compile(r'\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b|\b\d{4}-\d{2}-\d{2}\b')
SKIP_SECTIONS = ('removed', 'pruned', 'open decisions', 'design notes', 'sources')
COMMENT = re.compile(r'<!--.*?-->', re.S)
PATH_LINE = re.compile(r'[\w./-]+\.\w+:\d+')
TIER = re.compile(r'(strong|light)\b\W*(\w.*)?', re.I)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('%s: error: %s' % (self.prog, message), file=sys.stderr)
        sys.exit(64)


class Ids:
    """A scenario id pattern; ids are kept without the leading @."""

    def __init__(self, pattern):
        bare = pattern.strip().strip('`')
        bare = bare[1:] if bare.startswith('@') else bare
        self.tag = re.compile('@?(?:%s)' % bare)
        self.text = re.compile(r'(?<![A-Za-z0-9_])@?(?:%s)' % bare)

    def of_tag(self, tag):
        return tag.lstrip('@') if self.tag.fullmatch(tag) else None

    def in_text(self, text):
        return [m.group(0).lstrip('@') for m in self.text.finditer(text)]


def read(path):
    try:
        return path.read_text(encoding='utf-8')
    except OSError as error:
        print('cannot read %s: %s' % (path, error), file=sys.stderr)
        sys.exit(64)


def feature_scenarios(path, ids):
    """id -> set of tags, read from the tag lines above each scenario."""
    found, tags = collections.OrderedDict(), []
    for raw in read(path).splitlines():
        line = raw.strip()
        if line.startswith('@'):
            tags.extend(line.split())
        elif re.match(r'Scenario(?: Outline)?:', line):
            scenario_ids = [sid for sid in (ids.of_tag(t) for t in tags) if sid]
            for sid in scenario_ids:
                found[sid] = set(tags)
            if not scenario_ids:
                found['%s (no id)' % line] = set(tags)
            tags = []
    return found


def cells(line):
    return [c.strip() for c in re.split(r'(?<!\\)\|', line.strip().strip('|'))]


def register_rows(path):
    """Yield (section heading, header -> cell, cells) for every table row."""
    section, header = '', None
    for raw in read(path).splitlines():
        line = raw.strip()
        if line.startswith('#'):
            section, header = line.lstrip('#').strip(), None
        elif line.startswith('|'):
            row = cells(line)
            if all(re.fullmatch(r':?-{3,}:?', c) for c in row):
                continue
            if header is None:
                header = [c.lower() for c in row]
                continue
            yield section, dict(zip(header, row)), row
        else:
            header = None


def table_rows(text, wanted):
    """Yield header -> cell for every table row under a heading for which wanted(h2, h3) holds."""
    h2, h3, header = '', '', None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith('## '):
            h2, h3, header = line[3:].strip().lower(), '', None
        elif line.startswith('#'):
            h3, header = line.lstrip('#').strip().lower(), None
        elif line.startswith('|') and wanted(h2, h3):
            row = cells(line)
            if all(re.fullmatch(r':?-{3,}:?', c) for c in row):
                continue
            if header is None:
                header = [c.lower() for c in row]
            elif any(row):
                yield dict(zip(header, row))
        else:
            header = None


def check_compact(path, table, ids):
    """Compact plan (templates/plan.md, bug-fix only): one row per approved scenario the fix restores."""
    def column(named, *keys):
        return next((v for k, v in named.items() if any(key in k for key in keys)), '').strip()

    errors = []
    for n, named in enumerate(table, 1):
        found = ids.in_text(column(named, 'scenario'))
        label = found[0] if found else 'compact row %d' % n
        if not found:
            errors.append('compact row %d: no scenario id matching --id-pattern' % n)
        if not column(named, 'reproduc'):
            errors.append('%s: no reproduction' % label)
        if not PATH_LINE.search(column(named, 'cause')):
            errors.append('%s: the cause names no path:line' % label)
        if not column(named, 'files', 'owns'):
            errors.append('%s: no files the fix owns' % label)
        tier = TIER.match(column(named, 'tier'))
        if not tier or not tier.group(2):
            errors.append('%s: tier is not strong or light with a reason' % label)
        if not column(named, 'proof'):
            errors.append('%s: no proof' % label)
    if not table:
        errors.append('%s: a "Compact plan" section with no table rows' % path.name)
    print('%s: compact plan, %d scenario rows' % (path.name, len(table)))
    return errors


def check_coverage(path, proposed_re, ids):
    """Plan file (templates/plan.md): "## 2. Requirements" against "## 5. Scenario changes".

    Every requirement row names a scenario or says "none: <reason>". Every scenario row that is not removed and not
    "Not a gate scenario" has a Basis, Evidence (a frame reference when the basis names Design), a Test or a
    @blocked:<reason> tag, and appears in a requirement row. Rows under a "###" sub-heading of section 5 (pending or
    blocked scenarios) are not scenario changes. HTML comments are ignored. A plan with a "## Compact plan" section is
    checked by check_compact instead. Older draft reports ("Coverage", "Proposed scenarios",
    "Team decisions" sections) are read the same way.
    """
    def found_ids(text):
        return sorted(set(proposed_re.findall(text)) | set(ids.in_text(text)))

    text = COMMENT.sub('', read(path))
    if re.search(r'^##\s+compact plan\s*$', text, re.I | re.M):
        return check_compact(path, list(table_rows(text, lambda h2, h3: h2 == 'compact plan')), ids)
    errors, flags, defined, decided, covered = [], [], {}, set(), set()
    rows = skipped = bare = 0
    per_scenario = collections.Counter()
    h2, header, sub = '', None, False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith('## '):
            h2, header, sub = line[3:].lower(), None, False
        elif line.startswith('#'):
            header, sub = None, sub or line.startswith('###')
        elif line.startswith('|'):
            row = cells(line)
            if all(re.fullmatch(r':?-{3,}:?', c) for c in row):
                continue
            if header is None:
                header = [c.lower() for c in row]
                continue
            if not any(c.strip() for c in row):
                continue
            named = dict(zip(header, row))
            scenario_cell = next((v for k, v in named.items() if 'scenario' in k), row[0])
            if 'requirements' in h2 or 'coverage' in h2:
                rows += 1
                found = found_ids(scenario_cell)
                covered.update(found)
                per_scenario.update(found)
                if len(found) >= 3:
                    flags.append('review: requirement %s has %d scenarios (duplicates?)' % (row[0], len(found)))
                if not found:
                    reason = re.match(r'none\s*[:—–-]?\s*(.+)', scenario_cell, re.I)
                    if reason and len(reason.group(1).split()) >= 3:
                        skipped += 1
                    else:
                        bare += 1
                        errors.append('requirement %s: no scenario and no "none: <reason>"' % row[0])
            elif ('scenario changes' in h2 or 'proposed scenarios' in h2) and not sub:
                change = named.get('change', '').strip().lower()
                for sid in found_ids(scenario_cell if 'change' in named else row[0]):
                    defined[sid] = (change, named)
            elif 'team decision' in h2:
                decided.update(found_ids(row[0]))
        else:
            header = None
    if not rows:
        errors.append('%s: no rows under a "Requirements" heading' % path.name)
    for sid, (change, named) in defined.items():
        if change.startswith('remove') or change.startswith('not a gate scenario'):
            continue
        basis = named.get('basis', '')
        parts = [p.strip().lower() for p in basis.split('·')]
        main_basis = 'team decision' if parts[0].startswith('team decision') else parts[0]
        if main_basis not in BASES or any(e != DETAIL for e in parts[1:]):
            errors.append("%s: basis '%s' is not Spec, Design, Spec + Design or Team decision" % (sid, basis))
        evidence = ' '.join(v for k, v in named.items() if 'evidence' in k or 'clause' in k)
        if not evidence.strip():
            errors.append('%s: no evidence' % sid)
        elif 'design' in main_basis and not FRAME.search(evidence):
            errors.append('%s: basis names Design but no frame reference (D/<frame id>) is cited' % sid)
        if 'test' in named:
            test = named['test'].strip()
            if not test:
                errors.append('%s: no test and no @blocked:<reason>' % sid)
            elif re.fullmatch(r'@blocked:?', test):
                errors.append('%s: @blocked without a reason' % sid)
        if sid not in covered:
            errors.append('%s: in the scenario changes but in no requirement row (which requirement asks for it?)' % sid)
    for sid in sorted(covered - set(defined) - decided):
        errors.append('%s: named in a requirement row but not in the scenario changes' % sid)
    flags += ['review: %s covers %d requirements (too broad?)' % (sid, n) for sid, n in sorted(per_scenario.items()) if n >= 4]
    for flag in flags:
        print(flag)
    print('%s: %d requirements, %d covered, %d left out with a reason; %d scenario rows, %d kept, '
          '%d team decisions to confirm'
          % (path.name, rows, rows - skipped - bare, skipped, len(defined),
             sum(1 for c, _ in defined.values() if c.startswith('keep')),
             sum(1 for c, _ in defined.values() if c.startswith('team decision') and 'to confirm' in c) + len(decided)))
    return errors


def check_register(args, ids, scenarios, scenario_ids, strict, errors):
    counts = collections.Counter()
    based, decided = collections.defaultdict(list), {}
    for section, row, raw in register_rows(args.register):
        low = section.lower()
        if any(low.startswith(s) for s in SKIP_SECTIONS):
            continue
        row_ids = ids.in_text(raw[0]) if raw else []
        if low.startswith('team decisions'):
            for sid in row_ids:
                decided[sid] = ' '.join(raw)
        elif 'basis' in row:
            for sid in row_ids:
                based[sid].append(row)
    if not based:
        errors.append('%s: no table with a Basis column' % args.register.name)
    for sid in ([i for i in scenario_ids if i in strict] if args.only_strict else scenario_ids):
        rows = based.get(sid, [])
        if len(rows) != 1:
            errors.append('%s: %d register rows with a Basis (need 1)' % (sid, len(rows)))
            continue
        row = rows[0]
        parts = [p.strip().lower() for p in row['basis'].split('·')]
        main_basis, extra = parts[0], parts[1:]
        if main_basis not in BASES or any(e != DETAIL for e in extra):
            errors.append("%s: basis '%s' is not Spec, Design, Spec + Design or Team decision" % (sid, row['basis']))
            continue
        evidence = ' '.join(v for k, v in row.items() if 'clause' in k or 'evidence' in k or 'source' in k)
        if not evidence.strip():
            errors.append('%s: no spec clause and no evidence' % sid)
        if 'design' in main_basis and not FRAME.search(evidence):
            errors.append('%s: basis names Design but no frame reference (D/<frame id>) is cited' % sid)
        by_team = main_basis == 'team decision' or extra
        if by_team and sid not in decided:
            errors.append('%s: team decision without a row in "Team decisions"' % sid)
        elif by_team and not DATE.search(decided[sid]):
            errors.append('%s: its "Team decisions" row has no date' % sid)
        elif not by_team and sid in decided:
            errors.append("%s: listed in \"Team decisions\" but its basis is '%s'" % (sid, row['basis']))
        tests = next((v for k, v in row.items() if k in ('tests', 'binding', 'test')), '')
        if tests.strip():
            counts['tested'] += 1
        elif not any(t.startswith(PENDING) for t in scenarios[sid]):
            errors.append('%s: no test and no pending or blocked tag' % sid)
        if sid in strict:
            tags = scenarios[sid]
            soft = sorted(t for t in tags if t.startswith(PENDING) and not t.startswith(('@blocked', '@manual')))
            reasoned = any(re.fullmatch(r'@blocked:\S+', t) or t == '@manual' for t in tags)
            if soft:
                errors.append('%s: carries %s; only a test, @blocked:<reason> or @manual is accepted' % (sid, ', '.join(soft)))
            elif not tests.strip() and not reasoned:
                errors.append('%s: no test, and no @blocked:<reason> or @manual' % sid)
            elif any(t == '@blocked' for t in tags):
                errors.append('%s: @blocked without a reason' % sid)
        counts['team' if main_basis == 'team decision' else 'detail' if extra else 'sourced'] += 1
        if not by_team and 'design' in main_basis:
            counts['design'] += 1
    for sid in sorted(strict - set(scenario_ids)):
        errors.append('%s: named in --strict-ids but not in %s' % (sid, args.feature.name))
    for sid in sorted((set(based) | set(decided)) - set(scenario_ids)):
        errors.append('%s: in the register but not in %s' % (sid, args.feature.name))
    print('%d scenarios: %d by spec or design (%d cite a frame), %d with a detail by team decision, '
          '%d by team decision only, %d with a test'
          % (len(scenario_ids), counts['sourced'], counts['design'], counts['detail'], counts['team'], counts['tested']))


def main():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('feature', type=Path, nargs='?')
    parser.add_argument('register', type=Path, nargs='?')
    parser.add_argument('--report', type=Path, help='a test report that must name every scenario id')
    parser.add_argument('--id-pattern', default=r'@[A-Z]+_[A-Z0-9]+_\d+',
                        help='scenario id tag regex (profile key scenario_id_pattern)')
    parser.add_argument('--coverage', type=Path, help='a plan file (templates/plan.md) to check for coverage')
    parser.add_argument('--proposed-pattern', default=r'\bN\d+\b', help='id of a proposed scenario in a draft')
    parser.add_argument('--only-strict', action='store_true',
                        help='check only the --strict-ids scenarios (a register that does not cover the whole feature yet)')
    parser.add_argument('--strict-ids', default='',
                        help='comma-separated scenario ids that must have a test, @blocked:<reason> or @manual, '
                             'and no other pending tag')
    args = parser.parse_args()
    try:
        ids = Ids(args.id_pattern)
    except re.error as error:
        parser.error('bad --id-pattern: %s' % error)
    if args.coverage:
        errors = check_coverage(args.coverage, re.compile(args.proposed_pattern), ids)
        for error in errors:
            print(error, file=sys.stderr)
        print('gate check: ' + ('OK' if not errors else '%d problem(s)' % len(errors)))
        return 1 if errors else 0
    if not args.feature:
        parser.error('a feature file is needed unless --coverage is given')
    strict = {i.strip().lstrip('@') for i in args.strict_ids.split(',') if i.strip()}
    scenarios = feature_scenarios(args.feature, ids)
    errors = ['%s: %s' % (args.feature.name, sid) for sid in scenarios if sid.endswith('(no id)')]
    scenario_ids = [s for s in scenarios if not s.endswith('(no id)')]
    print('%s: %d scenarios, %d with an id' % (args.feature.name, len(scenarios), len(scenario_ids)))

    if args.register:
        check_register(args, ids, scenarios, scenario_ids, strict, errors)

    if args.report:
        present = set(ids.in_text(read(args.report)))
        for sid in scenario_ids:
            if sid not in present:
                errors.append('%s: missing from %s' % (sid, args.report.name))
        print('%s: %d of %d scenario ids present' % (args.report.name, len(set(scenario_ids) & present), len(scenario_ids)))

    for error in errors:
        print(error, file=sys.stderr)
    print('gate check: ' + ('OK' if not errors else '%d problem(s)' % len(errors)))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
