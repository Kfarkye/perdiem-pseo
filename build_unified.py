#!/usr/bin/env python3
"""Build a single-host static site for www.statelicensingreference.com."""
from __future__ import annotations

import json
import os
import runpy
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from build_shared import STATE_NAME_TO_ABBR, format_fee_display
from consumer_db_overrides import (
    DB_SPECIALTY_BY_VERTICAL,
    apply_consumer_db_overrides,
    fetch_supabase_rows,
)
from page_packet import build_route_context, build_page_packet
from reciprocity_index_builder import render_index
from site_linking import (
    build_nearby_state_links,
    build_same_state_specialties,
    load_vertical_catalog,
)

REPO = Path(__file__).resolve().parent
DIST_DIR = REPO / "dist"
API_DIR = DIST_DIR / "api"
PORTAL_DIR = REPO / "portal"
CANONICAL_HOST = "https://www.statelicensingreference.com"
TODAY = datetime.now().strftime("%Y-%m-%d")
IMAGES_FILE = REPO / "state_images.json"
STATE_IMAGES = json.loads(IMAGES_FILE.read_text(encoding="utf-8")) if IMAGES_FILE.exists() else {}
SHARED_TEMPLATES_DIR = REPO / "shared_templates"
VERTICAL_CATALOG = load_vertical_catalog(REPO)


def _is_full_document_override(path: Path) -> bool:
    """Detect legacy full HTML documents in content/ overrides.

    Unified pages should render through shared_templates/state-hub.html.
    Legacy full-document overrides bypass the shared design system.
    """
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:512].lstrip().lower()
    except OSError:
        return False
    return head.startswith("<!doctype html") or head.startswith("<html")


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
    API_DIR.mkdir(parents=True, exist_ok=True)


