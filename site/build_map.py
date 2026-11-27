#!/usr/bin/env python3
"""Build the data of the interactive skill map from the skill set itself.

  build_map.py            write site/skill-map/data.js
  build_map.py --check    say whether site/skill-map/data.js is what this script would write now

Nodes come from the files: each skill's frontmatter and contract table, each script's docstring, each role's and
reference's first paragraph. Links come from what a skill's text points to (scripts, references, roles, templates).
The curated views below (the flows) only place those nodes and name the people steps; a view that names a skill,
script, role or reference that no longer exists stops the build.

Exit codes:
  0   written; or --check: up to date
  1   --check: data.js is stale (run this script and commit the result)
  2   a view names a node that does not exist
  64  wrong usage
"""
import json
import re
import sys
from pathlib import Path

ORCHARD = Path(__file__).resolve().parents[1]
OUT = ORCHARD / 'site' / 'skill-map' / 'data.js'
REPO = 'https://github.com/hoangthuytruc/orchard-automata/blob/main/'  # leak-check: allow (the map links to its own source)

# One short line per skill: what a person gets from it. The long description comes from the skill file.
SKILLS = {
    'adopt': ('you', 'Set a project up'),
    'plan': ('you', 'What to build, and its proof'),
    'run': ('you', 'Build an approved plan'),
    'review': ('you', 'Independent review'),
    'debug': ('you', 'Find why it fails'),
    'test': ('you', 'Write or repair tests'),
    'debt': ('you', 'Rank the weakest code'),
    'update-docs': ('you', 'Record what shipped'),
    'retro': ('you', 'Learn from your runs'),
    'implement': ('run', 'One package, test first'),
    'verify': ('run', 'Run and record the checks'),
    'handoff': ('run', 'Report you can accept from'),
}
SCRIPT_SUBS = {
    'discover.sh': 'What the repository looks like', 'evidence.py': 'Records every check', 'gate_check.py': 'Checks scenarios and coverage',
    'leak_check.py': 'Finds private text in core', 'lock_check.py': 'Proves locked files unchanged', 'plan_seal.py': 'Binds approval to the text',
    'post_review.py': 'Posts one review, never approves', 'profile_check.py': 'Checks the project profile', 'runlog.py': 'Writes the run log',
    'verdict.py': 'Computes the verdict', 'sources/figma_frames.py': 'Reads design frames (optional)',
}
ROLE_SUBS = {
    'coordinator': 'The session you started', 'planner': 'The session you talk to', 'implementer': 'Separate agent, one per package',
    'verifier': 'Scripts, run by the coordinator', 'reviewer': 'Separate agent, read-only', 'documenter': 'Writes what a person keeps',
    'report-writer': 'Separate agent, Strict only', 'plan-verifier': 'Separate agent, checks the plan',
}
PEOPLE = {
    'p-ticket': ('Ticket or task', 'You bring it', 'A ticket, a spec and a design, or one sentence. The plan reads the sources fresh.'),
    'p-approve': ('You approve', 'the plan · decision 1 of 2', 'The plan becomes approved only on your word for the whole plan. Its text is then sealed: a later edit stops the run.'),
    'p-accept': ('You accept', 'or send back · decision 2 of 2', 'You read one report: a computed verdict, the proof per scenario, and what did not run. Accept, or send back in your own words.'),
    'p-commit': ('You commit', 'and open the pull request', 'No skill commits, pushes, or opens, approves or merges a pull request.'),
    'p-symptom': ('Something fails', 'what you saw and expected', 'A crash, a wrong value, a flaky test. Say what you saw and what you expected.'),
    'p-target': ('A change to review', 'PR, branch or working tree', 'A pull request number, a branch, a commit range, a path, or the uncommitted working tree.'),
    'p-post': ('You post it, or not', 'only on request', 'Nothing is written to the pull request unless you ask for a draft or a posted review. It is never an approval.'),
    'p-confirm': ('You confirm', 'the profile, once per project', 'Every value in the profile carries its source. You confirm each one; later runs re-check the sources by hash.'),
}
FILES = {
    'f-plan': ('The plan file', 'Sealed when approved', 'One file: a top part for you, working detail for the agents. Templates: templates/plan.md.', 'templates/plan.md'),
    'f-evidence': ('evidence.jsonl', 'One record per check', 'What ran, on which exact state of the change, with what result. Red runs keep the hash of their test files.', 'docs/principles.md'),
    'f-review': ('review-round-N.md', 'The reviewer, unchanged', 'The reviewer\'s final message, saved as it was returned. One file per round.', 'references/review-checklist.md'),
    'f-report': ('The test report', 'Verdict, proof, gaps', 'One screen on top in plain words, the evidence below, and a draft pull-request body.', 'templates/test-report.md'),
    'f-runlog': ('The run log', 'On your machine only', 'What each run did, written by a script: tiers, failed loops with their cause, findings, tokens and time when the tool reports them.', 'scripts/runlog.py'),
    'f-profile': ('.orchard/profile.md', 'The project\'s facts', 'Build, test and lint commands, where scenarios, specs and designs live, which files are locked. Each value with its source.', 'templates/project-profile.md'),
    'f-rules': ('.orchard/review-rules.md', 'Your own review rules', 'They win over the generic checklist.', 'templates/review-rules.md'),
    'f-agents': ('.orchard/agents.md', 'Who plays each role', 'Which agent and which model class plays each role. A personal override stays out of git.', 'templates/agents.md'),
    'f-features': ('Feature files', 'Gherkin, locked in a run', 'The scenario files are the single source of truth between product and engineering. Only update-docs writes them, after acceptance.', 'references/scenario-register.md'),
    'f-diagnosis': ('diagnosis.md', 'Cause, with one failing test', 'The reproduction, the hypotheses tried, the cause at path:line and the regression test that fails because of it.', 'skills/debug/SKILL.md'),
    'f-installed': ('.claude/skills/orchard', 'A copy, kept out of git', 'The install script copies the skill set into the project and adds it to the local git exclude.', 'adapters/claude-code/README.md'),
    's-install': ('install.sh', 'Copies the skill set in', 'adapters/claude-code/install.sh <project root>. Run it again to update.', 'adapters/claude-code/install.sh'),
}


