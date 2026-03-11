from __future__ import annotations


def render_index(*, domain: str, profile: dict, states_manifest: list[dict], css_hash: str, today: str) -> str:
    profession = profile['identity']['title_full']
    plural = profile['identity'].get('title_plural', profession + 's')
    sorted_states = sorted(states_manifest, key=lambda item: item['name'])
    latest_verified = today
    member_count = 0
    cdr_only_count = 0
    cards = []

    for s in sorted_states:
        member = bool(s.get('state_is_member'))
        license_required = bool(s.get('license_required', True))
        member_count += 1 if member else 0
        cdr_only_count += 1 if not license_required else 0

        tier = (s.get('processing_tier') or 'slow').lower()
        if tier not in {'fast', 'mid', 'slow', 'none'}:
            tier = 'slow'

        fee_value = s.get('endorsement_fee')
        fee = int(fee_value) if isinstance(fee_value, (int, float)) else 0
        processing_time = s.get('processing_time') or 'TBD'

        if not license_required:
            path_label = 'CDR State'
            path_class = 'badge-blue'
            path_filter = 'cdr-only'
            support_line = 'No state transfer application'
            tier = 'none'
            speed_label = 'No state wait'
            speed_class = 'speed-none'
            card_note = 'Use an active CDR credential to practice.'
        elif member:
            path_label = 'Compact'
            path_class = 'badge-green'
            path_filter = 'member'
            support_line = 'Compact privilege path'
            speed_label = {
                'fast': 'Fast timeline',
                'mid': 'Moderate timeline',
                'slow': 'Longer timeline',
            }.get(tier, 'Longer timeline')
            speed_class = {
                'fast': 'speed-fast',
                'mid': 'speed-mid',
                'slow': 'speed-slow',
            }.get(tier, 'speed-slow')
            card_note = ''
        else:
            path_label = 'Endorsement'
            path_class = 'badge-gray'
            path_filter = 'non-member'
            support_line = 'State endorsement required'
            speed_label = {
                'fast': 'Fast timeline',
                'mid': 'Moderate timeline',
                'slow': 'Longer timeline',
            }.get(tier, 'Longer timeline')
            speed_class = {
                'fast': 'speed-fast',
                'mid': 'speed-mid',
                'slow': 'speed-slow',
            }.get(tier, 'speed-slow')
            card_note = ''

        note_html = f'''\n        <p class="card-note">{card_note}</p>''' if card_note else ''

        cards.append(
            f'''      <a class="link-card" href="/{s['slug']}" data-state="{s['name'].lower()}" data-name="{s['name'].lower()}" data-fee="{fee}" data-path="{path_filter}" data-tier="{tier}">\n'''
            f'''        <div class="card-top">\n'''
            f'''          <div class="card-head">\n'''
            f'''            <h3>{s['name']}</h3>\n'''
            f'''            <p>{support_line}</p>\n'''
            f'''          </div>\n'''
            f'''          <span class="badge {path_class}">{path_label}</span>\n'''
            f'''        </div>\n'''
            f'''        <div class="card-meta">\n'''
            f'''          <span class="metric metric-fee"><span class="metric-label">Fee</span><strong>${fee}</strong></span>\n'''
            f'''          <span class="metric"><span class="metric-label">Timeline</span><strong>{processing_time}</strong></span>\n'''
            f'''        </div>\n'''
            f'''        <div class="card-foot">\n'''
            f'''          <span class="speed-indicator {speed_class}"><span class="speed-dot" aria-hidden="true"></span>{speed_label}</span>\n'''
            f'''          <span class="card-link">Open guide</span>\n'''
            f'''        </div>{note_html}\n'''
            f'''      </a>'''
        )
        latest_verified = max(latest_verified, s.get('last_updated') or today)

    cards_html = '\n'.join(cards)
    title = f"{profession} License Reciprocity by State - Compact Status, Fees and Transfer Timelines (2026)"
    desc = f"Compare {plural.lower()} license reciprocity rules by state, including compact paths, CDR-only states, endorsement fees, and processing timelines."
    popular = sorted_states[:4]
    popular_links = '\n'.join(f'<li><a href="/{s["slug"]}">{s["name"]}</a></li>' for s in popular)
    total_states = len(sorted_states)

    cdr_stat = f'<span class="hero-stat">CDR states <strong>{cdr_only_count}</strong></span>' if cdr_only_count else ''
    cdr_path_filter_button = '<button type="button" class="filter-pill" data-value="cdr-only">CDR State</button>' if cdr_only_count else ''
    cdr_tier_filter_button = '<button type="button" class="filter-pill" data-value="none">CDR State</button>' if cdr_only_count else ''

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
  --idx-card: rgba(255,255,255,0.9);
  --idx-border: rgba(16,24,32,0.12);
}}
body {{
  background:
    radial-gradient(circle at top left, rgba(188,94,54,.08), transparent 28%),
    radial-gradient(circle at top right, rgba(23,59,57,.08), transparent 32%),
    #fbf7ef;
}}
a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible {{
  outline: 3px solid #2f7d89;
  outline-offset: 2px;
}}
.site-nav {{
  position: sticky;
  top: 0;
  z-index: 30;
  backdrop-filter: blur(12px);
  background: rgba(16,24,32,.86);
  border-bottom: 1px solid rgba(255,255,255,.08);
}}
.site-nav-inner {{
  max-width: 1040px;
  margin: 0 auto;
  padding: .7rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .8rem;
}}
.site-nav-links {{
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: .35rem;
}}
.site-nav-links a {{
  text-decoration: none;
  color: rgba(255,250,245,.88);
  font-size: .72rem;
  letter-spacing: .08em;
  text-transform: uppercase;
  border-radius: 999px;
  padding: .32rem .62rem;
  border: 1px solid transparent;
}}
.site-nav-links a:hover {{
  border-color: rgba(255,255,255,.16);
  background: rgba(255,255,255,.12);
}}
.reciprocity-hero {{
  padding: 5.3rem 1.5rem 3.9rem;
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
.reciprocity-toolbar {{
  max-width: 1040px;
  margin: -1.8rem auto 1.4rem;
  padding: 1rem;
  background: rgba(255,255,255,.9);
  border-radius: 22px;
  box-shadow: 0 22px 48px rgba(16,24,32,.09);
  border: 1px solid rgba(16,24,32,.08);
  position: sticky;
  top: 62px;
  z-index: 18;
  backdrop-filter: blur(12px);
}}
.toolbar-grid {{ display:grid; grid-template-columns: minmax(0,1fr); gap:.85rem; }}
.toolbar-top {{ display:grid; grid-template-columns: minmax(0,1fr) auto auto; gap:.8rem; align-items:center; }}
.reciprocity-toolbar input {{ width: 100%; padding: .95rem 1rem; border-radius: 14px; border: 1px solid rgba(16,24,32,.14); background: #fff; }}
.sort-select {{ min-height: 44px; border: 1px solid rgba(16,24,32,.18); border-radius: 12px; background:#fff; color:rgba(16,24,32,.84); font-size:.82rem; padding: .55rem .75rem; }}
.result-count {{ font-size:.83rem; color:rgba(16,24,32,.66); text-align:right; }}
.filters {{ display:grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap:.75rem; }}
.filter-group {{ border:1px solid rgba(16,24,32,.08); border-radius:14px; background:rgba(255,255,255,.7); padding:.68rem; }}
.filter-label {{ display:block; font-size:.68rem; letter-spacing:.08em; text-transform:uppercase; color:rgba(16,24,32,.56); margin-bottom:.45rem; }}
.pill-row {{ display:flex; flex-wrap:wrap; gap:.45rem; }}
.filter-pill {{ border:1px solid rgba(16,24,32,.14); background:#fff; color:rgba(16,24,32,.76); border-radius:999px; font-size:.74rem; padding:.34rem .68rem; cursor:pointer; transition: all .15s ease; }}
.filter-pill:hover {{ border-color:rgba(23,59,57,.42); color:var(--idx-forest); }}
.filter-pill.active {{ background:var(--idx-forest); color:#fff; border-color:var(--idx-forest); }}
.reciprocity-grid {{ max-width: 1040px; margin: 0 auto 2.6rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(252px, 1fr)); gap: 1rem; padding: 0 1rem; }}
.link-card {{ display: block; background: var(--idx-card); border: 1px solid var(--idx-border); border-radius: 22px; padding: 1.05rem; color: inherit; text-decoration: none; box-shadow: 0 12px 28px rgba(16,24,32,.05); backdrop-filter: blur(12px); transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease; }}
.link-card:hover {{ transform: translateY(-2px); box-shadow: 0 18px 36px rgba(16,24,32,.1); border-color: rgba(23,59,57,.2); }}
.card-top {{ display:flex; justify-content:space-between; gap:.75rem; align-items:flex-start; }}
.card-head h3 {{ margin:0 0 .32rem; font-size:1.08rem; }}
.card-head p {{ margin:0; font-size:.86rem; color:rgba(16,24,32,.67); }}
.card-meta {{ display:grid; grid-template-columns:1fr 1fr; gap:.65rem; margin-top:1rem; }}
.metric {{ background: rgba(255,255,255,.72); border: 1px solid rgba(16,24,32,.08); border-radius: 14px; padding: .72rem .8rem; }}
.metric-fee {{ border-color: rgba(188,94,54,.32); background: rgba(255,248,242,.92); }}
.metric-label {{ display:block; font-size:.69rem; letter-spacing:.07em; text-transform:uppercase; color:rgba(16,24,32,.56); margin-bottom:.2rem; }}
.metric strong {{ color:var(--idx-ink); font-family: var(--serif); font-size:1rem; line-height:1.3; }}
.card-foot {{ margin-top:.85rem; display:flex; align-items:center; justify-content:space-between; gap:.6rem; }}
.speed-indicator {{ display:inline-flex; align-items:center; gap:.42rem; font-size:.76rem; color:rgba(16,24,32,.72); }}
.speed-dot {{ width:8px; height:8px; border-radius:999px; display:inline-block; }}
.speed-fast .speed-dot {{ background:#0f6b4a; }}
.speed-mid .speed-dot {{ background:#8a6512; }}
.speed-slow .speed-dot {{ background:#8f4d2a; }}
.speed-none .speed-dot {{ background:#0f4f87; }}
.card-link {{
  font-size:.72rem;
  color:#fff;
  letter-spacing:.07em;
  text-transform:uppercase;
  background: var(--idx-forest);
  border: 1px solid var(--idx-forest);
  border-radius: 999px;
  padding: .34rem .65rem;
}}
.card-note {{ margin:.6rem 0 0; font-size:.77rem; color:rgba(16,24,32,.64); }}
.badge {{ display:inline-flex; padding:.34rem .72rem; border-radius:999px; font-size:.69rem; text-transform:uppercase; letter-spacing:.08em; font-weight:700; white-space:nowrap; }}
.badge-green {{ background:#14532d; color:#f4fff7; }}
.badge-gray {{ background:#334155; color:#f8fafc; }}
.badge-blue {{ background:#0f4f87; color:#eef7ff; }}
.empty-state {{ display:none; max-width:1040px; margin: 0 auto 2.4rem; padding: 0 1rem; }}
.empty-card {{ border:1px dashed rgba(16,24,32,.2); border-radius:18px; padding:1.1rem; background:rgba(255,255,255,.7); color:rgba(16,24,32,.72); }}
.reciprocity-footer {{ max-width: 1040px; margin: 0 auto 3rem; padding: 0 1rem 0.5rem; display:grid; grid-template-columns:minmax(0,1.1fr) minmax(260px,.9fr); gap:1rem; }}
.footer-card {{ background: rgba(255,255,255,.84); border:1px solid rgba(16,24,32,.08); border-radius:22px; box-shadow: 0 16px 36px rgba(16,24,32,.05); padding:1.2rem; }}
.footer-card h2, .footer-card h3 {{ margin-bottom:.6rem; }}
.footer-card ul {{ padding-left:1.2rem; margin:0; display:grid; gap:.45rem; }}
.footer-card p {{ margin:0; color:rgba(16,24,32,.68); }}
@media (max-width: 820px) {{
  .toolbar-top {{ grid-template-columns: minmax(0,1fr); }}
  .result-count {{ text-align:left; }}
}}
@media (max-width: 720px) {{
  .reciprocity-hero {{ padding: 4.75rem 1rem 3.4rem; }}
  .reciprocity-toolbar {{ margin: -1.4rem .85rem 1.2rem; top: 56px; }}
  .filters, .reciprocity-footer, .card-meta {{ grid-template-columns: 1fr; }}
  .reciprocity-grid {{ padding: 0 .85rem; }}
  .site-nav-inner {{ flex-wrap: wrap; }}
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
      {cdr_stat}
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
          <option value="fee">Sort: Fee (Low to High)</option>
          <option value="speed">Sort: Timeline (Fast to Slow)</option>
          <option value="state">Sort: State</option>
        </select>
        <div id="resultCount" class="result-count"></div>
      </div>
      <div class="filters">
        <div class="filter-group">
          <span class="filter-label">Path type</span>
          <div class="pill-row" data-filter-group="path">
            <button type="button" class="filter-pill active" data-value="all">All</button>
            <button type="button" class="filter-pill" data-value="member">Compact</button>
            <button type="button" class="filter-pill" data-value="non-member">Endorsement</button>
            {cdr_path_filter_button}
          </div>
        </div>
        <div class="filter-group">
          <span class="filter-label">Timeline</span>
          <div class="pill-row" data-filter-group="tier">
            <button type="button" class="filter-pill active" data-value="all">All</button>
            <button type="button" class="filter-pill" data-value="fast">Fast</button>
            <button type="button" class="filter-pill" data-value="mid">Mid</button>
            <button type="button" class="filter-pill" data-value="slow">Slow</button>
            {cdr_tier_filter_button}
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
      <p>Start with path type first: compact, endorsement, or CDR-only. Then sort by fee and timeline to shortlist states with the fastest path to your next assignment.</p>
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
const pathPills = [...document.querySelectorAll('[data-filter-group="path"] .filter-pill')];
const tierPills = [...document.querySelectorAll('[data-filter-group="tier"] .filter-pill')];

let pathFilter = 'all';
let tierFilter = 'all';

function tierRank(value) {{
  if (value === 'none') return 0;
  if (value === 'fast') return 1;
  if (value === 'mid') return 2;
  return 3;
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
  if (pathFilter !== 'all') params.set('path', pathFilter); else params.delete('path');
  if (tierFilter !== 'all') params.set('tier', tierFilter); else params.delete('tier');
  if (sortSelect.value !== 'fee') params.set('sort', sortSelect.value); else params.delete('sort');
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
    const matchesPath = pathFilter === 'all' || card.dataset.path === pathFilter;
    const matchesTier = tierFilter === 'all' || card.dataset.tier === tierFilter;
    const visible = matchesSearch && matchesPath && matchesTier;
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
for (const pill of pathPills) {{
  pill.addEventListener('click', () => {{
    pathFilter = pill.dataset.value;
    setActive(pathPills, pathFilter);
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
const pathParam = params.get('path');
const tierParam = params.get('tier');
const sortParam = params.get('sort');
if (qParam) input.value = qParam;
if (pathParam && ['all', 'member', 'non-member', 'cdr-only'].includes(pathParam)) pathFilter = pathParam;
if (tierParam && ['all', 'fast', 'mid', 'slow', 'none'].includes(tierParam)) tierFilter = tierParam;
if (sortParam && ['state', 'fee', 'speed'].includes(sortParam)) sortSelect.value = sortParam;
setActive(pathPills, pathFilter);
setActive(tierPills, tierFilter);
applyFilters();
</script>
</body>
</html>'''
