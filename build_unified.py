#!/usr/bin/env python3
"""Build a single-host static site for www.statelicensingreference.com."""
from __future__ import annotations

import json
import os
import runpy
import shutil
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from build_shared import STATE_NAME_TO_ABBR, format_fee_display
from consumer_db_overrides import (
    DB_SPECIALTY_BY_VERTICAL,
    apply_consumer_db_overrides,
    fetch_supabase_rows,
)
from reciprocity_index_builder import render_index
from site_linking import (
    build_nearby_state_links,
    build_same_state_specialties,
    load_vertical_catalog,
)

REPO = Path(__file__).resolve().parent
DIST_DIR = REPO / "dist"
PORTAL_DIR = REPO / "portal"
CANONICAL_HOST = "https://www.statelicensingreference.com"
TODAY = datetime.now().strftime("%Y-%m-%d")
IMAGES_FILE = REPO / "state_images.json"
STATE_IMAGES = json.loads(IMAGES_FILE.read_text(encoding="utf-8")) if IMAGES_FILE.exists() else {}
SHARED_TEMPLATES_DIR = REPO / "shared_templates"
VERTICAL_CATALOG = load_vertical_catalog(REPO)


def run_build(cwd: Path, script: str) -> None:
    previous_cwd = Path.cwd()
    try:
        os.chdir(cwd)
        runpy.run_path(str(cwd / script), run_name="__main__")
    finally:
        os.chdir(previous_cwd)


def clean_dist() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)


def copy_portal_assets() -> None:
    portal_dist = PORTAL_DIR / "dist"
    shutil.copyfile(portal_dist / "index.html", DIST_DIR / "index.html")
    favicon = portal_dist / "favicon.svg"
    if favicon.exists():
        shutil.copyfile(favicon, DIST_DIR / "favicon.svg")
    social_card = portal_dist / "social-card.svg"
    if social_card.exists():
        shutil.copyfile(social_card, DIST_DIR / "social-card.svg")


