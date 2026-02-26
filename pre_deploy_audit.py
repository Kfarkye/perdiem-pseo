#!/usr/bin/env python3
"""
PRE-DEPLOY AUDIT — Comprehensive check of the perdiem-pseo repo.
Validates: JSON schema, HTML dist, sitemaps, robots.txt, file counts,
URL consistency, SEO meta tags, fingerprint data, board data, and more.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

REPO = Path("/Users/k.far.88/.gemini/antigravity/scratch/perdiem-pseo")

VERTICALS = [
    "dietitian-pseo", "slp-pseo", "ot-pseo", "pt-pseo",
    "rrt-pseo", "aud-pseo", "pharm-pseo", "pharmacist-pseo"
]

EXPECTED_STATES = 51  # 50 states + DC

# Required JSON keys (v2.1 schema)
REQUIRED_JSON_KEYS = [
    "state_slug", "state_name", "quick_facts", "board",
    "board_source_url", "fees_endorsement", "compact",
    "temp_license", "fingerprints"
]

# Required board subkeys
REQUIRED_BOARD_KEYS = ["phone", "url"]

# Required fingerprint subkeys
REQUIRED_FP_KEYS = [
    "required", "method_in_state", "method_out_of_state",
    "vendor", "fee", "delay_out_of_state_weeks", "vendor_url"
]

anomalies = []
warnings = []
stats = defaultdict(int)

def check(condition, msg, level="ERROR"):
    if not condition:
        if level == "WARN":
            warnings.append(msg)
        else:
            anomalies.append(msg)
        return False
    return True

print("=" * 70)
print("  PRE-DEPLOY AUDIT — perdiem-pseo")
print("=" * 70)

# ════════════════════════════════════════════════
# 1. REPO STRUCTURE
# ════════════════════════════════════════════════
print("\n[1/8] REPO STRUCTURE...")
check(REPO.exists(), f"Repo dir missing: {REPO}")
check((REPO / ".git").exists(), "Git repo not initialized")
check((REPO / ".gitignore").exists(), ".gitignore missing")

for v in VERTICALS:
    vdir = REPO / v
    check(vdir.exists(), f"Vertical dir missing: {v}")
    check((vdir / "build.py").exists(), f"{v}/build.py missing")
    check((vdir / "database" / "json").exists(), f"{v}/database/json/ missing")
    check((vdir / "dist").exists(), f"{v}/dist/ missing")

print("  ✓ Repo structure checks complete")

# ════════════════════════════════════════════════
# 2. JSON FILE COUNTS
# ════════════════════════════════════════════════
print("\n[2/8] JSON FILE COUNTS...")
total_json = 0
for v in VERTICALS:
    json_dir = REPO / v / "database" / "json"
    if not json_dir.exists():
        continue
    count = len(list(json_dir.glob("*.json")))
    total_json += count
    check(count == EXPECTED_STATES, f"{v}: Expected {EXPECTED_STATES} JSON files, got {count}")
    stats[f"{v}_json"] = count

print(f"  Total JSON files: {total_json}")
check(total_json == EXPECTED_STATES * len(VERTICALS),
      f"Expected {EXPECTED_STATES * len(VERTICALS)} total JSON, got {total_json}")

# ════════════════════════════════════════════════
# 3. ZERO PENDING
# ════════════════════════════════════════════════
print("\n[3/8] PENDING FIELD CHECK...")
pending_total = 0
pending_files = []
for v in VERTICALS:
    json_dir = REPO / v / "database" / "json"
    if not json_dir.exists():
        continue
    for f in json_dir.glob("*.json"):
        count = f.read_text(encoding="utf-8").count('"PENDING"')
        if count > 0:
            pending_total += count
            pending_files.append(f"{v}/{f.name} ({count})")

check(pending_total == 0, f"PENDING fields found: {pending_total} in {len(pending_files)} files")
if pending_files:
    for pf in pending_files[:10]:
        anomalies.append(f"  → {pf}")
print(f"  PENDING strings: {pending_total}")

# ════════════════════════════════════════════════
# 4. JSON SCHEMA INTEGRITY
# ════════════════════════════════════════════════
print("\n[4/8] JSON SCHEMA INTEGRITY...")
schema_issues = 0
for v in VERTICALS:
    json_dir = REPO / v / "database" / "json"
    if not json_dir.exists():
        continue
    for f in sorted(json_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            anomalies.append(f"JSON parse error: {v}/{f.name}: {e}")
            schema_issues += 1
            continue

        slug = data.get("state_slug", f.stem)

        # Required top-level keys
        for key in REQUIRED_JSON_KEYS:
            if key not in data:
                anomalies.append(f"{v}/{slug}: missing required key '{key}'")
                schema_issues += 1

        # Board subkeys
        board = data.get("board", {})
        if isinstance(board, dict):
            for bk in REQUIRED_BOARD_KEYS:
                val = board.get(bk, "")
                if not val or val == "PENDING":
                    anomalies.append(f"{v}/{slug}: board.{bk} is empty/PENDING")
                    schema_issues += 1

        # Fingerprint subkeys
        fp = data.get("fingerprints", {})
        if isinstance(fp, dict):
            for fk in REQUIRED_FP_KEYS:
                if fk not in fp:
                    anomalies.append(f"{v}/{slug}: fingerprints.{fk} missing")
                    schema_issues += 1
        else:
            anomalies.append(f"{v}/{slug}: fingerprints is not a dict")
            schema_issues += 1

        # board_source_url validation
        bsu = data.get("board_source_url", "")
        if not bsu or (not bsu.startswith("http") and bsu != "N/A"):
            anomalies.append(f"{v}/{slug}: invalid board_source_url: {bsu}")
            schema_issues += 1

        # mpje leak check
        if "mpje_required" in data:
            anomalies.append(f"{v}/{slug}: leaked root-level mpje_required")
            schema_issues += 1

print(f"  Schema issues: {schema_issues}")

# ════════════════════════════════════════════════
# 5. HTML DIST FILES
# ════════════════════════════════════════════════
print("\n[5/8] HTML DIST FILES...")
total_html = 0
for v in VERTICALS:
    dist_dir = REPO / v / "dist"
    if not dist_dir.exists():
        continue
    html_files = list(dist_dir.glob("*.html"))
    html_count = len(html_files)
    total_html += html_count

    # Must have at least 51 state pages + 1 index
    check(html_count >= EXPECTED_STATES + 1,
          f"{v}: Expected ≥{EXPECTED_STATES + 1} HTML files, got {html_count}",
          level="WARN")

    # Spot-check: index.html exists
    check((dist_dir / "index.html").exists(), f"{v}/dist/index.html missing")

    # Spot-check: a few state pages exist
    for test_state in ["texas", "california", "new-york"]:
        suffix = v.replace("-pseo", "")
        if suffix == "dietitian":
            expected_html = dist_dir / f"{test_state}-{suffix}.html"
        else:
            expected_html = dist_dir / f"{test_state}-{suffix}.html"
        if not expected_html.exists():
            warnings.append(f"{v}: missing {expected_html.name}")

    # Check HTML is not empty / has content
    for hf in html_files[:3]:
        size = hf.stat().st_size
        if size < 1000:
            anomalies.append(f"{v}/{hf.name}: suspiciously small ({size} bytes)")

    stats[f"{v}_html"] = html_count

print(f"  Total HTML pages: {total_html}")

# ════════════════════════════════════════════════
# 6. SITEMAP & ROBOTS.TXT
# ════════════════════════════════════════════════
print("\n[6/8] SITEMAP & ROBOTS.TXT...")
for v in VERTICALS:
    dist_dir = REPO / v / "dist"
    if not dist_dir.exists():
        continue

    sm = dist_dir / "sitemap.xml"
    rb = dist_dir / "robots.txt"

    check(sm.exists(), f"{v}/dist/sitemap.xml missing")
    check(rb.exists(), f"{v}/dist/robots.txt missing")

    if sm.exists():
        sm_content = sm.read_text(encoding="utf-8")
        url_count = sm_content.count("<loc>")
        check(url_count >= EXPECTED_STATES,
              f"{v}: sitemap has {url_count} URLs (expected ≥{EXPECTED_STATES})")
        stats[f"{v}_sitemap_urls"] = url_count

    if rb.exists():
        rb_content = rb.read_text(encoding="utf-8")
        check("Sitemap:" in rb_content, f"{v}: robots.txt missing Sitemap: directive")
        check("Disallow" not in rb_content or "Disallow: " in rb_content,
              f"{v}: robots.txt may be blocking crawlers", level="WARN")

print("  ✓ Sitemap/robots checks complete")

# ════════════════════════════════════════════════
# 7. SEO META TAG SPOT CHECK
# ════════════════════════════════════════════════
print("\n[7/8] SEO META TAG SPOT CHECK...")
seo_checked = 0
for v in VERTICALS:
    dist_dir = REPO / v / "dist"
    test_file = None
    for candidate in ["texas", "california", "florida"]:
        suffix = v.replace("-pseo", "")
        f = dist_dir / f"{candidate}-{suffix}.html"
        if f.exists():
            test_file = f
            break

    if not test_file:
        warnings.append(f"{v}: no test HTML file found for SEO check")
        continue

    html = test_file.read_text(encoding="utf-8")
    seo_checked += 1

    check("<title>" in html, f"{v}/{test_file.name}: missing <title> tag")
    check('name="description"' in html, f"{v}/{test_file.name}: missing meta description")
    check("<h1" in html, f"{v}/{test_file.name}: missing <h1> tag")
    check("</html>" in html, f"{v}/{test_file.name}: HTML not properly closed")

print(f"  Spot-checked {seo_checked} files")

# ════════════════════════════════════════════════
# 8. CROSS-VERTICAL DATA CONSISTENCY
# ════════════════════════════════════════════════
print("\n[8/8] CROSS-VERTICAL CONSISTENCY...")

# Check that every vertical has the same set of state slugs
state_sets = {}
for v in VERTICALS:
    json_dir = REPO / v / "database" / "json"
    if not json_dir.exists():
        continue
    slugs = set()
    for f in json_dir.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        slugs.add(data.get("state_slug", ""))
    state_sets[v] = slugs

if state_sets:
    reference = state_sets.get("dietitian-pseo", set())
    for v, slugs in state_sets.items():
        if v == "dietitian-pseo":
            continue
        diff = reference.symmetric_difference(slugs)
        if diff:
            warnings.append(f"{v}: state slug mismatch with dietitian: {diff}")

print("  ✓ Cross-vertical checks complete")

# ════════════════════════════════════════════════
# FINAL REPORT
# ════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  AUDIT RESULTS")
print("=" * 70)

print(f"\n  Verticals:         {len(VERTICALS)}")
print(f"  JSON files:        {total_json}")
print(f"  HTML pages:        {total_html}")
print(f"  PENDING fields:    {pending_total}")
print(f"  Schema issues:     {schema_issues}")

if anomalies:
    print(f"\n  ❌ {len(anomalies)} ERRORS:")
    for a in anomalies:
        print(f"     • {a}")
else:
    print(f"\n  ✅ ZERO ERRORS")

if warnings:
    print(f"\n  ⚠️  {len(warnings)} WARNINGS:")
    for w in warnings:
        print(f"     • {w}")
else:
    print(f"\n  ✅ ZERO WARNINGS")

if not anomalies and not warnings:
    print(f"\n  🚀 ALL CLEAR — READY TO DEPLOY")
elif not anomalies:
    print(f"\n  🟡 DEPLOY OK (warnings only, no blockers)")
else:
    print(f"\n  🛑 FIX ERRORS BEFORE DEPLOYING")

print("=" * 70)
