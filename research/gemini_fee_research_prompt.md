# Gemini Grounded Search — Fee Research Prompt

## System Instruction

```
You are a professional licensing researcher. Your task is to find the EXACT, CURRENT dollar amounts for healthcare professional licensing fees from official U.S. state board websites.

RULES:
1. ONLY cite official state board websites (.gov, .state.*, or the official board domain provided). Never cite aggregator sites, blog posts, or forums.
2. If the board website publishes a fee schedule PDF, cite the PDF URL.
3. If a fee is genuinely not published on the board site, respond with "NOT_PUBLISHED" — never guess.
4. Return dollar amounts as plain numbers without $ sign (e.g., 150, not $150).
5. For renewal cycles, use exact format: "Every X years" or "Annual".
6. For processing time, use exact format: "X to Y Weeks" or "X to Y Business Days".
7. If the board site is down or returns errors, respond with "SITE_UNAVAILABLE".
```

## Per-Item Prompt Template

Use this prompt once per state/vertical combo. Replace `{VARIABLES}` with values from the manifest.

```
Search the official {BOARD_NAME} website at {BOARD_URL} for the current licensing fees for {PROFESSION} in {STATE}.

I need the following specific data points:
{MISSING_FIELDS_LIST}

For each field, provide:
1. The exact dollar amount or value
2. The exact URL where you found it
3. A one-sentence quote from the source page that confirms the value

If the board publishes a fee schedule page or PDF, start there.

Respond in the exact JSON schema below. Do not add commentary outside the JSON.
```

## Response Schema (JSON)

```json
{
  "type": "object",
  "properties": {
    "state": { "type": "string" },
    "state_abbr": { "type": "string" },
    "vertical": { "type": "string" },
    "profession": { "type": "string" },
    "board_url_used": { "type": "string", "description": "The actual URL you navigated to" },
    "research_timestamp": { "type": "string", "format": "date-time" },
    "fields": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "value": {
            "type": "string",
            "description": "The fee amount (e.g. '150'), cycle (e.g. 'Every 2 years'), or time (e.g. '4 to 6 Weeks'). Use 'NOT_PUBLISHED' or 'SITE_UNAVAILABLE' if applicable."
          },
          "source_url": {
            "type": "string",
            "description": "Direct URL to the page or PDF where this value was found"
          },
          "source_quote": {
            "type": "string",
            "description": "Exact sentence or phrase from the source that confirms this value"
          },
          "confidence": {
            "type": "string",
            "enum": ["HIGH", "MEDIUM", "LOW"],
            "description": "HIGH = exact match on fee schedule. MEDIUM = inferred from related page. LOW = only partial match found."
          }
        },
        "required": ["value", "source_url", "source_quote", "confidence"]
      },
      "description": "Keys are the field paths like 'quick_facts.total_fee', 'quick_facts.renewal_fee', 'fees_endorsement.total_estimated_cost'"
    }
  },
  "required": ["state", "state_abbr", "vertical", "profession", "board_url_used", "research_timestamp", "fields"]
}
```

## Example Response

```json
{
  "state": "Alabama",
  "state_abbr": "AL",
  "vertical": "ot",
  "profession": "Occupational Therapist",
  "board_url_used": "http://www.ot.alabama.gov/fees.html",
  "research_timestamp": "2026-03-19T22:00:00Z",
  "fields": {
    "quick_facts.total_fee": {
      "value": "150",
      "source_url": "http://www.ot.alabama.gov/fees.html",
      "source_quote": "Endorsement Application Fee: $150.00",
      "confidence": "HIGH"
    },
    "quick_facts.renewal_fee": {
      "value": "100",
      "source_url": "http://www.ot.alabama.gov/fees.html",
      "source_quote": "Biennial Renewal Fee: $100.00",
      "confidence": "HIGH"
    },
    "fees_endorsement.total_estimated_cost": {
      "value": "150",
      "source_url": "http://www.ot.alabama.gov/fees.html",
      "source_quote": "Endorsement Application Fee: $150.00 (includes all licensing costs)",
      "confidence": "HIGH"
    }
  }
}
```

## Batch Strategy

The manifest contains **63 items** across these verticals:

| Vertical | Count | Primary Missing Fields |
|---|---|---|
| `ot` (Occupational Therapist) | 51 | `total_fee`, `renewal_fee`, `total_estimated_cost` |
| `lpn` (Licensed Practical Nurse) | 1 | `renewal_fee` |
| `dietitian` | 3 | `renewal_fee`, `renewal_cycle`, `license_duration` |
| `pharm` (Pharmacy Technician) | 4 | `background_check_fee` |
| `pharmacist` | 4 | `background_check_fee` |

### Recommended batching:
1. **OT first** (51 states) — biggest gap, all same 3 fields
2. **Pharm + Pharmacist** (8 states) — just background_check_fee
3. **Dietitian + LPN** (4 states) — mixed fields

For OT, you can batch 5-10 states per Gemini call since they all need the same 3 fields.
