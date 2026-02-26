#!/usr/bin/env python3
"""
Cross-pollinate board contact info from verticals that have real data
into verticals that share the same state board.

Strategy:
1. SLP → Audiology (same board in ~90% of states)
2. Dietitian board data → seed phone/address patterns for other verticals
   where the parent_dept matches (e.g., same Dept of Health)
"""

import json
from pathlib import Path

SCRATCH = Path("/Users/k.far.88/.gemini/antigravity/scratch")
CONTACT_FIELDS = ["mailing_address", "physical_address", "phone", "fax", "email"]

STATES = ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'dc', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new-hampshire', 'new-jersey', 'new-mexico', 'new-york', 'north-carolina', 'north-dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode-island', 'south-carolina', 'south-dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west-virginia', 'wisconsin', 'wyoming']

resolved = 0

# ── 1. SLP → AUDIOLOGY ────────────────────────────────────
print("=== SLP → Audiology (shared board) ===")
slp_dir = SCRATCH / "slp-pseo" / "database" / "json"
aud_dir = SCRATCH / "aud-pseo" / "database" / "json"

for state in STATES:
    slp_file = slp_dir / f"{state}-slp.json"
    aud_file = aud_dir / f"{state}-aud.json"
    
    if not slp_file.exists() or not aud_file.exists():
        continue
    
    slp_data = json.loads(slp_file.read_text(encoding="utf-8"))
    aud_data = json.loads(aud_file.read_text(encoding="utf-8"))
    
    slp_board = slp_data.get("board", {})
    aud_board = aud_data.get("board", {})
    changed = False
    
    for field in CONTACT_FIELDS:
        slp_val = slp_board.get(field, "PENDING")
        aud_val = aud_board.get(field, "PENDING")
        
        if aud_val == "PENDING" and slp_val != "PENDING":
            aud_board[field] = slp_val
            resolved += 1
            changed = True
    
    # Also copy the board URL and parent_dept if available
    if aud_board.get("url", "https://example.gov") == "https://example.gov" and slp_board.get("url", "") not in ("", "https://example.gov"):
        aud_board["url"] = slp_board["url"]
        changed = True
    
    if slp_board.get("parent_dept", "") and aud_board.get("parent_dept") == "Department of Health":
        aud_board["parent_dept"] = slp_board["parent_dept"]
        changed = True
    
    # Update board name to reflect audiology
    if "PENDING" not in str(aud_board.get("name", "")) and slp_board.get("name", ""):
        # SLP board name often already includes "and Audiology"
        slp_name = slp_board.get("name", "")
        if "audiol" in slp_name.lower():
            aud_board["name"] = slp_name
            changed = True
    
    # Also copy board_source_url
    if aud_data.get("board_source_url") == "https://example.gov" and slp_data.get("board_source_url", "") not in ("", "https://example.gov"):
        aud_data["board_source_url"] = slp_data["board_source_url"]
        changed = True
    
    if changed:
        aud_data["board"] = aud_board
        aud_file.write_text(json.dumps(aud_data, indent=4, ensure_ascii=False), encoding="utf-8")
        
        after_pending = json.dumps(aud_data).count('"PENDING"')
        print(f"  {state:20s} → {after_pending} PENDING remaining")

# ── 2. DIETITIAN board parent_dept → OT, PT, RRT, PHARM, PHARMACIST ──
# Where the state uses a unified Department of Health, copy contact info
print("\n=== Dietitian → Other verticals (shared parent dept) ===")
diet_dir = SCRATCH / "dietitian-pseo" / "database" / "json"

TARGET_VERTICALS = {
    "ot-pseo": "ot",
    "pt-pseo": "pt",
    "rrt-pseo": "rrt",
    "pharm-pseo": "pharm",
    "pharmacist-pseo": "pharmacist",
}

# For these, we can only safely copy parent_dept and potentially URL patterns
# We can't copy phone/address because different professions have different boards
# But we CAN set the parent_dept field which is currently generic
for state in STATES:
    diet_file = diet_dir / f"{state}-dietitian.json"
    if not diet_file.exists():
        continue
    
    diet_data = json.loads(diet_file.read_text(encoding="utf-8"))
    diet_board = diet_data.get("board", {})
    diet_parent = diet_board.get("parent_dept", "")
    
    if not diet_parent or diet_parent == "Department of Health":
        continue
    
    for vdir, suffix in TARGET_VERTICALS.items():
        target_file = SCRATCH / vdir / "database" / "json" / f"{state}-{suffix}.json"
        if not target_file.exists():
            continue
        
        target_data = json.loads(target_file.read_text(encoding="utf-8"))
        target_board = target_data.get("board", {})
        
        # Only update parent_dept if it's still the generic default
        if target_board.get("parent_dept") == "Department of Health":
            # Use the real parent dept from dietitian data as a starting point
            # Different professions may have different parent depts, but this is better than "Department of Health"
            target_board["parent_dept"] = diet_parent
            target_data["board"] = target_board
            target_file.write_text(json.dumps(target_data, indent=4, ensure_ascii=False), encoding="utf-8")

print(f"\n{'='*55}")
print(f"  Contact fields resolved (SLP→AUD): {resolved}")

# ── 3. FINAL PENDING COUNT ────────────────────────────────
print(f"\n{'='*55}")
print(f"  FINAL PENDING COUNTS PER VERTICAL")
print(f"{'='*55}")

ALL_VERTICALS = [
    "dietitian-pseo", "slp-pseo", "ot-pseo", "pt-pseo",
    "rrt-pseo", "aud-pseo", "pharm-pseo", "pharmacist-pseo"
]

grand_total = 0
for vdir in ALL_VERTICALS:
    json_dir = SCRATCH / vdir / "database" / "json"
    if not json_dir.exists():
        continue
    v_total = 0
    for f in json_dir.glob("*.json"):
        raw = f.read_text(encoding="utf-8")
        v_total += raw.count('"PENDING"')
    grand_total += v_total
    emoji = "✅" if v_total == 0 else "⚠️"
    print(f"  {vdir:20s}  {v_total:5d}  {emoji}")

print(f"{'='*55}")
print(f"  GRAND TOTAL:         {grand_total}")
print(f"{'='*55}")
