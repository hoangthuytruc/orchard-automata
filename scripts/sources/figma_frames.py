#!/usr/bin/env python3
"""Optional design-source adapter: read one version of a Figma file through its REST API.

Use it only when the profile's `design_source` names Figma. A tool connection that reads the live file cannot pin a
reference version; this script can.

  figma_frames.py --file <key> [--version <id>] frames <page or section id>      frames under a node: id, name, size
  figma_frames.py --file <key> [--version <id>] text <node id> [--cache <dir>]   visible text of each frame, and the
                                                                                 notes that sit outside frames
  figma_frames.py --file <key> [--version <id>] render <outdir> <id> [<id> ...]  2x PNG of each node
  figma_frames.py --file <key> [--version <id>] exists <id> [<id> ...]           are these nodes in that version?

Without --version the live file is read. The token comes from the FIGMA_TOKEN environment variable only and is
never printed or written. Hidden layers are skipped. A whole page can be 100 MB or more: pass --cache to keep the
JSON for later calls (keep the cache outside the repository).

Exit codes:
  0   done
  1   exists: at least one node is missing from that version
  2   no token, an HTTP error, or rate limited after retries
  64  wrong usage
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = 'https://api.figma.com/v1/'
CONTAINERS = ('FRAME', 'COMPONENT', 'COMPONENT_SET', 'INSTANCE')


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('%s: error: %s' % (self.prog, message), file=sys.stderr)
        sys.exit(64)


def stop(message):
    print(message, file=sys.stderr)
    sys.exit(2)


def token():
    value = os.environ.get('FIGMA_TOKEN', '').strip()
    if not value:
        stop('no Figma token: set the FIGMA_TOKEN environment variable')
    return value


def get(path, version):
    url = API + path
    if version:
        url += ('&' if '?' in path else '?') + 'version=' + version
    secret = token()
    for attempt in range(8):
        try:
            request = urllib.request.Request(url, headers={'X-Figma-Token': secret})
            with urllib.request.urlopen(request, timeout=300) as reply:
                return json.load(reply)
        except urllib.error.HTTPError as error:
            if error.code in (429, 500, 502, 503):
                time.sleep(15 * (attempt + 1))
                continue
            stop('HTTP %d for %s' % (error.code, path.split('?')[0]))
        except urllib.error.URLError as error:
            stop('cannot reach the Figma API: %s' % error.reason)
    stop('rate limited, try again later')


def node(args, node_id, depth=None):
    cache = getattr(args, 'cache', None)
    name = '%s-%s-%s.json' % (args.file, args.version or 'live', node_id.replace(':', '-'))
    if cache and os.path.exists(os.path.join(cache, name)):
        with open(os.path.join(cache, name), encoding='utf-8') as handle:
            data = json.load(handle)
    else:
        data = get('files/%s/nodes?ids=%s%s' % (args.file, node_id, '&depth=%d' % depth if depth else ''), args.version)
        if cache and not depth:
            os.makedirs(cache, exist_ok=True)
            with open(os.path.join(cache, name), 'w', encoding='utf-8') as handle:
                json.dump(data, handle)
    found = data.get('nodes', {}).get(node_id)
    if not found:
        stop('node %s is not in %s' % (node_id, args.version or 'the live file'))
    return found['document']


def texts(n, out):
    if not n.get('visible', True):
        return
    if n['type'] == 'TEXT' and n.get('characters', '').strip():
        out.append(' '.join(n['characters'].split()))
    for child in n.get('children', []):
        texts(child, out)


def print_text(n, depth):
    """Frames print their visible text; text placed outside any frame prints as a NOTE (designer annotations)."""
    for child in n.get('children', []):
        if not child.get('visible', True):
            continue
        pad = '  ' * depth
        if child['type'] == 'TEXT':
            if child.get('characters', '').strip():
                print('%sNOTE %s: %s' % (pad, child['id'], ' '.join(child['characters'].split())))
        elif child['type'] in CONTAINERS:
            found = []
            texts(child, found)
            print('%s%s [%s] %s' % (pad, child.get('name'), child['type'], child['id']))
            for line in found:
                print('%s  - %s' % (pad, line))
        else:
            print('%s%s [%s] %s' % (pad, child.get('name'), child['type'], child['id']))
            print_text(child, depth + 1)


def print_frames(n, depth):
    for child in n.get('children', []):
        box = child.get('absoluteBoundingBox') or {}
        print('%s%s [%s] %s %sx%s' % ('  ' * depth, child.get('name'), child['type'], child['id'],
                                      round(box.get('width', 0)), round(box.get('height', 0))))
        if child['type'] in ('SECTION', 'GROUP') and depth < 2:
            print_frames(child, depth + 1)


def main():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--file', required=True, help='Figma file key')
    parser.add_argument('--version', help='version id; omit for the live file')
    sub = parser.add_subparsers(dest='command', required=True, parser_class=Parser)
    sub.add_parser('frames').add_argument('id')
    text = sub.add_parser('text')
    text.add_argument('id')
    text.add_argument('--cache')
    render = sub.add_parser('render')
    render.add_argument('outdir')
    render.add_argument('ids', nargs='+')
    sub.add_parser('exists').add_argument('ids', nargs='+')
    args = parser.parse_args()

    if args.command == 'frames':
        print_frames(node(args, args.id, depth=3), 0)
    elif args.command == 'text':
        print_text(node(args, args.id), 0)
    elif args.command == 'render':
        os.makedirs(args.outdir, exist_ok=True)
        for start in range(0, len(args.ids), 10):
            chunk = args.ids[start:start + 10]
            data = get('images/%s?ids=%s&scale=2&format=png' % (args.file, ','.join(chunk)), args.version)
            for node_id, url in (data.get('images') or {}).items():
                if not url:
                    print('no render', node_id)
                    continue
                path = os.path.join(args.outdir, node_id.replace(':', '-') + '.png')
                urllib.request.urlretrieve(url, path)
                print(path)
    elif args.command == 'exists':
        missing = 0
        for start in range(0, len(args.ids), 50):
            chunk = args.ids[start:start + 50]
            data = get('files/%s/nodes?ids=%s&depth=1' % (args.file, ','.join(chunk)), args.version)
            for node_id in chunk:
                found = (data.get('nodes') or {}).get(node_id)
                missing += not found
                print('%s %s' % ('ok     ' if found else 'MISSING', node_id))
        return 1 if missing else 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
