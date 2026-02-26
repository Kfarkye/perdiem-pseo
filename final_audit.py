#!/usr/bin/env python3
"""
Comprehensive Audit of all 408 JSON files across 8 YMYL verticals.
Ensures schema adherence, zero PENDING fields, and valid URL structures.
"""

import json
from pathlib import Path

SCRATCH = Path("/Users/k.far.88/.gemini/antigravity/scratch")

VERTICALS = [
    "dietitian-pseo", "slp-pseo", "ot-pseo", "pt-pseo",
    "rrt-pseo", "aud-pseo", "pharm-pseo", "pharmacist-pseo"
]

REQUIRED_KEYS = [
    "state_slug", "state_name", "profession_name", "last_updated",
    "board", "board_source_url", "quick_facts", "fees_endorsement",
    "compact", "temp_license", "fingerprints"
]

anomalies = []
total_files = 0
pending_count = 0

for vertical in VERTICALS:
    json_dir = SCRATCH / vertical / "database" / "json"
    if not json_dir.exists():
        anomalies.append(f"Missing vertical dir: {vertical}")
        continue

    for f in sorted(json_dir.glob("*.json")):
        total_files += 1
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            anomalies.append(f"JSON Parse Error in {f.name}: {e}")
            continue

        state_slug = data.get("state_slug", f.stem)

        # 1. PENDING Check
        raw = json.dumps(data)
        count = raw.count('"PENDING"')
        if count > 0:
            pending_count += count
            anomalies.append(f"[{vertical}] {state_slug} has {count} PENDING fields")

        # 2. Schema Structure Check
        for key in REQUIRED_KEYS:
            if key not in data:
                anomalies.append(f"[{vertical}] {state_slug} missing required root key '{key}'")

        # 3. Board Source URL Validator (must be real HTTP link or N/A)
        bsu = data.get("board_source_url", "")
        if bsu == "https://example.gov" or (not bsu.startswith("http") and bsu != "N/A"):
            anomalies.append(f"[{vertical}] {state_slug} has placeholder/invalid board_source_url: {bsu}")

        # 4. Fingerprint Structure Check
        fp = data.get("fingerprints", {})
        if not fp:
            anomalies.append(f"[{vertical}] {state_slug} fingerprints block is empty")
        elif fp.get("required") and fp.get("fee") == "N/A":
            anomalies.append(f"[{vertical}] {state_slug} fingerprints required but fee is N/A")

        # 5. Overrides Check (e.g. mpje leaked out of pharmacy?)
        if "mpje_required" in data:
             anomalies.append(f"[{vertical}] {state_slug} leaked root-level mpje_required (FAIL V2.1 RULES)")

print(f"=== COMPREHENSIVE AUDIT ===")
print(f"Files scanned: {total_files}")
print(f"Total PENDING strings found: {pending_count}")

if not anomalies:
    print(f"\n✅ SYSTEM HEALTHY: Zero anomalies detected across 408 files.")
else:
    print(f"\n⚠️ {len(anomalies)} Anomalies Detected:")
    for a in anomalies:
        print(f"  - {a}")
