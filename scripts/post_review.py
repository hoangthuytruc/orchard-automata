#!/usr/bin/env python3
"""Post a review payload to a GitHub pull request as ONE review with inline comments. Never approves.

  post_review.py <pr number> <payload.json> --draft      leave a pending review (only you see it; submit on GitHub)
  post_review.py <pr number> <payload.json> --post       submit it: request changes when a finding blocks, else comment
  post_review.py <pr number> <payload.json> --dry-run    print what would be sent; write nothing

The payload is the one the reviewer role writes (roles/reviewer.md; labels in references/review-checklist.md):
{"commit_id", "body", "comments": [{"path", "line", "side", "start_line"?, "body"}]}. Before sending, every inline
comment is checked against the pull request's diff: GitHub rejects the whole review when one line is outside a hunk,
so a comment that cannot be anchored is moved into the summary under "Outside the diff". A comment blocks when the
first line of its body carries the type Blocker or Risk, or the severity High or Medium.

The script stops when the pull request's head is no longer the reviewed commit, or when you already hold a pending
review there. Uses the `gh` command line with its own sign-in; run it inside the repository. Posting is an action
for a person to ask for: a skill never runs --post or --draft on its own.

Exit codes:
  0   posted, left as draft, or printed (--dry-run)
  1   gh failed, the head moved, or a pending review already exists
  64  wrong usage, or the payload cannot be read
"""
import argparse
import json
import re
import subprocess
import sys

HUNK = re.compile(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@')
BLOCKING = re.compile(r'\b(?:Blocker|Risk)\b\s*[·.]|·\s*(?:High|Medium)\b')


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('%s: error: %s' % (self.prog, message), file=sys.stderr)
        sys.exit(64)


def fail(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def gh(*args, stdin=None):
    try:
        done = subprocess.run(['gh', *args], input=stdin, capture_output=True, text=True)
    except OSError as error:
        fail('cannot run gh: %s' % error)
    if done.returncode != 0:
        fail('gh %s failed: %s' % (' '.join(args[:3]), done.stderr.strip()))
    return done.stdout


def hunk_lines(patch):
    """({old line numbers}, {new line numbers}) that a comment may be anchored to."""
    left, right, old, new = set(), set(), 0, 0
    for line in (patch or '').splitlines():
        start = HUNK.match(line)
        if start:
            old, new = int(start.group(1)), int(start.group(2))
        elif line.startswith('+'):
            right.add(new)
            new += 1
        elif line.startswith('-'):
            left.add(old)
            old += 1
        elif not line.startswith('\\'):
            left.add(old)
            right.add(new)
            old += 1
            new += 1
    return left, right


def anchored(comment, lines):
    left, right = lines.get(comment.get('path'), (set(), set()))
    valid = left if comment.get('side', 'RIGHT') == 'LEFT' else right
    wanted = [comment.get('line')] + ([comment['start_line']] if comment.get('start_line') else [])
    return all(isinstance(n, int) and n in valid for n in wanted)


def load_json(path):
    try:
        with open(path, encoding='utf-8') as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        print('cannot read %s: %s' % (path, error), file=sys.stderr)
        sys.exit(64)


def main():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('pr', type=int)
    parser.add_argument('payload')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--draft', action='store_true')
    mode.add_argument('--post', action='store_true')
    mode.add_argument('--dry-run', action='store_true')
    parser.add_argument('--files-json', help='testing: a saved reply of the pull request files endpoint')
    args = parser.parse_args()

    payload = load_json(args.payload)
    comments = payload.get('comments') or []
    if args.files_json:
        files = load_json(args.files_json)
    else:
        head = json.loads(gh('pr', 'view', str(args.pr), '--json', 'headRefOid,url'))
        if payload.get('commit_id') and payload['commit_id'] != head['headRefOid']:
            fail('the pull request head is %s, the review was written for %s: review again'
                 % (head['headRefOid'][:9], payload['commit_id'][:9]))
        files = json.loads(gh('api', '--paginate', '--slurp', 'repos/{owner}/{repo}/pulls/%d/files' % args.pr))
        files = [item for page in files for item in page]
    lines = {item['filename']: hunk_lines(item.get('patch')) for item in files}

    inline = [c for c in comments if anchored(c, lines)]
    loose = [c for c in comments if not anchored(c, lines)]
    body = (payload.get('body') or '').rstrip()
    if loose:
        if '### Outside the diff' not in body:
            body += '\n\n### Outside the diff'
        for comment in loose:
            body += '\n- `%s:%s`: %s' % (comment.get('path'), comment.get('line'),
                                         ' '.join(comment.get('body', '').split()))
    blocking = sum(1 for c in comments if BLOCKING.search(c.get('body', '').split('\n', 1)[0]))
    review = {'body': body, 'comments': [
        {key: c[key] for key in ('path', 'line', 'side', 'start_line', 'start_side', 'body') if key in c}
        for c in inline]}
    for comment in review['comments']:
        comment.setdefault('side', 'RIGHT')
    if payload.get('commit_id'):
        review['commit_id'] = payload['commit_id']
    if args.post:
        review['event'] = 'REQUEST_CHANGES' if blocking else 'COMMENT'

    summary = '%d inline, %d moved to the summary, %d blocking' % (len(inline), len(loose), blocking)
    if args.dry_run:
        print(json.dumps(review, indent=2, ensure_ascii=False))
        print('dry run: %s; nothing written' % summary)
        return 0

    me = json.loads(gh('api', 'user'))['login']
    existing = json.loads(gh('api', '--paginate', '--slurp', 'repos/{owner}/{repo}/pulls/%d/reviews' % args.pr))
    if any(r['state'] == 'PENDING' and r['user']['login'] == me for page in existing for r in page):
        fail('you already have a pending review on this pull request: submit or discard it on GitHub first')
    reply = json.loads(gh('api', '-X', 'POST', 'repos/{owner}/{repo}/pulls/%d/reviews' % args.pr, '--input', '-',
                          stdin=json.dumps(review)))
    print('%s review: %s' % ('draft (pending)' if args.draft else reply.get('state', 'submitted').lower(),
                             reply.get('html_url', '')))
    print(summary)
    return 0


if __name__ == '__main__':
    sys.exit(main())
