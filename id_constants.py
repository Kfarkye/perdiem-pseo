"""
Cross-Project ID Constants — v1 (locked 2026-03-24)

Usage:
    from id_constants import NS, OBJ, EVT, SLUGS, make_object_id, make_event_id

    page_id = make_object_id(NS.SLR, OBJ.PAGE, "CA", "CNA")
    # → "SLR.OBJ.PAGE.CA.CNA"

    event_id = make_event_id(NS.QC, EVT.BROKEN_LINK, page_id, "20260324", 1)
    # → "QC.EVT.BROKEN_LINK.SLR.OBJ.PAGE.CA.CNA.20260324.001"
"""


class NS:
    """Namespaces."""
    SLR = "SLR"
    RX = "RX"
    DRIP = "DRIP"
    QC = "QC"
    SRC = "SRC"
    CLAIM = "CLAIM"
    AUDIT = "AUDIT"
    BOT = "BOT"


class OBJ:
    """Object types."""
    PAGE = "PAGE"
    STATE = "STATE"
    PROF = "PROF"
    PATH = "PATH"
    SEG = "SEG"
    RULE = "RULE"
    MED = "MED"
    SOURCE = "SOURCE"
    CLAIM = "CLAIM"
    MATCH = "MATCH"
    TEAM = "TEAM"
    REF = "REF"
    LINK = "LINK"


class EVT:
    """Event types."""
    LINK_CHECK = "LINK_CHECK"
    BROKEN_LINK = "BROKEN_LINK"
    CLAIM_VERIFY = "CLAIM_VERIFY"
    PAGE_AUDIT = "PAGE_AUDIT"
    RESEARCH_TASK = "RESEARCH_TASK"
    INGEST_RUN = "INGEST_RUN"
    VALIDATION_FAIL = "VALIDATION_FAIL"


class SLUGS:
    """Locked slug dictionaries."""

    STATES = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
        "DC", "PR", "GU", "VI",
    ]

    PROFESSIONS = [
        "CNA", "PHARMTECH", "DIETITIAN", "PT", "PTA", "OT", "OTA",
        "SLP", "SLPA", "RRT", "RT", "RADTECH", "MRI_TECH", "CT_TECH",
        "SONOGRAPHER", "MLT", "MLS", "DENTAL_HYGIENIST", "DENTAL_ASSISTANT",
        "LPN", "LVN", "RN", "NP", "PA", "PHARMACIST",
    ]

    PATHWAYS = ["NEW", "ENDORSEMENT", "RECIPROCITY", "RENEWAL", "VERIFY", "EXAM"]

    SEGMENTS = [
        "TRAVEL_NURSE", "TRAVEL_THERAPIST", "COLLEGE_STUDENT",
        "MILITARY", "DIGITAL_NOMAD", "SNOWBIRD", "SEASONAL_WORKER",
    ]

    MEDICATIONS = [
        "ADDERALL", "VYVANSE", "CONCERTA", "RITALIN",
        "XANAX", "AMBIEN", "OXYCONTIN", "TESTOSTERONE",
    ]

    LEAGUES = ["NBA", "NFL", "MLB", "NHL", "NCAAB", "SOCCER"]

    # ── Source keys: describe function, not URL or page title ──
    # Rule: UPPERCASE_SNAKE. Describes what the source DOES for the user.
    # Stable even if the URL changes. One key per functional purpose.
    SOURCE_KEYS = [
        "BOARD_WEBSITE",         # Board homepage
        "BOARD_CNA_PAGE",        # Board's profession-specific landing page
        "BOARD_APPLICATION",     # Application/endorsement page
        "BOARD_CONTACT",         # Contact page (non-email)
        "REGISTRY_LOOKUP",       # License/certification verification search
        "EXAM_PORTAL",           # Exam registration / scheduling
        "FEE_SCHEDULE",          # Official fee schedule page
        "FINGERPRINT_VENDOR",    # Fingerprint/background check vendor
        "COMPACT_PORTAL",        # Interstate compact portal
        "RENEWAL_PORTAL",        # Online renewal page
        "CE_PROVIDER",           # Continuing education provider/tracker
        "STATUTE",               # State statute or administrative code
        "BOARD_OF_PHARMACY",     # Pharmacy board (RX-specific)
        "TRANSFER_FORM",        # Downloadable transfer/endorsement form
    ]


