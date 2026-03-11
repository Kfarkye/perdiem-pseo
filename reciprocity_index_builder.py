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
            f'  <span class="r-time">{time_display}</span>\n'
            f'  <span class="r-speed"><span class="badge badge-{tier}">{tier_label}</span></span>\n'
            f'  <span class="r-fee">{fee_display}</span>\n'
            f'  <span class="r-chevron"><svg width="8" height="13" viewBox="0 0 8 13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M1.5 1.5L6.5 6.5L1.5 11.5"/></svg></span>\n'
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
  <section class="group animate-in" style="animation-delay: 0.15s" id="group-cdr">
    <div class="group-header">
      <h2>CDR States</h2>
      <span class="group-count">{cdr_state_count}</span>
    </div>
    <p class="group-desc">No state license required \u2014 national CDR credential only.</p>
    <div class="group-head-row">
      <span>State</span>
      <span>Timeline</span>
      <span class="align-right">Speed</span>
      <span class="align-right">Fee</span>
      <span></span>
    </div>
    <div class="group-rows" data-group="cdr-only">
{cdr_rows}
    </div>
  </section>'''
        cdr_filter_pill = '<button type="button" class="seg-btn" data-value="cdr-only">CDR</button>'
        cdr_stat_block = f'''
      <div class="stat-divider"></div>
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
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#F2F2F7">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#000000">
<style>
/* ── APPLE HIG DESIGN SYSTEM ────────────────── */
:root {{
  color-scheme: light dark;
  
  /* Light Mode Tokens */
  --bg-system: #F2F2F7;
  --bg-surface: #FFFFFF;
  --bg-surface-active: #E5E5EA;
  
  --label-primary: #000000;
  --label-secondary: rgba(60, 60, 67, 0.6);
  --label-tertiary: rgba(60, 60, 67, 0.3);
  
  --tint: #007AFF;
  --focus-ring: rgba(0, 122, 255, 0.4);
  
  --separator: rgba(60, 60, 67, 0.29);
  --fill-tertiary: rgba(118, 118, 128, 0.12);
  
  --toolbar-bg: rgba(255, 255, 255, 0.72);
  --toolbar-border: rgba(0, 0, 0, 0.08);
  --seg-active: #FFFFFF;
  
  --badge-fast-bg: #E4F4E9; --badge-fast-txt: #1E823D;
  --badge-mid-bg: #FFF3E0;  --badge-mid-txt: #B25000;
  --badge-slow-bg: #FDECEC; --badge-slow-txt: #C92A2A;
  --badge-none-bg: #F2F2F7; --badge-none-txt: rgba(60, 60, 67, 0.6);
  
  --shadow-card: 0 4px 20px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.02);
  --shadow-float: 0 12px 32px rgba(0,0,0,0.1), 0 2px 6px rgba(0,0,0,0.04);
  --shadow-seg: 0 3px 8px rgba(0,0,0,0.12), 0 3px 1px rgba(0,0,0,0.04);
}}

@media (prefers-color-scheme: dark) {{
  :root {{
    --bg-system: #000000;
    --bg-surface: #1C1C1E;
    --bg-surface-active: #2C2C2E;
    
    --label-primary: #FFFFFF;
    --label-secondary: rgba(235, 235, 245, 0.6);
    --label-tertiary: rgba(235, 235, 245, 0.3);
    
    --tint: #0A84FF;
    --focus-ring: rgba(10, 132, 255, 0.5);
    
    --separator: rgba(84, 84, 88, 0.65);
    --fill-tertiary: rgba(118, 118, 128, 0.24);
    
    --toolbar-bg: rgba(28, 28, 30, 0.72);
    --toolbar-border: rgba(255, 255, 255, 0.15);
    --seg-active: #636366;
    
    --badge-fast-bg: #1B3320; --badge-fast-txt: #32D74B;
    --badge-mid-bg: #332100;  --badge-mid-txt: #FF9F0A;
    --badge-slow-bg: #331515; --badge-slow-txt: #FF453A;
    --badge-none-bg: #2C2C2E; --badge-none-txt: rgba(235, 235, 245, 0.6);
    
    --shadow-card: 0 4px 20px rgba(0,0,0,0.4);
    --shadow-float: 0 12px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.08);
    --shadow-seg: 0 3px 8px rgba(0,0,0,0.3), 0 1px 1px rgba(0,0,0,0.1);
  }}
}}

*, *::before, *::after {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 0; }}
a {{ text-decoration: none; color: inherit; -webkit-tap-highlight-color: transparent; }}
button {{ font-family: inherit; cursor: pointer; -webkit-tap-highlight-color: transparent; border: none; background: none; }}
ul {{ list-style: none; margin: 0; padding: 0; }}

