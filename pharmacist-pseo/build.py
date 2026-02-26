"""
Programmatic SEO Compiler — Pharmacist State Licensing Reference
Merges JSON data + Jinja2 template → flat HTML in dist/

Key feature: Tier 2 hand-crafted overrides in content/ always win
over Jinja-compiled versions for the same slug.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, StrictUndefined

print("\n=== PROGRAMMATIC SEO COMPILER ===")

# ── PATHS ────────────────────────────────────────────────
JSON_DIR = Path("database/json")
DIST_DIR = Path("dist")
TEMPLATES_DIR = Path("src/templates")
CSS_SRC = Path("src/css/styles.css")
CSS_DIST = Path("dist/css/styles.css")
CONTENT_DIR = Path("content")
DOMAIN = "https://statelicensingreference.com"
TODAY = datetime.now().strftime("%Y-%m-%d")

DIST_DIR.mkdir(exist_ok=True)

# ── 1. COPY MASTER CSS ──────────────────────────────────
CSS_DIST.parent.mkdir(parents=True, exist_ok=True)
if CSS_SRC.exists():
    shutil.copy2(CSS_SRC, CSS_DIST)
    print(f"  CSS:      {CSS_SRC} -> {CSS_DIST} ({CSS_DIST.stat().st_size:,} bytes)")
else:
    print("  WARNING:  src/css/styles.css not found")

# ── 2. INITIALIZE JINJA (StrictUndefined) ────────────────
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    undefined=StrictUndefined,
    autoescape=False,
)

try:
    template = env.get_template("state-hub.html")
except Exception as e:
    print(f"  ERROR:    Template load failed: {e}")
    exit(1)

# ── 3. BUILD TIER 2 OVERRIDE INDEX ──────────────────────
# Any .html file in content/ overrides the compiled version
tier2_files = {}
if CONTENT_DIR.exists():
    for f in CONTENT_DIR.glob("*.html"):
        tier2_files[f.name] = f

# ── 4. COMPILE JSON -> HTML ─────────────────────────────
success_count = 0
tier2_count = 0
compiled_count = 0
states_manifest = []

for json_file in sorted(JSON_DIR.glob("*.json")):
    try:
        data = json.loads(json_file.read_text(encoding="utf-8"))
        slug = f"{data['state_slug']}-pharmacist"
        out_filename = f"{slug}.html"
        out_path = DIST_DIR / out_filename

        # Tier 2 override check
        if out_filename in tier2_files:
            shutil.copy2(tier2_files[out_filename], out_path)
            byte_size = out_path.stat().st_size
            label = "TIER2"
            tier2_count += 1
        else:
            html_output = template.render(**data)
            out_path.write_text(html_output, encoding="utf-8")
            byte_size = len(html_output.encode("utf-8"))
            label = "COMPILED"
            compiled_count += 1

        print(f"  {label:8s}  dist/{out_filename} ({byte_size:,} bytes | {data['state_name']})")
        success_count += 1

        # Extract processing time for bucketing
        fee_str = data["quick_facts"]["total_fee"]
        time_str = data["quick_facts"]["processing_time"]
        import re as _re

        # Time bucket
        week_match = _re.search(r'(\d+)', time_str)
        week_num = int(week_match.group(1)) if week_match else 0
        if 'n/a' in time_str.lower() or 'tbd' in time_str.lower() or week_num == 0:
            time_bucket = "varies"
        elif week_num <= 2:
            time_bucket = "fastest"
        elif week_num <= 4:
            time_bucket = "2-4wk"
        elif week_num <= 6:
            time_bucket = "4-6wk"
        else:
            time_bucket = "6-plus"

        # Fee bucket
        fee_match = _re.search(r'\$(\d[\d,.]*)', fee_str)
        fee_num = float(fee_match.group(1).replace(',', '')) if fee_match else 0
        
        # Invariant check: ensure breakdown sums up to total fee (MONEY correctness)
        breakdown_str = data["quick_facts"].get("fee_breakdown", "")
        if breakdown_str and "$" in breakdown_str:
            breakdown_nums = [float(match.replace(',', '')) for match in _re.findall(r'\$(\d[\d,.]*)', breakdown_str)]
            if sum(breakdown_nums) != fee_num and fee_num > 0:
                raise ValueError(f"MONEY RISK Invariant failed: {slug} fee breakdown sums to {sum(breakdown_nums)} but total_fee is {fee_num}")

        if fee_num == 0:
            fee_bucket = "no-fee"
        elif fee_num < 100:
            fee_bucket = "under-100"
        elif fee_num <= 200:
            fee_bucket = "100-200"
        else:
            fee_bucket = "over-200"

        states_manifest.append({
            "name": data["state_name"],
            "slug": slug,
            "nomenclature": data["credential_nomenclature"],
            "fee": fee_str,
            "time": time_str,
            "time_bucket": time_bucket,
            "fee_bucket": fee_bucket,
            "last_updated": data["last_updated"],
        })
    except Exception as e:
        print(f"  FAILED    {json_file.name}: {e}")

# ── 5. COPY STANDALONE TIER 2 SUB-PAGES ─────────────────
# These have no JSON (e.g., fingerprint guides, sub-topic pages)
standalone_tier2 = []
if CONTENT_DIR.exists():
    json_slugs = set()
    for f in JSON_DIR.glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        json_slugs.add(f"{d['state_slug']}-pharmacist.html")

    for content_file in sorted(CONTENT_DIR.glob("*.html")):
        if content_file.name not in json_slugs:
            shutil.copy2(content_file, DIST_DIR / content_file.name)
            byte_size = content_file.stat().st_size
            standalone_tier2.append(content_file.name)
            print(f"  TIER2     dist/{content_file.name} ({byte_size:,} bytes | standalone sub-page)")

# ── 6. GENERATE SITEMAP.XML ─────────────────────────────
sitemap_entries = []
sitemap_entries.append(
    f"  <url>\n    <loc>{DOMAIN}/</loc>\n"
    f"    <lastmod>{TODAY}</lastmod>\n"
    f"    <priority>1.0</priority>\n  </url>"
)
for s in states_manifest:
    sitemap_entries.append(
        f"  <url>\n    <loc>{DOMAIN}/{s['slug']}</loc>\n"
        f"    <lastmod>{s['last_updated']}</lastmod>\n"
        f"    <priority>0.8</priority>\n  </url>"
    )
for fname in standalone_tier2:
    slug = fname.replace(".html", "")
    sitemap_entries.append(
        f"  <url>\n    <loc>{DOMAIN}/{slug}</loc>\n"
        f"    <lastmod>{TODAY}</lastmod>\n"
        f"    <priority>0.6</priority>\n  </url>"
    )

sitemap_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "\n".join(sitemap_entries)
    + "\n</urlset>"
)
(DIST_DIR / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
print(f"  SITEMAP   dist/sitemap.xml ({len(sitemap_entries)} URLs)")

# ── 7. GENERATE ROBOTS.TXT ──────────────────────────────
robots_txt = f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n"
(DIST_DIR / "robots.txt").write_text(robots_txt, encoding="utf-8")
print("  ROBOTS    dist/robots.txt")

# ── 8. GENERATE INDEX.HTML ───────────────────────────────
sorted_states = sorted(states_manifest, key=lambda x: x["name"])
cards = []
for s in sorted_states:
    cards.append(
        f'      <a class="link-card" href="/{s["slug"]}"'
        f' data-state="{s["name"].lower()}"'
        f' data-time-bucket="{s["time_bucket"]}"'
        f' data-fee-bucket="{s["fee_bucket"]}">\n'
        f'        <h3>{s["name"]}</h3>\n'
        f'        <div class="link-card-reveal">\n'
        f'          <div class="link-card-desc">{s["nomenclature"]}</div>\n'
        f'          <span class="link-card-meta">{s["time"]} &middot; {s["fee"]}</span>\n'
        f'        </div>\n'
        f"      </a>"
    )
cards_html = "\n".join(cards)

index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pharmacist License Requirements by State &mdash; Fees, Board Contacts &amp; How to Apply (2026)</title>
<meta name="description" content="Complete 2026 guide to pharmacist licensing and registration requirements, fees, and board contacts for all 50 US states and DC.">
<meta name="keywords" content="Pharmacist license by state, PharmD license requirements, RPh license requirements, state board of pharmacy, pharmacist license cost">
<link rel="canonical" href="{DOMAIN}/">
<meta property="og:title" content="Pharmacist License Requirements by State (2026)">
<meta property="og:description" content="Compare pharmacist licensing fees, board contacts, and application steps across all 50 states.">
<meta property="og:type" content="website">
<meta property="og:url" content="{DOMAIN}/">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="State Licensing Reference">
<meta name="robots" content="index, follow">
<link rel="stylesheet" href="/css/styles.css">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300;1,9..40,400&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,400&display=swap" rel="stylesheet">
<style>
.hub-header {{ background: var(--sand-900); color: var(--sand-100); padding: 2.5rem 2rem 5rem; text-align: center; position: relative; overflow: hidden; }}
.hub-header::before {{ content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse 80% 60% at 20% 80%, rgba(46,139,139,.08) 0%, transparent 70%), radial-gradient(ellipse 60% 50% at 80% 20%, rgba(184,92,56,.06) 0%, transparent 70%); pointer-events: none; }}
.hub-header h1 {{ color: #fff; font-family: var(--serif); font-size: clamp(2rem, 5vw, 2.8rem); margin-bottom: 1rem; font-weight: 400; letter-spacing: -.02em; position: relative; }}
.hub-header em {{ color: var(--terracotta-light); font-style: italic; font-weight: 300; }}
.hub-header p {{ color: var(--sand-400); font-size: 0.92rem; max-width: 560px; margin: 0 auto; line-height: 1.6; position: relative; }}
.hub-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1px; background: var(--sand-200); border: 1px solid var(--sand-200); max-width: 1000px; margin: -2rem auto 4rem; position: relative; }}
.hub-grid .link-card {{ background: var(--sand-50); border: none; padding: 1.1rem 1.25rem; transition: all 0.25s ease; min-height: 56px; display: flex; flex-direction: column; justify-content: center; }}
.hub-grid .link-card:hover {{ background: var(--turquoise-light); }}
.hub-grid .link-card h3 {{ font-family: var(--serif); font-size: 1.05rem; font-weight: 500; color: var(--sand-900); margin: 0; transition: margin .25s ease; }}
.hub-grid .link-card:hover h3 {{ margin-bottom: .35rem; }}
/* Progressive disclosure — reveal on hover */
.hub-grid .link-card .link-card-reveal {{ max-height: 0; opacity: 0; overflow: hidden; transition: max-height .3s ease, opacity .25s ease; }}
.hub-grid .link-card:hover .link-card-reveal {{ max-height: 60px; opacity: 1; }}
.hub-grid .link-card .link-card-desc {{ font-size: 0.75rem; color: var(--sand-500); margin-bottom: .2rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.hub-grid .link-card .link-card-meta {{ font-size: 0.7rem; color: var(--turquoise); font-weight: 500; display: block; }}
.hub-grid .link-card[data-hidden="true"] {{ display: none; }}

/* ── Filter Toolbar ── */
.filter-toolbar {{ max-width: 1000px; margin: -1rem auto 0; padding: 0 1rem; position: relative; z-index: 2; }}
.filter-search {{ width: 100%; padding: .85rem 1.15rem .85rem 2.75rem; border: 1px solid var(--sand-200); background: var(--sand-50); font-family: var(--sans); font-size: .88rem; color: var(--sand-900); outline: none; transition: border-color .2s, box-shadow .2s; }}
.filter-search:focus {{ border-color: var(--turquoise); box-shadow: 0 0 0 3px rgba(46,139,139,.12); }}
.filter-search-wrap {{ position: relative; }}
.filter-search-wrap svg {{ position: absolute; left: .9rem; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: var(--sand-400); pointer-events: none; }}
.filter-row {{ display: flex; align-items: center; gap: .65rem; margin-top: .65rem; }}
.filter-label {{ font-family: var(--sans); font-size: .68rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--sand-400); min-width: 52px; flex-shrink: 0; }}
.filter-pills {{ display: flex; flex-wrap: wrap; gap: .5rem; }}
.filter-pill {{ font-family: var(--sans); font-size: .72rem; font-weight: 500; letter-spacing: .04em; text-transform: uppercase; padding: .4rem .85rem; border: 1px solid var(--sand-200); background: var(--sand-50); color: var(--sand-500); cursor: pointer; transition: all .2s; user-select: none; }}
.filter-pill:hover {{ border-color: var(--turquoise); color: var(--turquoise); }}
.filter-pill.active {{ background: var(--turquoise); border-color: var(--turquoise); color: #fff; }}
.filter-empty {{ display: none; text-align: center; padding: 3rem 1rem; color: var(--sand-400); font-family: var(--sans); font-size: .92rem; max-width: 1000px; margin: 0 auto; }}
.filter-empty.visible {{ display: block; }}
.filter-count {{ font-family: var(--sans); font-size: .72rem; color: var(--sand-400); margin-top: .5rem; text-align: right; }}
</style>
</head>
<body>

<a href="#main-content" class="skip-link">Skip to main content</a>

<nav class="site-nav" aria-label="Site navigation">
  <div class="site-nav-inner">
    <a href="/" class="site-nav-brand">State Licensing Reference</a>
    <ul class="site-nav-links">
      <li><a href="/" class="active">All States</a></li>
    </ul>
  </div>
</nav>

<header class="hub-header">
  <h1>Pharmacist License<br><em>State Directory</em></h1>
  <p>Find your state’s 2026 requirements, fees, and board contacts.</p>
</header>
<main id="main-content">
  <div class="filter-toolbar">
    <div class="filter-search-wrap">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" /></svg>
      <input type="text" class="filter-search" id="stateSearch" placeholder="Search by state name…" autocomplete="off" />
    </div>
    <div class="filter-row">
      <span class="filter-label">Timeline</span>
      <div class="filter-pills" data-group="time">
        <button class="filter-pill" data-filter="fastest">≤2 Weeks</button>
        <button class="filter-pill" data-filter="2-4wk">2–4 Weeks</button>
        <button class="filter-pill" data-filter="4-6wk">4–6 Weeks</button>
        <button class="filter-pill" data-filter="6-plus">6+ Weeks</button>
      </div>
    </div>
    <div class="filter-row">
      <span class="filter-label">Fee</span>
      <div class="filter-pills" data-group="fee">
        <button class="filter-pill" data-filter="no-fee">No Fee</button>
        <button class="filter-pill" data-filter="under-100">Under $100</button>
        <button class="filter-pill" data-filter="100-200">$100–$200</button>
        <button class="filter-pill" data-filter="over-200">Over $200</button>
      </div>
    </div>
    <div class="filter-count" id="filterCount"></div>
  </div>
  <div class="hub-grid" id="hubGrid">
{cards_html}
  </div>
  <div class="filter-empty" id="filterEmpty">No states match your search. Try a different name or clear the filter.</div>
</main>
<footer>
  <div class="footer-inner">
    <div class="footer-grid">
      <div>
        <div class="footer-brand">State Licensing Reference</div>
        <p class="footer-tagline">Independent, YMYL-compliant licensing guides for pharmacists across the United States.</p>
      </div>
      <div>
        <div class="footer-col-title">Popular States</div>
        <ul class="footer-links">
          <li><a href="/california-pharmacist">California</a></li>
          <li><a href="/texas-pharmacist">Texas</a></li>
          <li><a href="/florida-pharmacist">Florida</a></li>
          <li><a href="/new-york-pharmacist">New York</a></li>
        </ul>
      </div>
      <div>
        <div class="footer-col-title">More States</div>
        <ul class="footer-links">
          <li><a href="/illinois-pharmacist">Illinois</a></li>
          <li><a href="/ohio-pharmacist">Ohio</a></li>
          <li><a href="/georgia-pharmacist">Georgia</a></li>
          <li><a href="/pennsylvania-pharmacist">Pennsylvania</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="footer-disclaimer"><strong>Disclaimer:</strong> State Licensing Reference is an independent informational portal and is not affiliated with any government agency. Requirements and fees are subject to change. Always verify current regulations directly with the official state board.</p>
      <p class="footer-copyright">&copy; 2026 State Licensing Reference</p>
    </div>
  </div>
</footer>
<script>
(function(){{
  const search = document.getElementById('stateSearch');
  const cards = document.querySelectorAll('.hub-grid .link-card');
  const empty = document.getElementById('filterEmpty');
  const countEl = document.getElementById('filterCount');
  let activeTime = 'all';
  let activeFee = 'all';

  function applyFilters() {{
    const q = search.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach(c => {{
      const name = c.getAttribute('data-state') || '';
      const tb = c.getAttribute('data-time-bucket') || '';
      const fb = c.getAttribute('data-fee-bucket') || '';
      const matchName = !q || name.includes(q);
      const matchTime = activeTime === 'all' || tb === activeTime;
      const matchFee  = activeFee  === 'all' || fb === activeFee;
      const show = matchName && matchTime && matchFee;
      c.setAttribute('data-hidden', show ? 'false' : 'true');
      if (show) visible++;
    }});
    empty.classList.toggle('visible', visible === 0);
    if (activeTime !== 'all' || activeFee !== 'all' || q) {{
      countEl.textContent = visible + ' state' + (visible !== 1 ? 's' : '') + ' matched';
    }} else {{
      countEl.textContent = '';
    }}
  }}

  search.addEventListener('input', applyFilters);

  document.querySelectorAll('.filter-pills').forEach(group => {{
    const groupName = group.getAttribute('data-group');
    group.querySelectorAll('.filter-pill').forEach(pill => {{
      pill.addEventListener('click', function() {{
        const wasActive = this.classList.contains('active');
        group.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        if (wasActive) {{
          if (groupName === 'time') activeTime = 'all';
          else activeFee = 'all';
        }} else {{
          this.classList.add('active');
          const val = this.getAttribute('data-filter');
          if (groupName === 'time') activeTime = val;
          else activeFee = val;
        }}
        applyFilters();
      }});
    }});
  }});
}})();
</script>
</body>
</html>"""