def _parse_money(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("$", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def build_api_payload(*, data: dict[str, Any], slug_value: str) -> dict[str, Any]:
    state_name = data.get("state_name", "")
    profession_name = data.get("profession_name", "")
    canonical_url = f"{CANONICAL_HOST}/{slug_value}"

    board = data.get("board", {}) if isinstance(data.get("board"), dict) else {}
    quick_facts = data.get("quick_facts", {}) if isinstance(data.get("quick_facts"), dict) else {}
    fees_endorsement = data.get("fees_endorsement", {}) if isinstance(data.get("fees_endorsement"), dict) else {}
    reciprocity = data.get("reciprocity", {}) if isinstance(data.get("reciprocity"), dict) else {}
    compact = data.get("compact", {}) if isinstance(data.get("compact"), dict) else {}
    temp_license = data.get("temp_license", {}) if isinstance(data.get("temp_license"), dict) else {}
    fingerprints = data.get("fingerprints", {}) if isinstance(data.get("fingerprints"), dict) else {}

    title_term = (
        data.get("credential_type", {}).get("page_title_term")
        if isinstance(data.get("credential_type"), dict)
        else None
    ) or "License"
    service_name = f"{state_name} {profession_name} {title_term}".strip()

    app_fee_display = (
        fees_endorsement.get("app_fee")
        or quick_facts.get("total_fee")
        or reciprocity.get("endorsement_fee")
        or "See board"
    )
    renewal_fee_display = quick_facts.get("renewal_fee") or "See board"
    app_fee_num = _parse_money(app_fee_display)
    renewal_fee_num = _parse_money(renewal_fee_display)

    offers: list[dict[str, Any]] = []
    initial_offer: dict[str, Any] = {
        "@type": "Offer",
        "name": "Initial Application Fee",
        "description": str(app_fee_display),
    }
    if app_fee_num is not None:
        initial_offer["price"] = app_fee_num
        initial_offer["priceCurrency"] = "USD"
    offers.append(initial_offer)

    renewal_offer: dict[str, Any] = {
        "@type": "Offer",
        "name": "Renewal Fee",
        "description": str(renewal_fee_display),
    }
    if renewal_fee_num is not None:
        renewal_offer["price"] = renewal_fee_num
        renewal_offer["priceCurrency"] = "USD"
    offers.append(renewal_offer)

    payload: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "GovernmentService",
        "@id": canonical_url,
        "identifier": slug_value,
        "name": service_name,
        "description": data.get("seo", {}).get("description", "") if isinstance(data.get("seo"), dict) else "",
        "url": canonical_url,
        "provider": {
            "@type": "GovernmentOrganization",
            "name": board.get("name", "State Board"),
            "parentOrganization": board.get("parent_dept", ""),
            "url": board.get("url", ""),
            "telephone": board.get("phone", ""),
            "faxNumber": board.get("fax", ""),
            "email": board.get("email", ""),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": board.get("physical_address") or board.get("mailing_address") or "",
                "description": board.get("mailing_address", ""),
            },
        },
        "areaServed": {
            "@type": "State",
            "name": state_name,
        },
        "serviceType": "Professional License",
        "category": profession_name,
        "additionalType": data.get("credential_nomenclature", ""),
        "offers": offers,
        "processingTime": reciprocity.get("processing_time") or quick_facts.get("processing_time") or "See board",
        "licenseDuration": quick_facts.get("license_duration", ""),
        "renewalCycle": quick_facts.get("renewal_cycle", ""),
        "requiredDocuments": [
            {
                "name": doc.get("item", ""),
                "description": doc.get("detail", ""),
            }
            for doc in (data.get("documents") or [])
            if isinstance(doc, dict)
        ],
        "fingerprinting": fingerprints,
        "compactStatus": {
            "isCompactMember": bool(compact.get("is_compact_member", reciprocity.get("state_is_member", False))),
            "compactName": compact.get("compact_name") or reciprocity.get("compact_name") or "",
            "compactPrivilegeFee": compact.get("compact_privilege_fee", ""),
        },
        "temporaryLicense": {
            "available": bool(temp_license.get("available", reciprocity.get("temp_license_available", False))),
            "fee": temp_license.get("fee", "See board"),
            "processingTime": temp_license.get("processing_time", "See board"),
            "duration": temp_license.get("duration", "See board"),
        },
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq.get("question", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq.get("answer", ""),
                },
            }
            for faq in (data.get("faqs") or [])
            if isinstance(faq, dict)
        ],
        "sourceMetadata": {
            "lastUpdated": data.get("last_updated", TODAY),
            "lastVerifiedDate": data.get("last_verified_date") or data.get("last_updated", TODAY),
            "boardSourceUrl": data.get("board_source_url") or board.get("url", ""),
        },
    }
    return payload


def write_api_payload(*, data: dict[str, Any], slug_value: str) -> None:
    payload = build_api_payload(data=data, slug_value=slug_value)
    (API_DIR / f"{slug_value}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


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
            # ── ARCHITECTURE: object → route → packet → render ──

            # 1. Build route context (replaces ad-hoc slug inference)
            route = build_route_context(
                state_slug=data["state_slug"],
                profession_slug=slug,
                state_name=data.get("state_name", ""),
                state_abbr=data.get("reciprocity", {}).get("state_abbr", ""),
                slug_override=data.get("slug", ""),
            )
            slug_value = route.slug
            abbr = route.state_abbr
            out_name = f"{slug_value}.html"
            out_path = DIST_DIR / out_name

            # 2. Apply DB overrides to canonical object
            if abbr in db_rows:
                data = apply_consumer_db_overrides(data, db_rows[abbr])

            # 3. Render
            tier2_override = tier2_files.get(out_name)
            if tier2_override and not _is_full_document_override(tier2_override):
                shutil.copyfile(tier2_override, out_path)
            else:
                if tier2_override and _is_full_document_override(tier2_override):
                    print(f"Skipping legacy full-document override: {tier2_override}")
                # Build page packet (sole contract to template)
                packet = build_page_packet(
                    canonical_object=data,
                    route=route,
                    vertical_catalog=VERTICAL_CATALOG,
                    hero_image=STATE_IMAGES.get(abbr, {}),
                    verify_fee_and_timing_with_board=verify_fee_and_timing_with_board,
                )
                out_path.write_text(
                    template.render(**packet),
                    encoding="utf-8",
                )

            write_api_payload(data=data, slug_value=slug_value)

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
