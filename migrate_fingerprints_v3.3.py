#!/usr/bin/env python3
"""
SCHEMA MIGRATION v3.3 (Final Polish)
Add/normalize `fingerprints` blocks across JSON files.

Hardening upgrades vs v3.2:
- True Idempotency: Only writes if data actually changed (fingerprints, state_slug, or key ordering).
- Hardware-Level Safety: Added `os.fsync` and `shutil.copymode` to atomic writes to guarantee zero corruption and preserve file permissions.
- Safer QA Report Export: Automatically creates parent directories for the CSV export, and auto-sorts records.
- Stricter Schema Backfills: Handles missing, `""`, or `null` `state_slug` safely.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


VERTICALS_DEFAULT = [
    "dietitian-pseo", "slp-pseo", "ot-pseo", "pt-pseo",
    "rrt-pseo", "aud-pseo", "pharm-pseo", "pharmacist-pseo",
]

# Explicitly pre-populated for all targeted verticals so data teams can easily inject state exemptions
NO_FINGERPRINT_STATES: Dict[str, Set[str]] = {
    "dietitian-pseo": {"arizona", "california", "virginia"},
    "slp-pseo": set(),
    "ot-pseo": set(),
    "pt-pseo": set(),
    "rrt-pseo": set(),
    "aud-pseo": set(),
    "pharm-pseo": set(),
    "pharmacist-pseo": set(),
}

STATE_FINGERPRINT_OVERRIDES: Dict[str, Dict[str, str]] = {
    "florida": {
        "vendor": "FDLE / Cogent Systems",
        "fee": "$37.25",
        "vendor_url": "https://www.fdle.state.fl.us/Criminal-History-Records/Obtaining-Criminal-History-Records/Submitting-Fingerprints.aspx",
    },
    "new-york": {
        "vendor": "MorphoTrust / IdentoGO",
        "fee": "$102.00",
        "vendor_url": "https://uenroll.identogo.com/",
    },
    "texas": {
        "vendor": "IdentoGO (FAST Pass via DPS)",
        "fee": "$38.25",
        "vendor_url": "https://www.identogo.com/locations/texas",
    },
    "california": {
        "vendor": "California DOJ LiveScan",
        "fee": "$49.00",
        "vendor_url": "https://oag.ca.gov/fingerprints/locations",
    },
    "illinois": {
        "vendor": "IdentoGO / Illinois State Police",
        "fee": "$60.00",
        "vendor_url": "https://www.identogo.com/locations/illinois",
    },
    "pennsylvania": {
        "vendor": "IdentoGO / PA State Police",
        "fee": "$22.60",
        "vendor_url": "https://www.identogo.com/locations/pennsylvania",
    },
    "north-carolina": {
        "vendor": "IdentoGO / SBI",
        "fee": "$38.00",
        "vendor_url": "https://www.identogo.com/locations/north-carolina",
    },
    "washington": {
        "vendor": "IdentoGO / WSP",
        "fee": "$35.50",
        "vendor_url": "https://www.identogo.com/locations/washington",
    },
    "colorado": {
        "vendor": "IdentoGO / CBI",
        "fee": "$39.50",
        "vendor_url": "https://www.identogo.com/locations/colorado",
    },
    "minnesota": {
        "vendor": "IdentoGO / BCA",
        "fee": "$32.00",
        "vendor_url": "https://www.identogo.com/locations/minnesota",
    },
    "nevada": {
        "vendor": "IdentoGO",
        "fee": "$37.50",
        "vendor_url": "https://www.identogo.com/locations/nevada",
    },
    "maine": {
        "vendor": "IdentoGO / State Police",
        "fee": "$21.00",
        "vendor_url": "https://www.identogo.com/locations/maine",
    },
    "georgia": {
        "vendor": "IdentoGO / GCIC",
        "fee": "$35.00",
        "vendor_url": "https://www.identogo.com/locations/georgia",
    },
    "indiana": {
        "vendor": "IdentoGO / State Police",
        "fee": "$28.00",
        "vendor_url": "https://www.identogo.com/locations/indiana",
    },
}

DEFAULT_FINGERPRINT: Dict[str, Any] = {
    "required": True,
    "method_in_state": "LiveScan (IdentoGO)",
    "method_out_of_state": (
        "IdentoGO Out-of-State Live Scan (adds ~$39.95 fee) OR "
        "FD-258 hard card via mail (tip: moisturize hands for days prior to reduce smudge rejects)"
    ),
    "vendor": "IdentoGO (IDEMIA)",
    "fee": "$35-$50 (varies by state)",
    "delay_out_of_state_weeks": "2-4",
    "vendor_url": "https://uenroll.identogo.com/",
}

NO_FP_BLOCK: Dict[str, Any] = {
    "required": False,
    "method_in_state": "N/A",
    "method_out_of_state": "N/A",
    "vendor": "N/A",
    "fee": "N/A",
    "delay_out_of_state_weeks": "N/A",
    "vendor_url": "N/A",
}


@dataclass
class Counters:
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    warnings: int = 0


def _normalize_state_slug(raw: Any) -> str:
    s = str(raw).strip().lower() if raw else ""
    return s.replace("_", "-").replace(" ", "-")


def _derive_state_slug(data: Dict[str, Any], file_path: Path) -> str:
    candidate = data.get("state_slug") or file_path.stem
    return _normalize_state_slug(candidate)


def _order_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enforces logical key ordering. `fingerprints` belongs near `background_check`.
    Systemic keys like `metadata` are pushed to the absolute bottom.
    """
    top_keys = [
        "id", "name", "state_slug", "state_name", "status", "description", 
        "regulator", "fees", "education", "exams", "experience", 
        "background_check", "fingerprints", "continuing_education", 
        "renewal"
    ]
    bottom_keys = ["metadata"]
    
    ordered_data = {}
    
    # 1. Top priority keys
    for k in top_keys:
        if k in data:
            ordered_data[k] = data[k]
            
    # 2. Uncategorized (middle) keys
    for k in data:
        if k not in top_keys and k not in bottom_keys:
            ordered_data[k] = data[k]
            
    # 3. Bottom priority keys
    for k in bottom_keys:
        if k in data:
            ordered_data[k] = data[k]
            
    return ordered_data


