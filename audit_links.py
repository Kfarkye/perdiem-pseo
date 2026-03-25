#!/usr/bin/env python3
"""
Link Trust Auditor — Production QC for State Licensing Reference

Classifies every URL into one of 6 trust states:
  LIVE              → 200 OK, confirmed reachable
  BOT_BLOCKED       → 403 from automated request, likely live in browser
  AUTH_GATED        → 401/login required, expected for registries
  SSL_LEGACY        → TLS handshake failure, likely live with modern browser
  TIMEOUT_UNSTABLE  → Server didn't respond in time, needs retry
  TRUE_DEAD         → 404, DNS failure, or connection refused — needs re-research

Output: 3 actionable queues with canonical IDs
  Queue 1 (RE_RESEARCH)  → true_dead + dns_failure → feed to research agent
  Queue 2 (MANUAL_VERIFY) → bot_blocked + ssl_legacy + timeout → check in browser
  Queue 3 (EXPECTED)      → auth_gated → no action needed

Every result carries:
  target_id   → SLR.OBJ.PAGE.<STATE>.<PROF>
  event_id    → QC.EVT.<EVENT>.<TARGET_ID>.<YYYYMMDD>.<SEQ>  (actionable only)

Usage:
  python3 audit_links.py cna          # audit CNA vertical
  python3 audit_links.py all          # audit all 10 verticals
  python3 audit_links.py cna --json   # output machine-readable JSON
"""
import json, glob, sys, time
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from id_constants import (
    NS, OBJ, EVT, SLUGS,
    VERTICAL_TO_PROF,
    make_object_id, make_event_id,
)

# ── State name → abbreviation ──
STATE_TO_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC",
    "Puerto Rico": "PR", "Guam": "GU", "US Virgin Islands": "VI",
}

# ── Status taxonomy ──
LIVE = "LIVE"
BOT_BLOCKED = "BOT_BLOCKED"
AUTH_GATED = "AUTH_GATED"
SSL_LEGACY = "SSL_LEGACY"
TIMEOUT_UNSTABLE = "TIMEOUT_UNSTABLE"
TRUE_DEAD = "TRUE_DEAD"

QUEUE_MAP = {
    LIVE: "NO_ACTION",
    BOT_BLOCKED: "MANUAL_VERIFY",
    AUTH_GATED: "EXPECTED",
    SSL_LEGACY: "MANUAL_VERIFY",
    TIMEOUT_UNSTABLE: "MANUAL_VERIFY",
    TRUE_DEAD: "RE_RESEARCH",
}

# Map trust states to event types
STATUS_TO_EVT = {
    TRUE_DEAD: EVT.BROKEN_LINK,
    BOT_BLOCKED: EVT.LINK_CHECK,
    AUTH_GATED: EVT.LINK_CHECK,
    SSL_LEGACY: EVT.LINK_CHECK,
    TIMEOUT_UNSTABLE: EVT.LINK_CHECK,
    LIVE: EVT.LINK_CHECK,
}

ICONS = {
    LIVE: "✅",
    BOT_BLOCKED: "🛡️",
    AUTH_GATED: "🔐",
    SSL_LEGACY: "🔒",
    TIMEOUT_UNSTABLE: "⏱️",
    TRUE_DEAD: "❌",
}

VERTICALS = ["cna", "pharm", "ot", "pt", "slp", "rrt", "aud", "dietitian", "pharmacist", "da"]


