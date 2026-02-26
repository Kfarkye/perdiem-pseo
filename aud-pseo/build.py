"""
Programmatic SEO Compiler — Audiologist State Licensing Reference
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

# CSS cache-bust hash
import hashlib as _hashlib
CSS_HASH = _hashlib.md5(CSS_SRC.read_bytes()).hexdigest()[:8] if CSS_SRC.exists() else "0"

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
        slug = f"{data['state_slug']}-aud"
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
        json_slugs.add(f"{d['state_slug']}-aud.html")

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
<title>Audiologist License Requirements by State &mdash; Fees, Board Contacts &amp; How to Apply (2026)</title>
<meta name="description" content="Complete 2026 guide to audiologist (AuD) licensing requirements, fees, and board contacts for all 50 US states and DC.">
<meta name="keywords" content="audiologist license by state, audiology license requirements, AuD licensure, state audiology board, audiologist license cost, how to become an audiologist">
<link rel="canonical" href="{DOMAIN}/">
<meta property="og:title" content="Audiologist License Requirements by State (2026)">
<meta property="og:description" content="Compare audiologist licensing fees, board contacts, and application steps across all 50 states.">
<meta property="og:type" content="website">
<meta property="og:url" content="{DOMAIN}/">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="State Licensing Reference">
<meta name="robots" content="index, follow">
<link rel="stylesheet" href="/css/styles.css?v={CSS_HASH}">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300;1,9..40,400&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,400&display=swap" rel="stylesheet">
<style>
.hub-header {{ background: var(--sand-900); color: var(--sand-100); padding: var(--space-9) var(--space-7) var(--space-10); text-align: center; position: relative; overflow: hidden; }}
.hub-header::before {{ content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse 80% 60% at 20% 80%, hsla(180,50%,26%,.07) 0%, transparent 70%), radial-gradient(ellipse 60% 50% at 80% 20%, hsla(18,52%,47%,.05) 0%, transparent 70%); pointer-events: none; }}
.hub-header h1 {{ color: #fff; font-family: var(--serif); font-size: clamp(1.85rem, 4.5vw, 2.65rem); margin-bottom: var(--space-4); font-weight: 400; letter-spacing: -.025em; position: relative; }}
.hub-header em {{ color: var(--terracotta-light); font-style: italic; font-weight: 300; }}
.hub-header p {{ color: var(--sand-400); font-size: 0.88rem; max-width: 520px; margin: 0 auto; line-height: 1.6; position: relative; }}
.hub-header .overline {{ font-family: var(--sans); font-size: .58rem; font-weight: 600; letter-spacing: .18em; text-transform: uppercase; color: var(--sand-400); margin-bottom: var(--space-3); display: block; position: relative; }}
.hub-header .freshness {{ font-family: var(--sans); font-size: .68rem; color: var(--sand-400); margin-top: var(--space-5); display: flex; align-items: center; justify-content: center; gap: var(--space-3); flex-wrap: wrap; position: relative; }}
.hub-header .freshness span {{ display: inline-flex; align-items: center; gap: .3rem; }}

/* ── Filter Toolbar — contained card ── */
.filter-toolbar {{ max-width: 1000px; margin: -2.5rem auto var(--space-6); padding: var(--space-5) var(--space-6); position: relative; z-index: 2; background: #fff; border: var(--border-subtle); border-radius: var(--radius-lg); box-shadow: var(--shadow-md); }}
.filter-search {{ width: 100%; padding: .8rem 1rem; border: var(--border-default); border-radius: var(--radius-md); background: var(--sand-50); font-family: var(--sans); font-size: .86rem; color: var(--sand-900); outline: none; box-shadow: var(--shadow-xs); transition: border-color 120ms cubic-bezier(.2,0,0,1), box-shadow 180ms cubic-bezier(.2,0,0,1); }}
.filter-search:focus {{ border-color: var(--teal); box-shadow: 0 0 0 3px hsla(180,50%,26%,.1), var(--shadow-xs); }}
.filter-search-wrap {{ position: relative; }}
.filter-row {{ display: flex; align-items: center; gap: .75rem; margin-top: var(--space-3); }}
.filter-label {{ font-family: var(--sans); font-size: .62rem; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--sand-400); min-width: 56px; flex-shrink: 0; }}
.filter-pills {{ display: flex; flex-wrap: wrap; gap: var(--space-2); }}
.filter-pill {{ font-family: var(--sans); font-size: .7rem; font-weight: 500; letter-spacing: .04em; text-transform: uppercase; padding: .35rem .8rem; border: var(--border-default); border-radius: var(--radius-full); background: var(--sand-50); color: var(--sand-500); cursor: pointer; user-select: none; transition: border-color 120ms cubic-bezier(.2,0,0,1), color 120ms cubic-bezier(.2,0,0,1), background 120ms cubic-bezier(.2,0,0,1); }}
.filter-pill:hover {{ border-color: var(--teal); color: var(--teal); }}
.filter-pill.active {{ background: var(--teal); border-color: var(--teal); color: #fff; }}
.filter-count {{ font-family: var(--sans); font-size: .68rem; color: var(--sand-400); margin-top: var(--space-2); text-align: right; }}
.filter-empty {{ display: none; text-align: center; padding: var(--space-8) var(--space-4); color: var(--sand-400); font-family: var(--sans); font-size: .88rem; max-width: 1000px; margin: 0 auto; }}
.filter-empty.visible {{ display: block; }}

/* ── Boundaries micro-block ── */
.scope-block {{ max-width: 1000px; margin: 0 auto var(--space-6); padding: 0 var(--space-4); display: flex; gap: var(--space-6); justify-content: center; flex-wrap: wrap; }}
.scope-item {{ font-family: var(--sans); font-size: .78rem; color: var(--sand-500); display: flex; align-items: baseline; gap: .4rem; }}
.scope-item .scope-icon {{ font-size: .85rem; flex-shrink: 0; }}
.scope-item strong {{ color: var(--sand-700); font-weight: 600; }}

/* ── State Grid ── */
.hub-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--space-3); max-width: 1000px; margin: 0 auto var(--space-9); padding: 0 var(--space-4); position: relative; }}
.hub-grid .link-card {{ background: #fff; border: var(--border-subtle); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-5); box-shadow: var(--shadow-xs); min-height: 56px; display: flex; flex-direction: column; justify-content: center; will-change: transform; transition: transform 120ms cubic-bezier(.2,0,0,1), box-shadow 180ms cubic-bezier(.2,0,0,1), border-color 120ms cubic-bezier(.2,0,0,1); }}
.hub-grid .link-card:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: hsla(180,50%,26%,.15); }}
.hub-grid .link-card h3 {{ font-family: var(--serif); font-size: 1.02rem; font-weight: 500; color: var(--sand-900); margin: 0; transition: margin 180ms cubic-bezier(.2,0,0,1); }}
.hub-grid .link-card:hover h3 {{ margin-bottom: .3rem; }}
.hub-grid .link-card .link-card-reveal {{ max-height: 0; opacity: 0; overflow: hidden; transition: max-height 280ms cubic-bezier(.2,0,0,1), opacity 180ms cubic-bezier(.2,0,0,1); }}
.hub-grid .link-card:hover .link-card-reveal {{ max-height: 60px; opacity: 1; }}
.hub-grid .link-card .link-card-desc {{ font-size: 0.73rem; color: var(--sand-500); margin-bottom: .15rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.hub-grid .link-card .link-card-meta {{ font-size: 0.68rem; color: var(--teal); font-weight: 500; display: block; }}
.hub-grid .link-card[data-hidden="true"] {{ display: none; }}

/* ── Bottom CTA ── */
.bottom-cta {{ background: var(--sand-900); padding: var(--space-9) var(--space-7); text-align: center; position: relative; overflow: hidden; }}
.bottom-cta::before {{ content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse 60% 50% at 50% 100%, hsla(180,50%,26%,.06) 0%, transparent 70%); pointer-events: none; }}
.bottom-cta h2 {{ color: #fff; font-family: var(--serif); font-size: clamp(1.35rem, 3vw, 1.8rem); font-weight: 400; letter-spacing: -.02em; margin-bottom: var(--space-3); position: relative; }}
.bottom-cta p {{ color: var(--sand-400); font-size: .84rem; max-width: 480px; margin: 0 auto var(--space-5); line-height: 1.55; position: relative; }}
.bottom-cta .cta-select-wrap {{ max-width: 420px; margin: 0 auto; display: flex; gap: var(--space-2); position: relative; }}
.bottom-cta select {{ flex: 1; padding: .75rem 1rem; border: 1px solid hsla(0,0%,100%,.12); border-radius: var(--radius-md); background: hsla(0,0%,100%,.06); color: var(--sand-200); font-family: var(--sans); font-size: .84rem; outline: none; appearance: none; cursor: pointer; transition: border-color 120ms cubic-bezier(.2,0,0,1); }}
.bottom-cta select:focus {{ border-color: var(--teal); }}
.bottom-cta .cta-go {{ padding: .75rem 1.5rem; background: var(--teal); color: #fff; border: none; border-radius: var(--radius-md); font-family: var(--sans); font-size: .82rem; font-weight: 500; cursor: pointer; transition: background 120ms cubic-bezier(.2,0,0,1), transform 120ms cubic-bezier(.2,0,0,1); }}
.bottom-cta .cta-go:hover {{ background: var(--teal-hover); transform: translateY(-1px); }}
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
  <h1>Audiologist License<br><em>State Directory</em></h1>
  <p>State board websites are a mess. Get the real processing times, true out-of-pocket costs, and the exact instructions you need to clear compliance and lock in your next contract.</p>
  <div class="freshness">
    <span>Updated weekly</span>
    <span>&middot;</span>
    <span>Last verified: <strong>February 2026</strong></span>
    <span>&middot;</span>
    <span>Linked directly to official state boards</span>
  </div>
</header>
<main id="main-content">
  <div class="filter-toolbar">
    <div class="filter-search-wrap">
      <input type="text" class="filter-search" id="stateSearch" placeholder="Search for your next state..." autocomplete="off" />
    </div>
    <div class="filter-row">
      <span class="filter-label">Processing Time</span>
      <div class="filter-pills" data-group="time">
        <button class="filter-pill" data-filter="fastest">\u22642 Weeks</button>
        <button class="filter-pill" data-filter="2-4wk">2\u20134 Weeks</button>
        <button class="filter-pill" data-filter="4-6wk">4\u20136 Weeks</button>
        <button class="filter-pill" data-filter="6-plus">6+ Weeks</button>
      </div>
    </div>
    <div class="filter-row">
      <span class="filter-label">Total Cost</span>
      <div class="filter-pills" data-group="fee">
        <button class="filter-pill" data-filter="no-fee">No Fee</button>
        <button class="filter-pill" data-filter="under-100">Under $100</button>
        <button class="filter-pill" data-filter="100-200">$100\u2013$200</button>
        <button class="filter-pill" data-filter="over-200">Over $200</button>
      </div>
    </div>
    <div class="filter-count" id="filterCount"></div>
  </div>

  <div class="scope-block">
    <div class="scope-item"><strong>What this is:</strong> We don\'t file your paperwork. We give you the step-by-step playbook to avoid common board delays, skip the red tape, and hit your start date on time.</div>
  </div>

  <div class="hub-grid" id="hubGrid">
{cards_html}
  </div>
  <div class="filter-empty" id="filterEmpty">No states match your search. Try a different name or clear the filter.</div>
</main>

<section class="bottom-cta" aria-label="Get started">
  <h2>Don\u2019t let bad paperwork delay your first paycheck.</h2>
  <p>Select your target state to see board-sourced requirements, exact fees, and a step-by-step application roadmap.</p>
  <div class="cta-select-wrap">
    <select id="bottomStateSelect" aria-label="Select a state">
      <option value="">Select target state\u2026</option>
    </select>
    <button class="cta-go" id="bottomCtaGo">Continue \u2794</button>
  </div>
</section>

<footer>
  <div class="footer-inner">
    <div class="footer-grid">
      <div>
        <div class="footer-brand">State Licensing Reference</div>
        <p class="footer-tagline">Independent, YMYL-compliant licensing guides for audiologists across the United States.</p>
      </div>
      <div>
        <div class="footer-col-title">Popular States</div>
        <ul class="footer-links">
          <li><a href="/california-aud">California</a></li>
          <li><a href="/texas-aud">Texas</a></li>
          <li><a href="/florida-aud">Florida</a></li>
          <li><a href="/new-york-aud">New York</a></li>
        </ul>
      </div>
      <div>
        <div class="footer-col-title">More States</div>
        <ul class="footer-links">
          <li><a href="/illinois-aud">Illinois</a></li>
          <li><a href="/ohio-aud">Ohio</a></li>
          <li><a href="/georgia-aud">Georgia</a></li>
          <li><a href="/pennsylvania-aud">Pennsylvania</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="footer-disclaimer"><strong>Disclaimer:</strong> State Licensing Reference is an independent software tool and workflow resource. We are not a law firm, and we are not affiliated with ASHA, AAA, or any state or federal licensing board. While our roadmaps are board-sourced and statute-aligned, state laws change frequently. Users must always verify final regulatory requirements directly with their specific state board prior to submitting applications or fees.</p>
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

  /* Bottom CTA — populate select from state cards */
  const bottomSelect = document.getElementById('bottomStateSelect');
  const bottomGo = document.getElementById('bottomCtaGo');
  cards.forEach(c => {{
    const opt = document.createElement('option');
    opt.value = c.href;
    opt.textContent = c.querySelector('h3').textContent;
    bottomSelect.appendChild(opt);
  }});
  bottomGo.addEventListener('click', function() {{
    if (bottomSelect.value) window.location.href = bottomSelect.value;
  }});
  bottomSelect.addEventListener('change', function() {{
    if (this.value) window.location.href = this.value;
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