def _atomic_write_json(path: Path, payload: Dict[str, Any], indent: int = 4) -> None:
    """
    Writes JSON atomically to prevent corruption from mid-write crashes.
    Includes hardware fsync and copies existing file permissions.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_name = tempfile.mkstemp(prefix=path.stem + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=indent, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(tmp_fd)  # Hardware-level flush guarantees no corruption on VM crash
        
        # Inherit permissions from target file if it exists
        if path.exists():
            shutil.copymode(path, tmp_name)
            
        os.replace(tmp_name, path)  # Atomic replacement on same filesystem
    finally:
        if os.path.exists(tmp_name):
            try:
                os.remove(tmp_name)
            except OSError:
                pass


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_fingerprint_block(vertical: str, state_slug: str) -> Dict[str, Any]:
    no_fp_states = NO_FINGERPRINT_STATES.get(vertical, set())
    if state_slug in no_fp_states:
        return dict(NO_FP_BLOCK)

    fp = dict(DEFAULT_FINGERPRINT)
    if override := STATE_FINGERPRINT_OVERRIDES.get(state_slug):
        fp.update(override)
    return fp


def migrate_vertical(
    root: Path, 
    vertical: str, 
    overwrite: bool, 
    dry_run: bool, 
    backup: bool, 
    qa_records: Optional[List[Dict[str, Any]]] = None
) -> Counters:
    c = Counters()
    json_dir = root / vertical / "database" / "json"
    if not json_dir.exists():
        return c

    for f in sorted(json_dir.glob("*.json")):
        if not f.is_file():
            continue

        try:
            data = _load_json(f)
            if not isinstance(data, dict):
                raise ValueError("Top-level JSON is not an object")

            dirty = False
            state_slug = _derive_state_slug(data, f)

            # Schema Validation Backfills
            if not data.get("state_slug"):  # Handles missing, empty string, or null
                data["state_slug"] = state_slug
                dirty = True
            
            if "name" not in data:
                print(f"WARNING: '{f.name}' in '{vertical}' is missing a 'name' field.", file=sys.stderr)
                c.warnings += 1

            # Determine Target State
            has_existing = ("fingerprints" in data) and isinstance(data["fingerprints"], dict)
            target_fp = build_fingerprint_block(vertical, state_slug)

            # Idempotency / Overwrite Logic
            update_fp = False
            if not has_existing:
                update_fp = True
            elif overwrite and data["fingerprints"] != target_fp:
                update_fp = True

            if update_fp:
                data["fingerprints"] = target_fp
                dirty = True

            # Enforce Key Ordering
            ordered_data = _order_keys(data)
            if list(data.keys()) != list(ordered_data.keys()):
                dirty = True

            # Track for QA Report
            if qa_records is not None:
                record = {
                    "vertical": vertical,
                    "state_slug": state_slug,
                    "action": "dry-run" if (dry_run and dirty) else "updated" if dirty else "skipped"
                }
                record.update(ordered_data.get("fingerprints", {}))
                qa_records.append(record)

            # Execution
            if not dirty:
                c.skipped += 1
                continue

            if dry_run:
                c.updated += 1
                continue

            if backup:
                bak = f.with_suffix(f.suffix + ".bak")
                if not bak.exists():
                    shutil.copy2(f, bak)

            _atomic_write_json(f, ordered_data, indent=4)
            c.updated += 1

        except json.JSONDecodeError as e:
            print(f"ERROR processing '{f.name}': Invalid JSON: {e}", file=sys.stderr)
            c.errors += 1
        except Exception as e:
            print(f"ERROR processing '{f.name}': {type(e).__name__}: {e}", file=sys.stderr)
            c.errors += 1

    return c


def count_pending(root: Path, verticals: List[str]) -> int:
    total = 0
    for v in verticals:
        jd = root / v / "database" / "json"
        if not jd.exists():
            continue
        for fp in jd.glob("*.json"):
            if not fp.is_file():
                continue
            try:
                total += fp.read_text(encoding="utf-8").count('"PENDING"')
            except Exception:
                pass
    return total


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Add/normalize fingerprints blocks across vertical JSON directories.")
    ap.add_argument(
        "--root",
        type=Path,
        default=Path(os.environ.get("SCRATCH_ROOT", "")) if os.environ.get("SCRATCH_ROOT") else None,
        help="Root scratch path containing <vertical>/database/json. Can also set env SCRATCH_ROOT.",
    )
    ap.add_argument("--verticals", nargs="*", default=VERTICALS_DEFAULT, help="List of vertical directories to process.")
    ap.add_argument("--qa-report", type=Path, help="Export a unified QA CSV report of all fingerprint requirements.")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing fingerprints blocks if they differ.")
    ap.add_argument("--dry-run", action="store_true", help="Compute changes but do not write files.")
    ap.add_argument("--backup", action="store_true", help="Write a one-time .bak copy of each file before modifying.")
    args = ap.parse_args(argv)

    if args.root is None:
        print("ERROR: --root is required (or set SCRATCH_ROOT).", file=sys.stderr)
        return 2

    root: Path = args.root.expanduser().resolve()
    verticals: List[str] = list(args.verticals)

    totals = Counters()
    qa_records: Optional[List[Dict[str, Any]]] = [] if args.qa_report else None

    print("Starting Fingerprint Schema Migration...")
    print("-" * 62)

    for v in verticals:
        c = migrate_vertical(
            root=root, 
            vertical=v, 
            overwrite=args.overwrite, 
            dry_run=args.dry_run, 
            backup=args.backup, 
            qa_records=qa_records
        )
        totals.updated += c.updated
        totals.skipped += c.skipped
        totals.errors += c.errors
        totals.warnings += c.warnings
        
        # Consistent vertical alignment in printout
        if any((c.updated, c.skipped, c.errors, c.warnings)):
            print(f"{v:<20s} updated={c.updated:<4d} skipped={c.skipped:<4d} errors={c.errors:<3d} warnings={c.warnings:<3d}")

    # Generate Data QA Report
    if args.qa_report:
        if not qa_records:
            print(f"\nNotice: No data was processed. QA report ({args.qa_report}) was not created.")
        else:
            args.qa_report.parent.mkdir(parents=True, exist_ok=True)
            
            # Sort records for a cleaner QA experience
            qa_records.sort(key=lambda x: (x.get("vertical", ""), x.get("state_slug", "")))
            
            keys = [
                "vertical", "state_slug", "action", "required", "vendor", 
                "fee", "method_in_state", "method_out_of_state", 
                "delay_out_of_state_weeks", "vendor_url"
            ]
            
            # Dynamically capture any stray/extra keys added inside overrides
            all_keys = []
            for r in qa_records:
                for k in r.keys():
                    if k not in all_keys:
                        all_keys.append(k)
            
            fieldnames = [k for k in keys if k in all_keys] + [k for k in all_keys if k not in keys]
            
            try:
                with open(args.qa_report, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(qa_records)
                print(f"\n[+] Data QA report exported successfully: {args.qa_report}")
            except Exception as e:
                print(f"\nERROR writing QA report: {type(e).__name__}: {e}", file=sys.stderr)

    pending = count_pending(root, verticals)

    print("\n" + "=" * 62)
    print("MIGRATION SUMMARY")
    print(f"Target Root:  {root}")
    print(f"Run Mode:     {'DRY RUN' if args.dry_run else 'LIVE EXECUTION'}")
    print(f"Files Edited: {totals.updated}")
    print(f"Skipped:      {totals.skipped}")
    print(f"Warnings:     {totals.warnings}")
    print(f"Errors:       {totals.errors}")
    print(f"PENDING tags: {pending} (Target 0)")
    print("=" * 62)

    # Return 1 for CI pipelines to fail if there are errors or unhandled PENDING strings
    if totals.errors > 0 or pending > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
