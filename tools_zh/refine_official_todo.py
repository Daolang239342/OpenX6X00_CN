#!/usr/bin/env python3
"""把官方未译条目精筛成「需要翻译」与「建议保留」两份清单。

判定原则：
  需要翻译 = 自然语言 UI 文本（单词/短语/句子），或 UI 列标题/按钮标签。
  建议保留 = 协议命令、格式串、字符集、文件路径、模式/服务/品牌名、
             呼号模板、日志格式、时区偏移、波段名等。
"""
import os, re, sys, csv

HERE = os.path.dirname(os.path.abspath(__file__))
PO = sys.argv[1] if len(sys.argv) > 1 else '/tmp/zh_CN_v0313.po'

# ── 明确需要翻译（按 msgid 精确匹配）──────────────────────────────
FORCE_TRANSLATE = {
    'Bunker:', 'Ruin:', 'Ruine:', 'Remains:', 'Vestige:', 'Memorial:', 'Memoire:',
    'Abandoned:', 'Abandonne:', 'QSOs', 'SUBMODE', 'GRIDSQUARE', 'COUNTRY',
    'COMMENT', 'OPERATOR', 'Auto-L', 'Auto-R', 'BAND UP', 'BAND DOWN',
    ' fault settings',
    'the radio is in %s, not USB-D%s', ' (an app holds the mode)',
    'gpsd, let go',
}

FORCE_TRANSLATE_PREFIX = (
    ' APP ',        # " APP WeFax" 等
    'WiFi',         # "WiFi: %s" / "WiFi %s: %s"
    'Tailscale',    # "Tailscale: %s"
    'Winlink',      # "Winlink: %s"
    'Error: Failed',
    "Connection '%s'",
    ' funnel ',
)

# ── 明确保留（协议/命令/品牌/模式）────────────────────────────────
KEEP_EXACT = {
    'Zello', 'SVXConnect', 'Olivia', 'Contestia', 'CONTESTI', 'HEARTBEAT',
    'HEARTBEAT SNR', 'HEARING', 'HEARING?', 'INFO?', 'STATUS?', 'GRID?',
    'CALL?', 'AGN CALL', 'EXCH?', 'STATE?', 'SECTION?', 'ZONE?', 'RPRT?',
    'QUERY MSGS', 'QUERY CALL', 'QUERY MSGS?', 'MSGS?', 'RETRIEVE',
    'RETRIEVE MSG', '@GHOSTNET', '@GSTFLASH', '@APRSIS', '@ALLCALL',
    'APRS >', 'Dr', 'Tailscale', 'Funnel', 'TAILSCALE', 'Northwood',
    'PSK REPORTER', 'SmartCW (MIDI)', 'LH ARLHS', '70cm', 'hPa',
    'Robot 8', 'Robot 8 BW', 'Robot 36', 'Robot 72',
    'Martin M1', 'Martin M2', 'Scottie S1', 'Scottie S2', 'Scottie DX',
    'SHANNON VOLMET', 'SAST-2', 'AWST-8', 'AEST-10',
    'WWVH 5000', 'WWVH 10000', 'WWVH 15000',
    'CQ CONTEST', 'CQ FIELD',
    'OpenX6X00 TCI', 'OpenX6X00 Winlink', 'OpenX6X00 by RF.Guru',
    'Zello>RF', ' RF>Zello', ' Zello>RF',
    'RPRT 0', 'RPRT -1', 'RPRT -11',
    'CQ CQ CQ de <MYCALL> <MYCALL> <MYCALL> pse k',
    'TEST DE %s %s %s',
}


def parse_po(path):
    text = open(path, encoding='utf-8').read()
    out = []
    for b in re.split(r'\n[ \t]*\n', text):
        if 'msgid' not in b:
            continue
        refs, flags = [], []
        for line in b.split('\n'):
            s = line.strip()
            if s.startswith('#:'):
                refs.append(s[2:].strip())
            elif s.startswith('#,'):
                flags.append(s[2:].strip())

        def collect(key):
            m = re.search(r'^' + key + r'\s+"((?:[^"\\]|\\.)*)"', b, re.M)
            if not m:
                return None
            parts = [m.group(1)]
            for line in b[m.end():].split('\n'):
                s = line.strip()
                if not s:
                    continue
                if re.match(r'^msg(id|str|ctxt)', s) or s.startswith('#'):
                    break
                if s.startswith('"') and s.endswith('"'):
                    parts.append(s[1:-1])
            return ''.join(parts)

        mid = collect('msgid')
        if mid is None or mid == '':
            continue
        mstr = collect('msgstr')
        out.append((refs, mid, mstr if mstr is not None else '', flags))
    return out


def unescape(s):
    return (s.replace('\\n', '\n').replace('\\t', '\t')
             .replace('\\"', '"').replace('\\\\', '\\'))