def build_verticals() -> tuple[list[str], list[str]]:
    profiles = json.loads((REPO / "vertical_profiles.json").read_text(encoding="utf-8"))
    verticals = profiles["_meta"]["deployed_verticals"]
    profile_map = profiles["verticals"]
    state_urls: list[str] = []
    specialty_urls: list[str] = []

    template_env = Environment(
        loader=FileSystemLoader(SHARED_TEMPLATES_DIR),
        undefined=StrictUndefined,
        autoescape=False,
    )
    template = template_env.get_template("state-hub.html")

    for slug in verticals:
        vertical_dir = REPO / f"{slug}-pseo"
        if not vertical_dir.exists() and slug == "rrt":
            vertical_dir = REPO / "rrt-pseo"

        if slug == "cna":
            run_build(vertical_dir, "build_v2.py")
            
            dist_v2 = vertical_dir / "dist-v2"
            for f in dist_v2.iterdir():
                if f.is_file():
                    if f.name in ["robots.txt", "sitemap.xml"]:
                        continue
                    out_name = "cna.html" if f.name == "index.html" else f.name
                    shutil.copyfile(f, DIST_DIR / out_name)
                    
            for json_file in sorted((vertical_dir / "database" / "v2").glob("*.json")):
                data = json.loads(json_file.read_text(encoding="utf-8"))
                state_urls.append(f"{CANONICAL_HOST}/{data['routing']['canonical_slug']}")
                
            specialty_urls.append(f"{CANONICAL_HOST}/cna")
            continue

        json_dir = vertical_dir / "database" / "json"
        content_dir = vertical_dir / "content"
        tier2_files = {f.name: f for f in content_dir.glob("*.html")} if content_dir.exists() else {}
        states_manifest = []
        records = [
            (json_file, json.loads(json_file.read_text(encoding="utf-8")))
            for json_file in sorted(json_dir.glob("*.json"))
        ]
        verify_fee_and_timing_with_board = slug == "pharm"
        db_rows = fetch_supabase_rows(DB_SPECIALTY_BY_VERTICAL[slug]) if slug in DB_SPECIALTY_BY_VERTICAL else {}

        for json_file, data in records:
            vertical_slug = slug
            default_slug = data["state_slug"] if data["state_slug"].endswith(f"-{vertical_slug}") else f"{data['state_slug']}-{vertical_slug}"
            slug_value = data.get("slug") or default_slug
            out_name = f"{slug_value}.html"
            out_path = DIST_DIR / out_name
            state_abbr = data.get("reciprocity", {}).get("state_abbr")
            abbr = state_abbr or STATE_NAME_TO_ABBR.get(data["state_name"], "") or data["state_slug"][:2].upper()

            if abbr in db_rows:
                data = apply_consumer_db_overrides(data, db_rows[abbr])

            if out_name in tier2_files:
                shutil.copyfile(tier2_files[out_name], out_path)
            else:
                hero_img = STATE_IMAGES.get(abbr, {})
                render_data = {
                    **data,
                    "site_domain": CANONICAL_HOST,
                    "hero_image_url": hero_img.get("url", ""),
                    "hero_image_alt": hero_img.get("alt", ""),
                    "same_state_specialties": build_same_state_specialties(
                        state_slug=data["state_slug"],
                        current_vertical_slug=slug,
                        vertical_catalog=VERTICAL_CATALOG,
                    ),
                    "nearby_state_links": build_nearby_state_links(
                        state_name=data["state_name"],
                        current_vertical_slug=slug,
                    ),
                    "board_verification": data.get("board_verification", {}),
                    "board_verification_sources": data.get("board_verification_sources", {}),
                    "verify_fee_and_timing_with_board": verify_fee_and_timing_with_board,
                }
                out_path.write_text(
                    template.render(**render_data),
                    encoding="utf-8",
                )

            processing_time = data["reciprocity"].get("processing_time", "TBD")
            fee = data["reciprocity"].get("endorsement_fee", 0)
            board_verification = data.get("board_verification", {})
            fee_verified = bool(board_verification.get("fee_verified"))
            timeline_verified = bool(board_verification.get("timeline_verified"))

            if data["reciprocity"].get("license_required", True) and fee_verified:
                if isinstance(fee, (int, float)):
                    fee_display = format_fee_display(fee)
                else:
                    fee_display = str(fee)
            elif data["reciprocity"].get("license_required", True):
                fee_display = "See board"
            else:
                fee_display = "—"

            if not data["reciprocity"].get("license_required", True):
                time_display = "No state application"
            elif timeline_verified:
                time_display = processing_time
            else:
                time_display = "See board"

            states_manifest.append(
                {
                    "name": data["state_name"],
                    "slug": slug_value,
                    "last_updated": data.get("last_updated", TODAY),
                    "compact_label": data["reciprocity"].get("compact_name") or "Endorsement only",
                    "state_is_member": data["reciprocity"]["state_is_member"],
                    "endorsement_fee": fee,
                    "processing_time": processing_time,
                    "processing_tier": data["reciprocity"]["processing_tier"],
                    "license_required": data["reciprocity"].get("license_required", True),
                    "fingerprint_required": data["reciprocity"].get("fingerprint_required", False),
                    "jurisprudence_required": data["reciprocity"].get("jurisprudence_required", False),
                    "requires_psv": data["reciprocity"].get("requires_psv", False),
                    "board_fee_verified": fee_verified,
                    "board_timeline_verified": timeline_verified,
                    "fee_display": fee_display,
                    "time_display": time_display,
                }
            )
            state_urls.append(f"{CANONICAL_HOST}/{slug_value}")

        specialty_index_url = f"{CANONICAL_HOST}/{slug}"
        specialty_urls.append(specialty_index_url)
        index_html = render_index(
            domain=specialty_index_url,
            profile=profile_map[slug],
            states_manifest=states_manifest,
            css_hash="0",
            today=TODAY,
            suppress_compact_ui=(slug == "dietitian"),
            verify_fee_and_timing_with_board=verify_fee_and_timing_with_board,
        )
        (DIST_DIR / f"{slug}.html").write_text(index_html, encoding="utf-8")

    return specialty_urls, state_urls


def write_root_artifacts(specialty_urls: list[str], state_urls: list[str]) -> None:
    robots = f"User-agent: *\nAllow: /\n\nSitemap: {CANONICAL_HOST}/sitemap.xml\n"
    (DIST_DIR / "robots.txt").write_text(robots, encoding="utf-8")

    urls = [
        f"  <url><loc>{CANONICAL_HOST}/</loc><lastmod>{TODAY}</lastmod><priority>1.0</priority></url>"
    ]
    urls.extend(
        f"  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod><priority>0.9</priority></url>"
        for url in specialty_urls
    )
    urls.extend(
        f"  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod><priority>0.8</priority></url>"
        for url in state_urls
    )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (DIST_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def main() -> None:
    run_build(PORTAL_DIR, "build_portal.py")
    clean_dist()
    copy_portal_assets()
    specialty_urls, state_urls = build_verticals()
    write_root_artifacts(specialty_urls, state_urls)
    print(f"Unified build complete: {len(specialty_urls)} specialty pages, {len(state_urls)} state pages")


if __name__ == "__main__":
    main()
