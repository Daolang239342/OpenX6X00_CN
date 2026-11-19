"""Chinese translation dictionaries for OpenX6X00 UI strings.

Each module in this package defines a dict `D` mapping an original string
literal to its translation. `load()` merges them all.
"""
import os, importlib

def load():
    merged = {}
    here = os.path.dirname(__file__)
    for fn in sorted(os.listdir(here)):
        if fn.endswith('.py') and fn != '__init__.py':
            mod = importlib.import_module(f'dict_zh.{fn[:-3]}')
            d = getattr(mod, 'D')
            merged.update(d)
    return merged