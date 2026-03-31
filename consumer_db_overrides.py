from __future__ import annotations

import os
from typing import Any

import requests

DB_SPECIALTY_BY_VERTICAL = {
    "pharm": "PHARM_TECH",
}


def fetch_supabase_rows(db_specialty: str) -> dict[str, dict[str, Any]]:
    """Fetch consumer-safe licensing rows keyed by state abbreviation."""
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_ANON_KEY", "")

    if not url and not key:
        print(f"WARNING: SUPABASE_URL / SUPABASE_ANON_KEY not set — using JSON fallback for {db_specialty}.")
        return {}

    if not url or not key:
        raise RuntimeError("Both SUPABASE_URL and SUPABASE_ANON_KEY are required for build-time Supabase reads.")

    endpoint = f"{url}/rest/v1/v_consumer_licensing"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }
    params = {
        "specialty": f"eq.{db_specialty}",
        "select": "*",
    }

    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch {db_specialty} rows from v_consumer_licensing.") from exc

    rows = response.json()
    return {
        str(row["state_abbr"]).upper(): row
        for row in rows
        if row.get("state_abbr")
    }


def apply_consumer_db_overrides(data: dict[str, Any], db_row: dict[str, Any]) -> dict[str, Any]:
    board = data.setdefault("board", {})
    quick_facts = data.setdefault("quick_facts", {})
    reciprocity = data.setdefault("reciprocity", {})
    fees = data.setdefault("fees_endorsement", {})
    compact = data.setdefault("compact", {})

    board["name"] = _first_present(db_row, "board_name") or board.get("name", "")
    board["url"] = _first_present(db_row, "board_url") or board.get("url", "")
    board["phone"] = _first_present(db_row, "board_phone") or board.get("phone", "")

    fee_display = _first_present(db_row, "endorsement_cost_display")
    timeline_display = _first_present(db_row, "endorsement_timeline_display")
    renewal_fee_display = _first_present(db_row, "renewal_fee_display")
    renewal_cycle_display = _first_present(db_row, "renewal_cycle_display")
    app_fee_display = _first_present(db_row, "endorsement_app_fee_display")
    background_check_display = _first_present(db_row, "fingerprint_cost_display", "background_check_fee_display")
    jurisprudence_display = _first_present(db_row, "jurisprudence_exam_fee_display", "jurisprudence_fee_display")
    total_estimated_display = _first_present(db_row, "total_estimated_cost_display", "endorsement_cost_display")

    if fee_display is not None:
        quick_facts["total_fee"] = fee_display
        reciprocity["endorsement_fee"] = fee_display
    if timeline_display is not None:
        quick_facts["processing_time"] = timeline_display
        reciprocity["processing_time"] = timeline_display
    if renewal_fee_display is not None:
        quick_facts["renewal_fee"] = renewal_fee_display
    if renewal_cycle_display is not None:
        quick_facts["renewal_cycle"] = renewal_cycle_display
    if app_fee_display is not None:
        fees["app_fee"] = app_fee_display
    if background_check_display is not None:
        fees["background_check_fee"] = background_check_display
    if jurisprudence_display is not None:
        fees["jurisprudence_exam_fee"] = jurisprudence_display
    if total_estimated_display is not None:
        fees["total_estimated_cost"] = total_estimated_display

    reciprocity["fingerprint_required"] = _first_present(db_row, "fingerprint_required", default=reciprocity.get("fingerprint_required"))
    reciprocity["temp_license_available"] = _first_present(db_row, "temp_license_available", default=reciprocity.get("temp_license_available"))
    reciprocity["state_is_member"] = bool(_first_present(db_row, "compact_member", default=reciprocity.get("state_is_member", False)))
    reciprocity["board_url"] = _first_present(db_row, "board_url") or reciprocity.get("board_url", "")
    reciprocity["endorsement_url"] = _first_present(db_row, "board_url") or reciprocity.get("endorsement_url", "")

    compact["is_compact_member"] = bool(_first_present(db_row, "compact_member", default=compact.get("is_compact_member", False)))
    if _first_present(db_row, "compact_name"):
        compact["compact_name"] = db_row["compact_name"]
        reciprocity["compact_name"] = db_row["compact_name"]
    if _first_present(db_row, "compact_status"):
        reciprocity["compact_status"] = db_row["compact_status"]

    last_verified = _first_present(db_row, "last_verified")
    if last_verified:
        data["last_verified_date"] = str(last_verified)
        data["last_updated"] = str(last_verified)

    data["board_source_url"] = _primary_source_url(db_row) or data.get("board_source_url", "")
    data["board_verification"] = _build_board_verification(db_row)
    data["board_verification_sources"] = _build_board_verification_sources(db_row)
    return data


def _first_present(row: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return default


def _has_verified_display(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in {"", "See board", "N/A"}
    return True


def _source_urls(row: dict[str, Any]) -> list[str]:
    urls = row.get("source_urls") or []
    if isinstance(urls, list):
        return [str(url) for url in urls if url]
    return []


def _primary_source_url(row: dict[str, Any]) -> str:
    urls = _source_urls(row)
    if urls:
        return urls[0]
    return str(row.get("board_url") or "")


def _build_board_verification(row: dict[str, Any]) -> dict[str, bool]:
    verified = bool(row.get("verified"))
    fee_display = _first_present(row, "endorsement_cost_display")
    timeline_display = _first_present(row, "endorsement_timeline_display")
    renewal_fee_display = _first_present(row, "renewal_fee_display")
    renewal_cycle_display = _first_present(row, "renewal_cycle_display")
    background_check_display = _first_present(row, "fingerprint_cost_display", "background_check_fee_display")
    jurisprudence_display = _first_present(row, "jurisprudence_exam_fee_display", "jurisprudence_fee_display")
    total_estimated_display = _first_present(row, "total_estimated_cost_display", "endorsement_cost_display")

    return {
        "fee_verified": verified and _has_verified_display(fee_display),
        "timeline_verified": verified and _has_verified_display(timeline_display),
        "renewal_fee_verified": verified and _has_verified_display(renewal_fee_display),
        "renewal_cycle_verified": verified and _has_verified_display(renewal_cycle_display),
        "background_check_fee_verified": verified and _has_verified_display(background_check_display),
        "jurisprudence_fee_verified": verified and _has_verified_display(jurisprudence_display),
        "total_estimated_cost_verified": verified and _has_verified_display(total_estimated_display),
    }


def _build_board_verification_sources(row: dict[str, Any]) -> dict[str, str]:
    urls = _source_urls(row)
    board_url = str(row.get("board_url") or "")
    primary = urls[0] if len(urls) > 0 else board_url
    secondary = urls[1] if len(urls) > 1 else primary
    tertiary = urls[2] if len(urls) > 2 else secondary

    return {
        "fee": primary,
        "timeline": secondary or primary,
        "renewal": tertiary or secondary or primary,
    }
