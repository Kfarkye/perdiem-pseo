from __future__ import annotations


def format_fee_display(value: object) -> str:
    if isinstance(value, (int, float)):
        if float(value).is_integer():
            return f"${int(value)}"
        return f"${value:,.2f}"
    if isinstance(value, str):
        cleaned = value.replace('$', '').replace(',', '').strip()
        try:
            number = float(cleaned)
        except ValueError:
            return value
        if number.is_integer():
            return f"${int(number)}"
        return f"${number:,.2f}"
    return str(value)


def fee_sort_value(value: object) -> int:
    if isinstance(value, (int, float)):
        return int(round(float(value) * 100))

    if isinstance(value, str):
        cleaned = value.replace('$', '').replace(',', '').strip()
        try:
            return int(round(float(cleaned) * 100))
        except ValueError:
            return 999999

    return 999999


def extra_step_labels(item: dict) -> list[str]:
    labels = []
    if item.get("fp"):
        labels.append("Fingerprints")
    if item.get("exam"):
        labels.append("Exam")
    if item.get("psv"):
        labels.append("PSV")
    return labels


def extra_step_sort_value(item: dict) -> int:
    labels = extra_step_labels(item)
    if not labels:
        return 0
    score = len(labels) * 10
    if item.get("exam"):
        score += 3
    if item.get("fp"):
        score += 2
    if item.get("psv"):
        score += 1
    return score


