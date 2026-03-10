#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERTICALS = {
    'aud-pseo': {
        'suffix': 'aud',
        'compact_name': 'ASLP-IC',
        'compact_status': 'active',
        'compact_url': 'https://aslpcompact.com/',
        'members': {
            'Alabama','Arkansas','Colorado','Delaware','Georgia','Idaho','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Mississippi','Missouri','Montana','Nebraska','New Hampshire','North Carolina','North Dakota','Ohio','Oklahoma','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming'
        },
    },
    'dietitian-pseo': {
        'suffix': 'dietitian',
        'compact_name': 'Dietitian Compact',
        'compact_status': 'enacted',
        'compact_url': 'https://dietitianscompact.org/',
        'members': {
            'Georgia','Iowa','Nebraska','New Hampshire','Ohio','Oklahoma','South Dakota','Tennessee','Utah','Washington','West Virginia','Wisconsin','Wyoming'
        },
        'no_license_states': {'California','Colorado','Virginia','Michigan','Arizona'},
    },
    'ot-pseo': {
        'suffix': 'ot',
        'compact_name': 'OT Compact',
        'compact_status': 'enacted',
        'compact_url': 'https://otcompact.org/',
        'members': {
            'Alabama','Arizona','Arkansas','Colorado','Delaware','Georgia','Idaho','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Minnesota','Mississippi','Missouri','Montana','Nebraska','New Hampshire','North Carolina','North Dakota','Ohio','Oklahoma','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming'
        },
    },
    'pharm-pseo': {
        'suffix': 'pharm',
        'compact_name': '',
        'compact_status': 'none',
        'compact_url': '',
        'members': set(),
    },
    'pharmacist-pseo': {
        'suffix': 'pharmacist',
        'compact_name': '',
        'compact_status': 'none',
        'compact_url': '',
        'members': set(),
    },
    'pt-pseo': {
        'suffix': 'pt',
        'compact_name': 'PT Compact',
        'compact_status': 'active',
        'compact_url': 'https://ptcompact.org/ptc-states/',
        'members': {
            'Alabama','Arizona','Arkansas','Colorado','Delaware','Florida','Georgia','Idaho','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming'
        },
    },
    'rrt-pseo': {
        'suffix': 'rrt',
        'compact_name': '',
        'compact_status': 'none',
        'compact_url': '',
        'members': set(),
    },
    'slp-pseo': {
        'suffix': 'slp',
        'compact_name': 'ASLP-IC',
        'compact_status': 'active',
        'compact_url': 'https://aslpcompact.com/',
        'members': {
            'Alabama','Arkansas','Colorado','Delaware','Georgia','Idaho','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Mississippi','Missouri','Montana','Nebraska','New Hampshire','North Carolina','North Dakota','Ohio','Oklahoma','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming'
        },
    },
}

TIER_FAST = re.compile(r'(same day|same-day|1 to 2 week|1-2 week|2 to 4 week|2-4 week|1 week|2 week)', re.I)
TIER_MID = re.compile(r'(4 to 6 week|4-6 week|5 to 7 week|5-7 week|6 week)', re.I)
JURIS = re.compile(r'jurisprudence', re.I)
FINGER = re.compile(r'fingerprint|background check', re.I)
TEMP = re.compile(r'temporary|provisional|interim', re.I)
FEE_RE = re.compile(r'\$\s*([\d,]+(?:\.\d+)?)')


def parse_fee(*values: object) -> int:
    for value in values:
        if not value:
            continue
        match = FEE_RE.search(str(value))
        if match:
            return int(float(match.group(1).replace(',', '')))
    return 0


def processing_tier(value: str) -> str:
    text = (value or '').strip()
    if TIER_FAST.search(text):
        return 'fast'
    if TIER_MID.search(text):
        return 'mid'
    return 'slow'


def truthy_temp(temp_license: object, provisional_text: str, reciprocity_text: str) -> bool:
    if isinstance(temp_license, dict):
        available = temp_license.get('available')
        if isinstance(available, bool):
            return available
        if isinstance(available, str):
            return available.strip().lower() in {'yes', 'true', 'available'}
    return bool(TEMP.search(' '.join([provisional_text or '', reciprocity_text or ''])))


