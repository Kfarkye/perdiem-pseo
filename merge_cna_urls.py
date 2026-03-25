#!/usr/bin/env python3
import json
import glob
from pathlib import Path

v2_dir = Path('cna-pseo/database/v2')
v1_dir = Path('cna-pseo/database/json')

success_count = 0

for v2_file in v2_dir.glob('*.json'):
    try:
        with open(v2_file, 'r', encoding='utf-8') as f:
            v2_data = json.load(f)
            
        board_v2 = v2_data.get('shared_facts', {}).get('board', {})
        
        # We only care if v2 has these specific URLs
        verify_url = board_v2.get('verify_url')
        contact_url = board_v2.get('contact_url')
        website_url = board_v2.get('website')
        
        if not (verify_url or contact_url or website_url):
            continue

        state_slug = v2_file.stem.replace('-certified-nursing-assistant', '-cna')
        v1_file = v1_dir / f"{state_slug}.json"
        
        if not v1_file.exists():
            print(f"Skipping {state_slug}: v1 file not found.")
            continue
            
        with open(v1_file, 'r', encoding='utf-8') as f:
            v1_data = json.load(f)
            
        v1_board = v1_data.get('board', {})
        
        # Merge operation
        if verify_url:
            v1_board['verify_url'] = verify_url
        if contact_url:
            v1_board['contact_url'] = contact_url
            if contact_url.startswith('mailto:'):
                v1_board['email'] = contact_url.replace('mailto:', '')
        if website_url:
            v1_board['website'] = website_url
            
        v1_data['board'] = v1_board
        
        with open(v1_file, 'w', encoding='utf-8') as f:
            json.dump(v1_data, f, indent=2)
            
        print(f"Merged URLs for {v1_data.get('state_name', state_slug)}")
        success_count += 1
        
    except Exception as e:
        print(f"Error processing {v2_file.name}: {e}")

print(f"\nSuccessfully merged URLs for {success_count} states.")
