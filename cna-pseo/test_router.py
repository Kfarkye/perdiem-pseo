"""Test suite for the license-path-detail intent router.

Tests cover:
  1. Valid default path renders correctly
  2. Valid non-default path renders correctly
  3. Invalid query param falls back to default
  4. Missing variant payload falls back to default with matching UI/metadata
  5. Missing nested seo/hero/faq/cards/board fields do not crash
  6. Active FAQ schema matches only visible FAQ content
  7. Default selector link uses clean slug (no ?path=becoming)
  8. Temporary license block only renders under transfer

Run:
    pip install pytest pydantic jinja2
    pytest test_router.py -v
"""
from __future__ import annotations

import json
import copy
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT.parent / "shared_templates"
DATA_DIR = ROOT / "database" / "v2"
NC_CNA_PATH = DATA_DIR / "north-carolina-certified-nursing-assistant.json"


# ────────────────────────────────────────────────────────────────────
# Fixtures
# ────────────────────────────────────────────────────────────────────
@dataclass
class FakeRequest:
    """Simulate Flask request.args for server-side rendering tests."""
    args: dict = field(default_factory=dict)


def load_record() -> dict:
    return json.loads(NC_CNA_PATH.read_text(encoding="utf-8"))


def make_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        undefined=StrictUndefined,
        autoescape=False,
    )


def render_template(
    data: dict,
    request: Optional[FakeRequest] = None,
) -> str:
    """Render license-path-detail.html with the given data and optional request."""
    env = make_env()
    template = env.get_template("license-path-detail.html")

    render_data = {
        **data,
        "site_domain": "https://www.statelicensingreference.com",
        "hero_image_url": "",
        "hero_image_alt": "",
    }

    if request is not None:
        render_data["request"] = request

    return template.render(**render_data)


@pytest.fixture
def nc_cna() -> dict:
    return load_record()


# ────────────────────────────────────────────────────────────────────
# 1. Valid default path renders correctly
# ────────────────────────────────────────────────────────────────────
class TestDefaultPath:
    def test_renders_without_crash(self, nc_cna):
        html = render_template(nc_cna)
        assert "<!DOCTYPE html>" in html
        assert "Becoming a CNA in North Carolina" in html

    def test_default_variant_hero(self, nc_cna):
        html = render_template(nc_cna)
        assert "Becoming a CNA in North Carolina" in html
        assert "Start with the training, testing, and registry requirements." in html

    def test_default_seo_title(self, nc_cna):
        html = render_template(nc_cna)
        assert "<title>How to Become a CNA in North Carolina</title>" in html

    def test_default_breadcrumb_4_positions(self, nc_cna):
        html = render_template(nc_cna)
        assert 'itemprop="position" content="1"' in html
        assert 'itemprop="position" content="2"' in html
        assert 'itemprop="position" content="3"' in html
        assert 'itemprop="position" content="4"' in html

    def test_default_breadcrumb_shows_becoming(self, nc_cna):
        html = render_template(nc_cna)
        assert "data-breadcrumb-variant" in html
        assert ">Becoming<" in html

    def test_body_data_attributes(self, nc_cna):
        html = render_template(nc_cna)
        assert 'data-entity-key="north-carolina::certified-nursing-assistant"' in html
        assert 'data-active-intent="becoming"' in html


# ────────────────────────────────────────────────────────────────────
# 2. Valid non-default path renders correctly (server-side)
# ────────────────────────────────────────────────────────────────────
class TestNonDefaultPath:
    def test_transfer_via_request_args(self, nc_cna):
        request = FakeRequest(args={"path": "transfer"})
        html = render_template(nc_cna, request=request)
        assert "Transfer a CNA License to North Carolina" in html
        assert 'data-active-intent="transfer"' in html

    def test_state_application_via_request_args(self, nc_cna):
        request = FakeRequest(args={"path": "state_application"})
        html = render_template(nc_cna, request=request)
        assert "North Carolina CNA State Application" in html
        assert 'data-active-intent="state_application"' in html

    def test_transfer_cards(self, nc_cna):
        request = FakeRequest(args={"path": "transfer"})
        html = render_template(nc_cna, request=request)
        assert "10 business days" in html
        assert "No fee" in html

    def test_transfer_seo_title(self, nc_cna):
        request = FakeRequest(args={"path": "transfer"})
        html = render_template(nc_cna, request=request)
        assert "<title>North Carolina CNA Reciprocity and Transfer</title>" in html


