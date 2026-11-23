#!/usr/bin/env python3
"""Safe translator for the web configurator's visible text.

Translates only display text OUTSIDE <script> blocks (the scripts hold
back-end protocol values like "on"/"off"/"running" that must not change),
plus the navigation labels in base.html. Long keys match first so a heading
is not half-translated by a shorter key.
"""
import os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(os.path.join(HERE, '..', 'source', 'webserver', 'src', 'x6100_webserver'))
sys.path.insert(0, HERE)
from dict_zh import load as load_dict

SCRIPT_RE = re.compile(r'(<script\b[^>]*>.*?</script>)', re.S)
STYLE_RE = re.compile(r'(<style\b[^>]*>.*?</style>)', re.S)

def translate_segment(seg, tr):
    new = seg
    for k, v in sorted(tr.items(), key=lambda kv: -len(kv[0])):
        # text node
        new = new.replace('>' + k + '<', '>' + v + '<')
        # attribute value
        new = new.replace('"' + k + '"', '"' + v + '"')
    return new

def main():
    d = load_dict()
    tr = {k: v for k, v in d.items() if any(ord(c) > 0x7F for c in v)}
    # Do not translate back-end enum tokens used verbatim in scripts / markup.
    skip = {'on', 'off', 'On', 'Off', 'ON', 'OFF', 'true', 'false', 'running', 'stopped',
            'enable', 'disable', 'enabled', 'disabled', 'start', 'stop', 'auto', 'Auto'}
    for s in skip:
        tr.pop(s, None)
    print('translation entries:', len(tr))

    changed = 0
    for root, ds, fs in os.walk(os.path.join(WEB, 'views')):
        for f in fs:
            if not f.endswith('.html'):
                continue
            fp = os.path.join(root, f)
            text = open(fp, encoding='utf-8').read()

            # split into script/style blocks and visible segments
            parts = []
            pos = 0
            for m in re.finditer(r'(<script\b[^>]*>.*?</script>)|(<style\b[^>]*>.*?</style>)', text, re.S):
                parts.append(('vis', text[pos:m.start()]))
                parts.append(('code', m.group(0)))
                pos = m.end()
            parts.append(('vis', text[pos:]))

            new_parts = []
            for kind, seg in parts:
                new_parts.append((kind, translate_segment(seg, tr) if kind == 'vis' else seg))
            new = ''.join(p for _, p in new_parts)

            if new != text:
                open(fp, 'w', encoding='utf-8').write(new)
                changed += 1
                print('  wrote', os.path.relpath(fp, WEB))
    print('changed files:', changed)

if __name__ == '__main__':
    main()