html {{ scroll-behavior: smooth; }}

body {{
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg-system);
  color: var(--label-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  line-height: 1.5;
}}

h1, h2, h3, .stat-value {{ 
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
}}

a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible {{
  outline: 2px solid var(--tint);
  outline-offset: 2px;
  border-radius: 6px;
}}

/* ── ANIMATIONS ─────────────────────────────── */
@keyframes fadeScaleIn {{
  0% {{ opacity: 0; transform: scale(0.98) translateY(10px); }}
  100% {{ opacity: 1; transform: scale(1) translateY(0); }}
}}
.animate-in {{
  animation: fadeScaleIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}}

/* ── NAV ────────────────────────────────────── */
.nav {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 900px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem;
}}
.nav-brand {{
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.015em;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--label-primary);
}}
.nav-links {{ display: flex; gap: 1.5rem; }}
.nav-links a {{
  font-size: 14px;
  font-weight: 500;
  color: var(--label-secondary);
  transition: color 0.2s;
}}
.nav-links a:hover {{ color: var(--label-primary); }}

/* ── HERO ───────────────────────────────────── */
.hero-wrapper {{
  padding: 3rem 1.5rem 3rem;
  max-width: 760px;
  margin: 0 auto;
  text-align: center;
}}
.hero-wrapper h1 {{
  font-size: clamp(2.25rem, 5vw, 3.25rem);
  font-weight: 700;
  letter-spacing: -0.04em;
  line-height: 1.1;
  margin: 0 0 1rem;
}}
.hero-sub {{
  font-size: 1.15rem;
  color: var(--label-secondary);
  line-height: 1.4;
  margin: 0 auto;
  font-weight: 400;
}}

.stats-container {{
  display: inline-flex;
  background: var(--bg-surface);
  border-radius: 20px;
  padding: 1rem 1.5rem;
  margin-top: 2.5rem;
  box-shadow: var(--shadow-card);
  gap: 1.5rem;
  align-items: center;
}}
.stat {{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
}}
.stat-value {{
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.04em;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}}
.stat-label {{
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--label-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-top: 2px;
}}
.stat-divider {{
  width: 1px;
  height: 32px;
  background: var(--separator);
}}

/* ── FLOATING TOOLBAR ───────────────────────── */
.toolbar-wrap {{
  position: sticky;
  top: 1.5rem;
  z-index: 50;
  max-width: 900px;
  margin: 0 auto 3.5rem;
  padding: 0 1.5rem;
  pointer-events: none;
}}
.toolbar {{
  background: var(--toolbar-bg);
  backdrop-filter: blur(40px) saturate(200%);
  -webkit-backdrop-filter: blur(40px) saturate(200%);
  border: 1px solid var(--toolbar-border);
  border-radius: 16px;
  padding: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: var(--shadow-float);
  pointer-events: auto;
}}
.search-wrap {{
  flex: 1;
  min-width: 200px;
  position: relative;
}}
.search-icon {{
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--label-secondary);
  pointer-events: none;
}}
.search-input {{
  width: 100%;
  height: 36px;
  padding: 0 12px 0 36px;
  background: var(--fill-tertiary);
  border: none;
  border-radius: 10px;
  color: var(--label-primary);
  font-size: 15px;
  font-family: inherit;
  transition: all 0.2s;
}}
.search-input::placeholder {{ color: var(--label-secondary); font-weight: 400; }}
.search-input:focus {{ background: var(--bg-surface); box-shadow: 0 0 0 2px var(--focus-ring); outline: none; }}

.seg-group {{
  display: flex;
  background: var(--fill-tertiary);
  border-radius: 10px;
  padding: 2px;
  gap: 2px;
}}
.seg-btn {{
  height: 32px;
  padding: 0 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--label-secondary);
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  white-space: nowrap;
}}
.seg-btn:hover:not(.active) {{ color: var(--label-primary); }}
.seg-btn.active {{
  background: var(--seg-active);
  color: var(--label-primary);
  font-weight: 600;
  box-shadow: var(--shadow-seg);
}}

.sort-select {{
  height: 36px;
  padding: 0 32px 0 16px;
  background: var(--fill-tertiary);
  border: none;
  border-radius: 10px;
  color: var(--label-primary);
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L5 5L9 1' stroke='%2386868B' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  transition: all 0.2s;
}}
.sort-select:focus {{ background: var(--bg-surface); box-shadow: 0 0 0 2px var(--focus-ring); outline: none; }}

