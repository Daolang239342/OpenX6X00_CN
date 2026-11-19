#!/usr/bin/env python3
"""Apply the Chinese translation dictionary to the extracted string literals.

Reads tools_zh/candidates.json (literal occurrences with offsets) and the
dict_zh package. For each literal whose raw text is in the dictionary, replaces
the quoted literal in place. Files are rewritten only when changed.

The translation dictionary values are plain Python strings. Non-ASCII
characters (Chinese) are written as UTF-8; ASCII control characters are
escaped as C escapes (\\n, \\t, \\", \\\\, \\xNN).
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', 'source'))
sys.path.insert(0, HERE)
from dict_zh import load as load_dict

def c_escape(s: str) -> str:
    out = []
    for ch in s:
        o = ord(ch)
        if ch == '\\':
            out.append('\\\\')
        elif ch == '"':
            out.append('\\"')
        elif ch == '\n':
            out.append('\\n')
        elif ch == '\t':
            out.append('\\t')
        elif ch == '\r':
            out.append('\\r')
        elif o < 0x20 or o == 0x7f:
            out.append(f'\\x{o:02x}')
        else:
            out.append(ch)  # includes CJK UTF-8
    return ''.join(out)

def main():
    d = load_dict()
    print(f'loaded {len(d)} dictionary entries')

    cand_path = os.path.join(HERE, 'candidates.json')
    with open(cand_path, encoding='utf-8') as fh:
        rows = json.load(fh)

    # group by file
    from collections import defaultdict
    byfile = defaultdict(list)
    for r in rows:
        byfile[r['file']].append(r)

    changed_files = 0
    applied = 0
    skipped = 0
    for fp, rs in sorted(byfile.items()):
        absfp = os.path.normpath(os.path.join(ROOT, fp))
        if not os.path.abspath(absfp).startswith(ROOT):
            print('skip outside root:', fp)
            continue
        text = open(absfp, encoding='utf-8').read()
        # apply replacements from end to start
        edits = []
        for r in rs:
            raw = r['raw']
            if raw not in d:
                skipped += 1
                continue
            tr = d[raw]
            if tr == raw:
                skipped += 1
                continue
            start, end = r['start'], r['end']
            # sanity: the slice between quotes must equal raw
            if text[start:end] != raw:
                print(f"mismatch {fp}:{r['line']}: {raw!r} != {text[start:end]!r}")
                skipped += 1
                continue
            quoted = '"' + c_escape(tr) + '"'
            edits.append((start - 1, end + 1, quoted))
            applied += 1

        if not edits:
            continue
        # apply from end to start to keep offsets valid
        edits.sort(key=lambda x: -x[0])
        for s, e, rep in edits:
            text = text[:s] + rep + text[e:]
        open(absfp, 'w', encoding='utf-8').write(text)
        changed_files += 1
        print(f'  wrote {fp}: {len(edits)} literals')

    print(f'applied={applied} skipped={skipped} changed_files={changed_files}')

if __name__ == '__main__':
    main()