# ────────────────────────────────────────────────────────────────────
# 3. Invalid query param falls back to default
# ────────────────────────────────────────────────────────────────────
class TestInvalidParam:
    def test_garbage_param_falls_back(self, nc_cna):
        request = FakeRequest(args={"path": "nonexistent_variant"})
        html = render_template(nc_cna, request=request)
        assert "Becoming a CNA in North Carolina" in html
        assert 'data-active-intent="becoming"' in html

    def test_empty_param_falls_back(self, nc_cna):
        request = FakeRequest(args={"path": ""})
        html = render_template(nc_cna, request=request)
        assert "Becoming a CNA in North Carolina" in html

    def test_xss_param_falls_back(self, nc_cna):
        request = FakeRequest(args={"path": '<script>alert("xss")</script>'})
        html = render_template(nc_cna, request=request)
        assert "Becoming a CNA in North Carolina" in html
        assert '<script>alert' not in html


# ────────────────────────────────────────────────────────────────────
# 4. Missing variant payload falls back to default
# ────────────────────────────────────────────────────────────────────
class TestMissingPayload:
    def test_missing_transfer_payload_falls_back(self, nc_cna):
        data = copy.deepcopy(nc_cna)
        del data["variants"]["transfer"]
        request = FakeRequest(args={"path": "transfer"})
        html = render_template(data, request=request)
        # Should show default variant, not crash
        assert "Becoming a CNA in North Carolina" in html
        assert 'data-active-intent="becoming"' in html


# ────────────────────────────────────────────────────────────────────
# 5. Missing nested fields do not crash (anti-500)
# ────────────────────────────────────────────────────────────────────
class TestPartialPayload:
    def test_missing_seo_block(self, nc_cna):
        data = copy.deepcopy(nc_cna)
        data["variants"]["becoming"]["seo"] = {}
        html = render_template(data)
        # Falls back to computed title
        assert "<title>" in html
        assert "Certified Nursing Assistant" in html

    def test_missing_hero_block(self, nc_cna):
        data = copy.deepcopy(nc_cna)
        data["variants"]["becoming"]["hero"] = {}
        html = render_template(data)
        assert "<h1" in html

    def test_empty_faq(self, nc_cna):
        data = copy.deepcopy(nc_cna)
        data["variants"]["becoming"]["faq"] = []
        html = render_template(data)
        assert "<!DOCTYPE html>" in html

    def test_empty_cards(self, nc_cna):
        data = copy.deepcopy(nc_cna)
        data["variants"]["becoming"]["cards"] = []
        html = render_template(data)
        assert "<!DOCTYPE html>" in html

    def test_empty_board_phone(self, nc_cna):
        data = copy.deepcopy(nc_cna)
        data["shared_facts"]["board"]["phone"] = ""
        html = render_template(data)
        assert "<!DOCTYPE html>" in html


# ────────────────────────────────────────────────────────────────────
# 6. FAQ schema matches only visible FAQ content
# ────────────────────────────────────────────────────────────────────
class TestFaqSchema:
    def test_default_faq_schema_matches_becoming(self, nc_cna):
        html = render_template(nc_cna)
        # Becoming FAQ should be in schema
        assert '"What training is required to become a CNA in North Carolina?"' in html
        # Transfer FAQ should NOT be in structured data (rendered at build time for default)
        assert '"Is there a fee to transfer a CNA license to North Carolina?"' not in html.split("</script>")[0]

    def test_transfer_faq_schema_matches_transfer(self, nc_cna):
        request = FakeRequest(args={"path": "transfer"})
        html = render_template(nc_cna, request=request)
        ld_json_block = html.split('<script type="application/ld+json">')[1].split("</script>")[0]
        assert "Is there a fee to transfer" in ld_json_block


