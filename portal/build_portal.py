"""Build the profession portal front page directory.

Reads vertical_profiles.json and generates portal dist assets:
- dist/index.html
- dist/robots.txt
- dist/sitemap.xml
- dist/favicon.svg
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent
PROFILES_PATH = ROOT.parent / "vertical_profiles.json"
DIST_DIR = ROOT / "dist"
TEMPLATE_DIR = ROOT / "src" / "templates"
ASSET_DIR = ROOT / "src" / "assets"
TEMPLATE_NAME = "index.html.j2"
TODAY = datetime.now().strftime("%Y-%m-%d")

# Icons (SF Symbol-style SVG paths) for each profession.
VERTICAL_ICONS = {
    "dietitian": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c1.5 0 3-.3 4.3-.9"/><path d="M7 12.5c0-2.8 2.2-5 5-5s5 2.2 5 5"/><path d="M12 7.5V2"/><path d="M14.5 14.5l3-3"/><path d="M20 8l2 2-4 4"/></svg>',
    "ot": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/><rect x="2" y="20" width="20" height="0" rx="0"/></svg>',
    "pt": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="3"/><path d="M6.5 8a4 4 0 0 1 11 0"/><path d="M12 12v5"/><path d="M8 22l4-5 4 5"/></svg>',
    "rrt": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.5 0 10-4.5 10-10S17.5 2 12 2 2 6.5 2 12s4.5 10 10 10z"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01"/><path d="M15 9h.01"/></svg>',
    "slp": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 18.5a6.5 6.5 0 1 0 0-13 6.5 6.5 0 0 0 0 13z"/><path d="M12 2v3"/><path d="M12 19v3"/><path d="M5 12H2"/><path d="M22 12h-3"/></svg>',
    "aud": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/><path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>',
    "pharm": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.5 20H4a2 2 0 0 1-2-2V5c0-1.1.9-2 2-2h3.93a2 2 0 0 1 1.66.9l.54.8a2 2 0 0 0 1.66.9H20a2 2 0 0 1 2 2v2"/><circle cx="17" cy="17" r="3"/><path d="M17 14v6"/><path d="M14 17h6"/></svg>',
    "pharmacist": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2h8l4 6H4z"/><path d="M12 8v14"/><path d="M4 8h16"/><path d="M7 22h10"/><path d="M9 12h6"/><path d="M9 16h6"/></svg>',
}

# Accent colors per vertical (used for hover/active tint).
VERTICAL_COLORS = {
    "dietitian": "#34C759",
    "ot": "#FF9F0A",
    "pt": "#007AFF",
    "rrt": "#5856D6",
    "slp": "#FF2D55",
    "aud": "#AF52DE",
    "pharm": "#00C7BE",
    "pharmacist": "#FF6B35",
}

# Canonical deployment URLs for each specialty project.
VERTICAL_DOMAIN_OVERRIDES = {
    "dietitian": "https://dietitian.statelicensingreference.com",
    "ot": "https://ot.statelicensingreference.com",
    "pt": "https://pt.statelicensingreference.com",
    "slp": "https://slp.statelicensingreference.com",
    "aud": "https://aud.statelicensingreference.com",
    "rrt": "https://rt.statelicensingreference.com",
    "pharm": "https://pharm.statelicensingreference.com",
    "pharmacist": "https://pharmacist.statelicensingreference.com",
}


def compact_badge(status: str) -> dict[str, str]:
    if status == "active":
        return {"label": "Compact Active", "variant": "active"}
    if status == "enacted":
        return {"label": "Compact Enacted", "variant": "enacted"}
    return {"label": "No Compact", "variant": "none"}


def resolve_portal_domain(meta: dict) -> str:
    return meta.get("portal_domain") or "https://perdiem-portal.vercel.app"


def resolve_vertical_url(slug: str, meta: dict) -> str:
    if slug in VERTICAL_DOMAIN_OVERRIDES:
        return VERTICAL_DOMAIN_OVERRIDES[slug]

    overrides = meta.get("vertical_domain_overrides") or {}
    if slug in overrides:
        return overrides[slug]

    pattern = meta.get("vertical_domain_pattern") or "https://perdiem-{slug}.vercel.app"
    try:
        return pattern.format(slug=slug)
    except KeyError as exc:
        raise ValueError(f"vertical_domain_pattern missing placeholder: {exc}") from exc


def build() -> None:
    profiles = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    meta = profiles.get("_meta", {})
    deployed = meta.get("deployed_verticals", [])
    verticals = profiles.get("verticals", {})

    domain = resolve_portal_domain(meta)

    cards: list[dict] = []
    sitemap_urls: list[str] = []

    for slug in deployed:
        vertical = verticals[slug]
        identity = vertical["identity"]
        regulatory = vertical["regulatory"]
        url = resolve_vertical_url(slug, meta)

        cards.append(
            {
                "slug": slug,
                "url": url,
                "color": VERTICAL_COLORS.get(slug, "#007AFF"),
                "icon": VERTICAL_ICONS.get(slug, ""),
                "title_full": identity["title_full"],
                "title_plural": identity.get("title_plural", f"{identity['title_full']}s"),
                "credential": identity["credential"],
                "exam": regulatory["national_exam"],
                "badge": compact_badge(regulatory.get("compact_status", "none")),
            }
        )
        sitemap_urls.append(
            f"  <url><loc>{url}/</loc><lastmod>{TODAY}</lastmod><priority>0.9</priority></url>"
        )

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        undefined=StrictUndefined,
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(TEMPLATE_NAME)
    html = template.render(
        domain=domain,
        today=TODAY,
        cards=cards,
        deployed_count=len(deployed),
        foot_cards=cards,
    )

    DIST_DIR.mkdir(exist_ok=True)
    (DIST_DIR / "index.html").write_text(html, encoding="utf-8")

    # favicon
    favicon_src = ASSET_DIR / "favicon.svg"
    if favicon_src.exists():
        shutil.copy2(favicon_src, DIST_DIR / "favicon.svg")

    # robots.txt + sitemap use the same canonical domain
    robots = f"User-agent: *\nAllow: /\n\nSitemap: {domain}/sitemap.xml\n"
    (DIST_DIR / "robots.txt").write_text(robots, encoding="utf-8")

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{domain}/</loc><lastmod>{TODAY}</lastmod><priority>1.0</priority></url>\n"
        + "\n".join(sitemap_urls)
        + "\n</urlset>\n"
    )
    (DIST_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    print(f"Portal built: {len(cards)} profession cards -> {DIST_DIR / 'index.html'}")


if __name__ == "__main__":
    build()