/* ── LIST VIEWS (SETTINGS CARDS) ────────────── */
.content {{
  max-width: 900px;
  margin: 0 auto;
  padding: 0 1.5rem 4rem;
}}
.group {{ margin-bottom: 3.5rem; }}
.group-header {{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  padding: 0 16px;
}}
.group-header h2 {{
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.015em;
  margin: 0;
}}
.group-count {{
  font-size: 13px;
  font-weight: 600;
  color: var(--label-secondary);
  background: var(--fill-tertiary);
  padding: 2px 8px;
  border-radius: 99px;
  font-variant-numeric: tabular-nums;
}}
.group-desc {{
  font-size: 14px;
  color: var(--label-secondary);
  margin: 0 0 16px 16px;
}}

.group-head-row {{
  display: grid;
  grid-template-columns: 2fr 1.5fr 100px 80px 24px;
  padding: 0 24px 8px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  color: var(--label-secondary);
}}
.align-right {{ text-align: right; }}

.group-rows {{
  background: var(--bg-surface);
  border-radius: 16px;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}}

.row {{
  display: grid;
  grid-template-columns: 2fr 1.5fr 100px 80px 24px;
  align-items: center;
  padding: 14px 24px;
  position: relative;
  transition: background-color 0.15s;
}}
/* True 0.5px Inset Retina Hairline */
.row::after {{
  content: "";
  position: absolute;
  bottom: 0;
  left: 24px;
  right: 0;
  height: 1px;
  background: var(--separator);
  transform: scaleY(0.5);
  transform-origin: bottom;
}}
.row.no-border::after {{ display: none; }}
@media (hover: hover) {{ 
  .row:hover {{ background-color: var(--bg-surface-active); }} 
}}
.row:active {{ 
  background-color: var(--bg-surface-active); 
  transform: scale(0.995); 
  z-index: 1; 
  transition: transform 0.1s; 
}}

.r-name {{ font-size: 17px; font-weight: 500; letter-spacing: -0.022em; color: var(--label-primary); }}
.r-time {{ font-size: 15px; color: var(--label-secondary); }}
.r-speed {{ display: flex; justify-content: flex-end; }}
.r-fee {{ font-size: 17px; font-weight: 400; color: var(--label-secondary); text-align: right; font-variant-numeric: tabular-nums; }}
.r-chevron {{
  display: flex;
  justify-content: flex-end;
  color: var(--label-tertiary);
}}

/* ── SEMANTIC BADGES ────────────────────────── */
.badge {{
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.01em;
}}
.badge-fast {{ background: var(--badge-fast-bg); color: var(--badge-fast-txt); }}
.badge-mid  {{ background: var(--badge-mid-bg); color: var(--badge-mid-txt); }}
.badge-slow {{ background: var(--badge-slow-bg); color: var(--badge-slow-txt); }}
.badge-none {{ background: var(--badge-none-bg); color: var(--badge-none-txt); }}

/* ── EMPTY STATE ────────────────────────────── */
.empty {{
  display: none;
  text-align: center;
  padding: 5rem 2rem;
  background: var(--bg-surface);
  border-radius: 16px;
  box-shadow: var(--shadow-card);
}}
.empty svg {{ width: 44px; height: 44px; color: var(--label-tertiary); margin-bottom: 16px; }}
.empty h3 {{ font-size: 19px; font-weight: 600; margin: 0 0 8px; letter-spacing: -0.015em; color: var(--label-primary); }}
.empty p {{ font-size: 15px; color: var(--label-secondary); margin: 0; }}

/* ── FOOTER ─────────────────────────────────── */
.foot-wrapper {{
  padding: 3rem 1.5rem;
  margin-top: 2rem;
  border-top: 1px solid var(--separator);
}}
.foot {{
  max-width: 900px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 4rem;
}}
.foot h2, .foot h3 {{ font-size: 15px; font-weight: 600; color: var(--label-primary); margin: 0 0 12px; }}
.foot p {{ font-size: 14px; color: var(--label-secondary); line-height: 1.6; margin: 0; }}
.foot ul {{ display: grid; gap: 10px; }}
.foot li a {{ font-size: 14px; color: var(--tint); font-weight: 400; transition: opacity 0.2s; }}
.foot li a:hover {{ opacity: 0.8; }}
.foot-meta {{ font-size: 12px; color: var(--label-tertiary); margin-top: 1.5rem !important; display: block; }}

/* ── RESPONSIVE ─────────────────────────────── */
@media (max-width: 860px) {{
  .toolbar-wrap {{ top: 1rem; }}
  .toolbar {{ flex-wrap: wrap; padding: 12px; border-radius: 16px; }}
  .search-wrap {{ width: 100%; flex: none; order: 1; }}
  .seg-group {{ flex: 1; justify-content: space-between; order: 2; }}
  .seg-btn {{ flex: 1; padding: 0; text-align: center; }}
  .sort-select {{ flex: 1; order: 3; }}
}}

