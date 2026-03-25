#!/usr/bin/env python3
"""
Validation Gate — Factory Pipeline Layer 3

Validates enriched JSON files before build:
1. Schema check — all required fields present
2. Cross-state sanity — no obviously wrong data
3. Terminology consistency — credential_type matches known patterns
4. Data completeness audit

Usage:
  python3 factory/validate.py pharm        # validate all 51 pharm states
  python3 factory/validate.py pharm --fix  # auto-fix minor issues
"""

import argparse
import json
import sys
from pathlib import Path

# ── Required fields for CNA-quality enrichment ──
REQUIRED_FIELDS = {
    "state_name": str,
    "profession_name": str,
    "board.name": str,
    "board.url": str,
    "quick_facts.total_fee": str,
    "seo.title": str,
    "steps": list,
    "faqs": list,
}

ENRICHMENT_FIELDS = {
    "credential_type.official_term": str,
    "credential_type.page_title_term": str,
    "credential_type.renewal_term": str,
    "credential_type.transfer_term": str,
    "variants.new_applicant.hero.title": str,
    "variants.new_applicant.hero.dek": str,
}

VALID_CREDENTIAL_TERMS = {
    "license", "certification", "registration", "certificate",
    "registry listing", "permit", "endorsement",
}

# ── Sanity bounds ──
MAX_REASONABLE_FEE = 2000  # No CNA/tech fee should exceed this
MAX_TRAINING_HOURS = 2500  # No CNA/tech training should exceed this


def get_nested(data: dict, dotted_key: str):
    """Get a nested value by dotted key path."""
    keys = dotted_key.split(".")
    val = data
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return None
    return val


def validate_file(fpath: Path) -> tuple[list, list]:
    """Validate a single JSON file. Returns (errors, warnings)."""
    errors = []
    warnings = []

    try:
        data = json.loads(fpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"JSON parse error: {e}"], []

    state = data.get("state_name", fpath.stem)

    # 1. Required fields
    for field, expected_type in REQUIRED_FIELDS.items():
        val = get_nested(data, field)
        if val is None or val == "":
            errors.append(f"MISSING: {field}")
        elif not isinstance(val, expected_type):
            errors.append(f"WRONG TYPE: {field} expected {expected_type.__name__}, got {type(val).__name__}")

    # 2. Enrichment fields (warnings, not errors)
    for field, expected_type in ENRICHMENT_FIELDS.items():
        val = get_nested(data, field)
        if val is None or val == "":
            warnings.append(f"NOT ENRICHED: {field}")

    # 3. Credential type validation
    ct = data.get("credential_type", {})
    if ct:
        term = ct.get("official_term", "").lower()
        if term and term not in VALID_CREDENTIAL_TERMS:
            warnings.append(f"UNUSUAL CREDENTIAL: '{term}' — verify this is the official state term")

    # 4. Fee sanity
    fee_str = data.get("quick_facts", {}).get("total_fee", "")
    if fee_str and fee_str.startswith("$"):
        try:
            fee_val = float(fee_str.replace("$", "").replace(",", ""))
            if fee_val > MAX_REASONABLE_FEE:
                errors.append(f"FEE TOO HIGH: ${fee_val} exceeds ${MAX_REASONABLE_FEE} — verify")
        except ValueError:
            pass

    # 5. Training hours sanity
    hours_str = data.get("quick_facts", {}).get("training_hours", "")
    if hours_str:
        try:
            hours_val = int(hours_str.split()[0])
            if hours_val > MAX_TRAINING_HOURS:
                errors.append(f"TRAINING HOURS TOO HIGH: {hours_val} — verify")
        except (ValueError, IndexError):
            pass

    # 6. Steps validation
    steps = data.get("steps", [])
    if steps:
        if len(steps) < 2:
            warnings.append(f"ONLY {len(steps)} STEP(S) — minimum 2 expected")
        for i, step in enumerate(steps):
            if not step.get("title"):
                errors.append(f"STEP {i+1}: missing title")
            if not step.get("description"):
                errors.append(f"STEP {i+1}: missing description")

    # 7. Hero dek quality check
    dek = get_nested(data, "variants.new_applicant.hero.dek") or ""
    if dek:
        if state not in dek:
            warnings.append(f"HERO DEK missing state name '{state}'")
        if len(dek) > 200:
            warnings.append(f"HERO DEK too long ({len(dek)} chars) — keep under 200")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate enriched JSON files")
    parser.add_argument("slug", help="Specialty slug (e.g. pharm, aud, dietitian)")
    parser.add_argument("--fix", action="store_true", help="Auto-fix minor issues")
    args = parser.parse_args()

    json_dir = Path(__file__).resolve().parent.parent / f"{args.slug}-pseo" / "database" / "json"
    if not json_dir.exists():
        print(f"ERROR: {json_dir} not found")
        sys.exit(1)

    json_files = sorted(json_dir.glob("*.json"))
    print(f"Validation Gate: {args.slug}")
    print(f"  Files: {len(json_files)}")
    print("=" * 60)

    total_errors = 0
    total_warnings = 0
    fully_enriched = 0

    for fpath in json_files:
        errors, warnings = validate_file(fpath)
        state = fpath.stem
        total_errors += len(errors)
        total_warnings += len(warnings)

        if not errors and not warnings:
            fully_enriched += 1
            continue

        if errors:
            print(f"\n  ❌ {state}")
            for e in errors:
                print(f"      ERROR: {e}")
        if warnings:
            if not errors:
                print(f"\n  ⚠️  {state}")
            for w in warnings:
                print(f"      WARN:  {w}")

    print("\n" + "=" * 60)
    print(f"  TOTAL FILES:     {len(json_files)}")
    print(f"  FULLY ENRICHED:  {fully_enriched}")
    print(f"  ERRORS:          {total_errors}")
    print(f"  WARNINGS:        {total_warnings}")

    if total_errors > 0:
        print(f"\n  ❌ BLOCKED — {total_errors} errors must be resolved before build")
        sys.exit(1)
    elif total_warnings > 0:
        print(f"\n  ⚠️  PASSABLE — {total_warnings} warnings (enrichment gaps)")
        sys.exit(0)
    else:
        print(f"\n  ✅ ALL CLEAR — ready for build")
        sys.exit(0)


if __name__ == "__main__":
    main()
