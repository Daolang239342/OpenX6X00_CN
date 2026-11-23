#!/usr/bin/env python3
"""生成翻译对照 TXT + 两个 TSV（Excel 可直接打开）。

输出：
  tools_zh/translation_report.txt   完整对照（已译 / 保留 / 无需译 / 待译）
  tools_zh/translated.tsv           已翻译：来源 | 原文 | 译文
  tools_zh/todo.tsv                 待翻译：来源 | 原文 | （请填译文）
"""
import os, sys, re, csv

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(HERE, '..', 'source'))
sys.path.insert(0, HERE)
from dict_zh import load

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
ARR_START = re.compile(r'(?:static\s+)?(?:const\s+)?char\s*\*\s*(\w+)\s*\[\s*\]\s*=\s*\{')

def has_word(s):
    return sum(c.isalpha() for c in s) >= 2

def c_candidates(src):
    files = []
    for root, ds, fs in os.walk(os.path.join(src, 'src')):
        for f in fs:
            if f.endswith(('.c', '.cpp', '.inc')):
                files.append(os.path.join(root, f))
    files.sort()
    uniq = {}
    for fp in files:
        text = open(fp, encoding='utf-8', errors='replace').read()
        lines = text.split('\n')
        offs = [0]
        for ln in lines:
            offs.append(offs[-1] + len(ln) + 1)
        blocks = []
        for m in ARR_START.finditer(text):
            j, d = m.end(), 0
            while j < len(text):
                if text[j] == '{': d += 1
                elif text[j] == '}':
                    d -= 1
                    if d == 0:
                        blocks.append((m.end(), j)); break
                j += 1
        for i, line in enumerate(lines, 1):
            lo = offs[i-1]
            for m in STR.finditer(line):
                gs, ge = lo + m.start(1), lo + m.end(1)
                inside = any(a <= gs and ge <= b for a, b in blocks)
                raw = m.group(1)
                if has_word(raw) and inside:
                    uniq.setdefault(raw, 'gui')
            if CALL.search(line):
                for m in STR.finditer(line):
                    raw = m.group(1)
                    if has_word(raw):
                        uniq.setdefault(raw, 'gui')
            m = BTN.search(line)
            if m and has_word(m.group(1)):
                uniq.setdefault(m.group(1), 'gui')
            for m in MENU.finditer(line):
                raw = m.group(1)
                if has_word(raw):
                    uniq.setdefault(raw, 'gui')
    return uniq

def web_candidates(src):
    views = os.path.join(src, 'webserver', 'src', 'x6100_webserver', 'views')
    TEXT = re.compile(r'>([^<>\n]*[A-Za-z][^<>\n]*)<')
    ATTR = re.compile(r'\b(?:value|placeholder|title|label|alt)\s*=\s*"([^"]*[A-Za-z][^"]*)"')
    uniq = {}
    for f in sorted(os.listdir(views)):
        if not f.endswith('.html'): continue
        text = open(os.path.join(views, f), encoding='utf-8').read()
        text = re.sub(r'<script\b[^>]*>.*?</script>', '', text, flags=re.S)
        text = re.sub(r'<style\b[^>]*>.*?</style>', '', text, flags=re.S)
        for m in TEXT.finditer(text):
            s = m.group(1).strip()
            s = re.sub(r'^\s*%.*$', '', s, flags=re.M).strip()
            if s and has_word(s):
                uniq.setdefault(s, 'web')
        for m in ATTR.finditer(text):
            s = m.group(1)
            if has_word(s):
                uniq.setdefault(s, 'web')
    return uniq

TERMS = {
    'SSB','USB','LSB','CW','AM','FM','FT8','FT4','FT2','WSPR','JS8','PSK31','PSK63','PSK',
    'RTTY','JTTY','Olivia','Contestia','SSTV','WeFax','NavTex','AGC','ATT','ATU','PRE','VOX',
    'SWR','ALC','PWR','SNR','VFO','MFK','PTT','QSO','CQ','ADIF','DX','NTP','GPS','WiFi',
    'Bluetooth','Tailscale','Funnel','QRZ','Wavelog','Winlink','ARDOP','Mercury','XARA','VARA',
    'QTH','Grid','APRS','DXFUN','USB-D','LSB-D','TUNE','TX','RX','POTA','SOTA','HOTA','CAT',
    'TCI','MIC','AF','RF','IF','WFM','SAM','NFM','DSP','LSB','USB','Dstar','D-STAR',
}

