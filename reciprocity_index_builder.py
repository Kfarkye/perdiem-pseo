from __future__ import annotations


def render_index(*, domain: str, profile: dict, states_manifest: list[dict], css_hash: str, today: str) -> str:
    profession = profile['identity']['title_full']
    plural = profile['identity'].get('title_plural', profession + 's')
    sorted_states = sorted(states_manifest, key=lambda item: item['name'])
    latest_verified = today
    member_count = 0
    cards = []
    for s in sorted_states:
        member = s['state_is_member']
        member_count += 1 if member else 0
        badge_label = 'Compact' if member else 'Endorsement'
        badge_class = 'badge-green' if member else 'badge-gray'
        tier = s['processing_tier']
        tier_label = {'fast': 'Fast', 'mid': 'Mid', 'slow': 'Slow'}.get(tier, 'Slow')
        cards.append(
            f'''      <a class="link-card" href="/{s['slug']}" data-state="{s['name'].lower()}" data-name="{s['name'].lower()}" data-fee="{s['endorsement_fee']}" data-compact="{'member' if member else 'non-member'}" data-tier="{tier}">\n'''
            f'''        <div class="card-top">\n'''
            f'''          <div class="card-head">\n'''
            f'''            <h3>{s['name']}</h3>\n'''
            f'''            <p>{s['compact_label']}</p>\n'''
            f'''          </div>\n'''
            f'''          <span class="badge {badge_class}">{badge_label}</span>\n'''
            f'''        </div>\n'''
            f'''        <div class="card-meta">\n'''
            f'''          <span>Fee <strong>${s['endorsement_fee']}</strong></span>\n'''
            f'''          <span>Timeline <strong>{s['processing_time']}</strong></span>\n'''
            f'''        </div>\n'''
            f'''        <div class="card-foot">\n'''
            f'''          <span class="tier tier-{tier}">{tier_label} tier</span>\n'''
            f'''          <span class="card-link">Open State Guide ></span>\n'''
            f'''        </div>\n'''
            f'''      </a>'''
        )
        latest_verified = max(latest_verified, s.get('last_updated') or today)
    cards_html = '\n'.join(cards)
    title = f"{profession} License Reciprocity by State - Compact Status, Fees and Transfer Timelines (2026)"
    desc = f"Compare {plural.lower()} license reciprocity rules by state, including compact membership, endorsement fees, temporary license availability, and processing times."
    popular = sorted_states[:4]
    popular_links = '\n'.join(f'<li><a href="/{s["slug"]}">{s["name"]}</a></li>' for s in popular)
    total_states = len(sorted_states)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{domain}/">