def read(path):
    return (ORCHARD / path).read_text(encoding='utf-8')


def plain(text):
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    return re.sub(r'\s+', ' ', text.replace('`', '').replace('$ORCHARD/', '')).strip()


def first_sentences(text, limit=320):
    text = plain(text)
    if len(text) <= limit:
        return text
    cut = text[:limit]
    return cut[:cut.rfind('. ') + 1] if '. ' in cut else cut.rsplit(' ', 1)[0] + '…'


def skill_node(name):
    text = read('skills/%s/SKILL.md' % name)
    front = re.search(r'^description: (.*)$', text, re.M).group(1)
    hint = re.search(r'^argument-hint: "?(.*?)"?$', text, re.M)
    row = [c.strip() for c in re.search(r'^\| Reads \|.*\n\|[- |]+\n(\|.*)$', text, re.M).group(1).strip('|').split(' | ')]
    stance = re.search(r'^## Stance\n\n(.*)$', text, re.M)
    always = re.search(r'^## Rule that always holds\n\n(.*)$', text, re.M)
    kind, sub = SKILLS[name]
    links = {
        'scripts': sorted(set(re.findall(r'scripts/([a-z_/]+\.(?:py|sh))', text))),
        'references': sorted(set(re.findall(r'references/([a-z-]+)\.md', text))),
        'roles': sorted(set(re.findall(r'roles/([a-z-]+)\.md', text))),
    }
    return {
        'id': name, 'kind': 'skill-' + kind, 'title': name, 'sub': sub, 'path': 'skills/%s/SKILL.md' % name,
        'detail': first_sentences(front, 420),
        'facts': [f for f in (
            ('You type', '/orchard:%s %s' % (name, hint.group(1)) if hint else '/orchard:%s' % name),
            ('Writes', first_sentences(row[1], 260)),
            ('Never', first_sentences(row[2], 260)),
            ('Stance', first_sentences(stance.group(1), 200) if stance else ''),
            ('Always', first_sentences(always.group(1), 200) if always else ''),
        ) if f[1]],
        'view': 'skill-' + name, 'links': links,
    }


def script_node(rel):
    text = read('scripts/' + rel)
    if rel.endswith('.sh'):
        doc = ' '.join(line.lstrip('# ') for line in text.splitlines()[1:4])
    else:
        doc = re.search(r'"""(.*?)\n\n', text, re.S).group(1)
    return {'id': 's-' + rel, 'kind': 'script', 'title': rel.split('/')[-1], 'sub': SCRIPT_SUBS[rel], 'path': 'scripts/' + rel,
            'detail': first_sentences(doc, 360), 'facts': []}


