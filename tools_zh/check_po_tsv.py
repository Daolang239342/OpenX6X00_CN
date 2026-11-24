#!/usr/bin/env python3
"""校验译稿 TSV：占位符 / 颜色码 / 换行数 / 空译文。

用法：python3 tools_zh/check_po_tsv.py official_zh_CN_已翻译.tsv
"""
import csv
import re
import sys

TSV = sys.argv[1] if len(sys.argv) > 1 else 'official_zh_CN_已翻译.tsv'

CONV = re.compile(r'%[-+0-9.#]*[diouxXfFgGeEcsp%]')
COLOR = re.compile(r'#[0-9a-fA-F]{6}')


def main():
    rows = list(csv.reader(open(TSV, encoding='utf-8-sig'), delimiter='\t'))
    head, data = rows[0], [r for r in rows[1:] if len(r) >= 4]

    changed = [r for r in data if r[3].strip() and r[3].strip() != r[2].strip()]
    same = [r for r in data if not r[3].strip() or r[3].strip() == r[2].strip()]

    print('总条目      :', len(data))
    print('已翻译      :', len(changed))
    print('保持原文/空 :', len(same))

    problems = []
    for r in changed:
        idx, src, dst = r[0], r[2], r[3]
        a, b = CONV.findall(src), CONV.findall(dst)
        if a != b:
            problems.append(('占位符不符', idx, src, dst, str(a) + ' -> ' + str(b)))
            continue
        a, b = COLOR.findall(src), COLOR.findall(dst)
        if a != b:
            problems.append(('颜色码不符', idx, src, dst, str(a) + ' -> ' + str(b)))
            continue
        if src.count('\n') != dst.count('\n'):
            problems.append(('换行数不符', idx, src, dst,
                             str(src.count('\n')) + ' -> ' + str(dst.count('\n'))))
            continue
        # 译文里残留未译英文单词（>10 字母且非术语）——只做提示
    print()
    if problems:
        print('=== 必须修正', len(problems), '条 ===')
        for p in problems:
            print('[%s] %s' % (p[0], p[1]))
            print('   原文:', repr(p[2]))
            print('   译文:', repr(p[3]))
            print('   问题:', p[4])
    else:
        print('格式检查：全部通过（占位符 / 颜色码 / 换行数一致）')

    print()
    print('=== 已翻译条目一览 ===')
    for r in changed:
        print('[%s] %s  =>  %s' % (r[0], r[2].replace('\n', ' / '), r[3].replace('\n', ' / ')))


if __name__ == '__main__':
    main()