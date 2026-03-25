"""Build v2: License-path-detail pages from canonical state-profession objects.

Reads v2/ JSON records (routing + variants shape) and renders them using
shared_templates/license-path-detail.html. Also aggregates states and builds the state hub.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import sys

from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

from build_shared import STATE_NAME_TO_ABBR

# Shared hero images
IMAGES_FILE = ROOT.parent / "state_images.json"
STATE_IMAGES = json.loads(IMAGES_FILE.read_text(encoding="utf-8")) if IMAGES_FILE.exists() else {}

V2_JSON_DIR = ROOT / "database" / "v2"
DIST_DIR = ROOT / "dist-v2"
CANONICAL_HOST = "https://www.statelicensingreference.com"
TODAY = datetime.now().strftime("%Y-%m-%d")

DIST_DIR.mkdir(exist_ok=True)

env = Environment(
    loader=FileSystemLoader(ROOT.parent / "shared_templates"),
    undefined=StrictUndefined,
    autoescape=False,
)
template = env.get_template("license-path-detail.html")
hub_template = env.get_template("cna-states-hub.html")

urls: list[str] = []
built = 0
states_list = []

for json_file in sorted(V2_JSON_DIR.glob("*.json")):
    data = json.loads(json_file.read_text(encoding="utf-8"))

    slug = data["routing"]["canonical_slug"]
    state = data["state"]
    abbr = state.get("abbr", STATE_NAME_TO_ABBR.get(state["name"], ""))
    hero_img = STATE_IMAGES.get(abbr, {})

    render_data = {
        **data,
        "site_domain": CANONICAL_HOST,
        "hero_image_url": hero_img.get("url", ""),
        "hero_image_alt": hero_img.get("alt", ""),
    }

    out_path = DIST_DIR / f"{slug}.html"
    out_path.write_text(template.render(**render_data), encoding="utf-8")

    urls.append(
        f'  <url><loc>{CANONICAL_HOST}/{slug}</loc>'
        f'<lastmod>{data["shared_facts"]["last_verified"]}</lastmod>'
        f'<priority>0.8</priority></url>'
    )
    
    states_list.append({
        "name": state["name"],
        "abbr": abbr,
        "slug": slug,
        "profession_label": data.get("profession", {}).get("short_label", "CNA")
    })
    built += 1

# Sort states alphabetically by name
states_list.sort(key=lambda s: s["name"])

# Render the hub template to index.html
hub_render_data = {
    "states_list": states_list,
    "base_url": ""   # Keep relative for hrefs, e.g. /texas-cna if using vercel rewriting, or "" if hrefs should just map to "texas-cna.html". We will use "" for absolute root referencing on Vercel without domains, e.g. `<a href="/texas-cna">`. Wait, Vercel routes `/slug` to `/slug.html`. Since CANONICAL_HOST mapping does not exist in preview, we'll keep `base_url` empty. Actually, let's use `""`. So `"" / slug` becomes `/slug`.
}
(DIST_DIR / "index.html").write_text(hub_template.render(**hub_render_data), encoding="utf-8")

# Sitemap
sitemap_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "\n".join(urls)
    + "\n</urlset>\n"
)
(DIST_DIR / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")

# Robots
robots_txt = f"User-agent: *\nAllow: /\n\nSitemap: {CANONICAL_HOST}/sitemap.xml\n"
(DIST_DIR / "robots.txt").write_text(robots_txt, encoding="utf-8")

print(f"[v2] Built {built} license-path-detail pages and 1 hub index → {DIST_DIR}")

