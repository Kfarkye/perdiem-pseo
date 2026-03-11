from __future__ import annotations


def render_index(*, domain: str, profile: dict, states_manifest: list[dict], css_hash: str, today: str) -> str:
    profession = profile['identity']['title_full']
    plural = profile['identity'].get('title_plural', profession + 's')
    sorted_states = sorted(states_manifest, key=lambda item: item['name'])
    total_states = len(sorted_states)

    latest_verified = today
    member_count = 0
    cdr_state_count = 0
    cards = []

    for s in sorted_states:
        name = s['name']
        slug = s['slug']
        member = bool(s.get('state_is_member'))
        license_required = bool(s.get('license_required', True))
        fee_value = s.get('endorsement_fee')
        fee = int(fee_value) if isinstance(fee_value, (int, float)) else 0
        processing_time = s.get('processing_time') or 'TBD'
        tier = (s.get('processing_tier') or 'slow').lower()
        if tier not in {'fast', 'mid', 'slow', 'none'}:
            tier = 'slow'

        if member:
            member_count += 1
        if not license_required:
            cdr_state_count += 1

        if not license_required:
            path_label = 'CDR State'
            path_filter = 'cdr-only'
            tier = 'none'
            tier_label = 'No state wait'
            tier_class = 'tier-none'
            compact_sub = 'No state transfer application'
            meta_html = (
                '<div class="card-meta card-meta-cdr">'
                '<span>CDR credential only</span>'
                '<span>$0 state fee</span>'
                '</div>'
            )
        elif member:
            path_label = 'Compact'
            path_filter = 'member'
            tier_label = {'fast': 'Fast', 'mid': 'Moderate', 'slow': 'Long'}.get(tier, 'Long')
            tier_class = {'fast': 'tier-fast', 'mid': 'tier-mid', 'slow': 'tier-slow'}.get(tier, 'tier-slow')
            compact_sub = ''
            meta_html = (
                '<div class="card-meta">'
                f'<span><small>Fee</small><strong>${fee}</strong></span>'
                f'<span><small>Timeline</small><strong>{processing_time}</strong></span>'
                '</div>'
            )
        else:
            path_label = 'Endorsement'
            path_filter = 'non-member'
            tier_label = {'fast': 'Fast', 'mid': 'Moderate', 'slow': 'Long'}.get(tier, 'Long')
            tier_class = {'fast': 'tier-fast', 'mid': 'tier-mid', 'slow': 'tier-slow'}.get(tier, 'tier-slow')
            compact_sub = ''
            meta_html = (
                '<div class="card-meta">'
                f'<span><small>Fee</small><strong>${fee}</strong></span>'
                f'<span><small>Timeline</small><strong>{processing_time}</strong></span>'
                '</div>'
            )

        sub_html = f'''        <p class="sub">{compact_sub}</p>\n''' if compact_sub else ''

        cards.append(
            f'''      <a class="card" href="/{slug}" data-state="{name.lower()}" data-name="{name.lower()}" data-fee="{fee}" data-path="{path_filter}" data-tier="{tier}">\n'''
            f'''        <div class="card-head">\n'''
            f'''          <h3>{name}</h3>\n'''
            f'''          <span class="path">{path_label}</span>\n'''
            f'''        </div>\n'''
            f'''{sub_html}'''
            f'''        {meta_html}\n'''
            f'''        <div class="card-foot">\n'''
            f'''          <span class="tier {tier_class}">{tier_label}</span>\n'''
            f'''          <span class="open">Open guide</span>\n'''
            f'''        </div>\n'''
            f'''      </a>'''
        )

        latest_verified = max(latest_verified, s.get('last_updated') or today)

    cards_html = '\n'.join(cards)
    title = f"{profession} License Reciprocity by State - Compact Status, Fees and Transfer Timelines (2026)"
    desc = (
        f"Compare {plural.lower()} license reciprocity rules by state, including compact participation, "
        "endorsement fees, and processing timelines."
    )

    popular = sorted_states[:4]
    popular_links = '\n'.join(f'<li><a href="/{s["slug"]}">{s["name"]}</a></li>' for s in popular)

    cdr_stat = f'<span>CDR states <strong>{cdr_state_count}</strong></span>' if cdr_state_count else ''
    cdr_path_button = '<button type="button" class="pill" data-value="cdr-only">CDR State</button>' if cdr_state_count else ''
    cdr_tier_button = '<button type="button" class="pill" data-value="none">No state wait</button>' if cdr_state_count else ''

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
  --bg: #f5f5f2;
  --surface: #ffffff;
  --ink: #101316;
  --muted: #5f676f;
  --line: #d9dde1;
  --accent: #12212f;
  --compact: #0f5a3a;
  --endorsement: #36495b;
  --cdr: #0f4f87;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
}}
a {{ color: inherit; }}
a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible {{
  outline: 3px solid #2f7d89;
  outline-offset: 2px;
}}
.site-nav {{
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(245,245,242,.96);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(10px);
}}
.site-nav-inner {{
  max-width: 1100px;
  margin: 0 auto;
  padding: .85rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}}
