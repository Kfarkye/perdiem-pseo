#!/usr/bin/env python3
"""Final approval audit anchored to a single root-dist deploy path.

This gate enforces:
1) One source input path (vertical JSON records)
2) One production output path (root dist/)
3) One HTML/API contract (dist/{slug}.html + dist/api/{slug}.json)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
PROFILES_PATH = REPO / "vertical_profiles.json"
VERCEL_PATH = REPO / "vercel.json"
FIREBASE_PATH = REPO / "firebase.json"
FIREBASERC_PATH = REPO / ".firebaserc"
DEPLOY_CHECKLIST_PATH = REPO / "DEPLOY_CHECKLIST_ROOT_DIST.md"

DIST_DIR = REPO / "dist"
API_DIR = DIST_DIR / "api"
CANONICAL_HOST = "https://www.statelicensingreference.com"

errors: list[str] = []
warnings: list[str] = []
passes = 0


def ok(_: str) -> None:
    global passes
    passes += 1


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
        rest = href.split("://", 1)[1]
        path = "/" + rest.split("/", 1)[1] if "/" in rest else "/"
    else:
        path = href
    return path.split("?", 1)[0].split("#", 1)[0].strip("/")


def load_profiles() -> list[str]:
    if not PROFILES_PATH.exists():
        fail("vertical_profiles.json missing")
        return []

    profiles = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    deployed = list(profiles.get("_meta", {}).get("deployed_verticals", []))
    if not deployed:
        fail("No deployed_verticals in vertical_profiles.json")
    return deployed


def gate_source_records(deployed: list[str]) -> list[tuple[str, str, Path, dict]]:
    print("\n[1/6] Source record schema + slug uniqueness")
    required_keys = [
        "state_slug",
        "state_name",
        "profession_name",
        "seo",
        "board",
        "quick_facts",
        "fees_endorsement",
        "reciprocity",
    ]
    records: list[tuple[str, str, Path, dict]] = []
    seen_slugs: set[str] = set()

    for vertical_slug in deployed:
        vdir = REPO / f"{vertical_slug}-pseo"
        json_dir = vdir / "database" / "json"

        if not vdir.exists():
            fail(f"Missing vertical directory: {vdir}")
            continue
        if not json_dir.exists():
            fail(f"Missing JSON directory: {json_dir}")
            continue

        files = sorted(json_dir.glob("*.json"))
        if len(files) != 51:
            warn(f"{vertical_slug}: expected 51 JSON files, found {len(files)}")

        for json_file in files:
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                fail(f"JSON parse error in {json_file}: {exc}")
                continue

            for key in required_keys:
                if key not in data:
                    fail(f"{json_file}: missing key '{key}'")

            slug_value = expected_slug(data, vertical_slug)
            if slug_value in seen_slugs:
                fail(f"Duplicate slug generated: {slug_value}")
            seen_slugs.add(slug_value)
            records.append((vertical_slug, slug_value, json_file, data))

    print(f"  records={len(records)} unique_slugs={len(seen_slugs)}")
    if records:
        ok("source records loaded")
    return records


def gate_dist_contract(deployed: list[str], records: list[tuple[str, str, Path, dict]]) -> None:
    print("\n[2/6] Root dist HTML/API contract")
    if not DIST_DIR.exists():
        fail(f"Root dist missing: {DIST_DIR}")
        return
    if not API_DIR.exists():
        fail(f"Root dist api missing: {API_DIR}")
        return

    if not (DIST_DIR / "index.html").exists():
        fail("Missing root portal page: dist/index.html")

    for vertical_slug in deployed:
        hub = DIST_DIR / f"{vertical_slug}.html"
        if not hub.exists():
            fail(f"Missing specialty hub: {hub}")

    required_api_keys = {
        "@context",
        "@type",
        "@id",
        "identifier",
        "name",
        "url",
        "provider",
        "areaServed",
        "offers",
        "processingTime",
        "mainEntity",
        "sourceMetadata",
    }

    for _, slug_value, _, _ in records:
        html_path = DIST_DIR / f"{slug_value}.html"
        api_path = API_DIR / f"{slug_value}.json"

        if not html_path.exists():
            fail(f"Missing state HTML: {html_path}")
            continue
        if not api_path.exists():
            fail(f"Missing state API: {api_path}")
            continue

        html = html_path.read_text(encoding="utf-8", errors="ignore")
        canonical_slug = canonical_slug_from_html(html)
        if canonical_slug is None:
            fail(f"{html_path}: canonical link missing")
        elif canonical_slug != slug_value:
            fail(f"{html_path}: canonical slug '{canonical_slug}' != '{slug_value}'")

        expected_alt = f'/api/{slug_value}.json'
        if expected_alt not in html:
            warn(f"{html_path}: missing alternate API link {expected_alt}")

        try:
            payload = json.loads(api_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"{api_path}: invalid JSON ({exc})")
            continue

        missing_keys = sorted(required_api_keys - payload.keys())
        if missing_keys:
            fail(f"{api_path}: missing API keys {missing_keys}")

        expected_url = f"{CANONICAL_HOST}/{slug_value}"
        if payload.get("@type") != "GovernmentService":
            fail(f"{api_path}: @type must be GovernmentService")
        if payload.get("identifier") != slug_value:
            fail(f"{api_path}: identifier mismatch ({payload.get('identifier')} != {slug_value})")
        if payload.get("@id") != expected_url or payload.get("url") != expected_url:
            fail(f"{api_path}: @id/url mismatch expected {expected_url}")

    html_count = len(list(DIST_DIR.glob("*.html")))
    api_count = len(list(API_DIR.glob("*.json")))
    print(f"  html_count={html_count} api_count={api_count}")
    if html_count < len(records) + len(deployed) + 1:
        fail("Root dist HTML count lower than expected (states + hubs + portal)")
    if api_count != len(records):
        fail(f"Root dist API count {api_count} != state record count {len(records)}")
    if not errors:
        ok("root dist contract holds")


def gate_sitemap_and_robots(deployed: list[str], records: list[tuple[str, str, Path, dict]]) -> None:
    print("\n[3/6] Sitemap + robots consistency")
    robots = DIST_DIR / "robots.txt"
    sitemap = DIST_DIR / "sitemap.xml"

    if not robots.exists():
        fail("Missing dist/robots.txt")
    if not sitemap.exists():
        fail("Missing dist/sitemap.xml")
        return

    if robots.exists():
        robots_text = robots.read_text(encoding="utf-8")
        expected = f"Sitemap: {CANONICAL_HOST}/sitemap.xml"
        if expected not in robots_text:
            fail("robots.txt missing canonical sitemap directive")

    locs = set(re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8")))
    expected_urls = {f"{CANONICAL_HOST}/"}
    expected_urls.update({f"{CANONICAL_HOST}/{slug}" for slug in deployed})
    expected_urls.update({f"{CANONICAL_HOST}/{slug_value}" for _, slug_value, _, _ in records})

    missing = sorted(expected_urls - locs)
    extra = sorted(locs - expected_urls)
    if missing:
        fail(f"sitemap missing {len(missing)} expected URLs (sample: {missing[:5]})")
    if extra:
        warn(f"sitemap has {len(extra)} extra URLs (sample: {extra[:5]})")
    if not missing:
        ok("sitemap covers root truth")


def gate_trust_regression_guards() -> None:
    print("\n[4/6] Trust regression guards")
    banned_phrase = "varies, often around $100 to $200"
    pt_hits = 0
    for pt_html in sorted(DIST_DIR.glob("*-pt.html")):
        text = pt_html.read_text(encoding="utf-8", errors="ignore")
        if banned_phrase in text:
            pt_hits += 1
            fail(f"{pt_html}: contains banned generic PT fee phrase")

    canonical_license_hits = 0
    for html_path in sorted(DIST_DIR.glob("*.html")):
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'<link rel="canonical" href="[^"]+-license"', text):
            canonical_license_hits += 1
            fail(f"{html_path}: canonical contains '-license' slug residue")

    print(f"  pt_phrase_hits={pt_hits} canonical_license_hits={canonical_license_hits}")
    if pt_hits == 0 and canonical_license_hits == 0:
        ok("trust guards clean")


def gate_deploy_config_transition() -> None:
    print("\n[5/6] Deploy config + legacy API transition")
    start_errors = len(errors)
    if not VERCEL_PATH.exists():
        fail("Missing root vercel.json")
        return

    vercel = json.loads(VERCEL_PATH.read_text(encoding="utf-8"))
    if vercel.get("outputDirectory") != "dist":
        fail("vercel.json outputDirectory must be 'dist'")

    build_command = str(vercel.get("buildCommand", ""))
    if "build_unified.py" not in build_command:
        fail("vercel.json buildCommand must call build_unified.py")

    rewrites = vercel.get("rewrites", [])
    required_aliases = [
        ("/api/v1/:slug.json", "/api/:slug.json"),
        ("/:vertical-pseo/api/:slug.json", "/api/:slug.json"),
    ]
    for source, destination in required_aliases:
        found = any(
            isinstance(rw, dict)
            and rw.get("source") == source
            and rw.get("destination") == destination
            for rw in rewrites
        )
        if not found:
            fail(
                f"vercel.json missing legacy API alias rewrite: {source} -> {destination}"
            )

    vertical_vercels = sorted(str(path.relative_to(REPO)) for path in REPO.glob("*-pseo/vercel.json"))
    if vertical_vercels:
        warn(
            "Per-vertical vercel.json files still exist (legacy paths). Root deploy uses only /vercel.json. "
            f"Found {len(vertical_vercels)} files."
        )

    if not DEPLOY_CHECKLIST_PATH.exists():
        fail(f"Missing deploy checklist: {DEPLOY_CHECKLIST_PATH.name}")

    if not FIREBASE_PATH.exists():
        fail("Missing root firebase.json")
    else:
        firebase = json.loads(FIREBASE_PATH.read_text(encoding="utf-8"))
        hosting = firebase.get("hosting", {})
        if not isinstance(hosting, dict):
            fail("firebase.json hosting config must be an object")
        else:
            if hosting.get("public") != "dist":
                fail("firebase.json hosting.public must be 'dist'")
            if hosting.get("site") != "state-licensing-ref":
                fail("firebase.json hosting.site must be 'state-licensing-ref'")
            if hosting.get("cleanUrls") is not True:
                fail("firebase.json hosting.cleanUrls must be true")

            redirects = hosting.get("redirects", [])
            required_aliases = [
                ("/api/v1/:slug.json", "/api/:slug.json"),
                ("/:vertical-pseo/api/:slug.json", "/api/:slug.json"),
            ]
            for source, destination in required_aliases:
                found = any(
                    isinstance(rule, dict)
                    and rule.get("source") == source
                    and rule.get("destination") == destination
                    for rule in redirects
                )
                if not found:
                    fail(
                        f"firebase.json missing legacy API alias redirect: {source} -> {destination}"
                    )

    if not FIREBASERC_PATH.exists():
        fail("Missing root .firebaserc")
    else:
        firebaserc = json.loads(FIREBASERC_PATH.read_text(encoding="utf-8"))
        project_default = firebaserc.get("projects", {}).get("default")
        if project_default != "state-licensing-ref":
            fail(".firebaserc projects.default must be 'state-licensing-ref'")

    if len(errors) == start_errors:
        ok("deploy config enforces root dist")


def gate_api_slug_healthcheck(records: list[tuple[str, str, Path, dict]]) -> None:
    print("\n[6/6] API slug contract healthcheck")
    start_errors = len(errors)
    if not records:
        fail("No records loaded; cannot run API healthcheck")
        return

    sample_slugs = sorted({records[0][1], records[len(records) // 2][1], records[-1][1]})
    for slug_value in sample_slugs:
        api_path = API_DIR / f"{slug_value}.json"
        if not api_path.exists():
            fail(f"API healthcheck missing: {api_path}")
            continue
        payload = json.loads(api_path.read_text(encoding="utf-8"))
        provider_name = payload.get("provider", {}).get("name", "") if isinstance(payload.get("provider"), dict) else ""
        if not provider_name:
            warn(f"{api_path}: provider.name empty")
    if len(errors) == start_errors:
        ok("api healthcheck complete")


def main() -> None:
    print("=" * 72)
    print("  FINAL APPROVAL AUDIT — ROOT DIST SINGLE-TRUTH")
    print("=" * 72)
    print(f"Repo: {REPO}")

    deployed = load_profiles()
    records = gate_source_records(deployed)
    gate_dist_contract(deployed, records)
    gate_sitemap_and_robots(deployed, records)
    gate_trust_regression_guards()
    gate_deploy_config_transition()
    gate_api_slug_healthcheck(records)

    print("\n" + "=" * 72)
    print("  RESULTS")
    print("=" * 72)
    print(f"Gates passed: {passes}/6")
    print(f"Errors:       {len(errors)}")
    print(f"Warnings:     {len(warnings)}")

    if errors:
        print("\n❌ ERROR LIST")
        for msg in errors:
            print(f" - {msg}")
    if warnings:
        print("\n⚠️  WARNING LIST")
        for msg in warnings:
            print(f" - {msg}")

    if errors:
        print("\n🛑 DEPLOYMENT BLOCKED")
        sys.exit(1)

    print("\n✅ APPROVED FOR DEPLOYMENT (root-dist truth path)")
    if warnings:
        print("🟡 APPROVED WITH WARNINGS")


if __name__ == "__main__":
    main()