(DIST_DIR / "index.html").write_text(index_html, encoding="utf-8")
index_bytes = len(index_html.encode("utf-8"))
print(f"  INDEX     dist/index.html ({index_bytes:,} bytes | {len(states_manifest)} state cards)")

# ── SUMMARY ──────────────────────────────────────────────
total_files = success_count + len(standalone_tier2) + 3  # +index +sitemap +robots
print(f"\n{'=' * 55}")
print(f"  Compiled from template : {compiled_count}")
print(f"  Tier 2 overrides       : {tier2_count}")
print(f"  Tier 2 standalone      : {len(standalone_tier2)}")
print(f"  Sitemap URLs           : {len(sitemap_entries)}")
print(f"  Total dist/ files      : {total_files}")
print(f"{'=' * 55}")


# --- TIER 2 EDITORIAL OVERRIDE ENFORCER ---
print("\n=== APPLYING TIER 2 EDITORIAL OVERRIDES ===")
import shutil
CONTENT_DIR = Path("content")
if CONTENT_DIR.exists():
    for override_file in CONTENT_DIR.glob("*.html"):
        dest = DIST_DIR / override_file.name
        shutil.copy2(override_file, dest)
        byte_size = override_file.stat().st_size
        print(f"💎 OVERRIDE: Copied {override_file.name} to dist/ (Protected Tier 2 | {byte_size:,} bytes)")
