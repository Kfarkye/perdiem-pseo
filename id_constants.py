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
