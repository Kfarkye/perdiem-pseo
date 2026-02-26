---
description: Build a pSEO state-profession JSON file using the dual-engine workflow
---

# /build [STATE] | [PROFESSION]

## Overview

This workflow produces a single production-ready JSON file for a US state + profession combination.
The work is split between two engines:

- **Gemini (USER)** — Live .gov research, fee extraction, anti-bot navigation
- **Claude (AGENT)** — Schema enforcement, copywriting, JSON synthesis, file I/O

---

## Step 1: ENVIRONMENT CHECK (Agent)

// turbo

1. Run `mkdir -p ./database/json/`
2. Read all existing `.json` files in `./database/json/` to calibrate schema and tone
3. Confirm the state+profession combo doesn't already exist (if it does, ask user if this is an overwrite)

## Step 2: GENERATE GEMINI RESEARCH PROMPT (Agent)

The agent constructs a ready-to-paste Gemini prompt and gives it to the user.
The prompt MUST include:

- The exact state and profession
- All 12 data points needed (see Research Target Checklist below)
- Instruction to use ONLY `.gov` / `.us` sources
- Instruction to provide source URLs for every claim
- Instruction to note the EXACT credential title used by the state (not assumed)

### Research Target Checklist (what Gemini must find)

```
1.  CREDENTIAL NOMENCLATURE — exact legal title (e.g., "Certified Dietitian-Nutritionist", NOT generic "Licensed Dietitian")
2.  BOARD NAME — full official name of the licensing board or program
3.  PARENT DEPARTMENT — the state agency the board sits under
4.  BOARD CONTACT — mailing address, physical address, phone, fax, email, website URL
5.  FEE MATH — itemize EVERY fee: application, license, exam, background check, fingerprint, technology fee. Sum them.
6.  RENEWAL — renewal fee, cycle length, CE/CPE hours required
7.  PROCESSING TIME — stated or estimated timeline
8.  LICENSE DURATION — how long until first renewal
9.  LICENSE TYPES — all credential tiers/categories for this profession in this state
10. APPLICATION STEPS — ordered steps, including any state-specific exams (e.g., jurisprudence)
11. REQUIRED DOCUMENTS — what must be submitted
12. PROVISIONAL / TEMPORARY PERMITS — does the state offer them? conditions?
13. RECIPROCITY / ENDORSEMENT — how out-of-state applicants transfer
14. SOURCE URLs — .gov/.us URL for EVERY claim above
```

**The agent gives the user this prompt. The user runs it in Gemini. The user pastes the raw output back.**

## Step 3: INTAKE & VALIDATION (Agent)

When the user pastes back Gemini's research:

1. Parse all 14 data points from the raw text
2. Flag any MISSING items — ask user to re-query Gemini for those specific gaps
3. Flag any SUSPICIOUS items — fees that seem too low/high, nomenclature that doesn't match .gov source
4. Cross-check: does the credential nomenclature match what's on the .gov URL provided?
5. Do the fee math: independently sum the itemized fees and verify they match the stated total

## Step 4: JSON SYNTHESIS (Agent)

Once all 14 points are validated:

1. Read the 3 seed files to lock tone and formatting
2. Map data to the canonical schema (see schema in .cursorrules)
3. Write localized, state-specific copywriting for all text fields:
   - `seo.title` and `seo.description` — use EXACT credential_nomenclature, not generic
   - `seo.keywords` — 5-7 local keyword variations a professional would actually search
   - `license_types[].description` — synthesized from requirements, not copy-pasted
   - `steps[].description` — actionable, includes dollar amounts inline
   - `faqs` — 3-5 questions with explicit local data (fees, board names, exam names)
   - `provisional_text` — if none, explicitly state removal/absence
   - `reciprocity_text` — tailored to the state's actual endorsement process
4. Strict JSON rules:
   - No trailing commas
   - No markdown wrappers
   - URLs as plain strings (no markdown link syntax)
   - `<br>` for address line breaks
   - `mailto:` prefix on email
   - `last_updated` = today's date (YYYY-MM-DD)

## Step 5: FILE WRITE (Agent)

// turbo

1. Write raw JSON to `./database/json/[state-slug]-[profession-slug].json`
2. Validate the written file with `python3 -c "import json; json.load(open('...'))"`
3. Run schema key check against the 14 required top-level keys

## Step 6: VERIFICATION OUTPUT (Agent)

Print a summary table:

```
✅ File:     database/json/[slug].json
💰 Total:   $XXX ([breakdown])
🏛️ Board:   [Board Name]
📋 Nomenclature: [Exact credential title]
🔗 Sources: [list .gov URLs used]
```

Then ask: **"Next state?"**

---

## Edge Cases

### NO REGULATION (e.g., California)

If Gemini reports no state board exists:

- Set `board.name` = "No State Licensing Board"
- Set `total_fee` = "$0"
- Set contact fields to "Not Applicable"
- Adjust ALL copywriting to explicitly say no state license is required
- Still write the JSON file

### SPLIT CREDENTIALS (e.g., Dietitian AND Nutritionist are separate)

- Ask user: build one file per credential, or combine?
- Default: one file per credential (separate slugs)

### FEES NOT FOUND

- Set fee to `null` or "Not specified by board"
- NEVER guess a dollar amount
- Note the gap in the verification output