# ────────────────────────────────────────────────────────────────────
# 7. Default selector link uses clean slug
# ────────────────────────────────────────────────────────────────────
class TestSelectorLinks:
    def test_default_pill_clean_slug(self, nc_cna):
        html = render_template(nc_cna)
        # The becoming pill should link to the clean slug, NOT ?path=becoming
        assert 'href="/north-carolina-certified-nursing-assistant"' in html
        assert "?path=becoming" not in html

    def test_transfer_pill_has_param(self, nc_cna):
        html = render_template(nc_cna)
        assert "?path=transfer" in html

    def test_state_application_pill_has_param(self, nc_cna):
        html = render_template(nc_cna)
        assert "?path=state_application" in html

    def test_no_role_tab(self, nc_cna):
        html = render_template(nc_cna)
        assert 'role="tab"' not in html
        assert 'role="tablist"' not in html

    def test_aria_current_on_active(self, nc_cna):
        html = render_template(nc_cna)
        # Extract the becoming pill specifically
        assert 'aria-current="page"' in html


# ────────────────────────────────────────────────────────────────────
# 8. Temporary license only under transfer
# ────────────────────────────────────────────────────────────────────
class TestTemporaryLicense:
    def test_temp_license_not_on_becoming(self, nc_cna):
        html = render_template(nc_cna)
        assert "Temporary Licensure" not in html

    def test_temp_license_block_exists_when_enabled(self, nc_cna):
        data = copy.deepcopy(nc_cna)
        data["variants"]["transfer"]["temporary_license"]["enabled"] = True
        request = FakeRequest(args={"path": "transfer"})
        html = render_template(data, request=request)
        assert "Temporary Licensure" in html


# ────────────────────────────────────────────────────────────────────
# Pydantic schema validation tests
# ────────────────────────────────────────────────────────────────────
class TestSchemaValidation:
    def test_valid_record_passes(self, nc_cna):
        from schema import LicensePathRecord
        record = LicensePathRecord(**nc_cna)
        assert record.routing.canonical_slug == "north-carolina-certified-nursing-assistant"

    def test_mismatched_variant_keys_fails(self, nc_cna):
        from schema import LicensePathRecord
        data = copy.deepcopy(nc_cna)
        data["routing"]["allowed_variants"].append("nonexistent")
        with pytest.raises(Exception):
            LicensePathRecord(**data)

    def test_invalid_board_url_fails(self, nc_cna):
        from schema import LicensePathRecord
        data = copy.deepcopy(nc_cna)
        data["shared_facts"]["board"]["website"] = "not-a-url"
        with pytest.raises(Exception):
            LicensePathRecord(**data)

    def test_blank_faq_fails(self, nc_cna):
        from schema import LicensePathRecord
        data = copy.deepcopy(nc_cna)
        data["variants"]["becoming"]["faq"][0]["q"] = ""
        with pytest.raises(Exception):
            LicensePathRecord(**data)

    def test_temp_license_on_non_transfer_fails(self, nc_cna):
        from schema import LicensePathRecord
        data = copy.deepcopy(nc_cna)
        data["variants"]["becoming"]["temporary_license"] = {"enabled": True}
        with pytest.raises(Exception):
            LicensePathRecord(**data)

    def test_materially_distinct_warning(self, nc_cna):
        from schema import LicensePathRecord
        data = copy.deepcopy(nc_cna)
        # Make state_application identical to becoming
        data["variants"]["state_application"]["cards"] = copy.deepcopy(
            data["variants"]["becoming"]["cards"]
        )
        data["variants"]["state_application"]["sections"] = copy.deepcopy(
            data["variants"]["becoming"]["sections"]
        )
        data["variants"]["state_application"]["faq"] = copy.deepcopy(
            data["variants"]["becoming"]["faq"]
        )
        record = LicensePathRecord(**data)
        warnings = record.check_materially_distinct()
        assert len(warnings) > 0
        assert "state_application" in warnings[0]

    def test_invalid_card_status_fails(self, nc_cna):
        from schema import LicensePathRecord
        data = copy.deepcopy(nc_cna)
        data["variants"]["becoming"]["cards"][0]["status"] = "invalid_status"
        with pytest.raises(Exception):
            LicensePathRecord(**data)
