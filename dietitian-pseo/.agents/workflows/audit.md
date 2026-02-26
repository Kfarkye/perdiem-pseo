---
description: Audit all JSON files in the database for schema compliance and data quality
---

# /audit

## Overview

Validates every `.json` file in `./database/json/` against the canonical schema.
This is a Claude-only workflow (no Gemini needed).

---

## Step 1: SCAN

// turbo

1. List all `.json` files in `./database/json/`
2. For each file, run JSON parse validation
3. Check all 14 required top-level keys exist

## Step 2: SCHEMA DEEP CHECK

For each file, verify:

- `state_slug` matches the filename prefix (e.g., `new-mexico` in `new-mexico-dietitian.json`)
- `profession_name` matches the filename suffix
- `credential_nomenclature` is NOT generic "Licensed Dietitian" unless that's the actual state term
- `seo.title` contains the `credential_nomenclature` value (not a generic substitute)
- `seo.keywords` has 4+ comma-separated terms
- `board.email` starts with `mailto:` or is "Not Applicable"
- `board.url` is a valid URL string or "Not Applicable"
- `quick_facts.total_fee` starts with `$`
- `faqs` has at least 2 entries
- `faqs[].answer` contains at least one dollar amount or board name (no generic answers)
- `last_updated` is a valid YYYY-MM-DD date

## Step 3: REPORT

Output a table:

```
| File | Valid JSON | Keys | Nomenclature | SEO | Fees | FAQs | Status |
|------|-----------|------|-------------|-----|------|------|--------|
```

Flag any issues with ❌ and suggest fixes.
