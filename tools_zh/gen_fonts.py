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
SRC_DIR = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(os.path.join(HERE, '..', 'source'))
FONT_DIR = os.path.join(SRC_DIR, 'src', 'fonts')
PY = os.path.join(HERE, '.venv', 'bin', 'python')

# 文件仍叫 zh_<N>.c 表示“用于 sony_N”，但实际渲染字号按主字体行高缩小。
# 主字体 sony_N 的行高约 0.8*N，而 Noto CJK 的行高约 1.1*size，为不超出
# 主字体行高，中文字号取 int(sony_line_height / 1.1)。
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

    # lv_font_conv：文件名仍为 zh_<N>.c（用于 sony_N），但 --size 取该档
    # 主字体的行高换算值，避免中文行高超出按钮/行高导致顶部被裁切。
    for n in SIZES:
        sony = os.path.join(FONT_DIR, f'sony_{n}.c')
        lh = None
        if os.path.exists(sony):
            m = re.search(r'\.line_height\s*=\s*(\d+)', open(sony, encoding='utf-8', errors='ignore').read())
            if m:
                lh = int(m.group(1))
        if lh is None:
            lh = int(n * 0.8)
        actual = max(10, int(lh / 1.1))
        out = os.path.join(FONT_DIR, f'zh_{n}.c')
        cmd = ['npx', '--yes', 'lv_font_conv',
               '--bpp', '4', '--size', str(actual), '--font', SUBSET,
               '--symbols', symbols, '--no-compress',
               '--format', 'lvgl', '--force-fast-kern-format',
               '--lv-include', 'lvgl/lvgl.h', '-o', out]
        print(f'generating {out} (rendered size {actual} from sony_{n} LH {lh}) ...')
        subprocess.run(cmd, check=True)
    print('done')

if __name__ == '__main__':
    main()