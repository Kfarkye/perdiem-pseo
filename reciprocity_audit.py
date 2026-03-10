#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = {
    'compact_name', 'compact_status', 'state_is_member', 'compact_url', 'license_required',
    'fingerprint_required', 'temp_license_available', 'jurisprudence_required', 'endorsement_fee',
    'processing_time', 'processing_tier', 'board_url'
}


def check_url(url: str) -> tuple[bool, str]:
    if not url.startswith('http'):
        return False, 'non-http'
    req = urllib.request.Request(url, method='GET', headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return 200 <= resp.status < 400, str(resp.status)
    except Exception as exc:
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-urls', action='store_true')
    args = parser.parse_args()
    total = 0
    errors = []
    urls = {}
    for path in ROOT.glob('*-pseo/database/json/*.json'):
        total += 1
        data = json.loads(path.read_text(encoding='utf-8'))
        rec = data.get('reciprocity')
        if not isinstance(rec, dict):
            errors.append(f'{path}: missing reciprocity object')
            continue
        missing = sorted(REQUIRED - rec.keys())
        if missing:
            errors.append(f"{path}: missing reciprocity fields {', '.join(missing)}")
        if not isinstance(rec.get('endorsement_fee'), int):
            errors.append(f'{path}: endorsement_fee must be int')
        if rec.get('processing_tier') not in {'fast', 'mid', 'slow'}:
            errors.append(f'{path}: invalid processing_tier')
        if not isinstance(rec.get('state_is_member'), bool):
            errors.append(f'{path}: state_is_member must be bool')
        if args.check_urls:
            urls[path] = rec.get('board_url', '')
    if args.check_urls:
        for path, url in urls.items():
            ok, info = check_url(url)
            if not ok:
                errors.append(f'{path}: board_url failed {info} -> {url}')
    if errors:
        print(f'FAIL {len(errors)} issues across {total} files')
        for item in errors[:200]:
            print(item)
        return 1
    print(f'PASS {total} files, 0 errors')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
