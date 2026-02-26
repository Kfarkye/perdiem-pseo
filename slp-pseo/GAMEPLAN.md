# SLP pSEO — State Licensing Directory

## Architecture

Fork of `dietitian-pseo`. Same compiler, same design system.

**Schema delta from dietitian:**

- `profession_name`: "Speech-Language Pathologist"
- `credential_nomenclature`: varies by state (e.g., "Licensed SLP", "CCC-SLP", "SLP-CF")
- `telepractice_text`: NEW field — state-specific telehealth practice rules
- `provisional_text`: adapted for Clinical Fellowship (CF) context
- `license_types[]`: typically includes full SLP + Intern/CF license
- `steps[]`: includes Praxis exam (test code 5331, score 162), master's degree, CF completion
- `documents[]`: includes Praxis score report, CF verification, transcripts

## File Slug Pattern

`{state_slug}-slp.json` → compiles to `{state_slug}-slp.html`

## Build

```bash
python3 build.py
```

## JSON Schema Contract

Every state JSON MUST follow this exact structure:

```json
{
    "state_name": "...",
    "state_slug": "...",
    "profession_name": "Speech-Language Pathologist",
    "credential_nomenclature": "...",
    "last_updated": "2026-02-25",
    "seo": {
        "title": "...",
        "description": "...",
        "keywords": "..."
    },
    "board": {
        "name": "...",
        "parent_dept": "...",
        "mailing_address": "...",
        "physical_address": "...",
        "phone": "...",
        "fax": "...",
        "email": "mailto:...",
        "url": "https://..."
    },
    "quick_facts": {
        "total_fee": "$...",
        "fee_breakdown": "...",
        "renewal_fee": "$...",
        "renewal_cycle": "...",
        "processing_time": "...",
        "license_duration": "..."
    },
    "license_types": [
        {
            "title": "...",
            "description": "..."
        }
    ],
    "steps": [
        {
            "title": "...",
            "description": "..."
        }
    ],
    "documents": [
        {
            "item": "...",
            "detail": "..."
        }
    ],
    "telepractice_text": "...",
    "provisional_text": "...",
    "reciprocity_text": "...",
    "faqs": [
        {
            "question": "...",
            "answer": "..."
        }
    ]
}
```

## Agent Prompt (51 states)

For each of the 50 US states + DC, create a JSON file in `database/json/` following the schema above. Research each state's SLP licensing board website for:

1. **Board info**: name, parent department, mailing/physical address, phone, fax, email, URL
2. **Fees**: initial application fee, background check fee, examination fee, total; renewal fee and cycle
3. **Processing time**: typical turnaround from application to license issuance
4. **License types**: full SLP license, intern/CF license, temporary/provisional permits
5. **Application steps**: degree requirement, Praxis exam, Clinical Fellowship, application submission, background check
6. **Required documents**: transcripts, Praxis scores, CF verification, supervision plan
7. **Telepractice rules**: whether state permits telehealth SLP services, any restrictions, compact membership
8. **Provisional/CF rules**: how the state handles Clinical Fellows, supervision requirements
9. **Reciprocity**: endorsement pathways for out-of-state SLPs, ASHA CCC-SLP recognition
10. **FAQ**: 2-3 state-specific questions about cost, exam requirements, telepractice

### Key SLP-specific research notes

- **Praxis exam**: Most states require test code 5331, passing score 162 (ASHA standard). Some states may have different passing scores.
- **ASHA CCC-SLP**: The Certificate of Clinical Competence is the national credential. Many states accept it as proof of meeting educational/clinical requirements.
- **Clinical Fellowship (CF)**: 36 weeks full-time (1,260 hours minimum). States vary on whether they issue a separate intern/CF license.
- **Telepractice Compact**: Check if the state is a member of the ASLP-IC (Audiology and Speech-Language Pathology Interstate Compact).
- **States without SLP licensing**: Currently all 50 states + DC require SLP licensing, though requirements vary significantly.

### State slugs

alabama, alaska, arizona, arkansas, california, colorado, connecticut, dc, delaware, florida, georgia, hawaii, idaho, illinois, indiana, iowa, kansas, kentucky, louisiana, maine, maryland, massachusetts, michigan, minnesota, mississippi, missouri, montana, nebraska, nevada, new-hampshire, new-jersey, new-mexico, new-york, north-carolina, north-dakota, ohio, oklahoma, oregon, pennsylvania, rhode-island, south-carolina, south-dakota, tennessee, texas, utah, vermont, virginia, washington, west-virginia, wisconsin, wyoming

## Deployment

1. `python3 build.py`
2. `git add . && git commit -m "feat: launch 51-state SLP directory" && git push`
3. Submit sitemap to GSC
