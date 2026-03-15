from __future__ import annotations


def render_index(
    *,
    domain: str,
    profile: dict,
    states_manifest: list[dict],
    css_hash: str,
    today: str,
    suppress_compact_ui: bool = False,
) -> str:
    profession = profile['identity']['title_full']
    plural = profile['identity'].get('title_plural', profession + 's')
    compact_status = str(profile.get('regulatory', {}).get('compact_status', '')).lower()
    has_compact_framework = compact_status in {'active', 'enacted'}
    sorted_states = sorted(states_manifest, key=lambda item: item['name'])
    total_states = len(sorted_states)

    latest_verified = today
    compact_states = []
    endorsement_states = []
    cdr_states = []

    for s in sorted_states:
        name = s['name']
        slug = s['slug']
        tier = 'slow'
        license_required = bool(s.get('license_required', True))
        member = (
            has_compact_framework
            and bool(s.get('state_is_member'))
            and not (suppress_compact_ui and license_required)
        )
        fee_value = s.get('endorsement_fee')
        fee_raw = s.get('endorsement_fee', 0)
        processing_time = s.get('processing_time') or 'TBD'
        
        # Calculate administrative difficulty
        fp = bool(s.get('fingerprint_required'))
        exam = bool(s.get('jurisprudence_required'))
        psv = bool(s.get('requires_psv'))
        
        # New distribution to ensure realistic bucketing
        if exam:
            tier = 'slow'  # High difficulty (State-specific exam required)
        elif fp and psv:
            tier = 'mid'   # Medium difficulty (Both Fingerprints and Transcripts)
        else:
            tier = 'fast'  # Low difficulty (One or neither required)

        latest_verified = max(latest_verified, s.get('last_updated') or today)

        entry = {
            'name': name,
            'slug': slug,
            'fee_raw': fee_raw,
            'processing_time': processing_time,
            'tier': tier,
            'member': member,
            'license_required': license_required,
            'fp': fp,
            'exam': exam,
            'psv': psv
        }

        if not license_required:
            entry['tier'] = 'none'
            cdr_states.append(entry)
        elif member:
            compact_states.append(entry)
        else:
            endorsement_states.append(entry)

    compact_count = len(compact_states)
    cdr_state_count = len(cdr_states)
    endorsement_count = len(endorsement_states)
    show_compact_ui = has_compact_framework and not suppress_compact_ui

    def render_row(s: dict) -> str:
        tier = s['tier']
        tier_label = {
            'fast': 'Low',
            'mid': 'Med',
            'slow': 'High',
            'none': 'None',
        }.get(tier, 'High')

        if not s['license_required']:
            fee_display = '\u2014'
            time_display = 'No state app'
            s['fee'] = 0
        else:
            fee_val = s['fee_raw']
            if isinstance(fee_val, (int, float)):
                fee_display = f"${int(fee_val)}"
                s['fee'] = int(fee_val)
            elif isinstance(fee_val, str) and fee_val.replace('$', '').replace(',', '').isdigit():
                s['fee'] = int(fee_val.replace('$', '').replace(',', ''))
                fee_display = f"${s['fee']}"
            else:
                fee_display = str(fee_val) if fee_val else "TBD"
                s['fee'] = 0 if fee_display in ["TBD", "N/A", "Varies"] else 9999
            time_display = s['processing_time']

        return (
            f'<a class="row" href="/{s["slug"]}" data-state="{s["name"].lower()}" '
            f'data-fee="{s["fee"]}" data-tier="{tier}" '
            f'data-path="{"cdr-only" if not s["license_required"] else "member" if s["member"] else "non-member"}">\n'
            f'  <span class="r-name" title="{s["name"]}">{s["name"]}</span>\n'
            f'  <span class="r-time">{time_display}</span>\n'
            f'  <span class="r-speed"><span class="badge badge-{tier}">{tier_label}</span></span>\n'
            f'  <span class="r-fee">{fee_display}</span>\n'
            f'  <span class="r-chevron" aria-hidden="true"><svg width="8" height="13" viewBox="0 0 8 13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M1.5 1.5L6.5 6.5L1.5 11.5"/></svg></span>\n'
            f'</a>'
        )

    compact_rows = '\n'.join(render_row(s) for s in compact_states)
    endorsement_rows = '\n'.join(render_row(s) for s in endorsement_states)
    cdr_rows = '\n'.join(render_row(s) for s in cdr_states)

    if show_compact_ui:
        title = f"{profession} License Reciprocity by State - Compact Status, Fees and Transfer Timelines (2026)"
        desc = (
            f"Compare {plural.lower()} license reciprocity rules by state, including compact participation, "
            "endorsement fees, and processing timelines."
        )
    else:
        title = f"{profession} License Transfer by State - Endorsement Fees and Timelines (2026)"
        desc = (
            f"Compare {plural.lower()} transfer requirements by state, including endorsement fees, "
            "administrative difficulty tiers, and processing timelines."
        )

    cdr_section = ''
    cdr_filter_pill = ''
    cdr_stat_block = ''
    if cdr_state_count:
        cdr_section = f'''
  <section class="group" id="group-cdr" aria-labelledby="heading-cdr">
    <div class="group-header">
      <h2 id="heading-cdr">CDR States</h2>
      <span class="group-count">{cdr_state_count}</span>
    </div>
    <p class="group-desc">No state license required \u2014 national CDR credential only.</p>
    <div class="group-head-row" aria-hidden="true">
      <span>State</span>
      <span>Timeline</span>
      <span class="align-right">Difficulty</span>
      <span class="align-right">Fee</span>
      <span></span>
    </div>
    <div class="group-rows" data-group="cdr-only" role="list">
{cdr_rows}
    </div>
  </section>'''
        cdr_filter_pill = '<button type="button" class="seg-btn" data-value="cdr-only" aria-pressed="false">CDR</button>'
        cdr_stat_block = f'''
      <div class="stat-divider" aria-hidden="true"></div>
      <div class="stat">
        <span class="stat-value">{cdr_state_count}</span>
        <span class="stat-label">CDR States</span>
      </div>'''

    if show_compact_ui:
        hero_h1 = f"{profession} License<br>Reciprocity by State"
        hero_sub = f"Compare compact privileges, endorsement fees, and processing timelines across all {total_states} states and DC."
        primary_count = compact_count
        primary_label = "Compact States"
        path_filter_aria = "Filter by reciprocity path"
        compact_filter_btn = '<button type="button" class="seg-btn" data-value="member" aria-pressed="false">Compact</button>'
        compact_section = f'''
  <section class="group" id="group-compact" aria-labelledby="heading-compact">
    <div class="group-header">
      <h2 id="heading-compact">Compact States</h2>
      <span class="group-count" aria-label="{compact_count} states">{compact_count}</span>
    </div>
    <p class="group-desc">Your home-state license may already cover these states via compact privilege.</p>
    <div class="group-head-row" aria-hidden="true">
      <span>State</span>
      <span>Timeline</span>
      <span class="align-right">Difficulty</span>
      <span class="align-right">Fee</span>
      <span></span>
    </div>
    <div class="group-rows" data-group="member" role="list">
{compact_rows}
    </div>
  </section>
'''
        how_to_use_copy = "Start with the path filter to narrow by compact, endorsement, or CDR. Sort by fee or speed to find your fastest or cheapest route. Open any state to see the full board-verified guide with steps, documents, and renewal info."
        quick_link_compact = '<li><a href="#group-compact">Compact states</a></li>'
        allowed_path_values = "['all','member','non-member','cdr-only']"
    else:
        hero_h1 = f"{profession} License<br>Transfer by State"
        hero_sub = f"Compare endorsement fees, administrative difficulty, and processing timelines across all {total_states} states and DC."
        primary_count = endorsement_count
        primary_label = "Endorsement States"
        path_filter_aria = "Filter by licensure path"
        compact_filter_btn = ''
        compact_section = ''
        how_to_use_copy = "Use the path filter to focus on endorsement or CDR states. Sort by fee or difficulty to find your fastest or most practical route. Open any state for board-verified steps, documents, and renewal details."
        quick_link_compact = ''
        allowed_path_values = "['all','non-member','cdr-only']"

    # Render stats only when there is meaningful compact/CDR signal.
    # This suppresses "0 Compact States" noise on non-compact specialties.
    has_meaningful_stats = compact_count > 0 or cdr_state_count > 0

    if has_meaningful_stats:
        stats_block = f'''
  <div class="stats-container">
    <div class="stat">
      <span class="stat-value">{total_states}</span>
      <span class="stat-label">Jurisdictions</span>
    </div>
    <div class="stat-divider" aria-hidden="true"></div>
    <div class="stat">
      <span class="stat-value">{primary_count}</span>
      <span class="stat-label">{primary_label}</span>
    </div>{cdr_stat_block}
  </div>'''
    else:
        stats_block = ''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, maximum-scale=5.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{domain}/">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#ffffff">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Karla:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #ffffff;
  --paper: #faf9f7;
  --text: #222222;
  --muted: #666666;
  --line: #e5e1db;
  --link: #1a5f7a;
  --focus: rgba(26, 95, 122, 0.2);
  --badge-fast: #2f7a3b;
  --badge-mid: #9a5b12;
  --badge-slow: #8c2222;
  --badge-none: #777777;
}}

