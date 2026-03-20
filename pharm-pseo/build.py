"""Programmatic SEO compiler with reciprocity-first state pages."""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
import sys

from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent

# Load shared state hero images.
IMAGES_FILE = ROOT.parent / "state_images.json"
STATE_IMAGES = json.loads(IMAGES_FILE.read_text(encoding="utf-8")) if IMAGES_FILE.exists() else {}

sys.path.insert(0, str(ROOT.parent))

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

JSON_DIR = ROOT / "database" / "json"
DIST_DIR = ROOT / "dist"
TEMPLATES_DIR = ROOT / "src" / "templates"
CONTENT_DIR = ROOT / "content"
CANONICAL_HOST = "https://www.statelicensingreference.com"
TODAY = datetime.now().strftime("%Y-%m-%d")
VERTICAL_SLUG = ROOT.name.replace("-pseo", "")
CSS_HASH = "0"

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


def format_fee_display(value: object) -> str:
    if isinstance(value, (int, float)):
        if float(value).is_integer():
            return f"${int(value)}"
        return f"${value:,.2f}"
    if isinstance(value, str):
        cleaned = value.replace("$", "").replace(",", "").strip()
        try:
            number = float(cleaned)
        except ValueError:
            return value
        if number.is_integer():
            return f"${int(number)}"
        return f"${number:,.2f}"
    return str(value)


DIST_DIR.mkdir(exist_ok=True)

profiles = json.loads((ROOT.parent / "vertical_profiles.json").read_text(encoding="utf-8"))
VERTICAL_CATALOG = load_vertical_catalog(ROOT.parent)
profile = profiles["verticals"][VERTICAL_SLUG]
specialty_path = profile.get("slug", VERTICAL_SLUG)
specialty_index_url = f"{CANONICAL_HOST}/{specialty_path}"
suppress_compact_ui = VERTICAL_SLUG == "dietitian"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), undefined=StrictUndefined, autoescape=False)
template = env.get_template("state-hub.html")

tier2_files = {f.name: f for f in CONTENT_DIR.glob("*.html")} if CONTENT_DIR.exists() else {}
states_manifest = []
urls = []
records = [
    (json_file, json.loads(json_file.read_text(encoding="utf-8")))
    for json_file in sorted(JSON_DIR.glob("*.json"))
]

verify_fee_and_timing_with_board = VERTICAL_SLUG == "pharm"
db_rows = fetch_supabase_rows(DB_SPECIALTY_BY_VERTICAL[VERTICAL_SLUG]) if VERTICAL_SLUG in DB_SPECIALTY_BY_VERTICAL else {}

for json_file, data in records:
    default_slug = data["state_slug"] if data["state_slug"].endswith(f"-{VERTICAL_SLUG}") else f"{data['state_slug']}-{VERTICAL_SLUG}"
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
                current_vertical_slug=VERTICAL_SLUG,
                vertical_catalog=VERTICAL_CATALOG,
            ),
            "nearby_state_links": build_nearby_state_links(
                state_name=data["state_name"],
                current_vertical_slug=VERTICAL_SLUG,
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
    requires_psv = data["reciprocity"].get("requires_psv", False)
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
            "requires_psv": requires_psv,
            "board_fee_verified": fee_verified,
            "board_timeline_verified": timeline_verified,
            "fee_display": fee_display,
            "time_display": time_display,
        }
    )
    urls.append(
        f"  <url><loc>{CANONICAL_HOST}/{slug_value}</loc><lastmod>{data.get('last_updated', TODAY)}</lastmod><priority>0.8</priority></url>"
    )

index_html = render_index(
    domain=specialty_index_url,
    profile=profile,
    states_manifest=states_manifest,
    css_hash=CSS_HASH,
    today=TODAY,
    suppress_compact_ui=suppress_compact_ui,
    verify_fee_and_timing_with_board=verify_fee_and_timing_with_board,
)
(DIST_DIR / "index.html").write_text(index_html, encoding="utf-8")

robots_txt = "User-agent: *\nAllow: /\n\nSitemap: " + CANONICAL_HOST + "/sitemap.xml\n"
(DIST_DIR / "robots.txt").write_text(robots_txt, encoding="utf-8")

sitemap_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f"  <url><loc>{specialty_index_url}</loc><lastmod>{TODAY}</lastmod><priority>1.0</priority></url>\n"
    + "\n".join(urls)
    + "\n</urlset>\n"
)
(DIST_DIR / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")

print(f"Built {len(states_manifest)} pages for {VERTICAL_SLUG}")
