#!/usr/bin/env python3
"""恢复中文字体的编译与 fallback 挂载。

v2 从干净上游重建时丢失了 v1 手动加入的两处接线：
  1. src/fonts/font_select.c  —— 声明 zh_N 并挂到 fallback 链
  2. src/fonts/CMakeLists.txt —— 把 zh_*.c 加入编译源
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.abspath(os.path.join(HERE, '..', 'source', 'src', 'fonts'))

def patch_font_select():
    p = os.path.join(FONTDIR, 'font_select.c')
    s = open(p, encoding='utf-8').read()

    # 1) 声明 zh_N
    old = ("#define DECL(n) extern lv_font_t sony_##n; extern const lv_font_t roboto_##n, dejavu_##n, arial_##n, rcond_##n, codec_##n;\n"
           "SIZES(DECL)")
    new = ("#define DECL(n) extern lv_font_t sony_##n; extern const lv_font_t roboto_##n, dejavu_##n, arial_##n, rcond_##n, codec_##n, zh_##n;\n"
           "SIZES(DECL)")
    assert old in s, 'DECL block not found'
    s = s.replace(old, new, 1)

    # 2) zh 数组宏 + 数组定义（放在 codec 数组前）
    old = "#define CODEC(n) &codec_##n,\n"
    new = "#define CODEC(n) &codec_##n,\n#define ZH(n) &zh_##n,\n"
    assert old in s, 'CODEC macro not found'
    s = s.replace(old, new, 1)

    old = "static const lv_font_t *const codec[] = { SIZES(CODEC) };"
    new = ("static const lv_font_t *const zh[] = { SIZES(ZH) };\n"
           "static const lv_font_t *const codec[] = { SIZES(CODEC) };")
    assert old in s, 'codec array not found'
    s = s.replace(old, new, 1)

    # 3) fonts_apply：默认主题走 zh fallback
    old = """    for (unsigned i = 0; i < N_FONTS; i++) {
        if (!saved) orig[i] = *sony[i];
        *sony[i] = orig[i];
    }
    saved = true;
    buttons_h = 54;
    if (choice != FONT_ROBOTO && choice != FONT_DEJAVU && choice != FONT_ARIAL && choice != FONT_RCOND &&
        choice != FONT_PIXEL && choice != FONT_CODEC)
        return;
"""
    new = """    for (unsigned i = 0; i < N_FONTS; i++) {
        if (!saved) orig[i] = *sony[i];
        *sony[i]   = orig[i];
        orig[i].fallback = zh[i];
    }
    saved = true;
    buttons_h = 54;
    if (choice != FONT_ROBOTO && choice != FONT_DEJAVU && choice != FONT_ARIAL && choice != FONT_RCOND &&
        choice != FONT_PIXEL && choice != FONT_CODEC) {
        for (unsigned i = 0; i < N_FONTS; i++)
            sony[i]->fallback = zh[i];
        return;
    }
"""
    assert old in s, 'fonts_apply block not found'
    s = s.replace(old, new, 1)

    # 4) alt 主题仍经 orig->zh 链（orig.fallback 已在上面设好）
    # 无需额外改动：alt 会 fallback 到 orig，orig 再 fallback 到 zh。

    open(p, 'w', encoding='utf-8').write(s)
    print('patched', p)

def patch_cmake():
    p = os.path.join(FONTDIR, 'CMakeLists.txt')
    s = open(p, encoding='utf-8').read()
    old = """    matrix_20.c                                                         # the screensaver's rain (Noto Sans CJK JP, OFL-1.1)
    font_select.c
)"""
    new = """    matrix_20.c                                                         # the screensaver's rain (Noto Sans CJK JP, OFL-1.1)
    zh_14.c zh_16.c zh_18.c zh_20.c zh_22.c zh_24.c zh_26.c              # Chinese UI fallback (Noto Sans CJK SC, OFL-1.1)
    zh_28.c zh_30.c zh_32.c zh_34.c zh_36.c
    zh_38.c zh_40.c zh_42.c zh_44.c
    zh_60.c
    font_select.c
)"""
    assert old in s, 'CMakeLists matrix block not found'
    s = s.replace(old, new, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('patched', p)

if __name__ == '__main__':
    patch_font_select()
    patch_cmake()