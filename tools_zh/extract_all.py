#!/usr/bin/env python3
"""Extract natural-language-looking string literals from src/ (excluding fonts)."""
import re, os, json

STR = re.compile(r'"((?:[^"\\]|\\.)*)"')
SKIP_DIRS = {'fonts'}

def looks_natural(s):
    if not s:
        return False
    # too long = embedded source blob
    if len(s) > 160:
        return False
    letters = sum(c.isalpha() for c in s)
    if letters < 2:
        return False
    # heavy escapes / hex = data
    if s.count('\\') > 4:
        return False
    # allowed chars: letters, digits, spaces, common punctuation
    good = sum(c.isalnum() or c in " .:,;!?()/-+'%#=<>[]|*_@&" or c in '\n\t' for c in s)
    if good < len(s) * 0.85:
        return False
    return True

rows = []
for root, ds, fs in os.walk('src'):
    ds[:] = [d for d in ds if d not in SKIP_DIRS]
    for f in fs:
        if not f.endswith(('.c', '.cpp', '.inc')):
            continue
        fp = os.path.join(root, f)
        txt = open(fp, encoding='utf-8', errors='replace').read()
        for m in STR.finditer(txt):
            s = m.group(1)
            if looks_natural(s):
                rows.append((fp, s))

json.dump(rows, open('/tmp/all_natural.json', 'w'), ensure_ascii=False, indent=1)

uniq = sorted(set(s for _, s in rows))
print('total natural string literals:', len(rows))
print('unique:', len(uniq))
for u in uniq:
    print(u)