#!/usr/bin/env python3
"""Extract UI-translatable string literal occurrences with exact byte offsets.

Writes /tmp/zh_candidates.json and a local copy tools_zh/candidates.json.
Each record: {file, line, kind, raw, start, end}
  - start/end are offsets of the *inside* of the quote within the whole file.
Only literals with >=2 ASCII letters are kept; the translation dict decides
what to keep in English.

Kinds:
  call  - line contains a recognised UI setter call
  btn   - button_data_t .label = "..."
  menu  - popup menu item { "Label", "value" } (first string only)
  arr   - inside a 'static/const char *NAME[] = { ... };' block
"""
import re, os, json, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else 'src'
# 文件路径相对“仓库根”保存（默认 SRC=src → 前缀 src/；显式传 /x/v2/src → 前缀 src/）
REPO = os.path.dirname(os.path.abspath(SRC)) if os.path.basename(os.path.abspath(SRC)) == 'src' else os.path.abspath(SRC)

CALL = re.compile(
    r'(lv_label_set_text(?:_fmt)?|lv_btnmatrix_set_map|lv_dropdown_set_options|'
    r'lv_table_set_cell_value|msg_update_text(?:_fmt)?|msg_set_text(?:_fmt)?|'
    r'text_popup_show|dialog_title|title_set|row_label|wl_row_label|'
    r'lv_btn_set_text|btn_set_text|make_row|menu_add|list_add|add_item|'
    r'\bpara\b|\bsummary\b|\bbutton\b|\btext\b|\brow\b|\bstatus_line\b|'
    r'\bmsg_schedule_long_text_fmt\b|\bset_summary\b)\s*\('
)
BTN = re.compile(r'\.label\s*=\s*"((?:[^"\\]|\\.)*)"')
MENU = re.compile(r'\{\s*"((?:[^"\\]|\\.)*)"\s*,\s*"[^"]*"')
STR = re.compile(r'"((?:[^"\\]|\\.)*)"')

ARR_START = re.compile(
    r'(?:static\s+)?(?:const\s+)?char\s*\*\s*(\w+)\s*\[\s*\]\s*=\s*\{'
)

def has_word(s):
    return sum(c.isalpha() for c in s) >= 2

files = []
for root, ds, fs in os.walk(SRC):
    for f in fs:
        if f.endswith(('.c', '.cpp', '.inc')):
            files.append(os.path.join(root, f))
files.sort()

rows = []
seen_spans = set()

def add(fp, line, kind, raw, start, end, arr=None):
    key = (fp, start, end)
    if key in seen_spans:
        return
    seen_spans.add(key)
    rec = {'file': fp, 'line': line, 'kind': kind, 'raw': raw,
           'start': start, 'end': end}
    if arr is not None:
        rec['arr'] = arr
    rows.append(rec)

for fp_abs in files:
    fp = os.path.relpath(fp_abs, REPO)
    text = open(fp_abs, encoding='utf-8', errors='replace').read()
    lines = text.split('\n')
    # precompute line start offsets
    line_offs = [0]
    for ln in lines:
        line_offs.append(line_offs[-1] + len(ln) + 1)

    # array block spans (start,end) in text of the { ... } body
    arr_blocks = []
    for m in ARR_START.finditer(text):
        name = m.group(1)
        j = m.end()
        depth = 0
        n = len(text)
        while j < n:
            c = text[j]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    arr_blocks.append((name, m.end(), j))
                    break
            j += 1

    # per line, build line text and line start
    for i, line in enumerate(lines, 1):
        lstart = line_offs[i - 1]
        # array literals: any STR whose start lies within an arr block
        for m in STR.finditer(line):
            gstart = lstart + m.start(1)
            gend = lstart + m.end(1)
            inside_arr = None
            for aname, ab, ae in arr_blocks:
                if ab <= gstart and gend <= ae:
                    inside_arr = aname
                    break
            if inside_arr is not None:
                raw = m.group(1)
                if has_word(raw):
                    add(fp, i, 'arr', raw, gstart, gend, inside_arr)

        if CALL.search(line):
            for m in STR.finditer(line):
                raw = m.group(1)
                if has_word(raw):
                    add(fp, i, 'call', raw, lstart + m.start(1), lstart + m.end(1))
        m = BTN.search(line)
        if m:
            raw = m.group(1)
            if has_word(raw):
                add(fp, i, 'btn', raw, lstart + m.start(1), lstart + m.end(1))
        for m in MENU.finditer(line):
            raw = m.group(1)
            if has_word(raw):
                add(fp, i, 'menu', raw, lstart + m.start(1), lstart + m.end(1))

# write local + tmp copies
json.dump(rows, open('/tmp/zh_candidates.json', 'w'), ensure_ascii=False, indent=1)
out_local = os.path.join(os.path.dirname(__file__), 'candidates.json')
json.dump(rows, open(out_local, 'w'), ensure_ascii=False, indent=1)

uniq_raw = sorted(set(r['raw'] for r in rows))
uniq_out = os.path.join(os.path.dirname(__file__), 'candidates_uniq.txt')
with open(uniq_out, 'w') as fh:
    for u in uniq_raw:
        fh.write(repr(u) + '\n')

from collections import defaultdict
byfile = defaultdict(int)
for r in rows:
    byfile[r['file']] += 1
print('candidate sites:', len(rows))
print('unique raw literals:', len(uniq_raw))
for f in sorted(byfile, key=lambda x: -byfile[x]):
    print(f"{byfile[f]:4d}  {f}")