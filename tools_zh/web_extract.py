#!/usr/bin/env python3
"""Extract translatable webserver strings (views HTML + Python modules)."""
import os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.abspath(os.path.join(HERE, '..', 'source', 'webserver', 'src', 'x6100_webserver'))

# visible text between > and <
TEXT = re.compile(r'>([^<>{}]*[A-Za-z][^<>{}]*)<')
# translatable attributes
ATTR = re.compile(r'\b(value|placeholder|title|label|alt|data-label)\s*=\s*"([^"]*[A-Za-z][^"]*)"')
# python string literals
PYSTR = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')

rows = []
uniq = set()

def look(text):
    return sum(c.isalpha() for c in text) >= 2

for root, ds, fs in os.walk(WEB):
    ds[:] = [d for d in ds if d not in ('static',)]
    for f in fs:
        if not (f.endswith('.html') or f.endswith('.py')):
            continue
        fp = os.path.join(root, f)
        text = open(fp, encoding='utf-8').read()
        if f.endswith('.html'):
            for m in TEXT.finditer(text):
                s = m.group(1).strip()
                if look(s):
                    rows.append({'file': os.path.relpath(fp, WEB), 'kind': 'text', 'raw': s})
                    uniq.add(s)
            for m in ATTR.finditer(text):
                s = m.group(2)
                if look(s):
                    rows.append({'file': os.path.relpath(fp, WEB), 'kind': 'attr', 'raw': s})
                    uniq.add(s)
        else:
            for m in PYSTR.finditer(text):
                s = m.group(1)
                if look(s) and '\\' not in s:
                    rows.append({'file': os.path.relpath(fp, WEB), 'kind': 'py', 'raw': s})
                    uniq.add(s)

json.dump(rows, open(os.path.join(HERE, 'web_candidates.json'), 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, 'web_candidates_uniq.txt'), 'w') as fh:
    for u in sorted(uniq):
        fh.write(repr(u) + '\n')
print('webserver candidate sites:', len(rows))
print('unique:', len(uniq))