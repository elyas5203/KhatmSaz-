import json
from src.khatmsaz.i18n import _STRINGS
keys = [k for k in _STRINGS.keys() if k.startswith('help.')]
with open('help_strings.txt', 'w', encoding='utf-8') as f:
    for k in keys:
        f.write(f'{k}:\n{_STRINGS[k].get("fa", "N/A")}\n\n---\n\n')