def doc_node(folder, kind, name):
    lines = read('%s/%s.md' % (folder, name)).splitlines()
    title = lines[0].lstrip('# ').replace('Role: ', '')
    body = ' '.join(line for line in lines[2:8] if line and not line.startswith(('|', '#')))
    return {'id': '%s-%s' % (kind[0], name), 'kind': kind, 'title': name.replace('-', ' ') if kind == 'role' else name,
            'sub': ROLE_SUBS[name] if kind == 'role' else title, 'path': '%s/%s.md' % (folder, name),
            'detail': first_sentences(body, 360), 'facts': []}


def static_node(node_id, kind, spec):
    title, sub, detail = spec[:3]
    node = {'id': node_id, 'kind': kind, 'title': title, 'sub': sub, 'detail': detail, 'facts': []}
    if len(spec) > 3:
        node['path'] = spec[3]
    return node


def grid(rows):
    """Rows of cells -> [{id, col, row}]; '' leaves a gap."""
    return [{'id': cell, 'col': col, 'row': row} for row, cells in enumerate(rows) for col, cell in enumerate(cells) if cell]


def chain(*ids, kind='calls'):
    return [{'from': a, 'to': b, 'kind': kind} for a, b in zip(ids, ids[1:])]


def curated_views():
    loop = {'from': 'review', 'to': 'implement', 'kind': 'loop', 'label': 'fix, up to 3 rounds'}
    return [
        {'id': 'overview', 'title': 'From ticket to commit', 'about': 'The feature-development workflow. You decide twice; a run does not wait for you in between.',
         'path': 'workflows/feature-development.md',
         'place': grid([
             ['p-ticket', 'plan', 'p-approve', 'run', 'p-accept', 'update-docs', 'p-commit'],
             ['', '', 'implement', 'verify', 'review', 'handoff'],
             ['adopt', 'debug', 'test', 'debt', 'retro'],
         ]),
         'groups': [{'label': 'A run calls these, and does not ask', 'ids': ['implement', 'verify', 'review', 'handoff']},
                    {'label': 'Any time, each on its own', 'ids': ['debug', 'test', 'debt', 'retro']},
                    {'label': 'Once per project', 'ids': ['adopt']}],
         'edges': chain('p-ticket', 'plan', 'p-approve', 'run', 'implement', 'verify', 'review', 'handoff', 'p-accept', 'update-docs', 'p-commit')
                  + [loop, {'from': 'adopt', 'to': 'plan', 'kind': 'feeds', 'label': 'profile'},
                     {'from': 'debug', 'to': 'plan', 'kind': 'feeds', 'label': 'a diagnosis'}]},
        {'id': 'bug-fix', 'title': 'Bug fix', 'about': 'No fix before reproduction: debug leaves one failing test, and the fix starts from it. update-docs runs only when a scenario changed.',
         'path': 'workflows/bug-fix.md',
         'place': grid([
             ['p-symptom', 'debug', 'plan', 'p-approve', 'run', 'p-accept', 'update-docs', 'p-commit'],
             ['', 'f-diagnosis', '', 'implement', 'verify', 'review', 'handoff'],
         ]),
         'groups': [{'label': 'A run calls these, and does not ask', 'ids': ['implement', 'verify', 'review', 'handoff']}],
         'edges': chain('p-symptom', 'debug', 'plan', 'p-approve', 'run', 'implement', 'verify', 'review', 'handoff', 'p-accept', 'update-docs', 'p-commit')
                  + [loop, {'from': 'debug', 'to': 'f-diagnosis', 'kind': 'writes'},
                     {'from': 'f-diagnosis', 'to': 'plan', 'kind': 'feeds', 'label': 'compact plan'}]},
        {'id': 'review-only', 'title': 'Review only', 'about': 'A separate, read-only reviewer judges a change it did not write. Nothing is posted unless you ask.',
         'path': 'workflows/review-only.md',
         'place': grid([
             ['p-target', 'review', 'r-reviewer', 'f-review', 'p-post'],
             ['', 'f-rules', 'r-review-checklist', 'r-standards', 's-post_review.py'],
         ]),
         'groups': [{'label': 'What the reviewer reads', 'ids': ['f-rules', 'r-review-checklist', 'r-standards']}],
         'edges': chain('p-target', 'review') + [
             {'from': 'review', 'to': 'r-reviewer', 'kind': 'starts'}, {'from': 'r-reviewer', 'to': 'f-review', 'kind': 'writes'},
             {'from': 'f-review', 'to': 'p-post', 'kind': 'calls'}, {'from': 'p-post', 'to': 's-post_review.py', 'kind': 'calls', 'label': 'on request'},
             {'from': 'f-rules', 'to': 'r-reviewer', 'kind': 'feeds'}, {'from': 'r-review-checklist', 'to': 'r-reviewer', 'kind': 'feeds'},
             {'from': 'r-standards', 'to': 'r-reviewer', 'kind': 'feeds'}]},
        {'id': 'run', 'title': 'Inside a run', 'about': 'Agents work through files, never through each other. Scripts produce the evidence and compute the verdict.',
         'path': 'references/run-flow.md',
         'place': grid([
             ['f-plan', 'run', 'r-implementer', 'verify', 'r-reviewer', 'handoff', 'f-report'],
             ['s-plan_seal.py', 's-lock_check.py', 'implement', 's-evidence.py', 'review', 's-verdict.py'],
             ['f-features', 's-runlog.py', '', 'f-evidence', 'f-review'],
             ['', 'f-runlog'],
         ]),
         'groups': [{'label': 'A separate agent', 'ids': ['r-implementer']}, {'label': 'A separate agent', 'ids': ['r-reviewer']}],
         'edges': chain('f-plan', 'run') + [
             {'from': 'run', 'to': 'r-implementer', 'kind': 'starts', 'label': 'one per package'},
             {'from': 'r-implementer', 'to': 'verify', 'kind': 'calls'}, {'from': 'verify', 'to': 'r-reviewer', 'kind': 'starts'},
             {'from': 'r-reviewer', 'to': 'handoff', 'kind': 'calls'}, {'from': 'handoff', 'to': 'f-report', 'kind': 'writes'},
             {'from': 'r-reviewer', 'to': 'r-implementer', 'kind': 'loop', 'label': 'fix, up to 3 rounds'},
             {'from': 'f-plan', 'to': 's-plan_seal.py', 'kind': 'reads', 'label': 'seal'}, {'from': 'run', 'to': 's-lock_check.py', 'kind': 'calls'},
             {'from': 's-lock_check.py', 'to': 'f-features', 'kind': 'reads', 'label': 'locked'},
             {'from': 'r-implementer', 'to': 'implement', 'kind': 'calls', 'label': 'follows'}, {'from': 'verify', 'to': 's-evidence.py', 'kind': 'calls'},
             {'from': 's-evidence.py', 'to': 'f-evidence', 'kind': 'writes'}, {'from': 'r-reviewer', 'to': 'review', 'kind': 'calls', 'label': 'follows'},
             {'from': 'review', 'to': 'f-review', 'kind': 'writes'}, {'from': 'handoff', 'to': 's-verdict.py', 'kind': 'calls'},
             {'from': 'f-evidence', 'to': 's-verdict.py', 'kind': 'feeds'}, {'from': 'f-review', 'to': 's-verdict.py', 'kind': 'feeds'},
             {'from': 'run', 'to': 's-runlog.py', 'kind': 'calls'}, {'from': 's-runlog.py', 'to': 'f-runlog', 'kind': 'writes'}]},
        {'id': 'install', 'title': 'Install and adopt', 'about': 'Two commands to install, one skill to adopt. The project keeps one folder, .orchard/.',
         'path': 'adapters/claude-code/README.md',
         'place': grid([
             ['s-install', 'f-installed', 'adopt', 'p-confirm', 'f-profile'],
             ['', '', 's-discover.sh', 's-profile_check.py', 'f-rules'],
             ['', '', '', '', 'f-agents'],
         ]),
         'groups': [{'label': 'What your project gains', 'ids': ['f-profile', 'f-rules', 'f-agents']}],
         'edges': chain('s-install', 'f-installed', 'adopt', 'p-confirm', 'f-profile', kind='calls') + [
             {'from': 'adopt', 'to': 's-discover.sh', 'kind': 'calls'}, {'from': 'adopt', 'to': 's-profile_check.py', 'kind': 'calls'},
             {'from': 'adopt', 'to': 'f-rules', 'kind': 'writes'}, {'from': 'adopt', 'to': 'f-agents', 'kind': 'writes'}]},
    ]


