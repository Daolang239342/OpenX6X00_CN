#!/usr/bin/env python3
"""提取官方 OpenX6X00 v0.3.13 的 zh_CN.po 里未翻译条目，并分成：
  1) 需要翻译（自然语言文本）
  2) 无需翻译（代号、文件名、字符集、格式串、路径）

输出到项目根目录：
  official_zh_CN_待翻译.tsv   序号 / 源文件 / 原文 / 译文(请填写)
  official_zh_CN_待翻译.txt   同上，便于直接阅读
  official_zh_CN_无需翻译.txt 仅作说明，供核对

用法：
  python3 tools_zh/export_official_po_todo.py /tmp/zh_CN_v0313.po
"""
import os, re, sys, csv

HERE = os.path.dirname(os.path.abspath(__file__))
PO = sys.argv[1] if len(sys.argv) > 1 else '/tmp/zh_CN_v0313.po'


def parse_po(path):
    text = open(path, encoding='utf-8').read()
    raw_blocks = re.split(r'\n[ \t]*\n', text)
    out = []
    for b in raw_blocks:
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
            rest = b[m.end():]
            for line in rest.split('\n'):
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


def is_untranslatable(s):
    t = s.strip()
    if not t:
        return True
    # 纯格式串（占位符+标点，无完整单词）
    core = re.sub(r'%[-+0-9.#]*[diouxXfFgGeEcsp]', '', t)
    if not re.search(r'[A-Za-z]{2,}', core):
        return True
    # 文件路径 / 文件名
    if re.fullmatch(r'[\w./%\-]+\.(sstvtxt|txt|json|ini|db|csv|png|otf|po|pot|adi|cod|wav|mp3)', t):
        return True
    if '/' in t and ' ' not in t:
        return True
    # 字符集 / 键盘布局（连续大写字母无空格）
    if re.fullmatch(r'[A-Z0-9]{16,}', t):
        return True
    # 纯 8.3 样式代号（VOLMET xxx / LDOC / NAVTEX 站码）
    if re.fullmatch(r'(VOLMET|NAVTEX|SITOR|DSC)(\s+[A-Z]{2,4})?', t):
        return True
    if re.fullmatch(r'[A-Z]{3,6}', t):
        return True
    # strftime 模板
    if '%' in t and re.search(r'%[YmdHMS]', t):
        return True
    # 含 #RRGGBB 颜色码但无自然语言（只留纯色块）
    if re.fullmatch(r'#[0-9a-fA-F]{6}(\s+#)?', t):
        return True
    return False


def main():
    entries = parse_po(PO)
    total = len(entries)
    untranslated = [(r, m, f) for (r, m, s, f) in entries if not s.strip()]
    todo, skip = [], []
    for r, m, f in untranslated:
        (skip if is_untranslatable(unescape(m)) else todo).append((r, m, f))

    print(f'总条目            : {total}')
    print(f'未翻译            : {len(untranslated)}')
    print(f'  其中需要翻译    : {len(todo)}')
    print(f'  其中无需翻译    : {len(skip)}')
    done = total - len(untranslated)
    print(f'已翻译            : {done} ({100.0*done/total:.1f}%)')
    print(f'补全后可达        : {100.0*(done+len(todo))/total:.1f}%')

    tsv = os.path.join(HERE, '..', 'official_zh_CN_待翻译.tsv')
    txt = os.path.join(HERE, '..', 'official_zh_CN_待翻译.txt')
    stxt = os.path.join(HERE, '..', 'official_zh_CN_无需翻译.txt')

    with open(tsv, 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(['序号', '源文件', '原文', '译文(请填写)'])
        for i, (refs, mid, f) in enumerate(todo, 1):
            w.writerow([i, refs[0] if refs else '', unescape(mid), ''])

    with open(txt, 'w', encoding='utf-8') as fh:
        fh.write('OpenX6X00 v0.3.13 官方 po/zh_CN.po —— 待翻译条目\n')
        fh.write(f'总 {total} 条，未翻译 {len(untranslated)} 条；'
                 f'其中需要翻译 {len(todo)} 条，无需翻译 {len(skip)} 条。\n')
        fh.write(f'已翻译 {done} 条（{100.0*done/total:.1f}%），'
                 f'补全后可达 {100.0*(done+len(todo))/total:.1f}%。\n\n')
        fh.write('翻译规则：\n')
        fh.write('  1. %d %s %i %.1f 等占位符必须原样保留，顺序不变；\n')
        fh.write('  2. \\n 表示换行，按钮通常是两行、每行约 10 个字符；\n')
        fh.write('  3. #RRGGBB 颜色码保留在原位，只译 # 之外的文字；\n')
        fh.write('  4. 模式/按键/服务名不译：USB LSB CW AM FM FT8 FT4 JS8 WSPR PSK RTTY\n')
        fh.write('     SSTV WeFax NavTex Olivia Contestia JTTY MFK VOL APP PTT Winlink\n')
        fh.write('     Pat POTA SOTA WWBOTA HOTA WWFF TOTA WCA MOTA LH LLOTA Wavelog\n')
        fh.write('     ARDOP XARA Mercury VARA Tailscale QRZ APRS NTP GPS WiFi Bluetooth\n')
        fh.write('     AGC ATT ATU PRE VOX SWR ALC PWR SNR VFO QSO CQ ADIF DX QTH\n')
        fh.write('  5. 缩写词条目标题（如 UI 菜单缩写）按原样保留字母，只译其描述文字。\n')
        fh.write('=' * 78 + '\n\n')
        for i, (refs, mid, f) in enumerate(todo, 1):
            fh.write(f'[{i}] {", ".join(refs) if refs else "(无位置)"}\n')
            if f:
                fh.write(f'    flags: {", ".join(f)}\n')
            for line in unescape(mid).split('\n'):
                fh.write(f'    原文: {line}\n')
            fh.write('    译文: \n\n')

    with open(stxt, 'w', encoding='utf-8') as fh:
        fh.write('以下条目官方也未翻译，但它们不属于自然语言文本，'
                 '通常不需要翻译（航线/站码/文件名/字符集/时间格式）。\n')
        fh.write('如果你认为其中某条仍应翻译，告诉我序号，我会加回待翻译清单。\n')
        fh.write('=' * 78 + '\n\n')
        for i, (refs, mid, f) in enumerate(skip, 1):
            fh.write(f'[S{i}] {refs[0] if refs else ""} | {unescape(mid)!r}\n')

    print('已写出：')
    for p in (tsv, txt, stxt):
        print(' ', os.path.abspath(p))


if __name__ == '__main__':
    main()