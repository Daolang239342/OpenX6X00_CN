#!/usr/bin/env python3
"""合并用户补全的译文 + 页签/时区规范译文，输出 dict_zh/dict_user.py。

- 用户译文来自 待翻译清单_已补全.tsv（第三列）
- 页签 KEY (NAME\nN:M)   ->  缩写映射 + “第N/M面”
- 时区 KEY (Continent/City (ABBR)) -> 中文城市名（保留时区缩写）
"""
import os, sys, csv, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dict_zh import load as load_existing

# 页签缩写映射（按你的指示：把可读名称保留专业缩写/模式，非模式名译中文）
TAB = {
    'APP': '应用', 'BANDS': '波段', 'CLUSTER': '集群', 'CW KBD': 'CW键盘',
    'CW': 'CW', 'CWT': 'CW训练', 'DFN': '定义', 'DSC': 'DSC', 'FAX': '传真',
    'JTTY': 'JTTY', 'KEY': '按键', 'MEM': '记忆', 'MFK': 'MFK',
    'MSG': '消息', 'NAVTEX': 'NAVTEX', 'OLV': 'OLVIA', 'PAGE': '页',
    'PROP': '传播', 'PSK': 'PSK', 'RADE': 'RADE', 'RTTY': 'RTTY',
    'SCAN': '扫描', 'SETTINGS': '设置', 'SSTV': 'SSTV', 'VOL': '音量',
    'WLK': '对讲', 'WSPR': 'WSPR',
}

TZ = {
    'Africa/Johannesburg': '约翰内斯堡',
    'America/Anchorage': '安克雷奇',
    'America/Buenos_Aires': '布宜诺斯艾利斯',
    'America/Chicago': '芝加哥',
    'America/Denver': '丹佛',
    'America/Los_Angeles': '洛杉矶',
    'America/New_York': '纽约',
    'America/Sao_Paulo': '圣保罗',
    'Asia/Kolkata': '加尔各答',
    'Asia/Seoul': '首尔',
    'Asia/Shanghai': '上海',
    'Asia/Singapore': '新加坡',
    'Asia/Tokyo': '东京',
    'Australia/Brisbane': '布里斯班',
    'Australia/Perth': '珀斯',
    'Australia/Sydney': '悉尼',
    'Europe/Athens': '雅典',
    'Europe/London': '伦敦',
    'Europe/Moscow': '莫斯科',
    'Europe/Rome': '罗马',
    'Pacific/Auckland': '奥克兰',
    'Pacific/Honolulu': '火奴鲁鲁',
}

def main():
    ts = os.path.join(HERE, '..', '待翻译清单_已补全.tsv')
    rows = list(csv.reader(open(ts, encoding='utf-8-sig'), delimiter='\t'))
    assert rows[0][0].strip().startswith('来源'), rows[0]
    merged = dict(load_existing())

    for src, key, val in rows[1:]:
        key = key.strip()
        val = (val or '').replace('\ufeff', '')
        if not val:
            continue
        merged[key] = val

    # 页签规范化（覆盖用户页签译文，统一为“第N/M面”）
    tab_pat = re.compile(r'^\(([A-Z][A-Z0-9 ]*?)(?:\\n| )(\d):(\d)\)$')
    for key, val in list(merged.items()):
        m = tab_pat.match(key)
        if not m:
            continue
        name = m.group(1).strip()
        n, total = m.group(2), m.group(3)
        zh = TAB.get(name, name)
        merged[key] = f'（{zh}第{n}/{total}面）'

    # 时区规范化
    tz_pat = re.compile(r'^([A-Za-z_]+/[A-Za-z_]+) \(([A-Z+/]+)\)$')
    for key, val in list(merged.items()):
        m = tz_pat.match(key)
        if not m:
            continue
        city = TZ.get(m.group(1), m.group(1).split('/')[-1].replace('_', ' '))
        merged[key] = f'{city}（{m.group(2)}）'

    out = os.path.join(HERE, 'dict_zh', 'dict_user.py')
    with open(out, 'w', encoding='utf-8') as fp:
        fp.write('# -*- coding: utf-8 -*-\n')
        fp.write('# 用户补全 + 页签/时区规范化译文（自动生成，勿手改）\n')
        fp.write('D = {\n')
        import json as _json
        for k in sorted(merged):
            fp.write(f'    {_json.dumps(k, ensure_ascii=False)}: {_json.dumps(merged[k], ensure_ascii=False)},\n')
        fp.write('}\n')
    print('写入:', out, '共', len(merged), '条')

if __name__ == '__main__':
    main()