def render_index(
    *,
    domain: str,
    profile: dict,
    states_manifest: list[dict],
    css_hash: str,
    today: str,
    suppress_compact_ui: bool = False,
    verify_fee_and_timing_with_board: bool = False,
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
            'psv': psv,
            'board_fee_verified': bool(s.get('board_fee_verified')),
            'board_timeline_verified': bool(s.get('board_timeline_verified')),
            'fee_display': s.get('fee_display'),
            'time_display': s.get('time_display'),
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
        step_labels = extra_step_labels(s)
        step_count = extra_step_sort_value(s)
        if step_labels:
            steps_display = "".join(f'<span class="step-flag">{label}</span>' for label in step_labels)
        elif not s["license_required"]:
            steps_display = '<span class="step-plain">No state application</span>'
        else:
            steps_display = '<span class="step-plain">No extra state steps listed</span>'

        if not s['license_required']:
            fee_display = '\u2014'
            time_display = 'No state app'
            s['fee'] = 0
        elif verify_fee_and_timing_with_board:
            fee_display = s.get('fee_display') or 'See board'
            time_display = s.get('time_display') or 'See board'
            if s.get('board_fee_verified'):
                s['fee'] = fee_sort_value(s['fee_raw'])
            else:
                s['fee'] = 9999
        else:
            fee_val = s['fee_raw']
            if isinstance(fee_val, (int, float)):
                fee_display = format_fee_display(fee_val)
                s['fee'] = fee_sort_value(fee_val)
            elif isinstance(fee_val, str):
                parsed_fee = fee_sort_value(fee_val)
                if parsed_fee != 999999:
                    s['fee'] = parsed_fee
                    fee_display = format_fee_display(fee_val)
                else:
                    fee_display = str(fee_val) if fee_val else "TBD"
                    s['fee'] = 0 if fee_display in ["TBD", "N/A", "Varies"] else 9999
            else:
                fee_display = str(fee_val) if fee_val else "TBD"
                s['fee'] = 0 if fee_display in ["TBD", "N/A", "Varies"] else 9999
            time_display = s['processing_time']

        return (
            f'<a class="row" href="/{s["slug"]}" data-state="{s["name"].lower()}" '
            f'data-fee="{s["fee"]}" data-tier="{tier}" data-extra-steps="{step_count}" '
            f'data-path="{"cdr-only" if not s["license_required"] else "member" if s["member"] else "non-member"}">\n'
            f'  <span class="r-name" title="{s["name"]}">{s["name"]}</span>\n'
            f'  <span class="r-time">{time_display}</span>\n'
            f'  <span class="r-speed">{steps_display}</span>\n'
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
        if verify_fee_and_timing_with_board:
            title = f"{profession} License Transfer by State - Board Links and State Guides (2026)"
            desc = (
                f"Browse {plural.lower()} transfer guides by state with board links, licensing steps, "
                "and verification details."
            )
        else:
            title = f"{profession} License Transfer by State - Endorsement Fees and Timelines (2026)"
            desc = (
                f"Compare {plural.lower()} transfer requirements by state, including endorsement fees, "
                "fingerprints, exam requirements, and processing timelines."
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
      <span class="align-right">Extra steps</span>
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
        hero_h1 = profession
        hero_sub = "License Reciprocity by State"
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
      <span class="align-right">Extra steps</span>
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
        hero_h1 = profession
        hero_sub = "License Transfer by State"
        primary_count = endorsement_count
        primary_label = "Endorsement States"
        path_filter_aria = "Filter by licensure path"
        compact_filter_btn = ''
        compact_section = ''
        if verify_fee_and_timing_with_board:
            how_to_use_copy = "Use the path filter to focus on endorsement or CDR states. Sort by extra steps, then open any state guide to verify current fees and processing details directly with the board."
        else:
            how_to_use_copy = "Use the path filter to focus on endorsement or CDR states. Sort by fee or extra steps to find the cleanest route. Open any state for steps, documents, and renewal details."
        quick_link_compact = ''
        allowed_path_values = "['all','non-member','cdr-only']"

    fee_sort_option = '' if verify_fee_and_timing_with_board else '<option value="fee">Sort: Fee</option>'
    timeline_col_label = 'Board timing' if verify_fee_and_timing_with_board else 'Timeline'
    fee_col_label = 'Board fee' if verify_fee_and_timing_with_board else 'Fee'
    endorsement_desc = (
        "Open the state guide to verify current fee and timing details on the board site."
        if verify_fee_and_timing_with_board
        else "Requires a separate board application with fee and processing time."
    )
    allowed_sort_values = "['state','extra-steps']" if verify_fee_and_timing_with_board else "['state','fee','extra-steps']"
    site_root = domain.rsplit("/", 1)[0]
    share_image = f"{site_root}/social-card.svg"

    # Pull profession-level metadata for the stats block
    national_credential = profile['identity'].get('credential', '')
    national_exam = profile.get('regulatory', {}).get('national_exam', '')
    renewal_cycle = profile.get('regulatory', {}).get('renewal_cycle', '2 years')

    stats_block = f'''
  <div class="credential-bar">
    <div class="credential-item">
      <span class="credential-label">National License</span>
      <span class="credential-value">{national_credential}</span>
    </div>
    <div class="credential-item">
      <span class="credential-label">National Exam</span>
      <span class="credential-value">{national_exam}</span>
    </div>
    <div class="credential-item">
      <span class="credential-label">Renewal Cycle</span>
      <span class="credential-value">{renewal_cycle}</span>
    </div>
  </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, maximum-scale=5.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{domain}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#ffffff">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{domain}">
<meta property="og:site_name" content="State Licensing Reference">
<meta property="og:image" content="{share_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{share_image}">
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
  text-rendering: optimizeLegibility;
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
:root {{
  --accent: #b08a52;
  --accent-soft: rgba(176, 138, 82, 0.12);
  --shell: 1120px;
  --reading: 760px;
  --shadow-soft: 0 18px 42px rgba(37, 29, 20, 0.06);
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
  max-width: var(--shell);
  margin: 0 auto;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.8);
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
  max-width: var(--shell);
  margin: 0 auto;
  padding: 64px 24px 32px;
}}
.hero-kicker {{
  margin: 0 0 12px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7c7267;
}}
.hero-wrapper h1 {{
  font-size: clamp(30px, 4.8vw, 44px);
  margin-bottom: 12px;
  max-width: var(--reading);
}}
.hero-sub {{
  max-width: 52ch;
  font-size: 18px;
  color: #444;
  margin: 0;
}}

.credential-bar {{
  max-width: var(--shell);
  margin: 0 auto;
  padding: 0 24px 32px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}}
.credential-item {{
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  box-shadow: var(--shadow-soft);
}}
.credential-label {{
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #888;
  font-weight: 600;
}}
.credential-value {{
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: 17px;
  font-weight: 600;
  color: #191919;
  line-height: 1.35;
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
  max-width: var(--shell);
  margin: 0 auto 40px;
  padding: 0 24px;
}}
.toolbar {{
  border: 1px solid var(--line);
  border-radius: 18px;
  background: #fff;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: var(--shadow-soft);
}}
.toolbar-bottom-row {{
  display: flex;
  gap: 10px;
  width: 100%;
  align-items: center;
}}
.seg-group {{
  display: flex;
  gap: 6px;
}}
.seg-btn {{
  height: 40px;
  padding: 0 14px;
  border: 1px solid var(--line);
  border-radius: 999px;
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
  border-radius: 999px;
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
  max-width: var(--shell);
  margin: 0 auto;
  padding: 0 24px 72px;
}}
.group {{ margin-bottom: 48px; }}
.group-header {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}}
.group-header h2 {{
  font-size: 28px;
  font-weight: 600;
}}
.group-count {{
  font-size: 12px;
  color: #666;
  border: 1px solid #e0d4c5;
  border-radius: 999px;
  padding: 4px 8px;
  background: var(--accent-soft);
  font-variant-numeric: tabular-nums;
}}
.group-desc {{
  font-size: 15px;
  color: var(--muted);
  margin: 0 0 14px;
}}
.group-head-row {{
  display: grid;
  grid-template-columns: minmax(0, 2.2fr) minmax(0, 1.25fr) minmax(132px, 1.2fr) 96px 24px;
  gap: 16px;
  padding: 0 20px 8px;
  font-size: 11px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #777;
}}
.align-right {{ text-align: right; }}

.group-rows {{
  border: 1px solid var(--line);
  border-radius: 18px;
  overflow: hidden;
  background: #fff;
  box-shadow: var(--shadow-soft);
}}
.row {{
  display: grid;
  grid-template-columns: minmax(0, 2.2fr) minmax(0, 1.25fr) minmax(132px, 1.2fr) 96px 24px;
  gap: 16px;
  align-items: center;
  padding: 18px 20px;
  border-top: 1px solid var(--line);
}}
.row:first-child {{ border-top: 0; }}
.row:hover {{ background: #fcfaf7; }}
.row.no-border {{ border-top-color: transparent; }}

.r-name {{
  font-size: 17px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.r-time {{
  font-size: 15px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.r-speed {{
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 6px;
}}
.r-fee {{
  font-size: 16px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: #444;
}}
.step-flag,
.step-plain {{
  font-size: 12px;
  line-height: 1.35;
  color: #6f675e;
}}
.step-flag {{
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(176, 138, 82, 0.12);
  border: 1px solid rgba(176, 138, 82, 0.18);
  color: #6b5230;
  font-weight: 600;
}}
.r-chevron {{
  display: flex;
  justify-content: flex-end;
  color: #9a9a9a;
}}

.empty {{
  display: none;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper);
  padding: 32px 20px;
  text-align: center;
  box-shadow: var(--shadow-soft);
}}
.empty svg {{ width: 36px; height: 36px; color: #aaa; margin-bottom: 10px; }}
.empty h3 {{ font-size: 22px; margin: 0 0 6px; }}
.empty p {{ margin: 0; color: #666; }}

.foot-wrapper {{
  border-top: 1px solid var(--line);
  padding: 40px 24px 56px;
}}
.foot {{
  max-width: var(--shell);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 48px;
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
  .nav {{
    padding: 0 16px;
  }}
  .hero-wrapper {{
    padding: 36px 16px 24px;
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
  .credential-bar {{
    grid-template-columns: 1fr;\n    padding: 0 16px 24px;
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
    <a href="https://www.statelicensingreference.com">All Specialties</a>
    <a href="#how-to-use">How It Works</a>
  </div>
</nav>

<header class="hero-wrapper">
  <h1>{hero_h1}</h1>
  <p class="hero-sub">{hero_sub}</p>
</header>

{stats_block}



<main class="content" id="main-content">
  {compact_section}
  <section class="group" id="group-endorsement" aria-labelledby="heading-endorsement">
    <div class="group-header">
      <h2 id="heading-endorsement">Endorsement States</h2>
      <span class="group-count" aria-label="{endorsement_count} states">{endorsement_count}</span>
    </div>
    <p class="group-desc">{endorsement_desc}</p>
    <div class="group-head-row" aria-hidden="true">
      <span>State</span>
      <span>{timeline_col_label}</span>
      <span class="align-right">Extra steps</span>
      <span class="align-right">{fee_col_label}</span>
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

</body>
</html>'''