# JS8 / APRS / 命令行等协议内容：保留不译
PROTOCOL_TERMS = {
    'QUERY', 'QUERY CALL', 'QUERY MSGS', 'QUERY MSGS?', 'MSG TO:', 'MSG', 'CMD',
    'GRID', 'SNR?', 'SNR', 'HEARTBEAT SNR', 'HW CPY?', 'AGN?', 'MYINFO', 'CALL MSG',
    'INFO?', 'HEARING?', 'STATUS?', 'GRID?', 'ACK', 'RRR', '73', 'TU', 'CQ CQ',
    'TU NOW', 'TU CQ', 'Call 599', '599 Nr', '<MYINFO>', '@ALLCALL', 'APRS2SOTA', 'APSPOT',
}

def is_term(s):
    t = s.strip()
    if t in TERMS:
        return True
    if t in PROTOCOL_TERMS:
        return True
    # 4~6 个字母的纯大写缩略词保留不译
    if all(not c.islower() for c in t if c.isalpha()) and 4 <= len(t) <= 6:
        return True
    return False

def is_untranslatable(s):
    t = s.strip().rstrip('\\')
    if not t:
        return True
    # 纯格式化占位串（无自然语句）
    if re.search(r'%[-+0-9.#]*[diouxXfFgGeEcsp]', t) and ' ' not in t:
        return True
    # 命令行
    if t.startswith(('--', '%', '#')) or t.startswith(('wwbota-', 'x6100-', 'x6200-')):
        return True
    if re.search(r'\s--(call|ref|mode|freq|id)\b', t):
        return True
    # SQL / 数据库碎片
    if re.search(r'\b(CREATE|INSERT|SELECT|DELETE|UPDATE|TABLE|INDEX|ORDER BY|COLLATE|PRIMARY KEY|NOT NULL|UNIQUE|REFERENCES|INTEGER|REAL|BLOB|TEXT)\b', t, re.I):
        return True
    # 设置键名 xxx=...
    if re.fullmatch(r'[a-z_]+=.*', t):
        return True
    # 含 Tab 的程序化输出
    if '\t' in t:
        return True
    # 纯键盘布局 / 字符集
    if re.fullmatch(r'[A-Za-z0-9,;\.\'\[\]/\-]+', t):
        return True
    # 时区标识符（Continent/City (XXX)）—— 保留标准时区名
    if re.fullmatch(r'[A-Za-z]+/[A-Za-z_]+ \([A-Za-z/+]+\)', t):
        return True
    # 纯数字 + 单位（时间和频率）
    if re.fullmatch(r'[\d\s]+(min|s|Hz|km|W|dB|dBm|MHz|kHz|%)\b.*', t) and ' ' not in t.replace('\t', ' '):
        if re.fullmatch(r'[\d\s,.]+\s*(min|s|Hz|km|W|dB|dBm|MHz|kHz)', t):
            return True
    return False

def show(s):
    return s.replace('\n', '⏎').replace('\t', '→')

def main():
    d = load()
    allu = {}
    for k, v in c_candidates(SRC).items():
        allu.setdefault(k, v)
    for k, v in web_candidates(SRC).items():
        allu.setdefault(k, v)

    translated = []
    kept = []
    skipped = []
    todo = []
    for raw in sorted(allu, key=str.lower):
        kind = allu[raw]
        raw_ln = raw.replace('\r', '')
        if raw_ln in d:
            translated.append((kind, raw_ln, d[raw_ln]))
        elif is_term(raw_ln):
            kept.append((kind, raw_ln, raw_ln))
        elif is_untranslatable(raw_ln):
            skipped.append((kind, raw_ln, ''))
        else:
            todo.append((kind, raw_ln, ''))

    out = os.path.join(HERE, 'translation_report.txt')
    with open(out, 'w', encoding='utf-8') as fp:
        fp.write('OpenX6X00 中文化 翻译对照表\n')
        fp.write('注：换行⏎，制表符→\n')
        fp.write('=' * 62 + '\n')
        def block(title, items, tr):
            fp.write(f'\n【{title}】{len(items)} 条\n' + '-' * 62 + '\n')
            for kind, raw, trans in items:
                fp.write(f'{kind}\t{show(raw)}\t{show(trans)}\n' if tr else f'{kind}\t{show(raw)}\n')
        block('已翻译', translated, True)
        block('保留不译（模式/术语/协议命令）', kept, False)
        block('无需翻译（格式串/命令/SQL/键名/时区）', skipped, False)
        block('待翻译', todo, False)

    with open(os.path.join(HERE, 'translated.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['来源', '原文', '译文'])
        for kind, raw, trans in translated:
            w.writerow([kind, raw, trans])
    with open(os.path.join(HERE, 'todo.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['来源', '原文', '译文（请填写）'])
        for kind, raw, _ in todo:
            w.writerow([kind, raw, ''])

    print('报告:', out)
    print('已译', len(translated), '保留', len(kept), '跳过', len(skipped), '待译', len(todo))

if __name__ == '__main__':
    main()