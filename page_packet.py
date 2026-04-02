"""Page Packet Builder — the formal contract between data and UI.

Architecture: object → route → packet → render

This module implements the packet layer. A packet is the SOLE input to the
renderer/template.  Nothing outside this module should compute display values,
resolve slugs, or build cross-links.

Usage (build_unified.py):
    from page_packet import build_route_context, build_page_packet

    route = build_route_context(state_slug="arkansas", profession_slug="dietitian")
    packet = build_page_packet(canonical_object=data, route=route, ...)
    template.render(**packet)

The template should ONLY read fields from the packet dict.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

from build_shared import STATE_NAME_TO_ABBR, format_fee_display
from site_linking import (
    build_nearby_state_links,
    build_same_state_specialties,
    slugify_state_name,
)

# ──────────────────────────────────────────────────────────────────────────────
# 1. ROUTE CONTEXT — parse a URL/slug into structured identity
# ──────────────────────────────────────────────────────────────────────────────

CANONICAL_HOST = "https://www.statelicensingreference.com"

# Perdiem specialty codes mapped from profession names
PROFESSION_TO_PERDIEM: dict[str, str] = {
    "physical therapist": "pt",
    "occupational therapist": "ot",
    "speech-language pathologist": "slp",
    "respiratory therapist": "rrt",
    "dietitian": "dietsrv",
    "registered dietitian": "dietsrv",
    "cna": "cna",
    "certified nursing assistant": "cna",
    "audiologist": "aud",
    "registered nurse": "rn",
    "rn": "rn",
    "lpn": "lpn",
    "licensed practical nurse": "lpn",
    "pharmacist": "pharmacist",
    "pharmacy technician": "pharm_tech",
    "dental assistant": "da",
}


@dataclass(frozen=True)
class RouteContext:
    """Structured route identity — replaces ad-hoc slug inference."""

    # ── core identity ──
    state_slug: str             # e.g. "arkansas"
    state_abbr: str             # e.g. "AR"
    state_name: str             # e.g. "Arkansas"
    profession_slug: str        # e.g. "dietitian", "pt", "ot"

    # ── derived route ──
    slug: str                   # e.g. "arkansas-dietitian"
    page_type: str = "state_hub"  # state_hub | index | rate | tax
    canonical_url: str = ""
    object_id: str = ""         # stable identity key

    # ── grounding ──
    perdiem_specialty: str = "" # e.g. "dietsrv", "pt"
    perdiem_api_url: str = ""   # e.g. "https://perdiem-pseo.web.app/api/rates/ar/dietsrv.json"


def build_route_context(
    *,
    state_slug: str,
    profession_slug: str,
    state_name: str = "",
    state_abbr: str = "",
    slug_override: str = "",
    canonical_host: str = CANONICAL_HOST,
    perdiem_host: str = "https://perdiem-pseo.web.app",
) -> RouteContext:
    """Build a RouteContext from the minimum required inputs.

    This replaces all the scattered slug inference in build_unified.py lines 243-249.
    """
    # Resolve state_abbr from state_name if not given directly
    if not state_abbr and state_name:
        state_abbr = STATE_NAME_TO_ABBR.get(state_name, state_slug[:2].upper())
    elif not state_abbr:
        state_abbr = state_slug[:2].upper()

    # Resolve state_name from abbr if not given
    if not state_name:
        from site_linking import STATE_ABBR_TO_NAME
        state_name = STATE_ABBR_TO_NAME.get(state_abbr, state_slug.replace("-", " ").title())

    # Build canonical slug
    slug = slug_override or f"{state_slug}-{profession_slug}"
    canonical_url = f"{canonical_host}/{slug}"
    object_id = f"{state_abbr.lower()}-{profession_slug}"

    # Perdiem grounding
    perdiem_spec = PROFESSION_TO_PERDIEM.get(profession_slug.lower(), "")
    if not perdiem_spec:
        # Try the full profession name (will be resolved later from canonical object)
        perdiem_spec = ""
    perdiem_api = (
        f"{perdiem_host}/api/rates/{state_abbr.lower()}/{perdiem_spec}.json"
        if perdiem_spec
        else ""
    )

    return RouteContext(
        state_slug=state_slug,
        state_abbr=state_abbr,
        state_name=state_name,
        profession_slug=profession_slug,
        slug=slug,
        page_type="state_hub",
        canonical_url=canonical_url,
        object_id=object_id,
        perdiem_specialty=perdiem_spec,
        perdiem_api_url=perdiem_api,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 2. PAGE PACKET — the sole contract between data and renderer
# ──────────────────────────────────────────────────────────────────────────────


def build_page_packet(
    *,
    canonical_object: dict[str, Any],
    route: RouteContext,
    vertical_catalog: list[dict[str, str]],
    hero_image: dict[str, str] | None = None,
    verify_fee_and_timing_with_board: bool = False,
) -> dict[str, Any]:
    """Compress canonical object + route context into a render-ready packet.

    This is the ONLY function the template should consume.
    All display logic, field resolution, and cross-linking lives here.

    Returns a flat dict suitable for **kwargs to template.render().
    """
    data = canonical_object
    hero = hero_image or {}

    # ── credential type resolution ──
    ct = data.get("credential_type", {}) if isinstance(data.get("credential_type"), dict) else {}

    # ── perdiem grounding — resolve from profession_name if route didn't have it ──
    perdiem_spec = route.perdiem_specialty
    perdiem_api = route.perdiem_api_url
    if not perdiem_spec:
        prof_lower = data.get("profession_name", "").lower()
        perdiem_spec = PROFESSION_TO_PERDIEM.get(prof_lower, "")
        if perdiem_spec:
            perdiem_api = f"https://perdiem-pseo.web.app/api/rates/{route.state_abbr.lower()}/{perdiem_spec}.json"

    # ── cross-links ──
    same_state = build_same_state_specialties(
        state_slug=route.state_slug,
        current_vertical_slug=route.profession_slug,
        vertical_catalog=vertical_catalog,
    )
    nearby = build_nearby_state_links(
        state_name=route.state_name,
        current_vertical_slug=route.profession_slug,
    )

    # ── packet assembly ──
    # Start with the canonical object (preserves all existing template vars)
    packet: dict[str, Any] = {**data}

    # ── identity (from route, not inferred) ──
    packet["slug"] = route.slug
    packet["state_slug"] = route.state_slug
    packet["state_name"] = route.state_name
    packet["state_abbr"] = route.state_abbr
    packet["profession_slug"] = route.profession_slug
    packet["object_id"] = route.object_id
    packet["page_type"] = route.page_type

    # ── SEO / route metadata ──
    packet["site_domain"] = CANONICAL_HOST
    packet["canonical_url"] = route.canonical_url

    # ── presentation ──
    packet["hero_image_url"] = hero.get("url", "")
    packet["hero_image_alt"] = hero.get("alt", "")

    # ── cross-links ──
    packet["same_state_specialties"] = same_state
    packet["nearby_state_links"] = nearby

    # ── verification ──
    packet["board_verification"] = data.get("board_verification", {})
    packet["board_verification_sources"] = data.get("board_verification_sources", {})
    packet["verify_fee_and_timing_with_board"] = verify_fee_and_timing_with_board

    # ── grounding context (consumed by chat widget) ──
    packet["perdiem_specialty"] = perdiem_spec
    packet["perdiem_api_url"] = perdiem_api

    return packet