def skill_view(node, nodes):
    name = node['id']
    reads = ['r-' + r for r in node['links']['references']]
    scripts = ['s-' + s for s in node['links']['scripts']]
    roles = ['o-' + r for r in node['links']['roles'] if r not in ('planner', 'documenter')]
    right = len(scripts) + len(roles) + (0.5 if scripts and roles else 0)
    rows = max(len(reads), right, 1)
    place = [{'id': name, 'col': 1, 'row': (rows - 1) / 2}]
    place += [{'id': i, 'col': 0, 'row': (rows - len(reads)) / 2 + k} for k, i in enumerate(reads)]
    top = (rows - right) / 2
    place += [{'id': i, 'col': 2, 'row': top + k} for k, i in enumerate(scripts)]
    place += [{'id': i, 'col': 2, 'row': top + right - len(roles) + k} for k, i in enumerate(roles)]
    edges = ([{'from': i, 'to': name, 'kind': 'feeds'} for i in reads]
             + [{'from': name, 'to': i, 'kind': 'calls'} for i in scripts]
             + [{'from': name, 'to': i, 'kind': 'starts'} for i in roles])
    groups = [g for g in ({'label': 'It reads', 'ids': reads}, {'label': 'It runs', 'ids': scripts},
                          {'label': 'Roles it names', 'ids': roles}) if g['ids']]
    return {'id': 'skill-' + name, 'title': 'Skill: ' + name, 'path': node['path'],
            'about': '%s. What it reads, what it runs, and the roles it names. Click the skill for its contract.' % node['sub'],
            'place': place, 'groups': groups, 'edges': edges, 'parent': 'overview'}


