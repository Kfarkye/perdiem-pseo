"""Shared builder for non-pharm specialty verticals.

This keeps per-vertical `python3 build.py` entrypoints stable while removing
copy-pasted builder logic across specialty folders.
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from reciprocity_index_builder import render_index
from site_linking import (
    build_nearby_state_links,
    build_same_state_specialties,
    load_vertical_catalog,
)


STATE_NAME_TO_ABBR = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def build_vertical(vertical_root: Path) -> None:
    root = vertical_root.resolve()
    repo_root = root.parent

    images_file = repo_root / "state_images.json"
    state_images = json.loads(images_file.read_text(encoding="utf-8")) if images_file.exists() else {}

    sys.path.insert(0, str(repo_root))

    json_dir = root / "database" / "json"
    dist_dir = root / "dist"
    templates_dir = root / "src" / "templates"
    content_dir = root / "content"
    canonical_host = "https://www.statelicensingreference.com"
    today = datetime.now().strftime("%Y-%m-%d")
    vertical_slug = root.name.replace("-pseo", "")
    css_hash = "0"

    dist_dir.mkdir(exist_ok=True)

    profiles = json.loads((repo_root / "vertical_profiles.json").read_text(encoding="utf-8"))
    vertical_catalog = load_vertical_catalog(repo_root)
    profile = profiles["verticals"][vertical_slug]
    specialty_path = profile.get("slug", vertical_slug)
    specialty_index_url = f"{canonical_host}/{specialty_path}"
    suppress_compact_ui = vertical_slug == "dietitian"

    env = Environment(loader=FileSystemLoader(templates_dir), undefined=StrictUndefined, autoescape=False)
    template = env.get_template("state-hub.html")

    tier2_files = {f.name: f for f in content_dir.glob("*.html")} if content_dir.exists() else {}
    states_manifest = []
    urls = []

    for json_file in sorted(json_dir.glob("*.json")):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        default_slug = data["state_slug"] if data["state_slug"].endswith(f"-{vertical_slug}") else f"{data['state_slug']}-{vertical_slug}"
        slug_value = data.get("slug") or default_slug
        out_name = f"{slug_value}.html"
        out_path = dist_dir / out_name

        if out_name in tier2_files:
            shutil.copyfile(tier2_files[out_name], out_path)
        else:
            state_abbr = data.get("reciprocity", {}).get("state_abbr")
            abbr = state_abbr or STATE_NAME_TO_ABBR.get(data["state_name"], "") or data["state_slug"][:2].upper()
            hero_img = state_images.get(abbr, {})
            out_path.write_text(
                template.render(
                    **data,
                    site_domain=canonical_host,
                    hero_image_url=hero_img.get("url", ""),
                    hero_image_alt=hero_img.get("alt", ""),
                    same_state_specialties=build_same_state_specialties(
                        state_slug=data["state_slug"],
                        current_vertical_slug=vertical_slug,
                        vertical_catalog=vertical_catalog,
                    ),
                    nearby_state_links=build_nearby_state_links(
                        state_name=data["state_name"],
                        current_vertical_slug=vertical_slug,
                    ),
                ),
                encoding="utf-8",
            )

        processing_time = data["reciprocity"].get("processing_time", "TBD")
        requires_psv = data["reciprocity"].get("requires_psv", False)
        fee = data["reciprocity"].get("endorsement_fee", 0)

        states_manifest.append(
            {
                "name": data["state_name"],
                "slug": slug_value,
                "last_updated": data.get("last_updated", today),
                "compact_label": data["reciprocity"].get("compact_name") or "Endorsement only",
                "state_is_member": data["reciprocity"]["state_is_member"],
                "endorsement_fee": fee,
                "processing_time": processing_time,
                "processing_tier": data["reciprocity"]["processing_tier"],
                "license_required": data["reciprocity"].get("license_required", True),
                "fingerprint_required": data["reciprocity"].get("fingerprint_required", False),
                "jurisprudence_required": data["reciprocity"].get("jurisprudence_required", False),
                "requires_psv": requires_psv,
            }
        )
        urls.append(
            f"  <url><loc>{canonical_host}/{slug_value}</loc><lastmod>{data.get('last_updated', today)}</lastmod><priority>0.8</priority></url>"
        )

    index_html = render_index(
        domain=specialty_index_url,
        profile=profile,
        states_manifest=states_manifest,
        css_hash=css_hash,
        today=today,
        suppress_compact_ui=suppress_compact_ui,
    )
    (dist_dir / "index.html").write_text(index_html, encoding="utf-8")

    robots_txt = "User-agent: *\nAllow: /\n\nSitemap: " + canonical_host + "/sitemap.xml\n"
    (dist_dir / "robots.txt").write_text(robots_txt, encoding="utf-8")

    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{specialty_index_url}</loc><lastmod>{today}</lastmod><priority>1.0</priority></url>\n"
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (dist_dir / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")

    print(f"Built {len(states_manifest)} pages for {vertical_slug}")
