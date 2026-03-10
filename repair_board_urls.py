#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REMAP = {
    'https://www.arptb.org/': 'https://arptb.org/',
    'https://www.pharmacyboard.arkansas.gov/': 'https://pharmacyboard.arkansas.gov/',
    'https://www.rld.state.nm.us/boards-and-commissions/individual-boards-and-commissions/pharmacy/': 'https://www.rld.nm.gov/boards-and-commissions/individual-boards-and-commissions/pharmacy/',
    'https://www.rld.state.nm.us/boards-and-commissions/individual-boards-and-commissions/nutrition-and-dietetics/': 'https://www.rld.nm.gov/boards-and-commissions/individual-boards-and-commissions/nutrition-and-dietetics/',
}

changed = 0
for path in ROOT.glob('*-pseo/database/json/*.json'):
    data = json.loads(path.read_text(encoding='utf-8'))
    dirty = False
    for key_path in [
        ('board', 'url'),
        ('reciprocity', 'board_url'),
        ('reciprocity', 'endorsement_url'),
    ]:
        node = data
        for key in key_path[:-1]:
            node = node.get(key, {})
        key = key_path[-1]
        value = node.get(key)
        if value in REMAP:
            node[key] = REMAP[value]
            dirty = True
    if data.get('board_source_url') in REMAP:
        data['board_source_url'] = REMAP[data['board_source_url']]
        dirty = True
    if dirty:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
        changed += 1
print(f'Repaired {changed} files')
