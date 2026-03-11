from __future__ import annotations


def render_index(*, domain: str, profile: dict, states_manifest: list[dict], css_hash: str, today: str) -> str:
    profession = profile['identity']['title_full']
    plural = profile['identity'].get('title_plural', profession + 's')
    sorted_states = sorted(states_manifest, key=lambda item: item['name'])
    total_states = len(sorted_states)

    latest_verified = today
    compact_states = []
    endorsement_states = []
    cdr_states = []

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

        latest_verified = max(latest_verified, s.get('last_updated') or today)

        entry = {
            'name': name,
            'slug': slug,
            'fee': fee,
            'processing_time': processing_time,
            'tier': tier,
            'member': member,
            'license_required': license_required,
        }

        if not license_required:
            entry['tier'] = 'none'
            cdr_states.append(entry)
        elif member:
            compact_states.append(entry)
        else:
            endorsement_states.append(entry)

    member_count = len(compact_states)
    cdr_state_count = len(cdr_states)
    endorsement_count = len(endorsement_states)

    def render_row(s):
        tier = s['tier']

        tier_label = {
            'fast': 'Fast',
            'mid': 'Moderate',
            'slow': 'Long',
            'none': 'None',
        }.get(tier, 'Long')

        if not s['license_required']:
            fee_display = '\u2014'
            time_display = 'No state app'
        else:
            fee_display = f"${s['fee']}"
            time_display = s['processing_time']

        return (
            f'<a class="row" href="/{s["slug"]}" data-state="{s["name"].lower()}" '
            f'data-fee="{s["fee"]}" data-tier="{tier}" '
            f'data-path="{"cdr-only" if not s["license_required"] else "member" if s["member"] else "non-member"}">\n'
            f'  <span class="r-name">{s["name"]}</span>\n'
            f'  <span class="r-fee">{fee_display}</span>\n'
            f'  <span class="r-time">{time_display}</span>\n'
            f'  <span class="r-speed"><span class="badge badge-{tier}">{tier_label}</span></span>\n'
            f'  <span class="r-chevron"><svg width="8" height="13" viewBox="0 0 8 13" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1.5 1.5L6.5 6.5L1.5 11.5"/></svg></span>\n'
            f'</a>'
        )

    compact_rows = '\n'.join(render_row(s) for s in compact_states)
    endorsement_rows = '\n'.join(render_row(s) for s in endorsement_states)
    cdr_rows = '\n'.join(render_row(s) for s in cdr_states)

    title = f"{profession} License Reciprocity by State - Compact Status, Fees and Transfer Timelines (2026)"
    desc = (
        f"Compare {plural.lower()} license reciprocity rules by state, including compact participation, "
        "endorsement fees, and processing timelines."
    )

    cdr_section = ''
    cdr_filter_pill = ''
    cdr_stat_block = ''
    if cdr_state_count:
        cdr_section = f'''
  <section class="group" id="group-cdr">
    <div class="group-header">
      <h2>CDR States</h2>
      <span class="group-count">{cdr_state_count}</span>
    </div>
    <p class="group-desc">No state license required \u2014 national CDR credential only.</p>
    <div class="group-head-row">
      <span>State</span>
      <span>Fee</span>
      <span>Timeline</span>
      <span>Speed</span>
      <span></span>
    </div>
    <div class="group-rows" data-group="cdr-only">
{cdr_rows}
    </div>
  </section>'''
        cdr_filter_pill = '<button type="button" class="seg-btn" data-value="cdr-only">CDR</button>'
        cdr_stat_block = f'''
      <div class="stat">
        <span class="stat-value">{cdr_state_count}</span>
        <span class="stat-label">CDR States</span>
      </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{domain}/">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#F5F5F7">
<style>
/* ── RESET ──────────────────────────────────── */
*,*::before,*::after {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 0; }}
a {{ text-decoration: none; color: inherit; -webkit-tap-highlight-color: transparent; }}
button {{ font-family: inherit; cursor: pointer; -webkit-tap-highlight-color: transparent; }}
ul {{ list-style: none; margin: 0; padding: 0; }}

/* ── APPLE/FIGMA DESIGN TOKENS ─────────────── */
:root {{
  --font-sans: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-display: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  
  --bg-color: #F5F5F7;
  --surface: #FFFFFF;
  --surface-hover: #FBFBFD;
  
  --text-primary: #1D1D1F;
  --text-secondary: #86868B;
  --text-tertiary: #A1A1A6;
  
  --primary: #0071E3;
  --focus-ring: rgba(0, 113, 227, 0.3);
  
  --border: rgba(0, 0, 0, 0.08);
  --border-strong: rgba(0, 0, 0, 0.12);
  --divider: rgba(0, 0, 0, 0.06);
  
  --radius-lg: 16px;
  --radius-md: 10px;
  --radius-sm: 8px;
  
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.02);
  --shadow-card: 0 2px 8px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
  --shadow-seg: 0 3px 8px rgba(0,0,0,0.12), 0 3px 1px rgba(0,0,0,0.04);
  --shadow-float: 0 8px 32px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04);
  
  --transition: 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
}}

html {{ scroll-behavior: smooth; }}

body {{
  font-family: var(--font-sans);
  background: var(--bg-color);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  line-height: 1.5;
  letter-spacing: -0.01em;
}}

h1, h2, h3, h4, .stat-value {{ font-family: var(--font-display); }}

a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible {{
  outline: 2px solid var(--primary);
  outline-offset: 2px;
  border-radius: 4px;
}}

/* ── NAV ────────────────────────────────────── */
.nav {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem;
}}
.nav-brand {{
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}}
.nav-links {{ display: flex; gap: 1.5rem; }}
.nav-links a {{
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: color var(--transition);
}}
.nav-links a:hover {{ color: var(--text-primary); }}

/* ── HERO ───────────────────────────────────── */
.hero-wrapper {{
  padding: 3.5rem 1.5rem 2.5rem;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}}
.hero-wrapper h1 {{
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 700;
  letter-spacing: -0.04em;
  line-height: 1.1;
  margin: 0 0 1rem;
  color: var(--text-primary);
}}
.hero-sub {{
  font-size: 1.15rem;
  color: var(--text-secondary);
  line-height: 1.5;
  max-width: 55ch;
  margin: 0 auto;
  font-weight: 400;
}}
.stats {{
  display: flex;
  justify-content: center;
  gap: 1.25rem;
  margin-top: 2.5rem;
  flex-wrap: wrap;
}}
.stat {{
  background: var(--surface);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  min-width: 140px;
  flex: 1;
  max-width: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}}
.stat-value {{
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.04em;
  color: var(--text-primary);
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}}
.stat-label {{
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
}}

/* ── TOOLBAR (GLASSMORPHIC) ─────────────────── */
.toolbar-wrap {{
  position: sticky;
  top: 1.5rem;
  z-index: 50;
  max-width: 860px;
  margin: 0 auto 3.5rem;
  padding: 0 1.5rem;
  pointer-events: none;
}}
.toolbar {{
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: var(--shadow-float);
  pointer-events: auto;
}}
.search-wrap {{
  flex: 1;
  min-width: 180px;
  position: relative;
}}
.search-icon {{
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  pointer-events: none;
}}
.search-input {{
  width: 100%;
  height: 36px;
  padding: 0 12px 0 36px;
  background: rgba(118, 118, 128, 0.08);
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 15px;
  font-family: inherit;
  transition: all var(--transition);
}}
.search-input::placeholder {{ color: var(--text-secondary); }}
.search-input:focus {{
  background: var(--surface);
  box-shadow: 0 0 0 2px var(--focus-ring);
  outline: none;
}}
.seg-group {{
  display: flex;
  background: rgba(118, 118, 128, 0.1);
  border-radius: var(--radius-md);
  padding: 2px;
  gap: 2px;
}}
.seg-btn {{
  height: 32px;
  padding: 0 14px;
  border: none;
  background: transparent;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  transition: all var(--transition);
  white-space: nowrap;
}}
.seg-btn:hover:not(.active) {{ color: var(--text-primary); }}
.seg-btn.active {{
  background: var(--surface);
  color: var(--text-primary);
  font-weight: 600;
  box-shadow: var(--shadow-seg);
}}
.sort-select {{
  height: 36px;
  padding: 0 32px 0 14px;
  background: rgba(118, 118, 128, 0.08);
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L5 5L9 1' stroke='%2386868B' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  transition: all var(--transition);
}}
.sort-select:focus {{
  background: var(--surface);
  box-shadow: 0 0 0 2px var(--focus-ring);
  outline: none;
}}
.result-count {{
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  padding: 0 8px;
  font-variant-numeric: tabular-nums;
}}

/* ── CONTENT (iOS SETTINGS STYLE) ───────────── */
.content {{
  max-width: 860px;
  margin: 0 auto;
  padding: 0 1.5rem 4rem;
}}
.group {{ margin-bottom: 3.5rem; }}
.group-header {{
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 8px;
  padding: 0 8px;
}}
.group-header h2 {{
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
  margin: 0;
}}
.group-count {{
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  background: rgba(118, 118, 128, 0.08);
  padding: 2px 8px;
  border-radius: 99px;
  font-variant-numeric: tabular-nums;
}}
.group-desc {{
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0 0 20px 8px;
}}
.group-head-row {{
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr 1fr 32px;
  padding: 0 24px 8px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-secondary);
}}
.group-rows {{
  background: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--border);
  overflow: hidden;
}}
.row {{
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr 1fr 32px;
  align-items: center;
  padding: 16px 24px;
  position: relative;
  transition: background var(--transition);
}}
.row::after {{
  content: "";
  position: absolute;
  bottom: 0;
  left: 24px;
  right: 0;
  height: 1px;
  background: var(--divider);
}}
.row.last-visible::after {{ display: none; }}
.row:hover {{ background: var(--surface-hover); }}
.row:active {{ background: rgba(0,0,0,0.03); }}

.r-name {{ font-size: 16px; font-weight: 600; color: var(--text-primary); }}
.r-fee {{ font-size: 15px; font-weight: 500; color: var(--text-primary); font-variant-numeric: tabular-nums; }}
.r-time {{ font-size: 15px; color: var(--text-secondary); }}
.r-speed {{ display: flex; align-items: center; }}
.r-chevron {{
  display: flex;
  justify-content: flex-end;
  color: #C7C7CC;
  transition: transform var(--transition), color var(--transition);
}}
.row:hover .r-chevron {{
  transform: translateX(3px);
  color: var(--text-secondary);
}}

/* ── BADGES ─────────────────────────────────── */
.badge {{
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.01em;
}}
.badge-fast {{ background: rgba(52, 199, 89, 0.15); color: #14833D; }}
.badge-mid  {{ background: rgba(255, 149, 0, 0.15); color: #B25000; }}
.badge-slow {{ background: rgba(255, 59, 48, 0.12); color: #C00F0C; }}
.badge-none {{ background: rgba(142, 142, 147, 0.15); color: var(--text-secondary); }}

/* ── EMPTY STATE ────────────────────────────── */
.empty {{
  display: none;
  text-align: center;
  padding: 5rem 2rem;
  background: var(--surface);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--border-strong);
  box-shadow: var(--shadow-sm);
  margin-bottom: 2rem;
}}
.empty svg {{ width: 40px; height: 40px; color: var(--text-tertiary); margin-bottom: 1rem; }}
.empty h3 {{ font-size: 18px; font-weight: 600; margin: 0 0 8px; color: var(--text-primary); }}
.empty p {{ font-size: 15px; color: var(--text-secondary); margin: 0; }}

/* ── FOOTER ─────────────────────────────────── */
.foot-wrapper {{
  border-top: 1px solid var(--border-strong);
  background: var(--surface);
  padding: 3.5rem 1.5rem 4rem;
  margin-top: 2rem;
}}
.foot {{
  max-width: 860px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 4rem;
}}
.foot h2, .foot h3 {{ font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0 0 12px; }}
.foot p {{ font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin: 0; }}
.foot ul {{ display: grid; gap: 10px; }}
.foot li a {{ font-size: 14px; color: var(--primary); font-weight: 500; transition: opacity var(--transition); }}
.foot li a:hover {{ opacity: 0.8; }}
.foot-meta {{ font-size: 12px; color: var(--text-tertiary); margin-top: 1.5rem !important; }}

/* ── RESPONSIVE ─────────────────────────────── */
@media (max-width: 860px) {{
  .toolbar-wrap {{ top: 1rem; }}
  .toolbar {{ flex-wrap: wrap; padding: 10px; }}
  .search-wrap {{ width: 100%; flex: none; order: 1; }}
  .seg-group {{ flex: 1; justify-content: space-between; order: 2; }}
  .seg-btn {{ flex: 1; padding: 0; text-align: center; }}
  .sort-select {{ flex: 1; order: 3; }}
  .result-count {{ display: none; }}
}}

@media (max-width: 640px) {{
  .hero-wrapper {{ padding: 2rem 1rem 1rem; }}
  .stats {{ gap: 1rem; }}
  .stat {{ min-width: 40%; padding: 1rem; }}
  
  .group-head-row {{ display: none; }}
  .row {{
    grid-template-columns: 1fr auto 24px;
    grid-template-areas:
      "name fee chevron"
      "time speed chevron";
    gap: 6px 12px;
    padding: 16px 20px;
  }}
  .row::after {{ left: 20px; }}
  .r-name {{ grid-area: name; font-size: 16px; }}
  .r-fee {{ grid-area: fee; text-align: right; }}
  .r-fee::before {{ content: 'Fee: '; color: var(--text-tertiary); font-weight: 400; }}
  .r-time {{ grid-area: time; font-size: 13px; }}
  .r-speed {{ grid-area: speed; justify-content: flex-end; }}
  .r-chevron {{ grid-area: chevron; align-self: center; transform: none !important; color: #C7C7CC !important; }}
  
  .foot {{ grid-template-columns: 1fr; gap: 2.5rem; }}
}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ transition: none !important; }}
}}
</style>
</head>
<body>
<nav class="nav" aria-label="Site navigation">
  <div class="nav-brand">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
    State Licensing Reference
  </div>
  <div class="nav-links">
    <a href="/">Directory</a>
    <a href="#how-to-use">How It Works</a>
  </div>
</nav>

<header class="hero-wrapper">
  <div>
    <h1>{profession} License<br>Reciprocity by State</h1>
    <p class="hero-sub">Compare compact privileges, endorsement fees, and processing timelines across all {total_states} states and DC.</p>
    <div class="stats">
      <div class="stat">
        <span class="stat-value">{total_states}</span>
        <span class="stat-label">Jurisdictions</span>
      </div>
      <div class="stat">
        <span class="stat-value">{member_count}</span>
        <span class="stat-label">Compact States</span>
      </div>{cdr_stat_block}
      <div class="stat">
        <span class="stat-value">{latest_verified}</span>
        <span class="stat-label">Verified</span>
      </div>
    </div>
  </div>
</header>

<div class="toolbar-wrap">
  <div class="toolbar" role="search">
    <div class="search-wrap">
      <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="7" cy="7" r="5"/><path d="M11 11L15 15"/></svg>
      <input id="stateSearch" class="search-input" type="search" placeholder="Search states..." aria-label="Search states">
    </div>
    <div class="seg-group" data-filter-group="path" role="group" aria-label="Filter by path">
      <button type="button" class="seg-btn active" data-value="all">All</button>
      <button type="button" class="seg-btn" data-value="member">Compact</button>
      <button type="button" class="seg-btn" data-value="non-member">Endorsement</button>
      {cdr_filter_pill}
    </div>
    <select id="sortSelect" class="sort-select" aria-label="Sort states">
      <option value="state">Sort: A &ndash; Z</option>
      <option value="fee">Sort: Fee</option>
      <option value="speed">Sort: Speed</option>
    </select>
    <span id="resultCount" class="result-count"></span>
  </div>
</div>

<main class="content" id="main-content">
  <section class="group" id="group-compact">
    <div class="group-header">
      <h2>Compact States</h2>
      <span class="group-count">{member_count}</span>
    </div>
    <p class="group-desc">Your home-state license may already cover these states via compact privilege.</p>
    <div class="group-head-row">
      <span>State</span>
      <span>Fee</span>
      <span>Timeline</span>
      <span>Speed</span>
      <span></span>
    </div>
    <div class="group-rows" data-group="member">
{compact_rows}
    </div>
  </section>

  <section class="group" id="group-endorsement">
    <div class="group-header">
      <h2>Endorsement States</h2>
      <span class="group-count">{endorsement_count}</span>
    </div>
    <p class="group-desc">Requires a separate board application with fee and processing time.</p>
    <div class="group-head-row">
      <span>State</span>
      <span>Fee</span>
      <span>Timeline</span>
      <span>Speed</span>
      <span></span>
    </div>
    <div class="group-rows" data-group="non-member">
{endorsement_rows}
    </div>
  </section>
{cdr_section}

  <section class="empty" id="emptyState" aria-live="polite">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
    </svg>
    <h3>No States Found</h3>
    <p>Try adjusting your search or clearing your filters.</p>
  </section>
</main>

<div class="foot-wrapper">
  <section class="foot" id="how-to-use">
    <div>
      <h2>How to use this directory</h2>
      <p>Start with the path filter to narrow by compact, endorsement, or CDR. Sort by fee or speed to find your fastest or cheapest route. Open any state to see the full board-verified guide with steps, documents, and renewal info.</p>
    </div>
    <div>
      <h3>Quick links</h3>
      <ul>
        <li><a href="#group-compact">Compact states</a></li>
        <li><a href="#group-endorsement">Endorsement states</a></li>
      </ul>
      <p class="foot-meta">Last refreshed {latest_verified}</p>
    </div>
  </section>
</div>

<script>
const input = document.getElementById('stateSearch');
const allRows = [...document.querySelectorAll('.row')];
const groups = [...document.querySelectorAll('.group')];
const sortSelect = document.getElementById('sortSelect');
const resultCount = document.getElementById('resultCount');
const emptyState = document.getElementById('emptyState');
const pathBtns = [...document.querySelectorAll('[data-filter-group="path"] .seg-btn')];

let pathFilter = 'all';

function tierRank(v) {{
  if (v === 'none') return 0;
  if (v === 'fast') return 1;
  if (v === 'mid') return 2;
  return 3;
}}

function sortRows(rows) {{
  const mode = sortSelect.value;
  return [...rows].sort((a, b) => {{
    if (mode === 'fee') return Number(a.dataset.fee) - Number(b.dataset.fee);
    if (mode === 'speed') {{
      const d = tierRank(a.dataset.tier) - tierRank(b.dataset.tier);
      if (d !== 0) return d;
      return Number(a.dataset.fee) - Number(b.dataset.fee);
    }}
    return a.dataset.state.localeCompare(b.dataset.state);
  }});
}}

function syncUrl() {{
  const params = new URLSearchParams(window.location.search);
  const q = input.value.trim();
  if (q) params.set('q', q); else params.delete('q');
  if (pathFilter !== 'all') params.set('path', pathFilter); else params.delete('path');
  if (sortSelect.value !== 'state') params.set('sort', sortSelect.value); else params.delete('sort');
  const next = params.toString();
  const target = next ? `${{window.location.pathname}}?${{next}}` : window.location.pathname;
  window.history.replaceState(null, '', target);
}}

function applyFilters() {{
  const q = input.value.toLowerCase().trim();
  let shown = 0;

  for (const row of allRows) {{
    const matchQ = row.dataset.state.includes(q);
    const matchP = pathFilter === 'all' || row.dataset.path === pathFilter;
    const visible = matchQ && matchP;
    row.style.display = visible ? '' : 'none';
    if (visible) shown++;
  }}

  document.querySelectorAll('.group-rows').forEach(container => {{
    const visible = [...container.querySelectorAll('.row')].filter(r => r.style.display !== 'none');
    const hidden = [...container.querySelectorAll('.row')].filter(r => r.style.display === 'none');
    
    const sortedVisible = sortRows(visible);
    
    // Sort and fix the inset bottom border for the last visible row
    for (const r of sortedVisible) {{
      r.classList.remove('last-visible');
      container.appendChild(r);
    }}
    if (sortedVisible.length > 0) {{
      sortedVisible[sortedVisible.length - 1].classList.add('last-visible');
    }}
    
    // Keep hidden nodes at the bottom of the DOM so they don't break :last-child layout logic
    for (const r of hidden) {{
      r.classList.remove('last-visible');
      container.appendChild(r);
    }}
  }});

  for (const g of groups) {{
    const container = g.querySelector('.group-rows');
    if (!container) continue;
    const hasVisible = [...container.querySelectorAll('.row')].some(r => r.style.display !== 'none');
    g.style.display = hasVisible ? '' : 'none';
  }}

  resultCount.textContent = `${{shown}} result${{shown === 1 ? '' : 's'}}`;
  emptyState.style.display = shown === 0 ? 'block' : 'none';
  syncUrl();
}}

input.addEventListener('input', applyFilters);
sortSelect.addEventListener('change', applyFilters);

for (const btn of pathBtns) {{
  btn.addEventListener('click', () => {{
    pathFilter = btn.dataset.value;
    for (const b of pathBtns) b.classList.toggle('active', b.dataset.value === pathFilter);
    applyFilters();
  }});
}}

const params = new URLSearchParams(window.location.search);
if (params.get('q')) input.value = params.get('q');
if (params.get('path') && ['all','member','non-member','cdr-only'].includes(params.get('path'))) pathFilter = params.get('path');
if (params.get('sort') && ['state','fee','speed'].includes(params.get('sort'))) sortSelect.value = params.get('sort');
for (const b of pathBtns) b.classList.toggle('active', b.dataset.value === pathFilter);
applyFilters();
</script>
</body>
</html>'''
