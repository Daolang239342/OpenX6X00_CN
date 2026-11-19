#!/usr/bin/env python3
"""Dump UI-bound string literals with their RAW source form (escapes preserved).

Output accumulates each file's candidates; also writes a template dict where
every ORIGINAL literal maps to '' so the translation map can be filled in.
"""
import re, os, json

CALL = re.compile(
    r'(lv_label_set_text(?:_fmt)?|lv_btnmatrix_set_map|lv_dropdown_set_options|'
    r'lv_table_set_cell_value|msg_update_text(?:_fmt)?|msg_set_text(?:_fmt)?|'
    r'text_popup_show|dialog_title|title_set|row_label|wl_row_label|'
    r'lv_btn_set_text|btn_set_text|make_row|menu_add|list_add|add_item)\s*\('
)
BTN = re.compile(r'\.label\s*=\s*("(?:[^"\\]|\\.)*")')
# menu item initialisers like { "Connect", "", ... }
MENU = re.compile(r'\{\s*("(?:[^"\\]|\\.)*")\s*,\s*"[^"]*"')
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
                    raw = m.group(1)
                    if has_word(raw):
                        rows.append({'file': fp, 'line': i, 'kind': 'call',
                                     'raw': raw, 'line_src': line.strip()})
            m = BTN.search(line)
            if m:
                raw = re.match(r'"((?:[^"\\]|\\.)*)"', m.group(1)).group(1)
                if has_word(raw):
                    rows.append({'file': fp, 'line': i, 'kind': 'btn',
                                 'raw': raw, 'line_src': line.strip()})
            for m in MENU.finditer(line):
                raw = re.match(r'"((?:[^"\\]|\\.)*)"', m.group(1)).group(1)
                if has_word(raw):
                    rows.append({'file': fp, 'line': i, 'kind': 'menu',
                                 'raw': raw, 'line_src': line.strip()})

json.dump(rows, open('/tmp/ui_raw.json', 'w'), ensure_ascii=False, indent=1)

uniq = sorted(set(r['raw'] for r in rows))
with open('/tmp/ui_raw_uniq.txt', 'w') as fh:
    for u in uniq:
        fh.write(repr(u) + '\n')

print('candidate sites:', len(rows))
print('unique raw literals:', len(uniq))