*, *::before, *::after {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; scroll-padding-top: 110px; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: 'Karla', -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}}
a {{ color: inherit; text-decoration: none; }}
button {{ font: inherit; border: 0; background: none; cursor: pointer; }}
ul {{ list-style: none; margin: 0; padding: 0; }}
h1, h2, h3, .stat-value {{
  font-family: 'Source Serif 4', Georgia, serif;
  letter-spacing: -0.01em;
  line-height: 1.2;
  margin: 0;
  color: #191919;
}}
a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible {{
  outline: 0;
  box-shadow: 0 0 0 3px var(--focus);
}}

.nav {{
  position: sticky;
  top: 0;
  z-index: 100;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 920px;
  margin: 0 auto;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}}
.nav-brand {{
  font-size: 13px;
  font-weight: 600;
  color: #555;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.nav-links {{
  display: flex;
  align-items: center;
  gap: 20px;
}}
.nav-links a {{
  font-size: 13px;
  color: #888;
}}
.nav-links a:hover {{ color: #333; }}

.hero-wrapper {{
  max-width: 640px;
  margin: 0 auto;
  padding: 48px 24px 32px;
}}
.hero-wrapper h1 {{
  font-size: clamp(30px, 4.8vw, 44px);
  margin-bottom: 10px;
}}
.hero-sub {{
  font-size: 17px;
  color: #444;
  margin: 0;
}}

.stats-container {{
  margin-top: 24px;
  display: flex;
  align-items: stretch;
  gap: 16px;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
}}
.stat {{
  min-width: 0;
  display: flex;
  flex-direction: column;
}}
.stat-value {{
  font-size: 26px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}}
.stat-label {{
  margin-top: 4px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #666;
}}
.stat-divider {{
  width: 1px;
  background: var(--line);
}}

.toolbar-wrap {{
  position: sticky;
  top: 58px;
  z-index: 90;
  max-width: 920px;
  margin: 0 auto 32px;
  padding: 0 16px;
}}
.toolbar {{
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  padding: 12px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px 12px;
}}
.search-wrap {{
  min-width: 0;
  position: relative;
  display: flex;
  align-items: center;
}}
.search-icon {{
  position: absolute;
  left: 12px;
  color: #999;
  pointer-events: none;
}}
.search-input {{
  width: 100%;
  height: 40px;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0 38px;
  font-size: 15px;
  font-family: inherit;
  color: var(--text);
  background: #fff;
}}
.search-input::placeholder {{ color: #999; }}
.search-clear {{
  position: absolute;
  right: 9px;
  width: 22px;
  height: 22px;
  display: none;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid var(--line);
  color: #999;
  background: #fff;
}}
.toolbar-bottom-row {{
  display: flex;
  gap: 10px;
}}
.seg-group {{
  display: flex;
  gap: 6px;
}}
.seg-btn {{
  height: 40px;
  padding: 0 14px;
  border: 1px solid var(--line);
  border-radius: 6px;
  font-size: 13px;
  color: #666;
  background: #fff;
  white-space: nowrap;
}}
.seg-btn.active {{
  color: #1f1f1f;
  border-color: #d2cbc2;
  background: var(--paper);
  font-weight: 600;
}}
.sort-select {{
  height: 40px;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 0 36px 0 12px;
  font-size: 14px;
  font-family: inherit;
  color: var(--text);
  background: #fff;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L5 5L9 1' stroke='%23888' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
}}

.content {{
  max-width: 920px;
  margin: 0 auto;
  padding: 0 16px 56px;
}}
.group {{ margin-bottom: 36px; }}
.group-header {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}}
.group-header h2 {{
  font-size: 28px;
  font-weight: 600;
}}
.group-count {{
  font-size: 12px;
  color: #666;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 2px 6px;
  font-variant-numeric: tabular-nums;
}}
.group-desc {{
  font-size: 15px;
  color: var(--muted);
  margin: 0 0 10px;
}}
.group-head-row {{
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 1.5fr) 100px 80px 24px;
  gap: 12px;
  padding: 0 12px 6px;
  font-size: 11px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #777;
}}
.align-right {{ text-align: right; }}

.group-rows {{
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}}
.row {{
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 1.5fr) 100px 80px 24px;
  gap: 12px;
  align-items: center;
  padding: 14px 12px;
  border-top: 1px solid var(--line);
}}
.row:first-child {{ border-top: 0; }}
.row:hover {{ background: var(--paper); }}
.row.no-border {{ border-top-color: transparent; }}

.r-name {{
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.r-time {{
  font-size: 14px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.r-speed {{ display: flex; justify-content: flex-end; }}
.r-fee {{
  font-size: 15px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: #444;
}}
.r-chevron {{
  display: flex;
  justify-content: flex-end;
  color: #9a9a9a;
}}
.badge {{
  font-size: 12px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  font-weight: 600;
  background: none;
  border: 0;
  padding: 0;
}}
.badge-fast {{ color: var(--badge-fast); }}
.badge-mid {{ color: var(--badge-mid); }}
.badge-slow {{ color: var(--badge-slow); }}
.badge-none {{ color: var(--badge-none); }}

.empty {{
  display: none;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  padding: 32px 20px;
  text-align: center;
}}
.empty svg {{ width: 36px; height: 36px; color: #aaa; margin-bottom: 10px; }}
.empty h3 {{ font-size: 22px; margin: 0 0 6px; }}
.empty p {{ margin: 0; color: #666; }}

.foot-wrapper {{
  border-top: 1px solid var(--line);
  padding: 32px 16px 40px;
}}
.foot {{
  max-width: 920px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 28px;
}}
.foot h2, .foot h3 {{
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: 20px;
  margin: 0 0 8px;
}}
.foot p {{
  font-size: 14px;
  color: #666;
  margin: 0;
}}
.foot ul {{ display: grid; gap: 8px; }}
.foot li a {{
  font-size: 14px;
  color: var(--link);
  text-decoration: underline;
  text-decoration-color: rgba(26, 95, 122, 0.3);
}}
.foot-meta {{
  display: block;
  margin-top: 12px;
  font-size: 12px;
  color: #999;
}}

@media (max-width: 820px) {{
  .toolbar {{
    grid-template-columns: 1fr;
  }}
  .toolbar-bottom-row {{
    flex-wrap: wrap;
  }}
  .seg-group {{
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }}
  .seg-group::-webkit-scrollbar {{ display: none; }}
}}

@media (max-width: 640px) {{
  .nav-links {{ display: none; }}
  .hero-wrapper {{ padding: 36px 16px 24px; }}
  .stats-container {{
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }}
  .stat-divider {{
    width: 100%;
    height: 1px;
  }}
  .group-head-row {{ display: none; }}
  .row {{
    grid-template-columns: minmax(0, 1fr) auto 20px;
    grid-template-areas:
      "name fee chevron"
      "time speed chevron";
    gap: 6px 10px;
  }}
  .r-name {{ grid-area: name; }}
  .r-time {{ grid-area: time; }}
  .r-speed {{ grid-area: speed; justify-content: flex-start; }}
  .r-fee {{ grid-area: fee; }}
  .r-chevron {{ grid-area: chevron; align-self: center; }}
  .foot {{
    grid-template-columns: 1fr;
  }}
}}
</style>
</head>
<body>
<nav class="nav" aria-label="Site navigation">
  <div class="nav-brand">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#b08a52" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
    State Licensing Reference
  </div>
  <div class="nav-links">
    <a href="/">All States</a>
    <a href="https://perdiem-portal.vercel.app">All Specialties</a>
    <a href="#how-to-use">How It Works</a>
  </div>
</nav>

<header class="hero-wrapper">
  <h1>{hero_h1}</h1>
  <p class="hero-sub">{hero_sub}</p>
  
  {stats_block}
</header>

<div class="toolbar-wrap">
  <search class="toolbar" role="search">
    <div class="search-wrap">
      <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="7" cy="7" r="5"/><path d="M11 11L15 15"/></svg>
      <input id="stateSearch" class="search-input" type="text" placeholder="Search states..." aria-label="Search states by name" autocomplete="off" spellcheck="false">
      <button class="search-clear" id="searchClear" aria-label="Clear search">
        <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M1 1L13 13M1 13L13 1"/></svg>
      </button>
    </div>
    <div class="toolbar-bottom-row">
      <div class="seg-group" data-filter-group="path" role="group" aria-label="{path_filter_aria}">
        <button type="button" class="seg-btn active" data-value="all" aria-pressed="true">All</button>
        {compact_filter_btn}
        <button type="button" class="seg-btn" data-value="non-member" aria-pressed="false">Endorsement</button>
        {cdr_filter_pill}
      </div>
      <select id="sortSelect" class="sort-select" aria-label="Sort states">
        <option value="state">Sort: A &ndash; Z</option>
        <option value="fee">Sort: Fee</option>
        <option value="difficulty">Sort: Difficulty</option>
      </select>
    </div>
  </search>
</div>

<main class="content" id="main-content">
  {compact_section}
  <section class="group" id="group-endorsement" aria-labelledby="heading-endorsement">
    <div class="group-header">
      <h2 id="heading-endorsement">Endorsement States</h2>
      <span class="group-count" aria-label="{endorsement_count} states">{endorsement_count}</span>
    </div>
    <p class="group-desc">Requires a separate board application with fee and processing time.</p>
    <div class="group-head-row" aria-hidden="true">
      <span>State</span>
      <span>Timeline</span>
      <span class="align-right">Difficulty</span>
      <span class="align-right">Fee</span>
      <span></span>
    </div>
    <div class="group-rows" data-group="non-member" role="list">
{endorsement_rows}
    </div>
  </section>
{cdr_section}

  <section class="empty" id="emptyState" aria-live="polite">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
    </svg>
    <h3>No Matches Found</h3>
    <p>Try adjusting your search or clearing your filters.</p>
  </section>
</main>

<div class="foot-wrapper">
  <footer class="foot" id="how-to-use">
    <div>
      <h2>How to use this directory</h2>
      <p>{how_to_use_copy}</p>
    </div>
    <div>
      <h3>Quick links</h3>
      <ul>
        {quick_link_compact}
        <li><a href="#group-endorsement">Endorsement states</a></li>
      </ul>
      <span class="foot-meta">Verified updated &bull; {latest_verified}</span>
    </div>
  </footer>
</div>

<script>
const input = document.getElementById('stateSearch');
const searchClear = document.getElementById('searchClear');
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
    if (mode === 'difficulty') {{
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
  searchClear.style.display = q ? 'flex' : 'none';
  let shown = 0;

  for (const row of allRows) {{
    const matchQ = row.dataset.state.includes(q);
    const matchP = pathFilter === 'all' || row.dataset.path === pathFilter;
    const visible = matchQ && matchP;
    row.style.display = visible ? '' : 'none';
    if (visible) shown++;
  }}

  document.querySelectorAll('.group-rows').forEach(container => {{
    const fragment = document.createDocumentFragment();
    const visible = [...container.querySelectorAll('.row')].filter(r => r.style.display !== 'none');
    const hidden = [...container.querySelectorAll('.row')].filter(r => r.style.display === 'none');
    
    const sortedVisible = sortRows(visible);
    
    for (const r of sortedVisible) {{
      r.classList.remove('no-border');
      fragment.appendChild(r);
    }}
    if (sortedVisible.length > 0) {{
      sortedVisible[sortedVisible.length - 1].classList.add('no-border');
    }}
    
    for (const r of hidden) {{
      r.classList.remove('no-border');
      fragment.appendChild(r);
    }}
    
    container.appendChild(fragment);
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

input.addEventListener('input', () => requestAnimationFrame(applyFilters));
searchClear.addEventListener('click', () => {{
  input.value = '';
  input.focus();
  requestAnimationFrame(applyFilters);
}});
sortSelect.addEventListener('change', () => requestAnimationFrame(applyFilters));

for (const btn of pathBtns) {{
  btn.addEventListener('click', () => {{
    pathFilter = btn.dataset.value;
    for (const b of pathBtns) {{
      const isActive = b.dataset.value === pathFilter;
      b.classList.toggle('active', isActive);
      b.setAttribute('aria-pressed', isActive.toString());
    }}
    requestAnimationFrame(applyFilters);
  }});
}}

const params = new URLSearchParams(window.location.search);
if (params.get('q')) input.value = params.get('q');
if (params.get('path') && {allowed_path_values}.includes(params.get('path'))) pathFilter = params.get('path');
if (params.get('sort') && ['state','fee','difficulty'].includes(params.get('sort'))) sortSelect.value = params.get('sort');

for (const b of pathBtns) {{
  const isActive = b.dataset.value === pathFilter;
  b.classList.toggle('active', isActive);
  b.setAttribute('aria-pressed', isActive.toString());
}}

requestAnimationFrame(applyFilters);
</script>
</body>
</html>'''
