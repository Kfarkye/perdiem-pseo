import json
import glob
import os

files = glob.glob('cna-pseo/database/json/*.json')

for f in files:
    with open(f, 'r') as file:
        data = json.load(file)
    
    if 'selector' in data and 'variants' in data['selector']:
        new_variants = []
        for v in data['selector']['variants']:
            if v['key'] == 'becoming':
                v['key'] = 'new_applicant'
                v['label'] = 'New Applicant'
                new_variants.append(v)
            elif v['key'] == 'state_application':
                # Skip or repurpose? Let's just drop it entirely, we only want 3 tabs: new app, rec, renewal
                pass
            elif v['key'] == 'transfer':
                v['key'] = 'reciprocity'
                v['label'] = 'Reciprocity'
                new_variants.append(v)
        
        # Add Renewal
        new_variants.append({
            "key": "renewal",
            "label": "Renewal",
            "label_source": "manual",
            "description": "Renew your active license.",
            "evidence_considered": [],
            "rejected_alternatives": [],
            "selection_reason": "Standard phase"
        })
        data['selector']['variants'] = new_variants
        data['selector']['default_variant'] = 'new_applicant'
    
    if 'variants' in data:
        if 'becoming' in data['variants']:
            data['variants']['new_applicant'] = data['variants'].pop('becoming')
        if 'state_application' in data['variants']:
            del data['variants']['state_application']
        if 'transfer' in data['variants']:
            del data['variants']['transfer'] # this was never in the JSON actually
            
    with open(f, 'w') as file:
        json.dump(data, file, indent=2)

print(f"Updated {len(files)} files.")
