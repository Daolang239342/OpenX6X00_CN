#!/usr/bin/env python3
"""校验生成的中文 po 文件（不依赖 gettext 工具）。

检查：
  1. 每个块都有 msgid/msgstr
  2. 占位符（%d %s %.1f …）在 msgid/msgstr 中同序同量
  3. #RRGGBB 颜色码一致
  4. \\n 换行数一致
  5. 首尾空格一致（拼接安全）
"""
import re
import sys

PO = sys.argv[1] if len(sys.argv) > 1 else 'zh_CN.po'

CONV = re.compile(r'%[-+0-9.#]*[diouxXfFgGeEcsp%]')
COLOR = re.compile(r'#[0-9a-fA-F]{6}')


def unescape(s):
    return (s.replace('\\n', '\n').replace('\\t', '\t')
             .replace('\\"', '"').replace('\\\\', '\\'))


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
    text = open(PO, encoding='utf-8').read().replace('\r\n', '\n')
    blocks = re.split(r'\n{2,}', text)

    total = done = 0
    no_msgstr = []
    conv_bad = []
    color_bad = []
    nl_bad = []
    space_bad = []

    for b in blocks:
        if 'msgid' not in b:
            continue
        mid = field(b, 'msgid')
        if mid is None or mid == '':
            continue
        total += 1

        ms = field(b, 'msgstr')
        if ms is None:
            no_msgstr.append(mid)
            continue
        if not ms.strip():
            continue
        done += 1

        s, d = unescape(mid), unescape(ms)
        if CONV.findall(s) != CONV.findall(d):
            conv_bad.append((s, d, CONV.findall(s), CONV.findall(d)))
            continue
        if COLOR.findall(s) != COLOR.findall(d):
            color_bad.append((s, d))
            continue
        if s.count('\n') != d.count('\n'):
            nl_bad.append((s, d))
            continue
        if s.startswith(' ') != d.startswith(' ') or s.endswith(' ') != d.endswith(' '):
            space_bad.append((s, d))

    print('总条目       :', total)
    print('已翻译       : %d (%.1f%%)' % (done, 100.0 * done / total))
    print('未翻译       :', total - done)
    print()
    print('缺失 msgstr  :', len(no_msgstr))
    print('占位符不符   :', len(conv_bad))
    print('颜色码不符   :', len(color_bad))
    print('换行数不符   :', len(nl_bad))
    print('首尾空格不符 :', len(space_bad))
    print()

    for title, items in (('占位符', conv_bad), ('颜色码', color_bad),
                         ('换行', nl_bad), ('空格', space_bad)):
        if items:
            print('=== %s 问题（前 20）===' % title)
            for x in items[:20]:
                print(' 原文:', repr(x[0]))
                print(' 译文:', repr(x[1]))
                if len(x) > 2:
                    print(' 细节:', x[2], '->', x[3])
                print()

    if not (no_msgstr or conv_bad or color_bad or nl_bad or space_bad):
        print('✅ 全部检查通过')


if __name__ == '__main__':
    main()