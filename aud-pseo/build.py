"""Programmatic SEO compiler with reciprocity-first state pages."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
import sys

from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent
# Load shared state hero images
IMAGES_FILE = ROOT.parent / "state_images.json"
STATE_IMAGES = json.loads(IMAGES_FILE.read_text(encoding="utf-8")) if IMAGES_FILE.exists() else {}
sys.path.insert(0, str(ROOT.parent))

from reciprocity_index_builder import render_index
JSON_DIR = ROOT / "database" / "json"
DIST_DIR = ROOT / "dist"
TEMPLATES_DIR = ROOT / "src" / "templates"
CSS_SRC = ROOT / "src" / "css" / "styles.css"
CSS_DIST = DIST_DIR / "css" / "styles.css"
CONTENT_DIR = ROOT / "content"
DOMAIN = "https://aud.statelicensingreference.com"
TODAY = datetime.now().strftime("%Y-%m-%d")
VERTICAL_SLUG = "aud"

DIST_DIR.mkdir(exist_ok=True)
CSS_DIST.parent.mkdir(parents=True, exist_ok=True)
if CSS_SRC.exists():
    shutil.copy2(CSS_SRC, CSS_DIST)
css_hash = hashlib.md5(CSS_SRC.read_bytes()).hexdigest()[:8] if CSS_SRC.exists() else "0"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), undefined=StrictUndefined, autoescape=False)
template = env.get_template("state-hub.html")

tier2_files = {f.name: f for f in CONTENT_DIR.glob("*.html")} if CONTENT_DIR.exists() else {}
states_manifest = []
urls = []
for json_file in sorted(JSON_DIR.glob("*.json")):
    data = json.loads(json_file.read_text(encoding="utf-8"))
    default_slug = data['state_slug'] if data['state_slug'].endswith(f'-{VERTICAL_SLUG}') else f"{data['state_slug']}-{VERTICAL_SLUG}"
    slug_value = data.get("slug") or default_slug
    out_name = f"{slug_value}.html"
    out_path = DIST_DIR / out_name
    if out_name in tier2_files:
        shutil.copy2(tier2_files[out_name], out_path)
    else:
        state_abbr = data.get('reciprocity', {}).get('state_abbr') or data['state_slug'][:2].upper()
        # Map state name to abbreviation for image lookup
        STATE_NAME_TO_ABBR = {"Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY","District of Columbia":"DC"}
        abbr = STATE_NAME_TO_ABBR.get(data['state_name'], '')
        hero_img = STATE_IMAGES.get(abbr, {})
        out_path.write_text(template.render(**data, hero_image_url=hero_img.get('url',''), hero_image_alt=hero_img.get('alt','')), encoding="utf-8")
    states_manifest.append({
        'name': data['state_name'],
        'slug': slug_value,
        'last_updated': data.get('last_updated', TODAY),
        'compact_label': data['reciprocity'].get('compact_name') or 'Endorsement only',
        'state_is_member': data['reciprocity']['state_is_member'],
        'endorsement_fee': data['reciprocity']['endorsement_fee'],
        'processing_time': data['reciprocity']['processing_time'],
        'processing_tier': data['reciprocity']['processing_tier'],
        'license_required': data['reciprocity'].get('license_required', True),
    })
    urls.append(f"  <url><loc>{DOMAIN}/{slug_value}</loc><lastmod>{data.get('last_updated', TODAY)}</lastmod><priority>0.8</priority></url>")

profile = json.loads((ROOT.parent / 'vertical_profiles.json').read_text(encoding='utf-8'))['verticals'][VERTICAL_SLUG]
index_html = render_index(domain=DOMAIN, profile=profile, states_manifest=states_manifest, css_hash=css_hash, today=TODAY)
(DIST_DIR / 'index.html').write_text(index_html, encoding='utf-8')
robots_txt = "User-agent: *\nAllow: /\n\nSitemap: " + DOMAIN + "/sitemap.xml\n"
(DIST_DIR / 'robots.txt').write_text(robots_txt, encoding='utf-8')
sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>' + DOMAIN + '/</loc><lastmod>' + TODAY + '</lastmod><priority>1.0</priority></url>\n' + '\n'.join(urls) + '\n</urlset>\n'
(DIST_DIR / 'sitemap.xml').write_text(sitemap_xml, encoding='utf-8')
print(f'Built {len(states_manifest)} pages for {VERTICAL_SLUG}')
