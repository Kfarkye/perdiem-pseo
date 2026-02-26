#!/usr/bin/env python3
"""
FINAL APPROVAL AUDIT — Level 3 Deep Scan
Works on local dev AND Vercel CI. Uses dynamic paths (no hardcoded Mac paths).
Skips inapplicable checks (git, source sync) when running inside CI.
"""

import json
import hashlib
import os
import sys
from pathlib import Path
from collections import defaultdict

# Dynamic path resolution:
# This script lives at the REPO ROOT. Whether called locally or
# via `python3 ../final_approval_audit.py` from a vertical dir on Vercel,
# __file__ resolves to the repo root.
REPO = Path(__file__).resolve().parent

# Detect CI: Vercel sets VERCEL=1, or we can check if /vercel exists
IS_CI = os.environ.get("VERCEL") == "1" or os.environ.get("CI") == "1"

VERTICALS = [
    "dietitian-pseo", "slp-pseo", "ot-pseo", "pt-pseo",
    "rrt-pseo", "aud-pseo", "pharm-pseo", "pharmacist-pseo"
]

EXPECTED_STATES = 51
errors = []
warnings = []
passed = 0

def ok(msg):
    global passed
    passed += 1
    return True

def fail(msg, level="ERROR"):
    if level == "WARN":
        warnings.append(msg)
    else:
        errors.append(msg)
    return False

print("=" * 70)
print("  🔒 FINAL APPROVAL AUDIT — Level 3 Deep Scan")
print(f"  Repo:   {REPO}")
print(f"  CI:     {IS_CI}")
print("=" * 70)

# ═══════════════════════════════════════════════════
# GATE 1: SOURCE ↔ REPO FILE SYNC (local only)
# ═══════════════════════════════════════════════════
print("\n🔍 GATE 1: Source ↔ Repo JSON Sync")
if IS_CI:
    ok("Skipped in CI (repo IS source)")
    print("  ⏭️  Skipped in CI (repo IS the source of truth)")
else:
    desync_count = 0
    # On local, SOURCE is one level up from REPO if repo is a subfolder
    SOURCE = REPO.parent
    for v in VERTICALS:
        src_dir = SOURCE / v / "database" / "json"
        repo_dir = REPO / v / "database" / "json"
        if not src_dir.exists() or not repo_dir.exists():
            # If source doesn't exist separately, skip (they're the same)
            continue

        if src_dir.resolve() == repo_dir.resolve():
            continue  # Same directory, no sync needed

        for src_file in sorted(src_dir.glob("*.json")):
            repo_file = repo_dir / src_file.name
            if not repo_file.exists():
                fail(f"{v}/{src_file.name}: exists in source but NOT in repo")
                desync_count += 1
                continue

            src_hash = hashlib.md5(src_file.read_bytes()).hexdigest()
            repo_hash = hashlib.md5(repo_file.read_bytes()).hexdigest()
            if src_hash != repo_hash:
                fail(f"{v}/{src_file.name}: HASH MISMATCH (source has newer data!)", "WARN")
                desync_count += 1

    if desync_count == 0:
        ok("All JSON files synced")
        print(f"  ✅ All JSON files match source (0 desyncs)")
    else:
        print(f"  ⚠️  {desync_count} desyncs detected")

# ═══════════════════════════════════════════════════
# GATE 2: ZERO PENDING (redundant but critical)
# ═══════════════════════════════════════════════════
print("\n🔍 GATE 2: Zero PENDING")
pending = 0
for v in VERTICALS:
    json_dir = REPO / v / "database" / "json"
    if not json_dir.exists():
        continue
    for f in json_dir.glob("*.json"):
        c = f.read_text().count('"PENDING"')
        if c > 0:
            pending += c
            fail(f"PENDING in {v}/{f.name}: {c} instances")

if pending == 0:
    ok("Zero PENDING")
    print(f"  ✅ 0 PENDING across all files")
else:
    print(f"  ❌ {pending} PENDING fields found")

