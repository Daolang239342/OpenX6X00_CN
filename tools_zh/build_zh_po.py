#!/usr/bin/env python3
"""把用户译稿合成官方 zh_CN.po，并应用审阅建议的修正。

用法：
  python3 tools_zh/build_zh_po.py official_zh_CN_已翻译.tsv /tmp/zh_CN_v0313.po
输出：
  zh_CN.po                    完整中文翻译文件（可覆盖官方 po/zh_CN.po）
  official_zh_CN_最终对照.tsv  修正后的对照表
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))

TSV = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'official_zh_CN_已翻译.tsv')
SRC_PO = sys.argv[2] if len(sys.argv) > 2 else '/tmp/zh_CN_v0313.po'

# msgid -> 新译文；None 表示还原成英文（msgstr 留空）
CORRECTIONS = {
    # 1. 必须修正
    ' (an app holds the mode)': ' （某个应用程序正在占用该模式）',
    'RX %s %s  Hound: %s': '接收 %s %s  Hound: %s',

    # 2. 死条目：还原英文（i18n 拦截不到）
    'X6100 GUI Play': None,
    'X6100 GUI Capture': None,
    'X6100 GUI Network voice': None,
    'X6100 GUI Local': None,
    'X6100 GUI Station': None,
    'X6100 GUI Zello': None,
    'X6100 GUI SVXConnect': None,
    'X6100 GUI Monitor': None,
    ' fault settings': None,
    'rx on': None,
    'rx off': None,
    ' funnel on': None,
    ' funnel off': None,
    'gpsd, let go': None,

    # 3.1 xOTA 地点：英/法变体统一
    'Ruin:': '废墟：',
    'Ruine:': '废墟：',
    'Vestige:': '遗迹：',
    'Memorial:': '纪念物：',
    'Memoire:': '纪念物：',
    'Abandonne:': '已废弃：',

    # 3.2 电键模式
    'Auto-L': '自动(左)',
    'Auto-R': '自动(右)',

    # 3.3 Tailscale 产品功能名保留英文
    'Funnel': None,

    # 4. 漏译补充（注意首尾空格）
    ' APP WeFax ': ' 应用 传真 ',
    ' APP NavTex ': ' 应用 NAVTEX ',
    ' APP Zello ': ' 应用 Zello ',
    ' APP SVXConnect ': ' 应用 SVXConnect ',
    'SmartCW (MIDI)': 'SmartCW（MIDI）',
}


def unescape(s):
    return (s.replace('\\n', '\n')
             .replace('\\t', '\t')
             .replace('\\"', '"')
             .replace('\\\\', '\\'))


def escape_po(s):
    out = []
    for ch in s:
        if ch == '\\':
            out.append('\\\\')
        elif ch == '"':
            out.append('\\"')
        elif ch == '\n':
            out.append('\\n')
        elif ch == '\t':
            out.append('\\t')
        else:
            out.append(ch)
    return ''.join(out)


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
    rows = list(csv.reader(open(TSV, encoding='utf-8-sig'), delimiter='\t'))

    mapping = {}
    for r in rows[1:]:
        if len(r) < 4:
            continue
        src, dst = r[2], r[3]
        if not dst.strip() or dst.strip() == src.strip():
            continue
        mapping[src] = dst

    for src, new in CORRECTIONS.items():
        if new is None:
            mapping.pop(src, None)
        else:
            mapping[src] = new

    text = open(SRC_PO, encoding='utf-8').read()
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    blocks = re.split(r'\n{2,}', text)

    out = []
    changed = 0
    for b in blocks:
        if 'msgid' not in b:
            out.append(b)
            continue
        mid = field(b, 'msgid')
        if mid is None:
            out.append(b)
            continue
        mid_u = unescape(mid)
        if mid_u == '' or mid_u not in mapping:
            out.append(b)
            continue

        dst = mapping[mid_u]
        quoted = '""' if dst.strip() == mid_u.strip() else '"' + escape_po(dst) + '"'

        # 找到 msgstr 起点，替换到下一个 msg 关键字或块尾
        i = b.find('\nmsgstr')
        if i < 0:
            newb = b + '\nmsgstr ' + quoted
        else:
            tail = b[i + len('\nmsgstr'):]
            m = re.search(r'\nmsg(?:id|ctxt)\b', tail)
            if m:
                newb = b[:i] + '\nmsgstr ' + quoted + tail[m.start():]
            else:
                newb = b[:i] + '\nmsgstr ' + quoted

        newb = re.sub(r'^#,.*fuzzy.*\n', '', newb, flags=re.M)
        out.append(newb)
        changed += 1

    result = '\n\n'.join(out)

    done = total = 0
    for blk in re.split(r'\n{2,}', result):
        if 'msgid' not in blk:
            continue
        mid = field(blk, 'msgid')
        if mid is None or mid == '':
            continue
        total += 1
        ms = field(blk, 'msgstr')
        if ms and ms.strip():
            done += 1

    dst_po = os.path.join(ROOT, 'zh_CN.po')
    open(dst_po, 'w', encoding='utf-8').write(result)

    dst_tsv = os.path.join(ROOT, 'official_zh_CN_最终对照.tsv')
    with open(dst_tsv, 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(['序号', '源文件', '原文', '译文'])
        for r in rows[1:]:
            if len(r) < 4:
                continue
            src = r[2]
            if src in CORRECTIONS:
                new = CORRECTIONS[src]
                final = '' if new is None else new
            else:
                final = r[3]
            w.writerow([r[0], r[1], src, final])

    print('应用条目 :', changed)
    print('总条目   :', total)
    print('已翻译   : %d (%.1f%%)' % (done, 100.0 * done / total))
    print('未翻译   :', total - done)
    print()
    print('输出：')
    print(' ', dst_po)
    print(' ', dst_tsv)


if __name__ == '__main__':
    main()