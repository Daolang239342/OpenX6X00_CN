#!/usr/bin/env python3
"""列出关键 msgid 在源码中的所有出现处及上下文，判断是 UI 文本还是数据字段。"""
import re
import sys

SRC = 'source/src'
TARGETS = {
    'BAND': ['src/field/flog.c'],
    'FREQ': ['src/field/flog.c'],
    'MODE': ['src/field/flog.c', 'src/mic_keys.c'],
    'SUBMODE': ['src/field/flog.c'],
    'GRIDSQUARE': ['src/field/flog.c'],
    'COUNTRY': ['src/field/flog.c'],
    'COMMENT': ['src/field/flog.c'],
    'OPERATOR': ['src/field/flog.c'],
    'BAND UP': ['src/mic_keys.c'],
    'BAND DOWN': ['src/mic_keys.c'],
    'Auto-L': ['src/knob_info.cpp'],
    'Auto-R': ['src/knob_info.cpp'],
}

for key, files in TARGETS.items():
    print('=' * 70)
    print('MSGID:', repr(key))
    for rel in files:
        path = SRC + '/' + rel
        try:
            lines = open(path, encoding='utf-8', errors='ignore').read().split('\n')
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if '"' + key + '"' in line:
                lo = max(0, i - 4)
                hi = min(len(lines), i + 3)
                print('  %s:%d' % (rel, i))
                for j in range(lo, hi):
                    mark = '>>' if j == i - 1 else '  '
                    print('   %s %5d| %s' % (mark, j + 1, lines[j][:150]))
                print()