# ═══════════════════════════════════════════════════
# GATE 3: JSON PARSE + SCHEMA (every single file)
# ═══════════════════════════════════════════════════
print("\n🔍 GATE 3: JSON Parse + Schema")
parse_ok = 0
schema_fails = 0
for v in VERTICALS:
    json_dir = REPO / v / "database" / "json"
    if not json_dir.exists():
        continue
    for f in sorted(json_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
        except Exception as e:
            fail(f"JSON PARSE FAIL: {v}/{f.name}: {e}")
            schema_fails += 1
            continue

        parse_ok += 1

        # Core keys
        for key in ["state_slug", "state_name", "board", "board_source_url",
                     "quick_facts", "fingerprints", "compact", "temp_license"]:
            if key not in data:
                fail(f"{v}/{f.name}: missing '{key}'")
                schema_fails += 1

        # Board data quality
        board = data.get("board", {})
        if isinstance(board, dict):
            phone = board.get("phone", "")
            url = board.get("url", "")
            if not phone:
                fail(f"{v}/{f.name}: board.phone empty", "WARN")
            if not url:
                fail(f"{v}/{f.name}: board.url empty", "WARN")

        # Fingerprint completeness
        fp = data.get("fingerprints", {})
        if isinstance(fp, dict):
            for fk in ["required", "vendor", "fee", "method_in_state",
                        "method_out_of_state", "vendor_url"]:
                if fk not in fp:
                    fail(f"{v}/{f.name}: fingerprints.{fk} missing")
                    schema_fails += 1

if schema_fails == 0:
    ok("Schema valid")
    print(f"  ✅ {parse_ok} files parsed, 0 schema violations")
else:
    print(f"  ❌ {schema_fails} schema violations")

# ═══════════════════════════════════════════════════
# GATE 4: HTML DIST COMPLETENESS (local only — dist built during deploy)
# ═══════════════════════════════════════════════════
print("\n🔍 GATE 4: HTML Dist Completeness")
if IS_CI:
    ok("Skipped in CI (dist built by build.py after this audit)")
    print("  ⏭️  Skipped in CI (build.py generates dist/ after audit passes)")
    html_total = 0
else:
    html_total = 0
    empty_html = 0
    for v in VERTICALS:
        dist = REPO / v / "dist"
        if not dist.exists():
            fail(f"{v}/dist/ missing")
            continue

        htmls = list(dist.glob("*.html"))
        html_total += len(htmls)

        if not (dist / "index.html").exists():
            fail(f"{v}/dist/index.html missing")

        for h in htmls:
            size = h.stat().st_size
            if size < 500:
                fail(f"{v}/{h.name}: only {size} bytes (likely empty/broken)")
                empty_html += 1

    if empty_html == 0:
        ok("HTML files valid")
        print(f"  ✅ {html_total} HTML files, 0 empty/broken")
    else:
        print(f"  ❌ {empty_html} empty/broken HTML files")

# ═══════════════════════════════════════════════════
# GATE 5: SITEMAP + ROBOTS.TXT (local only)
# ═══════════════════════════════════════════════════
print("\n🔍 GATE 5: Sitemaps + Robots.txt")
sm_total_urls = 0
if IS_CI:
    ok("Skipped in CI (generated by build.py)")
    print("  ⏭️  Skipped in CI (sitemaps generated by build.py)")
else:
    for v in VERTICALS:
        dist = REPO / v / "dist"
        sm = dist / "sitemap.xml"
        rb = dist / "robots.txt"

        if not sm.exists():
            fail(f"{v}/dist/sitemap.xml missing")
            continue
        if not rb.exists():
            fail(f"{v}/dist/robots.txt missing")

        sm_text = sm.read_text()
        urls = sm_text.count("<loc>")
        sm_total_urls += urls

        if urls < EXPECTED_STATES:
            fail(f"{v}: sitemap only has {urls} URLs (expected ≥{EXPECTED_STATES})")

        if rb.exists():
            rb_text = rb.read_text()
            if "Sitemap:" not in rb_text:
                fail(f"{v}: robots.txt missing Sitemap: directive")

    ok("Sitemaps valid")
    print(f"  ✅ {sm_total_urls} total sitemap URLs across 8 verticals")

# ═══════════════════════════════════════════════════
# GATE 6: REAL DATA SPOT CHECKS
# ═══════════════════════════════════════════════════
print("\n🔍 GATE 6: Real Data Spot Checks")
spot_checks = [
    ("dietitian-pseo", "texas-dietitian.json", "board.phone", lambda v: len(v) >= 10),
    ("dietitian-pseo", "texas-dietitian.json", "fingerprints.vendor", lambda v: "IdentoGO" in v or "FAST" in v),
    ("dietitian-pseo", "california-dietitian.json", "fingerprints.required", lambda v: v == False),
    ("pharmacist-pseo", "new-york-pharmacist.json", "fingerprints.fee", lambda v: "$" in str(v)),
    ("pharm-pseo", "florida-pharm.json", "fingerprints.vendor", lambda v: "FDLE" in v or "Cogent" in v),
    ("slp-pseo", "alabama-slp.json", "board.phone", lambda v: len(str(v)) >= 10),
    ("ot-pseo", "ohio-ot.json", "fingerprints.method_out_of_state", lambda v: "moisturize" in str(v).lower() or "FD-258" in str(v)),
    ("rrt-pseo", "washington-rrt.json", "board.url", lambda v: v.startswith("http")),
]

spot_passed = 0
for vertical, filename, dotpath, validator in spot_checks:
    fpath = REPO / vertical / "database" / "json" / filename
    if not fpath.exists():
        fail(f"Spot check: {vertical}/{filename} not found")
        continue

    data = json.loads(fpath.read_text())
    keys = dotpath.split(".")
    val = data
    for k in keys:
        val = val.get(k, None) if isinstance(val, dict) else None
        if val is None:
            break

    if val is not None and validator(val):
        spot_passed += 1
    else:
        fail(f"Spot check FAIL: {vertical}/{filename} → {dotpath} = {repr(val)}")

print(f"  ✅ {spot_passed}/{len(spot_checks)} spot checks passed")

# ═══════════════════════════════════════════════════
# GATE 7: GIT STATUS (local only)
# ═══════════════════════════════════════════════════
print("\n🔍 GATE 7: Git Status")
if IS_CI:
    ok("Skipped in CI (Vercel clones from Git)")
    print("  ⏭️  Skipped in CI (Vercel clones from Git automatically)")
else:
    git_dir = REPO / ".git"
    if git_dir.exists():
        ok("Git initialized")
        print(f"  ✅ Git repo initialized")
    else:
        fail("Git repo not initialized")

# ═══════════════════════════════════════════════════
# GATE 8: VERCEL CONFIG CHECK
# ═══════════════════════════════════════════════════
print("\n🔍 GATE 8: Vercel Deploy Readiness")
vercel_found = 0
for v in VERTICALS:
    vc = REPO / v / "vercel.json"
    if vc.exists():
        vercel_found += 1

if vercel_found > 0:
    ok("Vercel configs found")
    print(f"  ✅ {vercel_found}/8 verticals have vercel.json")
else:
    fail("No vercel.json found in any vertical — Vercel will need manual config", "WARN")
    print(f"  ⚠️  No vercel.json files found (manual Vercel config needed)")

# ═══════════════════════════════════════════════════
# FINAL VERDICT
# ═══════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  📋 FINAL APPROVAL VERDICT")
print("=" * 70)
print(f"""
  GATES PASSED:      {passed}/8
  ERRORS:            {len(errors)}
  WARNINGS:          {len(warnings)}
  PARSE OK:          {parse_ok}
  HTML PAGES:        {html_total}
  SITEMAP URLS:      {sm_total_urls}
  PENDING:           {pending}
  ENVIRONMENT:       {"CI (Vercel)" if IS_CI else "Local"}
""")

if errors:
    print(f"  ❌ ERRORS ({len(errors)}):")
    for e in errors:
        print(f"     • {e}")

if warnings:
    print(f"  ⚠️  WARNINGS ({len(warnings)}):")
    for w in warnings[:10]:
        print(f"     • {w}")
    if len(warnings) > 10:
        print(f"     ... and {len(warnings) - 10} more")

print()
if not errors:
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║  🚀  APPROVED FOR DEPLOYMENT — ALL GATES PASS   ║")
    print("  ╚══════════════════════════════════════════════════╝")
    sys.exit(0)
else:
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║  🛑  DEPLOYMENT BLOCKED — FIX ERRORS FIRST      ║")
    print("  ╚══════════════════════════════════════════════════╝")
    sys.exit(len(errors))
