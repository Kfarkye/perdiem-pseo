"""Schema validation for the v2 license-path-detail data contract.

Pydantic V2 style. Enforces type safety, URL normalization, and the
"materially distinct variant" rule.

Usage:
    from schema import LicensePathRecord
    record = LicensePathRecord.model_validate_json(Path("...").read_text())
"""
from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, field_validator, model_validator


# ────────────────────────────────────────────────────────────────────
# Leaf models
# ────────────────────────────────────────────────────────────────────
class RoutingConfig(BaseModel):
    canonical_slug: str
    variant_param: str = "path"
    allowed_variants: List[str]

    @field_validator("canonical_slug")
    @classmethod
    def slug_is_clean(cls, v: str) -> str:
        v = v.strip().strip("/")
        if not v or " " in v:
            raise ValueError(f"canonical_slug must be a non-empty, space-free path segment: {v!r}")
        return v


class AnalyticsConfig(BaseModel):
    entity_key: str
    default_variant: str


class StateInfo(BaseModel):
    name: str
    abbr: str

    @field_validator("abbr")
    @classmethod
    def abbr_is_uppercase(cls, v: str) -> str:
        return v.upper()


class ProfessionInfo(BaseModel):
    key: str
    display_label: str
    short_label: str
    aliases: List[str] = []


class ContainerInfo(BaseModel):
    label: str
    label_source: str = "system"
    intro: str = ""


class SelectorVariant(BaseModel):
    key: str
    label: str
    label_source: str = "system"
    description: str = ""


class SelectorConfig(BaseModel):
    default_variant: str
    variants: List[SelectorVariant]

    @field_validator("variants")
    @classmethod
    def at_least_one(cls, v: list) -> list:
        if not v:
            raise ValueError("selector.variants must have at least one entry")
        return v


class BoardInfo(BaseModel):
    name: str
    phone: str = ""
    fax: str = ""
    contact_url: Optional[str] = None
    website: Optional[str] = None
    verify_url: Optional[str] = None

    @field_validator("contact_url", "website", "verify_url", mode="before")
    @classmethod
    def normalize_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError(f"Board URL must start with http:// or https://: {v!r}")
        return v


class SharedFacts(BaseModel):
    board: BoardInfo
    last_verified: str
    source_count: int = 1


# ────────────────────────────────────────────────────────────────────
# Variant content models
# ────────────────────────────────────────────────────────────────────
class HeroContent(BaseModel):
    title: str
    dek: str = ""


class SeoContent(BaseModel):
    title: str
    description: str = ""
    target_queries: List[str] = []


class CardContent(BaseModel):
    key: str
    label: str
    value: str
    status: str = "unknown"

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        allowed = {"confirmed", "estimated", "unknown"}
        if v not in allowed:
            raise ValueError(f"card.status must be one of {allowed}, got {v!r}")
        return v


class SectionContent(BaseModel):
    key: str
    label: str
    body: Optional[str] = None
    entries: List[str] = []


class FaqItem(BaseModel):
    q: str
    a: str

    @field_validator("q", "a")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("FAQ q and a must not be blank")
        return v.strip()


class TemporaryLicense(BaseModel):
    enabled: bool = False
    cards: List[CardContent] = []
    sections: List[SectionContent] = []


class VariantContent(BaseModel):
    hero: HeroContent
    seo: SeoContent
    cards: List[CardContent] = []
    sections: List[SectionContent] = []
    faq: List[FaqItem] = []
    temporary_license: Optional[TemporaryLicense] = None


# ────────────────────────────────────────────────────────────────────
# Top-level record
# ────────────────────────────────────────────────────────────────────
class LicensePathRecord(BaseModel):
    page_type: str = "license_path_detail"
    routing: RoutingConfig
    analytics: AnalyticsConfig
    state: StateInfo
    profession: ProfessionInfo
    container: ContainerInfo
    selector: SelectorConfig
    shared_facts: SharedFacts
    variants: Dict[str, VariantContent]

    @model_validator(mode="after")
    def variant_keys_consistent(self) -> "LicensePathRecord":
        """Ensure selector keys, routing keys, and variant dict keys are in sync."""
        selector_keys = {v.key for v in self.selector.variants}
        routing_keys = set(self.routing.allowed_variants)
        variant_keys = set(self.variants.keys())

        if selector_keys != routing_keys:
            raise ValueError(
                f"selector.variants keys {selector_keys} != "
                f"routing.allowed_variants {routing_keys}"
            )
        if selector_keys != variant_keys:
            raise ValueError(
                f"selector.variants keys {selector_keys} != "
                f"variants dict keys {variant_keys}"
            )
        return self

    @model_validator(mode="after")
    def default_variant_exists(self) -> "LicensePathRecord":
        """Ensure default_variant references an actual variant."""
        if self.selector.default_variant not in self.variants:
            raise ValueError(
                f"selector.default_variant '{self.selector.default_variant}' "
                f"not found in variants: {list(self.variants.keys())}"
            )
        if self.analytics.default_variant not in self.variants:
            raise ValueError(
                f"analytics.default_variant '{self.analytics.default_variant}' "
                f"not found in variants: {list(self.variants.keys())}"
            )
        return self

    @model_validator(mode="after")
    def temp_license_only_on_transfer(self) -> "LicensePathRecord":
        """temporary_license should only appear under transfer."""
        for key, variant in self.variants.items():
            if key != "transfer" and variant.temporary_license and variant.temporary_license.enabled:
                raise ValueError(
                    f"temporary_license.enabled=True on variant '{key}' — "
                    f"only 'transfer' may have temporary_license enabled"
                )
        return self

    def check_materially_distinct(self) -> list[str]:
        """Returns warnings for variants not materially distinct from default."""
        warnings = []
        default_key = self.selector.default_variant
        default_v = self.variants[default_key]
        default_sig = (
            frozenset((c.key, c.value) for c in default_v.cards),
            frozenset(s.key for s in default_v.sections),
            frozenset(f.q for f in default_v.faq),
        )

        for key, variant in self.variants.items():
            if key == default_key:
                continue
            sig = (
                frozenset((c.key, c.value) for c in variant.cards),
                frozenset(s.key for s in variant.sections),
                frozenset(f.q for f in variant.faq),
            )
            if sig == default_sig:
                warnings.append(
                    f"Variant '{key}' is not materially distinct from "
                    f"'{default_key}' — consider omitting its seo block "
                    f"to prevent crawl budget waste."
                )
        return warnings
