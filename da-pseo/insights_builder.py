"""
Quick Insights builder — computes top-3 per category from states_manifest.
Returns HTML string for insertion into the landing page index.html.

Categories:
  1. No License Needed (states with $0 fee and N/A processing time)
  2. Fastest Processing (sorted by estimated days)
  3. Lowest Fee (sorted by numeric fee, excluding $0 no-license states)
"""
import re


def _parse_days(time_str: str) -> float:
    """Convert processing time string to approximate days for sorting."""
    t = time_str.lower()
    nums = re.findall(r"(\d+)", t)
    if not nums:
        return 9999.0
    first = int(nums[0])
    if "business day" in t:
        return first * 1.4
    elif "day" in t:
        return float(first)
    elif "week" in t:
        return first * 7.0
    elif "month" in t:
        return first * 30.0
    return 9999.0


def _parse_fee_num(fee_str: str) -> float:
    """Extract numeric fee value."""
    if not fee_str or str(fee_str).lower() == "n/a":
        return 9999.0
    m = re.search(r"[\d,.]+", str(fee_str).replace(",", ""))
    return float(m.group()) if m else 9999.0

def _parse_years(duration_str: str) -> float:
    """Convert license duration to years for annualized cost."""
    t = str(duration_str).lower()
    if t == "n/a" or not t:
        return 1.0
    nums = re.findall(r"(\d+)", t)
    if not nums:
        return 1.0
    first = int(nums[0])
    if "month" in t:
        return first / 12.0
    return float(first) # assume years by default

def _build_insight_col(title: str, value_type: str, states: list) -> str:
    """Build a single 3-item column for the insights grid."""
    rows = []
    for s in states:
        if value_type == "Static list":
            if title == "Compact Member":
                val = "Yes"
            else:
                val = s.get("fee", "$0")
        elif value_type in ("processing time", "time string"):
            val = s.get("time", "N/A")
        elif value_type == "exam fee":
            val = s.get("jurisprudence", "N/A")
        elif value_type == "fee string":
            val = s.get("fee", "N/A")
        else:
            val = "N/A"
            
        row = (
            '      <div class="insight-row">'
            '<a href="/' + s.get("slug", "") + '">'
            + s.get("name", "") + "</a>"
            "<span>" + str(val) + "</span></div>"
        )
        rows.append(row)
        
    return (
        '    <div class="insight-col">\n'
        f'      <div class="insight-col-title">{title}</div>\n'
        + "\n".join(rows) +
        '\n    </div>'
    )


def build_insights_html(states_manifest: list) -> str:
    # ==========================================
    # DATA SORTS & FILTERS
    # ==========================================
    
    # 🟢 Quick Licensure Helpers (Best first)
    compact_states = [s for s in states_manifest if s.get("compact") is True]
    has_compact = len(compact_states) > 0

    no_fee_states = [
        s for s in states_manifest 
        if s.get("fee_bucket") == "no-fee" and ("n/a" in str(s.get("time", "")).lower() or "not applicable" in str(s.get("time", "")).lower())
    ]
    
    temp_license_states = sorted(
        [s for s in states_manifest if s.get("temp_license") is True], 
        key=lambda x: _parse_days(x.get("time", "999"))
    )
    
    fastest_states = sorted(
        [s for s in states_manifest if s.get("time") and "n/a" not in str(s.get("time")).lower() and "tbd" not in str(s.get("time")).lower() and s.get("time") != "?"],
        key=lambda x: _parse_days(x.get("time", "999"))
    )
    if not fastest_states: # Fallback just in case
        fastest_states = states_manifest

    # 🔴 Tough Board Process Helpers (Worst first)
    exam_states = sorted(
        [s for s in states_manifest if s.get("jurisprudence") and "n/a" not in str(s.get("jurisprudence")).lower() and _parse_fee_num(s.get("jurisprudence", "0")) > 0], 
        key=lambda x: _parse_fee_num(x.get("jurisprudence", "0")), 
        reverse=True
    )
    
    slowest_states = sorted(
        [s for s in states_manifest if s.get("time") and "n/a" not in str(s.get("time")).lower() and "tbd" not in str(s.get("time")).lower() and s.get("time") != "?"], 
        key=lambda x: _parse_days(x.get("time", "0")), 
        reverse=True
    )
    
    highest_fee_states = sorted(
        [s for s in states_manifest if s.get("fee") and "n/a" not in str(s.get("fee")).lower()], 
        key=lambda x: _parse_fee_num(x.get("fee", "0")), 
        reverse=True
    )

    html = []

    # ==========================================
    # 🟢 SECTION 1: QUICK LICENSURE
    # ==========================================
    html.append('<div class="insight-section">')
    html.append('  <div class="insight-section-label green">🟢 Quick Licensure &mdash; Where can I start working fastest?</div>')
    html.append('  <div class="insights">')
    
    c_cols = 0
    if has_compact:
        html.append(_build_insight_col("Compact Member", "Static list", compact_states[:3]))
        c_cols += 1
        if no_fee_states:
            html.append(_build_insight_col("No License Needed", "Static list", no_fee_states[:3]))
            c_cols += 1
    else:
        if no_fee_states:
            html.append(_build_insight_col("No License Needed", "Static list", no_fee_states[:3]))
            c_cols += 1
            
    if temp_license_states and c_cols < 3:
        html.append(_build_insight_col("Temp License Available", "processing time", temp_license_states[:3]))
        c_cols += 1
        
    if fastest_states and c_cols < 4: 
        html.append(_build_insight_col("Fastest Processing", "time string", fastest_states[:3]))

    html.append('  </div>')
    html.append('</div>')

    # ==========================================
    # 🔴 SECTION 2: TOUGH BOARD Process
    # ==========================================
    if exam_states or slowest_states or highest_fee_states:
        html.append('<div class="insight-section">')
        html.append('  <div class="insight-section-label red">🔴 Tough Board Process &mdash; Where should I expect friction?</div>')
        html.append('  <div class="insights">')
        
        t_cols = 0
        if exam_states:
             html.append(_build_insight_col("State Exam Required", "exam fee", exam_states[:3]))
             t_cols += 1
             
        if slowest_states and t_cols < 3:
             html.append(_build_insight_col("Slowest Processing", "time string", slowest_states[:3]))
             t_cols += 1
             
        if highest_fee_states and t_cols < 3:
             html.append(_build_insight_col("Highest Total Fee", "fee string", highest_fee_states[:3]))
             
        html.append('  </div>')
        html.append('</div>')

    return "\n".join(html)