def build_reciprocity(vertical: str, data: dict) -> dict:
    cfg = VERTICALS[vertical]
    state = data['state_name']
    board_url = data.get('board', {}).get('url') or data.get('board_source_url') or ''
    steps_blob = ' '.join((step.get('title', '') + ' ' + step.get('description', '')) for step in data.get('steps', []))
    docs_blob = ' '.join((doc.get('item', '') + ' ' + doc.get('detail', '')) for doc in data.get('documents', []))
    provisional_text = data.get('provisional_text', '') or ''
    reciprocity_text = data.get('reciprocity_text', '') or ''
    body_blob = ' '.join([steps_blob, docs_blob, provisional_text, reciprocity_text])
    member = state in cfg['members']
    compact_status = cfg['compact_status'] if member or cfg['compact_status'] == 'none' else 'none'
    license_required = state not in cfg.get('no_license_states', set())
    endorsement_fee = parse_fee(
        data.get('fees_endorsement', {}).get('total_estimated_cost'),
        data.get('quick_facts', {}).get('total_fee'),
        data.get('fees_endorsement', {}).get('app_fee'),
    )
    proc_time = data.get('quick_facts', {}).get('processing_time', 'Varies')
    reciprocity = {
        'compact_name': cfg['compact_name'],
        'compact_status': compact_status,
        'state_is_member': member,
        'compact_url': cfg['compact_url'],
        'compact_portal_url': cfg['compact_url'],
        'license_required': license_required,
        'fingerprint_required': bool(data.get('fingerprints', {}).get('required')) or bool(FINGER.search(body_blob)),
        'temp_license_available': truthy_temp(data.get('temp_license'), provisional_text, reciprocity_text),
        'jurisprudence_required': bool(JURIS.search(body_blob)),
        'endorsement_fee': endorsement_fee,
        'processing_time': proc_time,
        'processing_tier': processing_tier(proc_time),
        'board_url': board_url,
        'endorsement_url': board_url,
        'notes': reciprocity_text.strip(),
    }
    return reciprocity


def update_faqs(data: dict) -> list[dict]:
    faqs = list(data.get('faqs') or [])
    questions = {faq.get('question') for faq in faqs if isinstance(faq, dict)}
    state = data['state_name']
    profession = data['profession_name']
    rec = data['reciprocity']
    if rec['compact_status'] == 'active' and rec['state_is_member']:
        reciprocity_answer = f"Yes. {state} participates in the {rec['compact_name']}. If your home state and license qualify for compact privilege, you can typically practice in {state} without a separate endorsement application."
    elif rec['compact_status'] == 'enacted' and rec['state_is_member']:
        reciprocity_answer = f"{state} has enacted the {rec['compact_name']}, but compact privileges are not yet issuing. For now, {profession.lower()}s still apply by endorsement through the state board."
    else:
        reciprocity_answer = f"No interstate compact currently covers {profession.lower()} practice in {state}. To work in {state}, apply for licensure by endorsement through the state board."
    q1 = f"Does {state} have reciprocity for {profession.lower()}s?"
    q2 = f"How long does it take to transfer my {profession.lower()} license to {state}?"
    q3 = f"Can I start working in {state} while my endorsement application is processing?"
    additions = [
        {'question': q1, 'answer': reciprocity_answer},
        {'question': q2, 'answer': f"Most endorsement applications take {rec['processing_time']}. If you qualify for an active compact privilege, there may be no separate wait to start practicing."},
        {'question': q3, 'answer': 'A temporary or provisional credential is available while the full endorsement application is pending.' if rec['temp_license_available'] else 'Most applicants need to wait for full approval before starting work because the state does not clearly offer a temporary or provisional credential.'},
    ]
    for item in additions:
        if item['question'] not in questions:
            faqs.append(item)
    return faqs


def update_seo(data: dict, suffix: str) -> None:
    state = data['state_name']
    profession = data['profession_name']
    rec = data['reciprocity']
    year = '2026'
    title = f"{state} {profession} License Reciprocity - How to Transfer Your License ({year})"
    desc = f"Already licensed as a {profession.lower()}? Here's whether your license transfers to {state} - compact status, endorsement steps, fees, and processing time."
    keywords = [
        f"{profession.lower()} license reciprocity {state.lower()}",
        f"how to transfer {profession.lower()} license to {state.lower()}",
        f"{profession.lower()} compact {state.lower()}",
        f"{state.lower()} {profession.lower()} endorsement application",
    ]
    data.setdefault('seo', {})
    data['seo']['title'] = title
    data['seo']['description'] = desc
    data['seo']['keywords'] = ', '.join(keywords)
    data['slug'] = f"{data['state_slug']}-{suffix}"
    data['specialty'] = suffix


def main() -> int:
    changed = 0
    for vertical, cfg in VERTICALS.items():
        json_dir = ROOT / vertical / 'database' / 'json'
        for path in sorted(json_dir.glob('*.json')):
            data = json.loads(path.read_text(encoding='utf-8'))
            data['reciprocity'] = build_reciprocity(vertical, data)
            data['faqs'] = update_faqs(data)
            update_seo(data, cfg['suffix'])
            compact = data.setdefault('compact', {})
            compact['is_compact_member'] = data['reciprocity']['state_is_member']
            compact['compact_name'] = data['reciprocity']['compact_name'] or 'N/A'
            compact['compact_source_url'] = data['reciprocity']['compact_url']
            path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
            changed += 1
    profiles_path = ROOT / 'vertical_profiles.json'
    profiles = json.loads(profiles_path.read_text(encoding='utf-8'))
    for vertical, cfg in VERTICALS.items():
        key = cfg['suffix']
        profile = profiles['verticals'].get(key)
        if not profile:
            continue
        profile.setdefault('regulatory', {})
        profile['regulatory']['compact_name'] = cfg['compact_name'] or 'None'
        profile['regulatory']['compact_source_url'] = cfg['compact_url']
        profile['regulatory']['compact_status'] = cfg['compact_status']
    profiles_path.write_text(json.dumps(profiles, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print(f'Updated {changed} state JSON files and vertical_profiles.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
