#!/usr/bin/env python3
"""
SCHEMA MIGRATION: v2 -> v2.1
1. Moves `mpje_required` from root into `profession_overrides.pharmacy`
2. Counts all PENDING fields across 408 files as a progress audit
"""

import json
from pathlib import Path

SCRATCH = Path("/Users/k.far.88/.gemini/antigravity/scratch")

VERTICAL_DIRS = [
    "dietitian-pseo", "slp-pseo", "ot-pseo", "pt-pseo",
    "rrt-pseo", "aud-pseo", "pharm-pseo", "pharmacist-pseo"
]

moved = 0
pending_total = 0
files_with_pending = 0
total_files = 0

for vdir in VERTICAL_DIRS:
    json_dir = SCRATCH / vdir / "database" / "json"
    if not json_dir.exists():
        continue

    for json_file in sorted(json_dir.glob("*.json")):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        total_files += 1
        changed = False

        # -----------------------------------------------------------
        # 1. Move mpje_required into profession_overrides
        #    Gotcha #1 fix: don't type-check, just check key existence
        # -----------------------------------------------------------
        if "mpje_required" in data:
            mpje_val = data.pop("mpje_required")
            if "profession_overrides" not in data:
                data["profession_overrides"] = {}
            if "pharmacy" not in data["profession_overrides"]:
                data["profession_overrides"]["pharmacy"] = {}
            data["profession_overrides"]["pharmacy"]["mpje_required"] = mpje_val
            moved += 1
            changed = True

        # Ensure profession_overrides exists on all files (even if empty)
        if "profession_overrides" not in data:
            data["profession_overrides"] = {}
            changed = True

        # -----------------------------------------------------------
        # 2. Count PENDING fields for progress audit
        # -----------------------------------------------------------
        raw = json.dumps(data)
        count = raw.count('"PENDING"')
        if count > 0:
            pending_total += count
            files_with_pending += 1

        if changed:
            json_file.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")

print(f"\n{'='*55}")
print(f"  SCHEMA MIGRATION v2.1 COMPLETE")
print(f"{'='*55}")
print(f"  mpje_required moved to profession_overrides: {moved}")
print(f"  Total files scanned:       {total_files}")
print(f"  Files with PENDING fields: {files_with_pending}")
print(f"  Total PENDING fields:      {pending_total}")
print(f"{'='*55}")