<meta name="robots" content="index, follow">
<link rel="stylesheet" href="/css/styles.css?v={css_hash}">
<style>
:root {{
  --idx-ink: #101820;
  --idx-forest: #173b39;
  --idx-accent: #bc5e36;
  --idx-card: rgba(255,255,255,0.88);
  --idx-border: rgba(16,24,32,0.1);
}}
body {{
  background:
    radial-gradient(circle at top left, rgba(188,94,54,.08), transparent 28%),
    radial-gradient(circle at top right, rgba(23,59,57,.08), transparent 32%),
    #fbf7ef;
}}
a:focus-visible, button:focus-visible, input:focus-visible {{
  outline: 3px solid #2f7d89;
  outline-offset: 2px;
}}
.reciprocity-hero {{
  padding: 5.5rem 1.5rem 4rem;
  background:
    radial-gradient(circle at 18% 18%, rgba(245, 206, 182, .16), transparent 24%),
    radial-gradient(circle at 80% 24%, rgba(74, 132, 121, .18), transparent 24%),
    linear-gradient(180deg, #132622 0%, #101820 100%);
  color: #f7f3eb;
}}
.reciprocity-hero-inner {{ max-width: 1040px; margin: 0 auto; }}
.eyebrow {{ display:inline-flex; padding:.38rem .8rem; border-radius:999px; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.12); font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; color:#fff5ef; margin-bottom:1rem; }}
.reciprocity-hero h1 {{ color: #fff; max-width: 760px; margin-bottom: .9rem; }}
.reciprocity-hero p {{ max-width: 760px; color: rgba(255, 250, 245, 0.84); }}
.hero-stats {{ margin-top: 1rem; display:flex; flex-wrap:wrap; gap:.6rem; }}
.hero-stat {{ display:inline-flex; align-items:center; gap:.4rem; border:1px solid rgba(255,255,255,.16); background:rgba(255,255,255,.1); border-radius:999px; padding:.4rem .8rem; font-size:.74rem; color:#fff9f4; }}
.reciprocity-toolbar {{ max-width: 1040px; margin: -1.8rem auto 1.4rem; padding: 1rem; background: rgba(255,255,255,.86); border-radius: 22px; box-shadow: 0 22px 48px rgba(16,24,32,.08); border: 1px solid rgba(16,24,32,.08); position: relative; z-index: 3; backdrop-filter: blur(12px); }}
.toolbar-grid {{ display:grid; grid-template-columns: minmax(0,1fr); gap:.85rem; }}
.toolbar-top {{ display:grid; grid-template-columns: minmax(0,1fr) auto auto; gap:.8rem; align-items:center; }}
.reciprocity-toolbar input {{ width: 100%; padding: .95rem 1rem; border-radius: 14px; border: 1px solid rgba(16,24,32,.12); background: #fff; }}
.sort-select {{ min-height: 44px; border: 1px solid rgba(16,24,32,.14); border-radius: 12px; background:#fff; color:rgba(16,24,32,.78); font-size:.82rem; padding: .55rem .75rem; }}
.result-count {{ font-size:.83rem; color:rgba(16,24,32,.66); text-align:right; }}
.filters {{ display:grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap:.75rem; }}
.filter-group {{ border:1px solid rgba(16,24,32,.08); border-radius:14px; background:rgba(255,255,255,.68); padding:.68rem; }}
.filter-label {{ display:block; font-size:.68rem; letter-spacing:.08em; text-transform:uppercase; color:rgba(16,24,32,.56); margin-bottom:.45rem; }}
.pill-row {{ display:flex; flex-wrap:wrap; gap:.45rem; }}
.filter-pill {{ border:1px solid rgba(16,24,32,.14); background:#fff; color:rgba(16,24,32,.75); border-radius:999px; font-size:.74rem; padding:.34rem .68rem; cursor:pointer; transition: all .15s ease; }}
.filter-pill:hover {{ border-color:rgba(23,59,57,.4); color:var(--idx-forest); }}
.filter-pill.active {{ background:var(--idx-forest); color:#fff; border-color:var(--idx-forest); }}
.reciprocity-grid {{ max-width: 1040px; margin: 0 auto 2.6rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; padding: 0 1rem; }}
.link-card {{ display: block; background: var(--idx-card); border: 1px solid var(--idx-border); border-radius: 22px; padding: 1.05rem; color: inherit; text-decoration: none; box-shadow: 0 12px 28px rgba(16,24,32,.05); backdrop-filter: blur(12px); transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease; }}
.link-card:hover {{ transform: translateY(-2px); box-shadow: 0 18px 36px rgba(16,24,32,.09); border-color: rgba(23,59,57,.18); }}
.card-top {{ display:flex; justify-content:space-between; gap:.75rem; align-items:flex-start; }}
.card-head h3 {{ margin:0 0 .35rem; font-size:1.08rem; }}
.card-head p {{ margin:0; font-size:.88rem; color:rgba(16,24,32,.68); }}
.card-meta {{ display:grid; grid-template-columns:1fr 1fr; gap:.65rem; margin-top:1rem; font-size:.84rem; color:rgba(16,24,32,.66); }}
.card-meta span {{ background: rgba(255,255,255,.72); border: 1px solid rgba(16,24,32,.08); border-radius: 14px; padding: .72rem .8rem; }}
.card-meta strong {{ display:block; margin-top:.2rem; color:var(--idx-ink); font-family: var(--serif); font-size:1rem; }}
.card-foot {{ margin-top:.8rem; display:flex; align-items:center; justify-content:space-between; gap:.6rem; }}
.card-link {{ font-size:.78rem; color:var(--idx-forest); letter-spacing:.04em; text-transform:uppercase; }}
.tier {{ display:inline-flex; padding:.28rem .62rem; border-radius:999px; font-size:.68rem; letter-spacing:.08em; text-transform:uppercase; font-weight:700; }}
.tier-fast {{ background:#def5ec; color:#0f5f43; }}
.tier-mid {{ background:#fff1cf; color:#7e5d12; }}
.tier-slow {{ background:#f6e7df; color:#8f4d2a; }}
.badge {{ display:inline-flex; padding:.34rem .72rem; border-radius:999px; font-size:.7rem; text-transform:uppercase; letter-spacing:.08em; font-weight:700; white-space:nowrap; }}
.badge-green {{ background:#ddf3e5; color:#155b35; }}
.badge-gray {{ background:#e9eef1; color:#41535f; }}
.empty-state {{ display:none; max-width:1040px; margin: 0 auto 2.4rem; padding: 0 1rem; }}
.empty-card {{ border:1px dashed rgba(16,24,32,.2); border-radius:18px; padding:1.1rem; background:rgba(255,255,255,.7); color:rgba(16,24,32,.72); }}
.reciprocity-footer {{ max-width: 1040px; margin: 0 auto 3rem; padding: 0 1rem 0.5rem; display:grid; grid-template-columns:minmax(0,1.1fr) minmax(260px,.9fr); gap:1rem; }}
.footer-card {{ background: rgba(255,255,255,.84); border:1px solid rgba(16,24,32,.08); border-radius:22px; box-shadow: 0 16px 36px rgba(16,24,32,.05); padding:1.2rem; }}
.footer-card h2, .footer-card h3 {{ margin-bottom:.6rem; }}
.footer-card ul {{ padding-left:1.2rem; margin:0; display:grid; gap:.45rem; }}
.footer-card p {{ margin:0; color:rgba(16,24,32,.68); }}
@media (max-width: 720px) {{
  .reciprocity-hero {{ padding: 4.75rem 1rem 3.4rem; }}
  .reciprocity-toolbar {{ margin: -1.4rem .85rem 1.2rem; }}
  .toolbar-top, .filters, .reciprocity-footer, .card-meta {{ grid-template-columns: 1fr; }}
  .result-count {{ text-align:left; }}
  .reciprocity-grid {{ padding: 0 .85rem; }}
}}
</style>
</head>
<body>
<nav class="site-nav" aria-label="Site navigation"><div class="site-nav-inner"><a href="/" class="site-nav-brand">State Licensing Reference</a><ul class="site-nav-links"><li><a href="/">Directory</a></li><li><a href="#main-content">Tool</a></li><li><a href="#how-to-use">How It Works</a></li></ul></div></nav>
<header class="reciprocity-hero">
  <div class="reciprocity-hero-inner">
    <span class="eyebrow">License Transfer Tool</span>
    <h1>{profession} License Reciprocity by State</h1>
    <p>Compare compact participation, endorsement fees, fingerprint rules, temporary license availability, and current transfer timelines before you commit to a state.</p>
    <div class="hero-stats">
      <span class="hero-stat">States <strong>{total_states}</strong></span>
      <span class="hero-stat">Compact states <strong>{member_count}</strong></span>
      <span class="hero-stat">Updated <strong>{latest_verified}</strong></span>
    </div>
  </div>
</header>
<main id="main-content">
  <section class="reciprocity-toolbar" aria-label="Reciprocity filters">
    <div class="toolbar-grid">
      <div class="toolbar-top">
        <input id="stateSearch" type="search" placeholder="Search by state name" aria-label="Search states">
        <select id="sortSelect" class="sort-select" aria-label="Sort states">
          <option value="state">Sort: State</option>
          <option value="fee">Sort: Fee (Low to High)</option>
          <option value="speed">Sort: Timeline (Fast to Slow)</option>
        </select>
        <div id="resultCount" class="result-count"></div>
      </div>
      <div class="filters">
        <div class="filter-group">
          <span class="filter-label">Compact status</span>
          <div class="pill-row" data-filter-group="compact">
            <button type="button" class="filter-pill active" data-value="all">All</button>
            <button type="button" class="filter-pill" data-value="member">Compact</button>
            <button type="button" class="filter-pill" data-value="non-member">Endorsement</button>
          </div>
        </div>
        <div class="filter-group">
          <span class="filter-label">Processing tier</span>
          <div class="pill-row" data-filter-group="tier">
            <button type="button" class="filter-pill active" data-value="all">All</button>
            <button type="button" class="filter-pill" data-value="fast">Fast</button>
            <button type="button" class="filter-pill" data-value="mid">Mid</button>
            <button type="button" class="filter-pill" data-value="slow">Slow</button>
          </div>
        </div>
      </div>
    </div>
  </section>
  <section class="reciprocity-grid" id="reciprocityGrid">
{cards_html}
  </section>
  <section class="empty-state" id="emptyState" aria-live="polite">
    <div class="empty-card">No states match your current filters. Clear one filter or search term and try again.</div>
  </section>
  <section class="reciprocity-footer">
    <article id="how-to-use" class="footer-card">
      <h2>How to use this directory</h2>
      <p>Open your target state first. The lead section on each page answers the practical question up front: compact privilege or endorsement, total fee, fingerprinting, and how fast the board usually moves.</p>
    </article>
    <article class="footer-card">
      <h3>Popular reciprocity pages</h3>
      <ul>{popular_links}</ul>
      <p>Last refreshed {latest_verified}.</p>
    </article>
  </section>
</main>
<script>
const input = document.getElementById('stateSearch');
const cards = [...document.querySelectorAll('.link-card')];
const grid = document.getElementById('reciprocityGrid');
const sortSelect = document.getElementById('sortSelect');
const resultCount = document.getElementById('resultCount');
const emptyState = document.getElementById('emptyState');
const compactPills = [...document.querySelectorAll('[data-filter-group="compact"] .filter-pill')];
const tierPills = [...document.querySelectorAll('[data-filter-group="tier"] .filter-pill')];

let compactFilter = 'all';
let tierFilter = 'all';

function tierRank(value) {{
  if (value === 'fast') return 0;
  if (value === 'mid') return 1;
  return 2;
}}

function sortVisible(list) {{
  const mode = sortSelect.value;
  return [...list].sort((a, b) => {{
    if (mode === 'fee') return Number(a.dataset.fee) - Number(b.dataset.fee);
    if (mode === 'speed') {{
      const tierDelta = tierRank(a.dataset.tier) - tierRank(b.dataset.tier);
      if (tierDelta !== 0) return tierDelta;
      return Number(a.dataset.fee) - Number(b.dataset.fee);
    }}
    return a.dataset.name.localeCompare(b.dataset.name);
  }});
}}

function syncUrl() {{
  const params = new URLSearchParams(window.location.search);
  const q = input.value.trim();
  if (q) params.set('q', q); else params.delete('q');
  if (compactFilter !== 'all') params.set('compact', compactFilter); else params.delete('compact');
  if (tierFilter !== 'all') params.set('tier', tierFilter); else params.delete('tier');
  if (sortSelect.value !== 'state') params.set('sort', sortSelect.value); else params.delete('sort');
  const next = params.toString();
  const target = next ? `${{window.location.pathname}}?${{next}}` : window.location.pathname;
  window.history.replaceState(null, '', target);
}}

function setActive(pills, value) {{
  for (const pill of pills) {{
    pill.classList.toggle('active', pill.dataset.value === value);
  }}
}}

function applyFilters() {{
  const q = input.value.toLowerCase().trim();
  let shown = 0;
  const visibleCards = [];
  for (const card of cards) {{
    const matchesSearch = card.dataset.state.includes(q);
    const matchesCompact = compactFilter === 'all' || card.dataset.compact === compactFilter;
    const matchesTier = tierFilter === 'all' || card.dataset.tier === tierFilter;
    const visible = matchesSearch && matchesCompact && matchesTier;
    card.style.display = visible ? '' : 'none';
    if (visible) visibleCards.push(card);
    shown += visible ? 1 : 0;
  }}
  for (const card of sortVisible(visibleCards)) {{
    grid.appendChild(card);
  }}
  resultCount.textContent = `${{shown}} of ${{cards.length}} states`;
  emptyState.style.display = shown === 0 ? '' : 'none';
  syncUrl();
}}

input.addEventListener('input', applyFilters);
sortSelect.addEventListener('change', applyFilters);
for (const pill of compactPills) {{
  pill.addEventListener('click', () => {{
    compactFilter = pill.dataset.value;
    setActive(compactPills, compactFilter);
    applyFilters();
  }});
}}
for (const pill of tierPills) {{
  pill.addEventListener('click', () => {{
    tierFilter = pill.dataset.value;
    setActive(tierPills, tierFilter);
    applyFilters();
  }});
}}

const params = new URLSearchParams(window.location.search);
const qParam = params.get('q');
const compactParam = params.get('compact');
const tierParam = params.get('tier');
const sortParam = params.get('sort');
if (qParam) input.value = qParam;
if (compactParam && ['all', 'member', 'non-member'].includes(compactParam)) compactFilter = compactParam;
if (tierParam && ['all', 'fast', 'mid', 'slow'].includes(tierParam)) tierFilter = tierParam;
if (sortParam && ['state', 'fee', 'speed'].includes(sortParam)) sortSelect.value = sortParam;
setActive(compactPills, compactFilter);
setActive(tierPills, tierFilter);
applyFilters();
</script>
</body>
</html>'''
