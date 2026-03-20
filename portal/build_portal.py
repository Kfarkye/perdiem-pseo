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

# Unified single-host deployment uses root-host paths per specialty.
VERTICAL_DOMAIN_OVERRIDES = {}

POPULAR_GUIDES = (
    ("Michigan Dietitian", "/michigan-dietitian"),
    ("North Carolina Dietitian", "/north-carolina-dietitian"),
    ("Tennessee Dietitian", "/tennessee-dietitian"),
    ("Montana Dietitian", "/montana-dietitian"),
)


def load_state_options(root: Path, deployed_verticals: list[str]) -> list[dict[str, str]]:
    for slug in deployed_verticals:
        json_dir = root.parent / f"{slug}-pseo" / "database" / "json"
        if not json_dir.exists():
            continue

        options = []
        for json_file in sorted(json_dir.glob("*.json")):
            data = json.loads(json_file.read_text(encoding="utf-8"))
            options.append(
                {
                    "label": data["state_name"],
                    "slug": data["state_slug"],
                }
            )
        return sorted(options, key=lambda item: item["label"])

    return []


def resolve_portal_domain(meta: dict) -> str:
    return (meta.get("portal_domain") or "https://www.statelicensingreference.com").rstrip("/")


def resolve_vertical_url(slug: str, meta: dict) -> str:
    if slug in VERTICAL_DOMAIN_OVERRIDES:
        return VERTICAL_DOMAIN_OVERRIDES[slug]

    overrides = meta.get("vertical_domain_overrides") or {}
    if slug in overrides:
        return overrides[slug]

    pattern = meta.get("vertical_domain_pattern") or (resolve_portal_domain(meta) + "/{slug}")
    try:
        return pattern.format(slug=slug)
    except KeyError as exc:
        raise ValueError(f"vertical_domain_pattern missing placeholder: {exc}") from exc


def build() -> None:
    profiles = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    meta = profiles.get("_meta", {})
    deployed = meta.get("deployed_verticals", [])
    verticals = profiles.get("verticals", {})
    state_options = load_state_options(ROOT, deployed)

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
                "title_full": identity["title_full"],
                "title_plural": identity.get("title_plural", f"{identity['title_full']}s"),
                "credential": identity["credential"],
                "exam": regulatory["national_exam"],
            }
        )
        sitemap_urls.append(
            f"  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod><priority>0.9</priority></url>"
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
        state_options=state_options,
        popular_guides=[
            {"label": label, "url": f"{domain}{path}"}
            for label, path in POPULAR_GUIDES
        ],
    )

    DIST_DIR.mkdir(exist_ok=True)
    (DIST_DIR / "index.html").write_text(html, encoding="utf-8")

    # favicon
    favicon_src = ASSET_DIR / "favicon.svg"
    if favicon_src.exists():
        shutil.copyfile(favicon_src, DIST_DIR / "favicon.svg")
    social_card_src = ASSET_DIR / "social-card.svg"
    if social_card_src.exists():
        shutil.copyfile(social_card_src, DIST_DIR / "social-card.svg")

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
