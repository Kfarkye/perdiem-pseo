#!/usr/bin/env python3
"""Root-dist pre-deploy audit for statelicensingreference.com.

Source of truth model:
- Input: deployed vertical JSON records
- Output: root dist/*.html + root dist/api/*.json + root sitemap/robots
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
PROFILES_PATH = REPO / "vertical_profiles.json"
DIST_DIR = REPO / "dist"
API_DIR = DIST_DIR / "api"
CANONICAL_HOST = "https://www.statelicensingreference.com"

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def expected_slug(data: dict, vertical_slug: str) -> str:
    default_slug = (
        data["state_slug"]
        if data["state_slug"].endswith(f"-{vertical_slug}")
        else f"{data['state_slug']}-{vertical_slug}"
    )
    return data.get("slug") or default_slug


def canonical_slug_from_html(html: str) -> str | None:
    match = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if not match:
        return None
    href = match.group(1)
    if "://" in href:
        path = "/" + href.split("://", 1)[1].split("/", 1)[1] if "/" in href.split("://", 1)[1] else "/"
    else:
        path = href
    return path.split("?", 1)[0].split("#", 1)[0].strip("/")


print("=" * 72)
print("  PRE-DEPLOY AUDIT — ROOT DIST SOURCE OF TRUTH")
print("=" * 72)

if not PROFILES_PATH.exists():
    fail("vertical_profiles.json missing")
    print("\n❌ vertical_profiles.json missing")
    sys.exit(1)

profiles = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
deployed = list(profiles.get("_meta", {}).get("deployed_verticals", []))
if not deployed:
    fail("No deployed_verticals found in vertical_profiles.json")

print(f"\nDeployed verticals: {len(deployed)} -> {deployed}")

records: list[tuple[str, str, Path, dict]] = []
required_json_keys = [
    "state_slug",
    "state_name",
    "profession_name",
    "seo",
    "board",
    "quick_facts",
    "fees_endorsement",
    "reciprocity",
]

print("\n[1/6] JSON source records...")
for slug in deployed:
    vdir = REPO / f"{slug}-pseo"
    json_dir = vdir / "database" / "json"

    if not vdir.exists():
        fail(f"Missing vertical directory: {vdir}")
        continue
    if not json_dir.exists():
        fail(f"Missing JSON directory: {json_dir}")
        continue

    files = sorted(json_dir.glob("*.json"))
    if len(files) != 51:
        warn(f"{slug}: expected 51 JSON files, found {len(files)}")

    for json_file in files:
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"JSON parse error in {json_file}: {exc}")
            continue

        for key in required_json_keys:
            if key not in data:
                fail(f"{json_file}: missing key '{key}'")

        records.append((slug, expected_slug(data, slug), json_file, data))

print(f"  Collected records: {len(records)}")

print("\n[2/6] Root dist artifact checks...")
if not DIST_DIR.exists():
    fail(f"Root dist missing: {DIST_DIR}")
if not (DIST_DIR / "robots.txt").exists():
    fail("Root dist/robots.txt missing")
if not (DIST_DIR / "sitemap.xml").exists():
    fail("Root dist/sitemap.xml missing")
if not API_DIR.exists():
    fail("Root dist/api missing")

print("\n[3/6] HTML + API file parity checks...")
for vertical_slug, slug_value, json_file, _ in records:
    html_path = DIST_DIR / f"{slug_value}.html"
    api_path = API_DIR / f"{slug_value}.json"

    if not html_path.exists():
        fail(f"Missing state HTML: {html_path}")
        continue
    if not api_path.exists():
        fail(f"Missing state API JSON: {api_path}")

    html = html_path.read_text(encoding="utf-8", errors="ignore")
    canonical_slug = canonical_slug_from_html(html)
    if canonical_slug is None:
        fail(f"{html_path}: canonical link missing")
    elif canonical_slug != slug_value:
        fail(f"{html_path}: canonical slug '{canonical_slug}' != '{slug_value}'")

    expected_alt = f'/api/{slug_value}.json'
    if expected_alt not in html:
        warn(f"{html_path}: missing alternate API link {expected_alt}")

print("\n[4/6] Specialty hub checks...")
for slug in deployed:
    hub_path = DIST_DIR / f"{slug}.html"
    if not hub_path.exists():
        fail(f"Missing specialty hub page: {hub_path}")

if not (DIST_DIR / "index.html").exists():
    fail("Missing portal page: dist/index.html")

print("\n[5/6] Sitemap coverage checks...")
if (DIST_DIR / "sitemap.xml").exists():
    sm_text = (DIST_DIR / "sitemap.xml").read_text(encoding="utf-8")
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm_text))

    expected_urls = {f"{CANONICAL_HOST}/"}
    expected_urls.update({f"{CANONICAL_HOST}/{slug}" for slug in deployed})
    expected_urls.update({f"{CANONICAL_HOST}/{slug_value}" for _, slug_value, _, _ in records})

    missing = sorted(expected_urls - locs)
    extra = sorted(locs - expected_urls)

    if missing:
        fail(f"Sitemap missing {len(missing)} expected URLs (sample: {missing[:5]})")
    if extra:
        warn(f"Sitemap has {len(extra)} extra URLs (sample: {extra[:5]})")

print("\n[6/6] PT trust phrase guard...")
for pt_html in sorted(DIST_DIR.glob("*-pt.html")):
    html = pt_html.read_text(encoding="utf-8", errors="ignore")
    if "varies, often around $100 to $200" in html:
        fail(f"{pt_html}: contains banned generic PT fee phrase")

print("\n" + "=" * 72)
print("  RESULTS")
print("=" * 72)
print(f"Errors:   {len(errors)}")
print(f"Warnings: {len(warnings)}")

if errors:
    print("\n❌ ERROR LIST")
    for msg in errors:
        print(f" - {msg}")

if warnings:
    print("\n⚠️  WARNING LIST")
    for msg in warnings:
        print(f" - {msg}")

if errors:
    print("\n🛑 BLOCKED: fix errors before deploy")
    sys.exit(1)

print("\n✅ PASS: root dist is consistent with source records")
if warnings:
    print("🟡 PASS WITH WARNINGS")