def build():
    nodes = {}
    for name in SKILLS:
        nodes[name] = skill_node(name)
    for path in sorted((ORCHARD / 'scripts').rglob('*')):
        if path.suffix in ('.py', '.sh') and path.name != 'selftest.py':
            node = script_node(path.relative_to(ORCHARD / 'scripts').as_posix())
            nodes[node['id']] = node
    for path in sorted((ORCHARD / 'references').glob('*.md')):
        node = doc_node('references', 'reference', path.stem)
        nodes[node['id']] = node
    for path in sorted((ORCHARD / 'roles').glob('*.md')):
        node = doc_node('roles', 'role', path.stem)
        node['id'] = 'o-' + path.stem
        nodes[node['id']] = node
    # the two separate agents are referred to by short ids in the curated views
    nodes['r-implementer'] = dict(nodes['o-implementer'], id='r-implementer')
    nodes['r-reviewer'] = dict(nodes['o-reviewer'], id='r-reviewer')
    for node_id, spec in PEOPLE.items():
        nodes[node_id] = static_node(node_id, 'person', spec)
    for node_id, spec in FILES.items():
        nodes[node_id] = static_node(node_id, 'script' if node_id.startswith('s-') else 'file', spec)
    views = curated_views() + [skill_view(nodes[name], nodes) for name in SKILLS]
    missing = sorted({i for v in views for i in [p['id'] for p in v['place']] + [e[k] for e in v['edges'] for k in ('from', 'to')]
                      + [g for group in v['groups'] for g in group['ids']] if i not in nodes})
    if missing:
        print('a view names nodes that do not exist: %s' % ', '.join(missing), file=sys.stderr)
        sys.exit(2)
    for node in nodes.values():
        node.pop('links', None)
    data = {'repo': REPO, 'nodes': nodes, 'views': views}
    return '// Generated by site/build_map.py from the skill set. Do not edit by hand.\nwindow.ORCHARD_MAP = %s;\n' % json.dumps(
        data, indent=1, ensure_ascii=False, sort_keys=True)


def main():
    args = sys.argv[1:]
    if args not in ([], ['--check']):
        print(__doc__, file=sys.stderr)
        return 64
    text = build()
    if args:
        current = OUT.read_text(encoding='utf-8') if OUT.exists() else ''
        print('skill map data: %s' % ('up to date' if current == text else 'stale; run site/build_map.py'))
        return 0 if current == text else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding='utf-8')
    data = json.loads(text[text.index('{'):text.rindex('}') + 1])
    print('skill map data: %d nodes, %d views -> %s' % (len(data['nodes']), len(data['views']), OUT.relative_to(ORCHARD)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
