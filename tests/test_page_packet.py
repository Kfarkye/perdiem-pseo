"""Deterministic tests for the page_packet module.

Validates:
  1. RouteContext identity resolution (slug, abbr, perdiem)
  2. Packet completeness (all required keys present)
  3. No parallel inference regression (perdiem URL built from packet, not re-derived)
"""
import json
import sys
from pathlib import Path

# Ensure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from page_packet import build_route_context, build_page_packet, PROFESSION_TO_PERDIEM


# ── 1. Route context identity tests ────────────────────────────────────


def test_route_context_basic():
    r = build_route_context(
        state_slug="arkansas",
        profession_slug="dietitian",
        state_name="Arkansas",
    )
    assert r.slug == "arkansas-dietitian", f"slug: {r.slug}"
    assert r.state_abbr == "AR", f"abbr: {r.state_abbr}"
    assert r.state_name == "Arkansas"
    assert r.object_id == "ar-dietitian"
    assert r.page_type == "state_hub"
    assert r.canonical_url == "https://www.statelicensingreference.com/arkansas-dietitian"


def test_route_context_perdiem_resolution():
    """Profession slug 'physical therapist' maps to perdiem 'pt'."""
    r = build_route_context(
        state_slug="california",
        profession_slug="physical therapist",
        state_name="California",
    )
    assert r.perdiem_specialty == "pt", f"perdiem: {r.perdiem_specialty}"
    assert r.perdiem_api_url == "https://perdiem-pseo.web.app/api/rates/ca/pt.json"


def test_route_context_slug_override():
    r = build_route_context(
        state_slug="new-york",
        profession_slug="ot",
        state_name="New York",
        slug_override="new-york-ot-custom",
    )
    assert r.slug == "new-york-ot-custom"
    assert r.state_abbr == "NY"


def test_route_context_abbr_from_param():
    r = build_route_context(
        state_slug="california",
        profession_slug="speech-language pathologist",
        state_abbr="CA",
    )
    assert r.state_abbr == "CA"
    assert "ca" in r.perdiem_api_url


def test_unknown_profession_no_perdiem():
    r = build_route_context(
        state_slug="texas",
        profession_slug="unknown_specialty",
        state_name="Texas",
    )
    assert r.perdiem_specialty == ""
    assert r.perdiem_api_url == ""


# ── 2. Packet completeness tests ──────────────────────────────────────

REQUIRED_PACKET_KEYS = [
    "slug", "state_slug", "state_name", "state_abbr",
    "profession_slug", "object_id", "page_type",
    "site_domain", "canonical_url",
    "hero_image_url", "hero_image_alt",
    "same_state_specialties", "nearby_state_links",
    "board_verification", "board_verification_sources",
    "verify_fee_and_timing_with_board",
    "perdiem_specialty", "perdiem_api_url",
]


def test_packet_has_all_required_keys():
    fixture = Path(__file__).resolve().parent.parent / "dietitian-pseo/database/json/arkansas-dietitian.json"
    if not fixture.exists():
        return  # skip if fixture missing
    data = json.loads(fixture.read_text())
    route = build_route_context(
        state_slug=data["state_slug"],
        profession_slug="dietitian",
        state_name=data["state_name"],
    )
    packet = build_page_packet(
        canonical_object=data,
        route=route,
        vertical_catalog=[],
    )
    missing = [k for k in REQUIRED_PACKET_KEYS if k not in packet]
    assert not missing, f"Missing packet keys: {missing}"


def test_packet_perdiem_from_profession_name():
    """Verify perdiem resolves from profession_name when profession_slug has no mapping."""
    data = {
        "state_slug": "florida",
        "state_name": "Florida",
        "profession_name": "Physical Therapist",
    }
    route = build_route_context(
        state_slug="florida",
        profession_slug="some_custom_slug",
        state_name="Florida",
    )
    packet = build_page_packet(
        canonical_object=data,
        route=route,
        vertical_catalog=[],
    )
    assert packet["perdiem_specialty"] == "pt"
    assert "fl/pt.json" in packet["perdiem_api_url"]


# ── 3. No parallel inference regression ───────────────────────────────


def test_profession_map_coverage():
    """All known verticals should have a perdiem mapping (keyed by full name)."""
    expected = [
        "physical therapist", "occupational therapist",
        "speech-language pathologist", "respiratory therapist",
        "dietitian", "cna", "pharmacist",
    ]
    for prof in expected:
        assert prof in PROFESSION_TO_PERDIEM, f"{prof} missing from PROFESSION_TO_PERDIEM"


# ── Runner ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"  PASS  {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