def make_object_id(namespace: str, obj_type: str, *keys: str) -> str:
    """Build a canonical object ID.

    >>> make_object_id(NS.SLR, OBJ.PAGE, "CA", "CNA")
    'SLR.OBJ.PAGE.CA.CNA'
    """
    parts = [namespace, "OBJ", obj_type] + [k.upper().replace(" ", "_") for k in keys]
    return ".".join(parts)


def make_event_id(namespace: str, event_type: str, target_id: str, date: str, seq: int = 1) -> str:
    """Build an event ID referencing a canonical target.

    >>> make_event_id(NS.QC, EVT.BROKEN_LINK, "SLR.OBJ.PAGE.CA.CNA", "20260324", 1)
    'QC.EVT.BROKEN_LINK.SLR.OBJ.PAGE.CA.CNA.20260324.001'
    """
    return f"{namespace}.EVT.{event_type}.{target_id}.{date}.{seq:03d}"


def make_source_id(property_ns: str, state_abbr: str, source_key: str) -> str:
    """Build a canonical source object ID.

    >>> make_source_id("SLR", "CA", "BOARD_WEBSITE")
    'SRC.OBJ.SOURCE.SLR.CA.BOARD_WEBSITE'

    >>> make_source_id("RX", "FL", "BOARD_OF_PHARMACY")
    'SRC.OBJ.SOURCE.RX.FL.BOARD_OF_PHARMACY'
    """
    return make_object_id(NS.SRC, OBJ.SOURCE, property_ns, state_abbr.upper(), source_key.upper())


def normalize_source_key(field_path: str) -> str:
    """Map a JSON field path to a canonical SOURCE_KEY.

    This is the normalization layer that prevents drift.
    Field paths from data files map to stable functional names.

    >>> normalize_source_key("board.url")
    'BOARD_WEBSITE'
    >>> normalize_source_key("board.verify_url")
    'REGISTRY_LOOKUP'
    >>> normalize_source_key("reciprocity.endorsement_url")
    'BOARD_APPLICATION'
    """
    FIELD_TO_SOURCE = {
        # Board fields
        "board.url": "BOARD_WEBSITE",
        "board.website": "BOARD_WEBSITE",
        "board_source_url": "BOARD_CNA_PAGE",
        "board.verify_url": "REGISTRY_LOOKUP",
        "board.contact_url": "BOARD_CONTACT",
        # Reciprocity fields
        "reciprocity.board_url": "BOARD_CNA_PAGE",
        "reciprocity.endorsement_url": "BOARD_APPLICATION",
        "reciprocity.board_source_url": "BOARD_CNA_PAGE",
        "reciprocity.compact_url": "COMPACT_PORTAL",
        "reciprocity.compact_portal_url": "COMPACT_PORTAL",
        # Verification sources
        "board_verification_sources.fee": "FEE_SCHEDULE",
        "board_verification_sources.timeline": "BOARD_APPLICATION",
        "board_verification_sources.registry": "REGISTRY_LOOKUP",
        "board_verification_sources.exam_portal": "EXAM_PORTAL",
        "board_verification_sources.info_page": "BOARD_CNA_PAGE",
        # Fingerprints
        "fingerprints.vendor_url": "FINGERPRINT_VENDOR",
        # Compact
        "compact.compact_source_url": "COMPACT_PORTAL",
    }
    return FIELD_TO_SOURCE.get(field_path, "BOARD_WEBSITE")


# ── Vertical slug → profession slug mapping ──
VERTICAL_TO_PROF = {
    "cna": "CNA",
    "pharm": "PHARMTECH",
    "pharmacist": "PHARMACIST",
    "ot": "OT",
    "pt": "PT",
    "slp": "SLP",
    "rrt": "RRT",
    "aud": "AUD",
    "dietitian": "DIETITIAN",
    "da": "DENTAL_ASSISTANT",
}
