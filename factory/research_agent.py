#!/usr/bin/env python3
"""
CNA-Quality Research Agent — Factory Pipeline Layer 2

Takes a specialty slug (e.g. 'pharm', 'aud', 'dietitian') and enriches all
51 state JSON files with CNA-level polish:
  - credential_type schema
  - consumer-friendly hero dek
  - state-specific step copy
  - training hours / exam name / CE requirement (if missing)

Uses Gemini 2.0 Flash for structured research.

Usage:
  python3 factory/research_agent.py pharm              # enrich all 51 pharm states
  python3 factory/research_agent.py pharm --state AZ   # enrich just Arizona
  python3 factory/research_agent.py pharm --dry-run     # preview without writing
  python3 factory/research_agent.py cna --from-audit   # consume audit re-research queue
"""

import argparse
import json
import os
import sys
import time
import glob
from pathlib import Path
from datetime import datetime

# ── Cross-project ID system ──
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from id_constants import NS, OBJ, EVT, VERTICAL_TO_PROF, make_object_id, make_event_id

# ── Gemini client ──
from google import genai

# ── Load API key ──
def load_api_key():
    """Load from .env or environment."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')
    print("ERROR: GEMINI_API_KEY not found in env or .env file")
    sys.exit(1)


# ── State list ──
STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
    "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
]

STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}


def build_research_prompt(state_name: str, profession_name: str, existing_data: dict) -> str:
    """Build the Gemini research prompt for a single state."""

    existing_qf = existing_data.get("quick_facts", {})
    board = existing_data.get("board", {})

    return f"""You are a healthcare licensing researcher. Research the official {state_name} requirements for becoming a {profession_name}.

EXISTING DATA (already in our system — verify and fill gaps):
- Board: {board.get('name', 'Unknown')}
- Board URL: {board.get('url', 'Unknown')}
- Total fee: {existing_qf.get('total_fee', 'MISSING')}
- Training hours: {existing_qf.get('training_hours', 'MISSING')}
- Exam name: {existing_qf.get('exam_name', 'MISSING')}
- CE requirement: {existing_qf.get('ce_requirement', 'MISSING')}
- Renewal cycle: {existing_qf.get('renewal_cycle', 'MISSING')}
- Processing time: {existing_qf.get('processing_time', 'MISSING')}

Return a JSON object with EXACTLY these fields. Use real official data only. If you cannot determine a value with confidence, use null.

{{
  "credential_type": {{
    "official_term": "<what the state officially calls this credential: 'license', 'certification', 'registration', 'permit', etc.>",
    "page_title_term": "<capitalized version for page titles: 'License', 'Certification', 'Registration', etc.>",
    "renewal_term": "<how renewal is described: 'license renewal', 'certification renewal', etc.>",
    "transfer_term": "<how out-of-state transfer is described: 'endorsement', 'reciprocity', 'transfer', etc.>"
  }},
  "training_hours": "<e.g. '120 hours' or null if not applicable>",
  "exam_name": "<official exam name, e.g. 'PTCB' or 'ExCPT' or null>",
  "ce_requirement": "<e.g. '20 hours per renewal cycle' or null>",
  "renewal_cycle": "<e.g. 'Every 2 years' or null>",
  "hero_dek": "<1-sentence consumer-friendly summary: '[State] [profession] [credential_term] requires [key requirement 1], [key requirement 2], and [key requirement 3].'>",
  "steps": [
    {{
      "title": "<step 1 title — clear, consumer-friendly>",
      "description": "<1-sentence state-specific description>"
    }},
    {{
      "title": "<step 2 title>",
      "description": "<1-sentence state-specific description>"
    }},
    {{
      "title": "<step 3 title>",
      "description": "<1-sentence state-specific description>"
    }}
  ]
}}

RULES:
- Use the state's official terminology (license vs certification vs registration)
- Hero dek must name the state and profession, feel consumer-facing, not bureaucratic
- Steps should be 3 steps max, state-specific language, concise
- If the profession is typically "licensed" in this state, use "license". If "certified", use "certification".
- Return ONLY the JSON object, no markdown, no commentary
"""


def parse_gemini_response(text: str) -> dict:
    """Extract JSON from Gemini response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        # Strip markdown code fence
        lines = text.split("\n")
        lines = lines[1:]  # remove opening ```json
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)


def apply_enrichment(existing: dict, research: dict) -> dict:
    """Merge research results into existing JSON, preserving what's already there."""
    data = existing.copy()
    state = data["state_name"]
    profession = data["profession_name"]

    # 1. credential_type — always write (this is the main new field)
    ct = research.get("credential_type", {})
    if ct and ct.get("official_term"):
        data["credential_type"] = ct

    # 2. quick_facts — fill gaps only
    qf = data.setdefault("quick_facts", {})
    if research.get("training_hours") and not qf.get("training_hours"):
        qf["training_hours"] = research["training_hours"]
    if research.get("exam_name") and not qf.get("exam_name"):
        qf["exam_name"] = research["exam_name"]
    if research.get("ce_requirement") and not qf.get("ce_requirement"):
        qf["ce_requirement"] = research["ce_requirement"]
    if research.get("renewal_cycle") and qf.get("renewal_cycle") in (None, "", "See board"):
        qf["renewal_cycle"] = research["renewal_cycle"]

    # 3. hero dek — always write
    cred_term = (ct or {}).get("official_term", "licensing")
    hero_dek = research.get("hero_dek")
    if hero_dek:
        v = data.setdefault("variants", {}).setdefault("new_applicant", {})
        hero = v.setdefault("hero", {})
        hero["title"] = f"Become a {profession} in {state}"
        hero["dek"] = hero_dek

    # 4. steps — always write (overwrite generic steps)
    new_steps = research.get("steps")
    if new_steps and len(new_steps) >= 2:
        data["steps"] = new_steps

    return data


