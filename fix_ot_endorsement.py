"""Inject real endorsement data for 16 non-compact OT states."""
import json
from pathlib import Path

OT_DIR = Path(__file__).resolve().parent / "ot-pseo" / "database" / "json"

# Research results from official state board sources [1-16]
CORRECTIONS = {
    "Alaska": {
        "endorsement_fee": 350,
        "processing_time": "4 to 6 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": True,
    },
    "California": {
        "endorsement_fee": 150,
        "processing_time": "6 to 8 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": True,
    },
    "Connecticut": {
        "endorsement_fee": 200,
        "processing_time": "4 to 6 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": True,
    },
    "District of Columbia": {
        "endorsement_fee": 314,
        "processing_time": "4 to 6 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": True,
    },
    "Florida": {
        "endorsement_fee": 180,
        "processing_time": "4 to 6 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": True,
        "requires_psv": False,
    },
    "Hawaii": {
        "endorsement_fee": 279,
        "processing_time": "4 to 6 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": True,
    },
    "Illinois": {
        "endorsement_fee": 25,
        "processing_time": "4 to 6 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": False,
    },
    "Massachusetts": {
        "endorsement_fee": 265,
        "processing_time": "4 to 6 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": True,
    },
    "Michigan": {
        "endorsement_fee": 187,
        "processing_time": "4 to 6 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": True,
    },
    "Nevada": {
        "endorsement_fee": 500,
        "processing_time": "3 to 5 Business Days",
        "fingerprint_required": True,
        "jurisprudence_required": True,
        "requires_psv": False,
    },
    "New Jersey": {
        "endorsement_fee": 260,
        "processing_time": "7 to 10 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": True,
    },
    "New Mexico": {
        "endorsement_fee": 110,
        "processing_time": "2 to 4 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": True,
        "requires_psv": True,
    },
    "New York": {
        "endorsement_fee": 294,
        "processing_time": "6 to 8 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": True,
    },
    "Oregon": {
        "endorsement_fee": 330,
        "processing_time": "1 to 2 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": True,
        "requires_psv": False,
    },
    "Pennsylvania": {
        "endorsement_fee": 30,
        "processing_time": "4 to 6 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": False,
    },
    "Rhode Island": {
        "endorsement_fee": 140,
        "processing_time": "4 to 6 Weeks",
        "fingerprint_required": True,
        "jurisprudence_required": False,
        "requires_psv": True,
    },
}

updated = 0
for json_file in sorted(OT_DIR.glob("*.json")):
    data = json.loads(json_file.read_text(encoding="utf-8"))
    state_name = data["state_name"]
    
    if state_name in CORRECTIONS:
        corr = CORRECTIONS[state_name]
        r = data["reciprocity"]
        
        for key, val in corr.items():
            old = r.get(key)
            r[key] = val
            if old != val:
                print(f"  {state_name}: {key}: {old} -> {val}")
        
        data["reciprocity"] = r
        json_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        updated += 1

print(f"\nUpdated {updated} state files.")
