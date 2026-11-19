#!/usr/bin/env python3
"""Extract UI-bound string literals from the OpenX6X00 C/C++ sources.

UI call sites: lv_label_set_text(_fmt), lv_btnmatrix_set_map, lv_dropdown_set_options,
lv_table_set_cell_value, msg_update_text(_fmt), text_popup_*, title/label helpers,
BTN_TEXT labels, and the .items menus used by the built-in popup menus.
"""
import re, os, json

CALL = re.compile(
    r'(lv_label_set_text(?:_fmt)?|lv_btnmatrix_set_map|lv_dropdown_set_options|'
    r'lv_table_set_cell_value|msg_update_text(?:_fmt)?|msg_set_text(?:_fmt)?|'
    r'text_popup_show|dialog_title|title_set|row_label|wl_row_label|'
    r'lv_btn_set_text|btn_set_text|make_row|menu_add|list_add|add_item)\s*\('
)
BTN = re.compile(r'\.label\s*=\s*"([^"]*)"')
BTNM = re.compile(r'(?:static\s+)?(?:const\s+)?char\s*\*?\s*\w+\[\]\[\]\s*=\s*\{')
STR = re.compile(r'"((?:[^"\\]|\\.)*)"')

def has_word(s):
    return sum(c.isalpha() for c in s) >= 2

rows = []
for root, ds, fs in os.walk('src'):
    for f in fs:
        if not f.endswith(('.c', '.cpp', '.inc')):
            continue
        fp = os.path.join(root, f)
        lines = open(fp, encoding='utf-8', errors='replace').read().split('\n')
        for i, line in enumerate(lines, 1):
            if CALL.search(line):
                for m in STR.finditer(line):
                    s = m.group(1).replace('\\"', '"').replace('\\n', '\\n')
                    if has_word(s):
                        rows.append({'file': fp, 'line': i, 'kind': 'call',
                                     'raw': line.strip(), 's': s})
            m = BTN.search(line)
            if m:
                s = m.group(1)
                if has_word(s):
                    rows.append({'file': fp, 'line': i, 'kind': 'btn',
                                 'raw': line.strip(), 's': s})

json.dump(rows, open('/tmp/ui_candidates.json', 'w'), ensure_ascii=False, indent=1)

# Summaries
from collections import defaultdict, Counter
byfile = defaultdict(int)
uniq = set()
for r in rows:
    byfile[r['file']] += 1
    uniq.add(r['s'])
print('files with UI candidates:', len(byfile))
for fp in sorted(byfile, key=lambda x: -byfile[x]):
    if byfile[fp] >= 2:
        print(f"{byfile[fp]:4d}  {fp}")
print('TOTAL candidate sites:', len(rows))
print('UNIQUE candidate strings:', len(uniq))