def research_state(client, state_name: str, profession_name: str, existing_data: dict) -> dict:
    """Call Gemini to research a single state and return enrichment data."""
    prompt = build_research_prompt(state_name, profession_name, existing_data)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    return parse_gemini_response(response.text)


def main():
    parser = argparse.ArgumentParser(description="CNA-quality research agent for any specialty")
    parser.add_argument("slug", help="Specialty slug (e.g. pharm, aud, dietitian)")
    parser.add_argument("--state", help="Single state abbreviation (e.g. AZ). If omitted, runs all 51.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between API calls (seconds)")
    parser.add_argument("--from-audit", action="store_true", help="Consume audit_reresearch_<slug>.json queue")
    args = parser.parse_args()

    today = datetime.now().strftime("%Y%m%d")

    slug = args.slug
    json_dir = Path(__file__).resolve().parent.parent / f"{slug}-pseo" / "database" / "json"

    if not json_dir.exists():
        print(f"ERROR: {json_dir} not found")
        sys.exit(1)

    # Load API key and create client
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)

    # Find JSON files
    json_files = sorted(json_dir.glob("*.json"))
    if not json_files:
        print(f"ERROR: No JSON files in {json_dir}")
        sys.exit(1)

    # Filter to single state if requested
    if args.state:
        abbr = args.state.upper()
        # Find the state name
        target_state = None
        for name, ab in STATE_ABBR.items():
            if ab == abbr:
                target_state = name
                break
        if not target_state:
            print(f"ERROR: Unknown state abbreviation: {abbr}")
            sys.exit(1)
        json_files = [f for f in json_files if target_state.lower().replace(" ", "-") in f.stem]

    print(f"{'DRY RUN — ' if args.dry_run else ''}Research Agent: {slug}")
    print(f"  JSON dir: {json_dir}")
    print(f"  States to process: {len(json_files)}")
    print(f"  Delay: {args.delay}s between calls")
    print("=" * 60)

    success = 0
    errors = 0

    # ── Event tracking ──
    event_log = []
    event_seq = {}

    for i, fpath in enumerate(json_files, 1):
        data = json.loads(fpath.read_text(encoding="utf-8"))
        state = data.get("state_name", fpath.stem)
        profession = data.get("profession_name", slug)

        # ── Derive canonical target_id ──
        abbr = STATE_ABBR.get(state, state[:2].upper())
        prof_slug = VERTICAL_TO_PROF.get(slug, slug.upper())
        target_id = make_object_id(NS.SLR, OBJ.PAGE, abbr, prof_slug)

        # Skip if already enriched (unless --from-audit forces re-check)
        if not args.from_audit and data.get("credential_type", {}).get("official_term"):
            print(f"  ⏭️  [{i}/{len(json_files)}] {state} ({target_id}) — already enriched")
            success += 1
            continue

        print(f"  🔍 [{i}/{len(json_files)}] {state} ({target_id})...", end=" ", flush=True)

        # ── Emit BOT.EVT.RESEARCH_TASK ──
        if target_id not in event_seq:
            event_seq[target_id] = 0
        event_seq[target_id] += 1
        research_event_id = make_event_id(NS.BOT, EVT.RESEARCH_TASK, target_id, today, event_seq[target_id])

        try:
            research = research_state(client, state, profession, data)
            enriched = apply_enrichment(data, research)

            # ── Stamp canonical ID on the record ──
            enriched["_target_id"] = target_id
            enriched["_last_research_event"] = research_event_id

            if args.dry_run:
                ct = research.get("credential_type", {})
                print(f"→ {ct.get('official_term', '?')} | {research.get('hero_dek', '?')[:60]}...")
            else:
                fpath.write_text(
                    json.dumps(enriched, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                ct = enriched.get("credential_type", {})
                print(f"✅ {ct.get('official_term', '?')}")

            event_log.append({
                "event_id": research_event_id,
                "target_id": target_id,
                "status": "SUCCESS",
                "state": state,
                "timestamp": datetime.now().isoformat(),
            })
            success += 1

        except Exception as e:
            print(f"❌ {e}")
            event_log.append({
                "event_id": research_event_id,
                "target_id": target_id,
                "status": "ERROR",
                "state": state,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            })
            errors += 1

        # Rate limit
        if i < len(json_files):
            time.sleep(args.delay)

    print("=" * 60)
    print(f"  Done: {success} enriched, {errors} errors")

    # ── Write event log ──
    if event_log:
        log_path = Path(f"research_events_{slug}_{today}.jsonl")
        with open(log_path, "a", encoding="utf-8") as f:
            for evt in event_log:
                f.write(json.dumps(evt) + "\n")
        print(f"  Events written to {log_path}")


if __name__ == "__main__":
    main()
