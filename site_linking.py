from __future__ import annotations

import json
from pathlib import Path

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

STATE_ABBR_TO_NAME = {abbr: name for name, abbr in STATE_NAME_TO_ABBR.items()}

STATE_NEIGHBORS = {
    "AL": ("FL", "GA", "MS", "TN"),
    "AK": (),
    "AZ": ("CA", "CO", "NM", "NV", "UT"),
    "AR": ("LA", "MO", "MS", "OK", "TN", "TX"),
    "CA": ("AZ", "NV", "OR"),
    "CO": ("AZ", "KS", "NE", "NM", "OK", "UT", "WY"),
    "CT": ("MA", "NY", "RI"),
    "DC": ("MD", "VA"),
    "DE": ("MD", "NJ", "PA"),
    "FL": ("AL", "GA"),
    "GA": ("AL", "FL", "NC", "SC", "TN"),
    "HI": (),
    "IA": ("IL", "MN", "MO", "NE", "SD", "WI"),
    "ID": ("MT", "NV", "OR", "UT", "WA", "WY"),
    "IL": ("IA", "IN", "KY", "MO", "WI"),
    "IN": ("IL", "KY", "MI", "OH"),
    "KS": ("CO", "MO", "NE", "OK"),
    "KY": ("IL", "IN", "MO", "OH", "TN", "VA", "WV"),
    "LA": ("AR", "MS", "TX"),
    "MA": ("CT", "NH", "NY", "RI", "VT"),
    "MD": ("DC", "DE", "PA", "VA", "WV"),
    "ME": ("NH"),
    "MI": ("IN", "OH", "WI"),
    "MN": ("IA", "ND", "SD", "WI"),
    "MO": ("AR", "IA", "IL", "KS", "KY", "NE", "OK", "TN"),
    "MS": ("AL", "AR", "LA", "TN"),
    "MT": ("ID", "ND", "SD", "WY"),
    "NC": ("GA", "SC", "TN", "VA"),
    "ND": ("MN", "MT", "SD"),
    "NE": ("CO", "IA", "KS", "MO", "SD", "WY"),
    "NH": ("MA", "ME", "VT"),
    "NJ": ("DE", "NY", "PA"),
    "NM": ("AZ", "CO", "OK", "TX", "UT"),
    "NV": ("AZ", "CA", "ID", "OR", "UT"),
    "NY": ("CT", "MA", "NJ", "PA", "RI", "VT"),
    "OH": ("IN", "KY", "MI", "PA", "WV"),
    "OK": ("AR", "CO", "KS", "MO", "NM", "TX"),
    "OR": ("CA", "ID", "NV", "WA"),
    "PA": ("DE", "MD", "NJ", "NY", "OH", "WV"),
    "RI": ("CT", "MA", "NY"),
    "SC": ("GA", "NC"),
    "SD": ("IA", "MN", "MT", "ND", "NE", "WY"),
    "TN": ("AL", "AR", "GA", "KY", "MO", "MS", "NC", "VA"),
    "TX": ("AR", "LA", "NM", "OK"),
    "UT": ("AZ", "CO", "ID", "NM", "NV", "WY"),
    "VA": ("DC", "KY", "MD", "NC", "TN", "WV"),
    "VT": ("MA", "NH", "NY"),
    "WA": ("ID", "OR"),
    "WI": ("IA", "IL", "MI", "MN"),
    "WV": ("KY", "MD", "OH", "PA", "VA"),
    "WY": ("CO", "ID", "MT", "NE", "SD", "UT"),
}


def slugify_state_name(name: str) -> str:
    return name.lower().replace("district of columbia", "district-of-columbia").replace(" ", "-")


def load_vertical_catalog(repo_root: Path) -> list[dict[str, str]]:
    profiles = json.loads((repo_root / "vertical_profiles.json").read_text(encoding="utf-8"))
    deployed_verticals = profiles.get("_meta", {}).get("deployed_verticals", [])
    verticals = profiles.get("verticals", {})

    catalog = []
    for slug in deployed_verticals:
        identity = verticals[slug]["identity"]
        catalog.append(
            {
                "slug": slug,
                "label": identity.get("title_short") or identity["title_full"],
            }
        )
    return catalog


def build_same_state_specialties(
    *,
    state_slug: str,
    current_vertical_slug: str,
    vertical_catalog: list[dict[str, str]],
) -> list[dict[str, str]]:
    return [
        {
            "label": entry["label"],
            "url": f"/{state_slug}-{entry['slug']}",
        }
        for entry in vertical_catalog
        if entry["slug"] != current_vertical_slug
    ]


def build_nearby_state_links(
    *,
    state_name: str,
    current_vertical_slug: str,
    limit: int = 4,
) -> list[dict[str, str]]:
    state_abbr = STATE_NAME_TO_ABBR.get(state_name, "")
    neighbor_abbrs = STATE_NEIGHBORS.get(state_abbr, ())
    links = []

    for abbr in neighbor_abbrs[:limit]:
        neighbor_name = STATE_ABBR_TO_NAME.get(abbr)
        if not neighbor_name:
            continue
        links.append(
            {
                "label": neighbor_name,
                "url": f"/{slugify_state_name(neighbor_name)}-{current_vertical_slug}",
            }
        )

    return links