def extract_urls(data, prefix=""):
    """Recursively extract every URL string from nested JSON."""
    urls = {}
    if isinstance(data, dict):
        for k, v in data.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, str) and v.startswith("http"):
                urls[path] = v
            elif isinstance(v, (dict, list)):
                urls.update(extract_urls(v, path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            urls.update(extract_urls(item, f"{prefix}[{i}]"))
    return urls


def classify_url(url, timeout=12, retries=2):
    """Check URL and return (trust_status, http_code, detail)."""
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    for attempt in range(retries):
        for method in ["HEAD", "GET"]:
            try:
                req = Request(url, method=method, headers=headers)
                resp = urlopen(req, timeout=timeout)
                return LIVE, resp.status, "OK"

            except HTTPError as e:
                code = e.code
                if method == "HEAD" and code in (403, 405, 406):
                    continue

                if code == 401:
                    return AUTH_GATED, code, "Login/auth required"
                elif code == 403:
                    return BOT_BLOCKED, code, "Forbidden — likely bot-blocked, probably live in browser"
                elif code == 404:
                    return TRUE_DEAD, code, "Page not found"
                elif code == 410:
                    return TRUE_DEAD, code, "Gone (permanently removed)"
                elif 400 <= code < 500:
                    return TRUE_DEAD, code, f"Client error {code}"
                elif code == 999:
                    return BOT_BLOCKED, code, "Anti-bot response (LinkedIn-style)"
                elif code >= 500:
                    if attempt < retries - 1:
                        time.sleep(2)
                        break
                    return TIMEOUT_UNSTABLE, code, f"Server error {code}"
                else:
                    return TRUE_DEAD, code, f"HTTP {code}"

            except URLError as e:
                reason = str(e.reason)
                if "timed out" in reason.lower() or "timeout" in reason.lower():
                    if attempt < retries - 1:
                        time.sleep(3)
                        break
                    return TIMEOUT_UNSTABLE, 0, "Connection timed out"
                elif "ssl" in reason.lower() or "tlsv1" in reason.lower():
                    return SSL_LEGACY, 0, f"SSL/TLS handshake failure — {reason[:60]}"
                elif "nodename" in reason.lower() or "name resolution" in reason.lower():
                    return TRUE_DEAD, 0, "DNS failure — domain does not resolve"
                elif "connection refused" in reason.lower():
                    return TRUE_DEAD, 0, "Connection refused — server down"
                elif "connection reset" in reason.lower():
                    if attempt < retries - 1:
                        time.sleep(2)
                        break
                    return TIMEOUT_UNSTABLE, 0, "Connection reset by peer"
                else:
                    return TRUE_DEAD, 0, f"URL error: {reason[:80]}"

            except Exception as e:
                return TRUE_DEAD, 0, f"Unexpected: {str(e)[:80]}"
        else:
            continue
        continue

    return TIMEOUT_UNSTABLE, 0, "All retries exhausted"


def derive_target_id(state_name, vertical):
    """Derive canonical target_id from state name and vertical slug."""
    abbr = STATE_TO_ABBR.get(state_name, state_name[:2].upper())
    prof = VERTICAL_TO_PROF.get(vertical, vertical.upper())
    return make_object_id(NS.SLR, OBJ.PAGE, abbr, prof)


def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "cna"
    json_output = "--json" in sys.argv
    today = datetime.now().strftime("%Y%m%d")

    if slug == "all":
        patterns = [(s, f"{s}-pseo/database/json/*.json") for s in VERTICALS]
    else:
        patterns = [(slug, f"{slug}-pseo/database/json/*.json")]

    # ── Phase 1: Collect URLs with full identity context ──
    url_sources = {}  # url -> [(state_name, field, vertical, target_id)]
    for vertical, pattern in patterns:
        for fpath in sorted(glob.glob(pattern)):
            data = json.loads(Path(fpath).read_text())
            state_name = data.get("state_name", Path(fpath).stem)
            target_id = derive_target_id(state_name, vertical)

            for field, url in extract_urls(data).items():
                if url not in url_sources:
                    url_sources[url] = []
                url_sources[url].append((state_name, field, vertical, target_id))

    total = len(url_sources)
    if not json_output:
        print(f"Link Trust Audit — {slug.upper()}")
        print(f"{'=' * 60}")
        print(f"Unique URLs to check: {total}")
        print(f"Date: {today}")
        print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'=' * 60}\n")

    # ── Phase 2: Check each URL and assign IDs ──
    results = []
    event_seq = {}  # target_id -> counter for sequential event IDs

    for i, (url, sources) in enumerate(sorted(url_sources.items()), 1):
        status, code, detail = classify_url(url)
        queue = QUEUE_MAP[status]
        evt_type = STATUS_TO_EVT[status]

        # Derive target IDs from all affected pages
        target_ids = list({s[3] for s in sources})
        primary_target = target_ids[0]

        # Generate event IDs for actionable findings only
        event_ids = []
        if queue in ("RE_RESEARCH", "MANUAL_VERIFY"):
            for tid in target_ids:
                if tid not in event_seq:
                    event_seq[tid] = 0
                event_seq[tid] += 1
                eid = make_event_id(NS.QC, evt_type, tid, today, event_seq[tid])
                event_ids.append(eid)

        result = {
            "url": url,
            "target_ids": target_ids,
            "primary_target": primary_target,
            "event_ids": event_ids,
            "status": status,
            "queue": queue,
            "http_code": code,
            "detail": detail,
            "affected_states": sorted({s[0] for s in sources}),
            "affected_fields": sorted({s[1] for s in sources}),
            "affected_verticals": sorted({s[2] for s in sources}),
            "source_count": len(sources),
        }
        results.append(result)

        if not json_output:
            icon = ICONS[status]
            tid_short = primary_target.replace("SLR.OBJ.PAGE.", "")
            print(f"  {icon} [{i}/{total}] {status:18s} {tid_short:10s} {url[:60]}")

        time.sleep(0.3)

    # ── Phase 3: Route into queues ──
    q_reresearch = [r for r in results if r["queue"] == "RE_RESEARCH"]
    q_manual = [r for r in results if r["queue"] == "MANUAL_VERIFY"]
    q_expected = [r for r in results if r["queue"] == "EXPECTED"]
    q_live = [r for r in results if r["queue"] == "NO_ACTION"]

    if json_output:
        output = {
            "audit_timestamp": datetime.now().isoformat(),
            "audit_date": today,
            "vertical": slug,
            "total_urls": total,
            "summary": {
                "live": len(q_live),
                "re_research": len(q_reresearch),
                "manual_verify": len(q_manual),
                "expected_restricted": len(q_expected),
            },
            "queue_re_research": q_reresearch,
            "queue_manual_verify": q_manual,
            "queue_expected": q_expected,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'=' * 60}")
        print(f"SUMMARY")
        print(f"{'=' * 60}")
        print(f"  ✅ Live:                {len(q_live)}")
        print(f"  ❌ Re-research needed:  {len(q_reresearch)}")
        print(f"  🔍 Manual verify:       {len(q_manual)}")
        print(f"  🔐 Expected restricted: {len(q_expected)}")
        print(f"  Total:                  {total}")

        if q_reresearch:
            print(f"\n{'=' * 60}")
            print(f"QUEUE 1 — RE-RESEARCH (feed to research agent)")
            print(f"{'=' * 60}")
            for r in q_reresearch:
                print(f"\n  ❌ {r['detail']}")
                print(f"     URL:       {r['url']}")
                print(f"     Target:    {r['primary_target']}")
                print(f"     Event:     {r['event_ids'][0] if r['event_ids'] else 'N/A'}")
                print(f"     States:    {', '.join(r['affected_states'])}")
                print(f"     Fields:    {', '.join(r['affected_fields'][:3])}")

        if q_manual:
            print(f"\n{'=' * 60}")
            print(f"QUEUE 2 — MANUAL VERIFY (check in browser)")
            print(f"{'=' * 60}")
            for r in q_manual:
                print(f"\n  {ICONS[r['status']]} {r['detail']}")
                print(f"     URL:       {r['url']}")
                print(f"     Target:    {r['primary_target']}")
                print(f"     States:    {', '.join(r['affected_states'])}")

        if q_expected:
            print(f"\n{'=' * 60}")
            print(f"QUEUE 3 — EXPECTED RESTRICTED (no action needed)")
            print(f"{'=' * 60}")
            for r in q_expected:
                print(f"\n  🔐 {r['detail']}")
                print(f"     URL:       {r['url']}")
                print(f"     Target:    {r['primary_target']}")
                print(f"     States:    {', '.join(r['affected_states'])}")

        # Write re-research queue for research agent pipeline
        if q_reresearch:
            out_path = Path(f"audit_reresearch_{slug}.json")
            out_path.write_text(json.dumps(q_reresearch, indent=2))
            print(f"\n→ Re-research queue written to {out_path}")
            print(f"  Contains {len(q_reresearch)} items with target_ids for research_agent.py")

    # ── Phase 4: Append to audit history ──
    history_path = Path("audit_history.jsonl")
    audit_record = {
        "audit_date": today,
        "audit_timestamp": datetime.now().isoformat(),
        "vertical": slug,
        "total_urls": total,
        "live": len(q_live),
        "re_research": len(q_reresearch),
        "manual_verify": len(q_manual),
        "expected": len(q_expected),
    }
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(audit_record) + "\n")

    if not json_output:
        print(f"\n→ Audit record appended to {history_path}")

    return len(q_reresearch)


if __name__ == "__main__":
    sys.exit(main())