.site-nav-brand {{
  font-size: .84rem;
  letter-spacing: .03em;
  text-decoration: none;
  color: var(--muted);
}}
.site-nav-links {{
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: .7rem;
}}
.site-nav-links a {{
  text-decoration: none;
  font-size: .74rem;
  letter-spacing: .07em;
  text-transform: uppercase;
  color: #3d4650;
}}
.hero {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.2rem 1rem 1.2rem;
}}
.hero h1 {{
  margin: 0 0 .55rem;
  font-size: clamp(1.55rem, 2.8vw, 2.15rem);
  letter-spacing: -.02em;
}}
.hero p {{
  margin: 0;
  max-width: 72ch;
  color: var(--muted);
  line-height: 1.55;
}}
.hero-stats {{
  margin-top: .95rem;
  display: flex;
  flex-wrap: wrap;
  gap: .8rem;
  color: #49525b;
  font-size: .8rem;
}}
.hero-stats span {{
  padding-right: .8rem;
  border-right: 1px solid var(--line);
}}
.hero-stats span:last-child {{ border-right: 0; padding-right: 0; }}
main {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1rem 2.4rem;
}}
.toolbar {{
  position: sticky;
  top: 58px;
  z-index: 20;
  background: rgba(245,245,242,.96);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: .9rem;
  backdrop-filter: blur(8px);
}}
.toolbar-top {{
  display: grid;
  grid-template-columns: minmax(0,1fr) auto auto;
  gap: .65rem;
  align-items: center;
}}
.toolbar input, .toolbar select {{
  min-height: 42px;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: .65rem .78rem;
  background: var(--surface);
  color: var(--ink);
}}
.result-count {{
  font-size: .8rem;
  color: var(--muted);
  text-align: right;
}}
.filters {{
  margin-top: .7rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: .65rem;
}}
.filter-box {{
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--surface);
  padding: .6rem;
}}
.filter-label {{
  display: block;
  margin-bottom: .45rem;
  font-size: .67rem;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: #6a737d;
}}
.pill-row {{ display: flex; flex-wrap: wrap; gap: .4rem; }}
.pill {{
  border: 1px solid var(--line);
  background: #fff;
  color: #3f4852;
  border-radius: 999px;
  font-size: .72rem;
  padding: .28rem .6rem;
  cursor: pointer;
}}
.pill.active {{
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}}
.grid {{
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(255px, 1fr));
  gap: .75rem;
}}
.card {{
  display: block;
  text-decoration: none;
  color: inherit;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: .88rem;
  transition: border-color .15s ease, transform .15s ease;
}}
.card:hover {{
  transform: translateY(-1px);
  border-color: #aeb6be;
}}
.card-head {{
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: .55rem;
}}
.card h3 {{
  margin: 0;
  font-size: 1.04rem;
}}
.path {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: .2rem .52rem;
  border-radius: 999px;
  font-size: .64rem;
  text-transform: uppercase;
  letter-spacing: .08em;
  font-weight: 700;
  color: #fff;
  background: var(--endorsement);
}}
.card[data-path="member"] .path {{ background: var(--compact); }}
.card[data-path="cdr-only"] .path {{ background: var(--cdr); }}
.sub {{
  margin: .38rem 0 .55rem;
  font-size: .78rem;
  color: var(--muted);
}}
.card-meta {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: .5rem;
}}
.card-meta span {{
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: .54rem .62rem;
  background: #fff;
}}
.card-meta small {{
  display: block;
  font-size: .64rem;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: #6e7781;
  margin-bottom: .15rem;
}}
.card-meta strong {{
  font-size: .94rem;
  color: var(--ink);
}}
.card-meta-cdr {{ grid-template-columns: 1fr 1fr; }}
.card-meta-cdr span {{
  font-size: .75rem;
  color: #1f4f78;
  border-color: #c7d9ea;
  background: #f3f8fd;
}}
.card-foot {{
  margin-top: .62rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .5rem;
}}
.tier {{
  display: inline-flex;
  align-items: center;
  font-size: .72rem;
  color: #4f5861;
}}
.tier::before {{
  content: '';
  width: 7px;
  height: 7px;
  border-radius: 999px;
  margin-right: .35rem;
  background: #8b949e;
}}
.tier-fast::before {{ background: #0f6b4a; }}
.tier-mid::before {{ background: #8a6512; }}
.tier-slow::before {{ background: #8f4d2a; }}
.tier-none::before {{ background: #0f4f87; }}
.open {{
  font-size: .68rem;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--accent);
}}
.empty {{
  display: none;
  margin-top: 1rem;
  border: 1px dashed #b9c0c7;
  border-radius: 12px;
  padding: .9rem;
  color: var(--muted);
  background: #fff;
}}
.footer {{
  margin-top: 1.1rem;
  display: grid;
  grid-template-columns: 1.2fr .8fr;
  gap: .7rem;
}}
.footer section {{
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #fff;
  padding: .9rem;
}}
.footer h2, .footer h3 {{ margin: 0 0 .45rem; font-size: 1rem; }}
.footer p {{ margin: 0; color: var(--muted); font-size: .88rem; line-height: 1.5; }}
.footer ul {{ margin: 0; padding-left: 1.1rem; display: grid; gap: .35rem; }}
@media (max-width: 860px) {{
  .toolbar-top {{ grid-template-columns: 1fr; }}
  .result-count {{ text-align: left; }}
  .filters, .footer {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 720px) {{
  .site-nav-inner {{ flex-wrap: wrap; }}
  .toolbar {{ top: 54px; }}
}}
</style>
</head>
<body>
<nav class="site-nav" aria-label="Site navigation">
  <div class="site-nav-inner">
    <a href="/" class="site-nav-brand">State Licensing Reference</a>
    <ul class="site-nav-links">
      <li><a href="/">Directory</a></li>
      <li><a href="#main-content">Tool</a></li>
      <li><a href="#how-to-use">How It Works</a></li>
    </ul>
  </div>
</nav>
<header class="hero">
  <h1>{profession} License Reciprocity by State</h1>
  <p>Find your fastest path to practice: compact privilege, endorsement, or CDR State route.</p>
  <div class="hero-stats">
    <span>States <strong>{total_states}</strong></span>
    <span>Compact states <strong>{member_count}</strong></span>
    {cdr_stat}
    <span>Updated <strong>{latest_verified}</strong></span>
  </div>
</header>
<main id="main-content">
  <section class="toolbar" aria-label="Reciprocity filters">
    <div class="toolbar-top">
      <input id="stateSearch" type="search" placeholder="Search state" aria-label="Search states">
      <select id="sortSelect" aria-label="Sort states">
        <option value="fee">Sort: Fee (Low to High)</option>
        <option value="speed">Sort: Timeline (Fast to Slow)</option>
        <option value="state">Sort: State</option>
      </select>
      <div id="resultCount" class="result-count"></div>
    </div>
    <div class="filters">
      <div class="filter-box">
        <span class="filter-label">Path</span>
        <div class="pill-row" data-filter-group="path">
          <button type="button" class="pill active" data-value="all">All</button>
          <button type="button" class="pill" data-value="member">Compact</button>
          <button type="button" class="pill" data-value="non-member">Endorsement</button>
          {cdr_path_button}
        </div>
      </div>
      <div class="filter-box">
        <span class="filter-label">Timeline</span>
        <div class="pill-row" data-filter-group="tier">
          <button type="button" class="pill active" data-value="all">All</button>
          <button type="button" class="pill" data-value="fast">Fast</button>
          <button type="button" class="pill" data-value="mid">Mid</button>
          <button type="button" class="pill" data-value="slow">Slow</button>
          {cdr_tier_button}
        </div>
      </div>
    </div>
  </section>

  <section class="grid" id="reciprocityGrid">
{cards_html}
  </section>

  <section class="empty" id="emptyState" aria-live="polite">
    No states match your filters. Clear one filter and try again.
  </section>

  <section class="footer">
    <section id="how-to-use">
      <h2>How to use this directory</h2>
      <p>Filter by path first, then sort by fee or speed. Open a state guide to confirm board steps, documents, and renewal requirements.</p>
    </section>
    <section>
      <h3>Popular states</h3>
      <ul>{popular_links}</ul>
      <p>Last refreshed {latest_verified}.</p>
    </section>
  </section>
</main>

<script>
const input = document.getElementById('stateSearch');
const cards = [...document.querySelectorAll('.card')];
const grid = document.getElementById('reciprocityGrid');
const sortSelect = document.getElementById('sortSelect');
const resultCount = document.getElementById('resultCount');
const emptyState = document.getElementById('emptyState');
const pathPills = [...document.querySelectorAll('[data-filter-group="path"] .pill')];
const tierPills = [...document.querySelectorAll('[data-filter-group="tier"] .pill')];

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
  const visibleCards = [];
  let shown = 0;

  for (const card of cards) {{
    const matchesSearch = card.dataset.state.includes(q);
    const matchesPath = pathFilter === 'all' || card.dataset.path === pathFilter;
    const matchesTier = tierFilter === 'all' || card.dataset.tier === tierFilter;
    const visible = matchesSearch && matchesPath && matchesTier;
    card.style.display = visible ? '' : 'none';
    if (visible) visibleCards.push(card);
    if (visible) shown += 1;
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
