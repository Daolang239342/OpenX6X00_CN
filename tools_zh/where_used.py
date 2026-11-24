#!/usr/bin/env python3
"""查每个 msgid 在 po 里登记的所有源位置。"""
import re
import sys

PO = sys.argv[1] if len(sys.argv) > 1 else '/tmp/zh_CN_v0313.po'
KEYS = ['BAND', 'FREQ', 'MODE', 'SUBMODE', 'GRIDSQUARE', 'COUNTRY',
        'COMMENT', 'OPERATOR', 'QSOs', 'BAND UP', 'BAND DOWN',
        'Auto-L', 'Auto-R', ' fault settings', 'Funnel', 'Tailscale']

text = open(PO, encoding='utf-8').read()
for k in KEYS:
    pat = '#: ([^\\n]*)\\n(?:#[^\\n]*\\n)*msgid "' + re.escape(k) + '"'
    refs = re.findall(pat, text)
    print('%-16s -> %s' % (k, refs))