#!/usr/bin/env python3
"""
Fee Research Runner — Uses Gemini API with Google Search grounding
to research missing licensing fees from official state board websites.

Prerequisites:
  pip install google-genai

Usage:
  export GEMINI_API_KEY="your-key-here"
  python3 research/fee_research_runner.py

Outputs results to research/results/ot-batch-{N}.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Install the Gemini SDK: pip install google-genai")
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

MANIFEST_PATH = Path(__file__).resolve().parent / "fee_research_manifest.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

# ── Gemini client ──────────────────────────────────────────────
API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not API_KEY:
    print("Set GEMINI_API_KEY environment variable")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

SYSTEM_INSTRUCTION = """You are a professional licensing researcher. Your task is to find the EXACT, CURRENT dollar amounts for healthcare professional licensing fees from official U.S. state board websites.

RULES:
1. ONLY cite official state board websites (.gov, .state.*, or the official board domain). Never cite aggregator sites, blog posts, or forums.
2. If the board website publishes a fee schedule PDF, cite the PDF URL.
3. If a fee is genuinely not published on the board site, respond with "NOT_PUBLISHED".
4. Return dollar amounts as plain numbers without $ sign (e.g., 150, not $150).
5. For renewal cycles, use exact format: "Every X years" or "Annual".
6. For processing time, use exact format: "X to Y Weeks" or "X to Y Business Days".
7. If the board site is down or returns errors, respond with "SITE_UNAVAILABLE".
8. Always respond with valid JSON only. No markdown fences, no commentary outside the JSON."""

RESPONSE_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "state": {"type": "STRING"},
            "state_abbr": {"type": "STRING"},
            "vertical": {"type": "STRING"},
            "profession": {"type": "STRING"},
            "board_url_used": {"type": "STRING"},
            "fields": {
                "type": "OBJECT",
                "properties": {
                    "quick_facts.total_fee": {
                        "type": "OBJECT",
                        "properties": {
                            "value": {"type": "STRING"},
                            "source_url": {"type": "STRING"},
                            "source_quote": {"type": "STRING"},
                            "confidence": {"type": "STRING", "enum": ["HIGH", "MEDIUM", "LOW"]},
                        },
                        "required": ["value", "source_url", "source_quote", "confidence"],
                    },
                    "quick_facts.renewal_fee": {
                        "type": "OBJECT",
                        "properties": {
                            "value": {"type": "STRING"},
                            "source_url": {"type": "STRING"},
                            "source_quote": {"type": "STRING"},
                            "confidence": {"type": "STRING", "enum": ["HIGH", "MEDIUM", "LOW"]},
                        },
                        "required": ["value", "source_url", "source_quote", "confidence"],
                    },
                    "fees_endorsement.total_estimated_cost": {
                        "type": "OBJECT",
                        "properties": {
                            "value": {"type": "STRING"},
                            "source_url": {"type": "STRING"},
                            "source_quote": {"type": "STRING"},
                            "confidence": {"type": "STRING", "enum": ["HIGH", "MEDIUM", "LOW"]},
                        },
                        "required": ["value", "source_url", "source_quote", "confidence"],
                    },
                },
            },
        },
        "required": ["state", "state_abbr", "vertical", "profession", "board_url_used", "fields"],
    },
}

STATE_ABBRS = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}


def build_batch_prompt(items: list[dict]) -> str:
    """Build a prompt for a batch of states."""
    lines = [
        "Search the official state board websites for OCCUPATIONAL THERAPIST licensing fees.",
        "For each state below, find these 3 data points:",
        "- quick_facts.total_fee: The total endorsement/reciprocity application fee for an OT transferring from another state",
        "- quick_facts.renewal_fee: The biennial or annual license renewal fee",
        "- fees_endorsement.total_estimated_cost: The total estimated cost for endorsement (application + background check + any other mandatory fees)",
        "",
        "STATES:",
    ]
    for i, item in enumerate(items, 1):
        abbr = STATE_ABBRS.get(item["state"], "??")
        lines.append(
            f'{i}. {item["state"]} ({abbr}) — {item["board_name"]} — {item["board_url"]}'
        )

    lines.append("")
    lines.append("Return a JSON array with one object per state. Use vertical='ot', profession='Occupational Therapist'.")
    lines.append("Dollar values as plain numbers (no $ sign). confidence = HIGH/MEDIUM/LOW.")
    lines.append("If a fee cannot be found, use value='NOT_PUBLISHED'.")
    return "\n".join(lines)


def run_batch(batch_name: str, items: list[dict]) -> list[dict]:
    """Run a single batch through Gemini with Search grounding."""
    prompt = build_batch_prompt(items)
    print(f"\n{'='*60}")
    print(f"Running batch: {batch_name} ({len(items)} states)")
    print(f"{'='*60}")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.1,
            ),
        )

        # Extract text from response
        text = response.text.strip()

        # Clean markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()

        results = json.loads(text)

        # Save results
        out_path = RESULTS_DIR / f"{batch_name}.json"
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"  Saved {len(results)} results to {out_path}")

        # Print summary
        for r in results:
            fields = r.get("fields", {})
            vals = []
            for k, v in fields.items():
                val = v.get("value", "?")
                conf = v.get("confidence", "?")
                vals.append(f"{k}={'$'+val if val.isdigit() else val}({conf})")
            print(f"  {r['state']}: {', '.join(vals)}")

        return results

    except Exception as e:
        print(f"  ERROR: {e}")
        return []


def main():
    # Filter to OT items only (biggest gap)
    ot_items = [item for item in MANIFEST if item["vertical"] == "ot"]
    other_items = [item for item in MANIFEST if item["vertical"] != "ot"]

    # Batch OT into groups of 10
    batches = []
    for i in range(0, len(ot_items), 10):
        batch_num = i // 10 + 1
        batches.append((f"ot-batch-{batch_num}", ot_items[i : i + 10]))

    # Add non-OT as a single batch
    if other_items:
        batches.append(("other-batch", other_items))

    all_results = []
    for batch_name, items in batches:
        results = run_batch(batch_name, items)
        all_results.extend(results)
        # Rate limit
        if batch_name != batches[-1][0]:
            print("  Waiting 5s before next batch...")
            time.sleep(5)

    # Write combined results
    combined_path = RESULTS_DIR / "all_results.json"
    with open(combined_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"DONE — {len(all_results)} total results saved")
    print(f"Combined: {combined_path}")
    print(f"\nNext step: python3 research/apply_fee_research.py")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