def noise(s):
    """结构性噪声：命令/格式/字符集/路径/正则。"""
    t = s.strip()
    if not t:
        return True
    if re.match(r'^(hwclock|x6100-|gpsd|update |qrz-upload|wwbota-spot| funnel |rx on|rx off|/dev/null)', t):
        return True
    if re.search(r'\s--(call|recover|freq-khz|ref|mode|id)\b', t):
        return True
    if t.startswith('(') and 'recover' in t:
        return True
    if t.startswith('(?:') or 'HTTP/1.0' in t or t.startswith('GET '):
        return True
    if re.match(r'^(# X6100|X6100 JS8|<adif_ver|time,vbat)', t):
        return True
    if re.match(r'^clk (slow|ntp|gps|ok|set) ', t):
        return True
    if t.startswith('239.255.') or ',gateway' in t:
        return True
    if re.match(r'^,?sam,wfm$', t):
        return True
    if t.startswith('@APRSIS') or t.startswith('WLNK-1') or t.startswith('EMAIL-2'):
        return True
    if re.match(r'^%s (QUERY|RETRIEVE)', t):
        return True
    if 'QUERY MSG' in t and '%s' in t:
        return True
    if re.search(r'[A-Za-z0-9]{20,}', t):
        return True
    if re.search(r'\.(sstvtxt|txt|otf)$', t):
        return True
    if '/' in t and ' ' not in t:
        return True
    if re.match(r'^#%06x ', t):
        return True
    return False


def classify(t):
    s = t.strip()
    if s in FORCE_TRANSLATE:
        return 'translate'
    if any(p in s for p in FORCE_TRANSLATE_PREFIX):
        return 'translate'
    if s in KEEP_EXACT:
        return 'keep'
    if noise(t):
        return 'keep'
    if len(re.findall(r'[A-Za-z]{2,}', s)) >= 2:
        return 'translate'
    return 'keep'


def main():
    entries = parse_po(PO)
    total = len(entries)
    untranslated = [(r, m, f) for (r, m, s, f) in entries if not s.strip()]

    todo, keep = [], []
    for refs, mid, flags in untranslated:
        t = unescape(mid)
        (todo if classify(t) == 'translate' else keep).append((refs, t, flags))

    done = total - len(untranslated)
    print(f'官方总条目     : {total}')
    print(f'官方已翻译     : {done} ({100.0*done/total:.1f}%)')
    print(f'未翻译         : {len(untranslated)}')
    print(f'  需要翻译     : {len(todo)}')
    print(f'  建议保留     : {len(keep)}')
    print(f'补全后可达     : {100.0*(done+len(todo))/total:.1f}%')

    tsv = os.path.join(HERE, '..', 'official_zh_CN_待翻译.tsv')
    txt = os.path.join(HERE, '..', 'official_zh_CN_待翻译.txt')
    ktxt = os.path.join(HERE, '..', 'official_zh_CN_建议保留.txt')

    with open(tsv, 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(['序号', '源文件', '原文', '译文(请填写)'])
        for i, (refs, t, f) in enumerate(todo, 1):
            w.writerow([i, refs[0] if refs else '', t, ''])

    with open(txt, 'w', encoding='utf-8') as fh:
        fh.write('OpenX6X00 v0.3.13 官方 zh_CN.po —— 需要翻译的条目\n')
        fh.write(f'官方 {total} 条，已译 {done} 条（{100.0*done/total:.1f}%），'
                 f'未译 {len(untranslated)} 条，其中需你补写 {len(todo)} 条。\n')
        fh.write(f'补全后官方中文可达 {100.0*(done+len(todo))/total:.1f}%。\n\n')
        fh.write('规则：\n')
        fh.write('  1. %d %s %i %.1f 等占位符原样保留，顺序不变；\n')
        fh.write('  2. \\n 是换行符（按钮常为两行）；\n')
        fh.write('  3. #RRGGBB 颜色码留在原位，只译 # 外的文字；\n')
        fh.write('  4. 模式/服务/品牌名保留：USB LSB CW AM FM FT8 JS8 Olivia Contestia\n')
        fh.write('     SSTV Martin Scottie Robot WeFax NavTex Zello SVXConnect Tailscale\n')
        fh.write('     Winlink Pat POTA SOTA HOTA WWFF Wavelog ARDOP XARA Mercury AGC ATT ATU\n')
        fh.write('     SWR ALC PWR SNR VFO QSO CQ ADIF QTH APRS GPS NTP WiFi Bluetooth MFK\n')
        fh.write('=' * 78 + '\n\n')
        for i, (refs, t, f) in enumerate(todo, 1):
            fh.write(f'[{i}] {", ".join(refs) if refs else "(无位置)"}\n')
            if f:
                fh.write(f'    flags: {", ".join(f)}\n')
            for line in t.split('\n'):
                fh.write(f'    原文: {line}\n')
            fh.write('    译文: \n\n')

    with open(ktxt, 'w', encoding='utf-8') as fh:
        fh.write('以下官方也未翻译，判断为协议/命令/品牌/模式名等，建议保持原样。\n')
        fh.write('如需翻译其中某个，请告诉我序号。\n')
        fh.write('=' * 78 + '\n\n')
        for i, (refs, t, f) in enumerate(keep, 1):
            one = t.replace('\n', '⏎')
            fh.write(f'[K{i}] {refs[0] if refs else ""} | {one!r}\n')

    print('\n已写出：')
    for p in (tsv, txt, ktxt):
        print(' ', os.path.abspath(p))


if __name__ == '__main__':
    main()