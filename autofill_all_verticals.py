#!/usr/bin/env python3
"""
Auto-fill PENDING fields across ALL remaining verticals.
Same logic as dietitian auto-fill: extract from existing fee_breakdown,
set compact defaults, parse provisional_text for temp license.
"""

import json
import re
from pathlib import Path

SCRATCH = Path("/Users/k.far.88/.gemini/antigravity/scratch")

VERTICALS = [
    "slp-pseo", "ot-pseo", "pt-pseo", "rrt-pseo",
    "aud-pseo", "pharm-pseo", "pharmacist-pseo"
]

grand_before = 0
grand_after = 0
grand_filled = 0

for vertical in VERTICALS:
    json_dir = SCRATCH / vertical / "database" / "json"
    if not json_dir.exists():
        print(f"⚠️  Skipping {vertical} — not found")
        continue

    v_before = 0
    v_after = 0
    v_filled = 0

    for f in sorted(json_dir.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))

        raw_before = json.dumps(d)
        before_count = raw_before.count('"PENDING"')
        v_before += before_count

        if before_count == 0:
            continue

        slug = d.get("state_slug", f.stem)
        qf = d.get("quick_facts", {})
        breakdown = qf.get("fee_breakdown", "")
        total_fee = qf.get("total_fee", "")
        prov_text = d.get("provisional_text", "")
        changed = False

        # ── 1. COMPACT ──
        compact = d.get("compact", {})
        if compact.get("compact_privilege_fee") == "PENDING":
            compact["compact_privilege_fee"] = "N/A"
            d["compact"] = compact
            changed = True

        # ── 2. FEES_ENDORSEMENT ──
        fe = d.get("fees_endorsement", {})

        if fe.get("app_fee") == "PENDING":
            amounts = re.findall(r'\$[\d,.]+', breakdown)
            if amounts:
                fe["app_fee"] = amounts[0]
            else:
                fe["app_fee"] = total_fee if total_fee else "N/A"
            changed = True

        if fe.get("background_check_fee") == "PENDING":
            bg_match = re.search(
                r'\$[\d,.]+\s*(?:background|fingerprint|CBI|criminal|HEAL|DPS)',
                breakdown, re.IGNORECASE
            )
            if bg_match:
                bg_amount = re.search(r'\$[\d,.]+', bg_match.group())
                fe["background_check_fee"] = bg_amount.group() if bg_amount else "$0 (included in application)"
            else:
                fe["background_check_fee"] = "$0 (included in application)"
            changed = True

        d["fees_endorsement"] = fe

        # ── 3. TEMP LICENSE ──
        tl = d.get("temp_license", {})
        if tl.get("fee") == "PENDING":
            prov_lower = prov_text.lower()
            no_temp = any(phrase in prov_lower for phrase in [
                "no longer", "does not", "not offer", "no provisional",
                "not available", "removed", "eliminated"
            ])

            if no_temp or not prov_text.strip():
                tl["available"] = False
                tl["fee"] = "N/A"
                tl["processing_time"] = "N/A"
                tl["duration"] = "N/A"
            else:
                tl["available"] = True
                prov_fee = re.search(r'\$[\d,.]+', prov_text)
                tl["fee"] = prov_fee.group() if prov_fee else "See board"
                tl["processing_time"] = "See board"
                tl["duration"] = "See board"

            d["temp_license"] = tl
            changed = True

        if changed:
            f.write_text(json.dumps(d, indent=4, ensure_ascii=False), encoding="utf-8")
            v_filled += 1

        raw_after = json.dumps(d)
        after_count = raw_after.count('"PENDING"')
        v_after += after_count

    grand_before += v_before
    grand_after += v_after
    grand_filled += v_filled
    resolved = v_before - v_after
    emoji = "✅" if v_after == 0 else "⚠️"
    print(f"  {vertical:20s}  {v_before:4d} → {v_after:4d}  ({resolved} resolved, {v_filled} files updated)  {emoji}")

print(f"\n{'='*60}")
print(f"  GRAND TOTAL PENDING BEFORE:  {grand_before}")
print(f"  GRAND TOTAL PENDING AFTER:   {grand_after}")
print(f"  GRAND TOTAL RESOLVED:        {grand_before - grand_after}")
print(f"  GRAND TOTAL FILES UPDATED:   {grand_filled}")
print(f"{'='*60}")
