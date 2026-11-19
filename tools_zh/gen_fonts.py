#!/usr/bin/env python3
"""Generate the CJK fallback LVGL fonts (zh_<size>.c) from the translation dict.

Steps:
  1. Collect every non-ASCII character used by the Chinese translation dict.
  2. pyftsubset NotoSansSC-Regular.otf to a minimal OTF keeping ASCII controls
     plus that CJK character set.
  3. Run lv_font_conv for each size used by src/fonts (SIZES) using --symbols.

Requires: fonttools (tools_zh/.venv) and `lv_font_conv` (npx).
"""
import os, subprocess, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_FONT = os.path.join(HERE, 'assets', 'NotoSansSC-Regular.otf')
SUBSET = os.path.join(HERE, 'assets', 'NotoSansSC-zh.otf')
SRC_DIR = os.path.abspath(os.path.join(HERE, '..', 'source'))
FONT_DIR = os.path.join(SRC_DIR, 'src', 'fonts')
PY = os.path.join(HERE, '.venv', 'bin', 'python')

SIZES = [14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 60]

def load_chars():
    chars = set()
    sys.path.insert(0, HERE)
    from dict_zh import load
    for v in load().values():
        for ch in v:
            if ord(ch) > 0x7F:
                chars.add(ch)
    # already-translated source literals (manual edits included)
    for root, ds, fs in os.walk(os.path.join(SRC_DIR, 'src')):
        ds[:] = [d for d in ds if d != 'fonts']
        for f in fs:
            if not f.endswith(('.c', '.cpp', '.inc')):
                continue
            text = open(os.path.join(root, f), encoding='utf-8', errors='ignore').read()
            for ch in text:
                if ord(ch) > 0x7F:
                    chars.add(ch)
    # always include layout punctuation and common symbols
    for ch in '，。：；、（）“”‘’…—《》·':
        chars.add(ch)
    return sorted(chars)

def main():
    chars = load_chars()
    print('unique CJK chars:', len(chars))
    unicodes = [f'U+{ord(c):04X}' for c in chars]
    unicodes.extend(['U+0020', 'U+0030-0039', 'U+0025', 'U+002E', 'U+002C',
                     'U+003A', 'U+003B', 'U+002D', 'U+002B', 'U+003D',
                     'U+0028', 'U+0029', 'U+005B', 'U+005D', 'U+003E',
                     'U+003C', 'U+002F', 'U+003F', 'U+0021', 'U+0023',
                     'U+0024', 'U+0040', 'U+00B0', 'U+00B1', 'U+00D7',
                     'U+00B7'])
    os.makedirs(os.path.dirname(SUBSET), exist_ok=True)

    if not os.path.exists(SRC_FONT):
        print('missing source font, downloading...')
        url = ('https://raw.githubusercontent.com/notofonts/noto-cjk/main/'
               'Sans/SubsetOTF/SC/NotoSansSC-Regular.otf')
        os.makedirs(os.path.dirname(SRC_FONT), exist_ok=True)
        subprocess.run(['curl', '-fsSL', '-o', SRC_FONT, url], check=True)

    # subset
    cmd = [PY, '-m', 'fontTools.subset', '--output-file=' + SUBSET]
    cmd += ['--unicodes=' + ','.join(unicodes)]
    cmd += ['--layout-features=']
    cmd += ['--glyph-names', '--symbol-cmap', '--legacy-cmap',
            '--notdef-glyph', '--notdef-outline']
    cmd += ['--recommended-glyphs', '--name-IDs=*', '--name-legacy', '--name-languages=*']
    cmd += [SRC_FONT]
    print('running pyftsubset...')
    subprocess.run(cmd, check=True)
    print('subset written:', SUBSET, os.path.getsize(SUBSET), 'bytes')

    symbols = ''.join(chars)
    ascii_extra = ' 0123456789%. ,:;-+=()[]></?!#$@'
    for s in ascii_extra:
        if s not in symbols:
            symbols += s

    # lv_font_conv
    for size in SIZES:
        out = os.path.join(FONT_DIR, f'zh_{size}.c')
        cmd = ['npx', '--yes', 'lv_font_conv',
               '--bpp', '4', '--size', str(size), '--font', SUBSET,
               '--symbols', symbols, '--no-compress',
               '--format', 'lvgl', '--force-fast-kern-format',
               '--lv-include', 'lvgl/lvgl.h', '-o', out]
        print('generating', out, '...')
        subprocess.run(cmd, check=True)
    print('done')

if __name__ == '__main__':
    main()