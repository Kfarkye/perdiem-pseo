#!/usr/bin/env python3
"""Apply Gemini fee research results back into the perdiem-pseo JSON data files.

Usage:
  1. Run Gemini grounded search using the prompt in gemini_fee_research_prompt.md
  2. Save each JSON response into research/results/ as {state_abbr}-{vertical}.json
  3. Run: python3 research/apply_fee_research.py

The script will:
  - Read each result file
  - Find the matching state JSON in the correct vertical directory
  - Patch only the fields that were researched
  - Write a backup before modifying
  - Print a summary of changes
"""
from __future__ import annotations

import json
import glob
import shutil
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent.parent
RESULTS_DIR = Path(__file__).resolve().parent / "results"
TODAY = datetime.now().strftime("%Y-%m-%d")

# Field path → how to format the value for the JSON
FIELD_FORMATTERS = {
    "quick_facts.total_fee": lambda v: f"${v}" if v.isdigit() else v,
    "quick_facts.renewal_fee": lambda v: f"${v}" if v.isdigit() else v,
    "quick_facts.renewal_cycle": lambda v: v,  # "Every 2 years"
    "quick_facts.license_duration": lambda v: v,
    "fees_endorsement.total_estimated_cost": lambda v: f"${v}" if v.isdigit() else v,
    "fees_endorsement.background_check_fee": lambda v: f"${v}" if v.isdigit() else v,
    "fees_endorsement.app_fee": lambda v: f"${v}" if v.isdigit() else v,
}


def find_state_json(vertical: str, state: str) -> Path | None:
    """Find the JSON file for a given vertical and state name."""
    slug = state.lower().replace(" ", "-")
    # Try common patterns
    for pattern in [
        f"{vertical}-pseo/database/json/{slug}-{vertical}.json",
        f"{vertical}-pseo/database/json/{slug}.json",
    ]:
        p = REPO / pattern
        if p.exists():
            return p

    # Fallback: glob
    candidates = list((REPO / f"{vertical}-pseo" / "database" / "json").glob(f"{slug}*.json"))
    candidates = [c for c in candidates if not c.name.endswith(".bak")]
    if len(candidates) == 1:
        return candidates[0]
    return None


def set_nested(data: dict, field_path: str, value: str) -> None:
    """Set a value in a nested dict using dot notation."""
    parts = field_path.split(".")
    obj = data
    for part in parts[:-1]:
        obj = obj.setdefault(part, {})
    obj[parts[-1]] = value


def main() -> None:
    if not RESULTS_DIR.exists():
        print(f"No results directory at {RESULTS_DIR}")
        print("Create research/results/ and place Gemini JSON responses there.")
        return

    result_files = sorted(RESULTS_DIR.glob("*.json"))
    if not result_files:
        print(f"No result files in {RESULTS_DIR}")
        return

    total_patched = 0
    total_skipped = 0
    changes_log = []

    for rf in result_files:
        try:
            result = json.loads(rf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  SKIP {rf.name}: invalid JSON ({e})")
            total_skipped += 1
            continue

        vertical = result["vertical"]
        state = result["state"]
        fields = result.get("fields", {})

        target = find_state_json(vertical, state)
        if not target:
            print(f"  SKIP {rf.name}: cannot find JSON for {state}/{vertical}")
            total_skipped += 1
            continue

        # Read existing data
        data = json.loads(target.read_text(encoding="utf-8"))

        # Backup
        backup = target.with_suffix(".json.pre-research-bak")
        if not backup.exists():
            shutil.copyfile(target, backup)

        patched_fields = []
        for field_path, field_data in fields.items():
            value = field_data.get("value", "")
            confidence = field_data.get("confidence", "")

            # Skip non-results
            if value in ("NOT_PUBLISHED", "SITE_UNAVAILABLE", ""):
                continue

            # Only apply HIGH or MEDIUM confidence
            if confidence == "LOW":
                changes_log.append(f"  LOW-SKIP {state}/{vertical}: {field_path} = {value}")
                continue

            # Format the value
            formatter = FIELD_FORMATTERS.get(field_path, lambda v: v)
            formatted = formatter(value)

            set_nested(data, field_path, formatted)
            patched_fields.append(f"{field_path}={formatted}")

        if patched_fields:
            # Update last_verified_date
            data["last_verified_date"] = TODAY

            target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            total_patched += 1
            changes_log.append(f"  PATCHED {state}/{vertical}: {', '.join(patched_fields)}")
        else:
            changes_log.append(f"  NO-OP {state}/{vertical}: no HIGH/MEDIUM values")

    print(f"\n{'='*60}")
    print(f"Fee Research Applied")
    print(f"{'='*60}")
    print(f"Patched: {total_patched}")
    print(f"Skipped: {total_skipped}")
    print(f"{'='*60}")
    for line in changes_log:
        print(line)


if __name__ == "__main__":
    main()
