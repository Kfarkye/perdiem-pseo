import json

data = {
  "alabama-rrt.json": {
    "endorsement_fee": 100,
    "processing_time": "4 to 6 Weeks",
    "fingerprint_required": False,
    "jurisprudence_required": False,
    "processing_tier": "mid",
    "requires_psv": True,
    "board_fee_verified": True,
    "board_timeline_verified": False,
    "board_source_url": "https://www.asbrt.alabama.gov/"
  },
  "alaska-rrt.json": {
    "endorsement_fee": 0,
    "processing_time": "0 Weeks",
    "fingerprint_required": False,
    "jurisprudence_required": False,
    "processing_tier": "fast",
    "requires_psv": False,
    "board_fee_verified": True,
    "board_timeline_verified": True,
    "board_source_url": "https://www.commerce.alaska.gov/web/cbpl/ProfessionalLicensing.aspx"
  },
  "arizona-rrt.json": {
    "endorsement_fee": 220,
    "processing_time": "6 to 8 Weeks",
    "fingerprint_required": True,
    "jurisprudence_required": False,
    "processing_tier": "slow",
    "requires_psv": True,
    "board_fee_verified": True,
    "board_timeline_verified": True,
    "board_source_url": "https://respiratorycare.az.gov/"
  },
  "arkansas-rrt.json": {
    "endorsement_fee": 4,
    "processing_time": "4 to 6 Weeks",
    "fingerprint_required": True,
    "jurisprudence_required": False,
    "processing_tier": "mid",
    "requires_psv": True,
    "board_fee_verified": True,
    "board_timeline_verified": False,
    "board_source_url": "https://www.armedicalboard.org/"
  },
  "california-rrt.json": {
    "endorsement_fee": 300,
    "processing_time": "4 to 8 Weeks",
    "fingerprint_required": True,
    "jurisprudence_required": True,
    "processing_tier": "mid",
    "requires_psv": True,
    "board_fee_verified": True,
    "board_timeline_verified": False,
    "board_source_url": "https://www.rcb.ca.gov/"
  }
}

for filename, new_reciprocity_data in data.items():
    filepath = f"rrt-pseo/database/json/{filename}"
    with open(filepath, 'r') as f:
        state_data = json.load(f)
    
    state_data.setdefault('reciprocity', {}).update(new_reciprocity_data)
    
    with open(filepath, 'w') as f:
        json.dump(state_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
