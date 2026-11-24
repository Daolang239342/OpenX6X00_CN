#!/usr/bin/env python3
"""精筛官方 zh_CN.po 的未译条目，输出最终待译清单。

排除：VOLMET 区域代号、音频源显示名、协议标记、机构署名、
      命令行/重定向、字体列表、时间戳文件名。
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
PO = sys.argv[1] if len(sys.argv) > 1 else '/tmp/zh_CN_v0313.po'

# 不做主观过滤：全部列出，留空的条目在固件里继续显示英文，不会出错
EXCLUDE = []
EXCLUDE_RE = [re.compile(p) for p in EXCLUDE]


def unescape(s):
    return (s.replace('\\n', '\n')
             .replace('\\t', '\t')
             .replace('\\"', '"')
             .replace('\\\\', '\\'))


def field(block, key):
    m = re.search(r'^' + key + r' "((?:[^"\\]|\\.)*)"', block, re.M)
    if not m:
        return None
    parts = [m.group(1)]
    for line in block[m.end():].split('\n'):
        s = line.strip()
        if not s:
            continue
        if re.match(r'^msg(id|str|ctxt)', s) or s.startswith('#'):
            break
        if s.startswith('"') and s.endswith('"'):
            parts.append(s[1:-1])
    return ''.join(parts)


def main():
    text = open(PO, encoding='utf-8').read()
    blocks = re.split(r'\n[ \t]*\n', text)

    total = 0
    untranslated = 0
    rows = []

    for b in blocks:
        if 'msgid' not in b:
            continue
        mid = field(b, 'msgid')
        if mid is None or mid == '':
            continue
        total += 1
        mstr = field(b, 'msgstr')
        if mstr is None or mstr.strip():
            continue
        untranslated += 1
        t = unescape(mid)
        if any(r.search(t.strip()) for r in EXCLUDE_RE):
            continue
        refs = re.findall(r'^#: (.*)$', b, re.M)
        rows.append((refs[0] if refs else '', t))

    done = total - untranslated

    tsv = os.path.join(ROOT, 'official_zh_CN_待翻译.tsv')
    txt = os.path.join(ROOT, 'official_zh_CN_待翻译.txt')

    with open(tsv, 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(['序号', '源文件', '原文', '译文(请填写)'])
        for i, (ref, t) in enumerate(rows, 1):
            w.writerow([i, ref, t, ''])

    head = [
        'OpenX6X00 v0.3.13 官方 po/zh_CN.po —— 待补译条目',
        '官方共 {0} 条，已译 {1} 条（{2:.1f}%），未译 {3} 条，'
        '本清单需补 {4} 条。'.format(total, done, 100.0 * done / total,
                                     untranslated, len(rows)),
        '补全后中文可达 {0:.1f}%。'.format(100.0 * (done + len(rows)) / total),
        '',
        '翻译规则：',
        '  1. %d %s %i %.1f 等占位符原样保留，顺序不变；',
        '  2. \\n 表示换行，按钮通常两行；',
        '  3. #RRGGBB 颜色码留在原位，只译 # 外的文字；',
        '  4. 以下不译：USB LSB CW AM FM FT8 JS8 Olivia Contestia SSTV',
        '     Martin Scottie Robot WeFax NavTex Zello SVXConnect Tailscale',
        '     Winlink Pat POTA SOTA HOTA WWFF Wavelog ARDOP XARA Mercury',
        '     AGC ATT ATU SWR ALC PWR SNR VFO QSO CQ ADIF QTH APRS GPS',
        '     NTP WiFi Bluetooth MFK',
        '=' * 76,
        '',
    ]

    with open(txt, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(head) + '\n')
        for i, (ref, t) in enumerate(rows, 1):
            fh.write('[{0}] {1}\n'.format(i, ref))
            for ln in t.split('\n'):
                fh.write('    原文: {0}\n'.format(ln))
            fh.write('    译文: \n\n')

    print('total={0} untranslated={1} todo={2} done={3:.1f}%'.format(
        total, untranslated, len(rows), 100.0 * done / total))
    print(tsv)
    print(txt)


if __name__ == '__main__':
    main()