@media (max-width: 640px) {{
  .hero-wrapper {{ padding: 2rem 1rem 1rem; }}
  .stats-container {{ display: flex; flex-direction: column; width: 100%; align-items: stretch; padding: 1.5rem; gap: 1rem; border-radius: 16px; }}
  .stat-divider {{ width: 100%; height: 1px; }}
  
  .group-head-row {{ display: none; }}
  .group-header, .group-desc {{ padding-left: 8px; }}
  
  .row {{
    grid-template-columns: 1fr auto 20px;
    grid-template-areas:
      "name fee chevron"
      "time speed chevron";
    gap: 4px 12px;
    padding: 14px 16px;
  }}
  .row::after {{ left: 16px; }}
  .r-name {{ grid-area: name; font-size: 17px; }}
  .r-time {{ grid-area: time; font-size: 14px; }}
  .r-fee {{ grid-area: fee; text-align: right; }}
  .r-speed {{ grid-area: speed; justify-content: flex-end; padding-right: 0; }}
  .badge {{ font-size: 12px; padding: 2px 8px; }}
  .r-chevron {{ grid-area: chevron; align-self: center; }}
  
  .foot {{ grid-template-columns: 1fr; gap: 2.5rem; }}
}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ transition: none !important; animation: none !important; }}
}}
</style>
</head>
<body>
<nav class="nav animate-in" aria-label="Site navigation">
  <div class="nav-brand">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--tint)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
    State Licensing Reference
  </div>
  <div class="nav-links">
    <a href="/">Directory</a>
    <a href="#how-to-use">How It Works</a>
  </div>
</nav>

<header class="hero-wrapper animate-in" style="animation-delay: 0.05s">
  <h1>{profession} License<br>Reciprocity by State</h1>
  <p class="hero-sub">Compare compact privileges, endorsement fees, and processing timelines across all {total_states} states and DC.</p>
  
  <div class="stats-container">
    <div class="stat">
      <span class="stat-value">{total_states}</span>
      <span class="stat-label">Jurisdictions</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat">
      <span class="stat-value">{member_count}</span>
      <span class="stat-label">Compact States</span>
    </div>{cdr_stat_block}
  </div>
</header>

<div class="toolbar-wrap animate-in" style="animation-delay: 0.1s">
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
  </div>
</div>

<main class="content" id="main-content">
  <section class="group animate-in" style="animation-delay: 0.15s" id="group-compact">
    <div class="group-header">
      <h2>Compact States</h2>
      <span class="group-count">{member_count}</span>
    </div>
    <p class="group-desc">Your home-state license may already cover these states via compact privilege.</p>
    <div class="group-head-row">
      <span>State</span>
      <span>Timeline</span>
      <span class="align-right">Speed</span>
      <span class="align-right">Fee</span>
      <span></span>
    </div>
    <div class="group-rows" data-group="member">
{compact_rows}
    </div>
  </section>

  <section class="group animate-in" style="animation-delay: 0.2s" id="group-endorsement">
    <div class="group-header">
      <h2>Endorsement States</h2>
      <span class="group-count">{endorsement_count}</span>
    </div>
    <p class="group-desc">Requires a separate board application with fee and processing time.</p>
    <div class="group-head-row">
      <span>State</span>
      <span>Timeline</span>
      <span class="align-right">Speed</span>
      <span class="align-right">Fee</span>
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
    <h3>No Matches Found</h3>
    <p>Try adjusting your search or clearing your filters.</p>
  </section>
</main>

<div class="foot-wrapper">
  <section class="foot animate-in" id="how-to-use" style="animation-delay: 0.25s">
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
      <span class="foot-meta">Verified updated &bull; {latest_verified}</span>
    </div>
  </section>
</div>

<script>
const input = document.getElementById('stateSearch');
const allRows = [...document.querySelectorAll('.row')];
const groups = [...document.querySelectorAll('.group')];
const sortSelect = document.getElementById('sortSelect');
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
    
    // Automatically manages the hidden bottom border rule for the last visible element
    for (const r of sortedVisible) {{
      r.classList.remove('no-border');
      container.appendChild(r);
    }}
    if (sortedVisible.length > 0) {{
      sortedVisible[sortedVisible.length - 1].classList.add('no-border');
    }}
    
    // Keep hidden rows out of the way to preserve the structural flex/grid flow
    for (const r of hidden) {{
      r.classList.remove('no-border');
      container.appendChild(r);
    }}
  }});

  for (const g of groups) {{
    const container = g.querySelector('.group-rows');
    if (!container) continue;
    const hasVisible = [...container.querySelectorAll('.row')].some(r => r.style.display !== 'none');
    g.style.display = hasVisible ? '' : 'none';
  }}

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

// Trigger initial filter to process borders
applyFilters();
</script>
</body>
</html>'''
