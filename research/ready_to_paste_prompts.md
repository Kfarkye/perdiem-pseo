# Ready-to-Paste Gemini Prompts for Fee Research

## How to Use

1. Open Gemini (gemini.google.com) with **Gemini 2.5 Pro** or **Gemini 2.0 Flash** with **Google Search grounding** enabled
2. Copy-paste each batch prompt below
3. Save each response as `research/results/{batch_name}.json`
4. Run `python3 research/apply_fee_research.py` to hydrate the data files

---

## BATCH 1: OT States A–I (13 states)

```
You are researching OCCUPATIONAL THERAPIST licensing fees for U.S. state boards. Use Google Search to find the current fee schedules on each state board's official website.

For each state below, find these 3 data points:
- quick_facts.total_fee: The total endorsement/reciprocity application fee
- quick_facts.renewal_fee: The license renewal fee
- fees_endorsement.total_estimated_cost: The total estimated cost for endorsement (including app fee + any background check fee)

STATES:
1. Alabama — Board: Alabama State Board of Occupational Therapy — http://www.ot.alabama.gov
2. Alaska — Board: Alaska PT & OT Board — https://www.commerce.alaska.gov/web/cbpl/ProfessionalLicensing/PhysicalTherapyOccupationalTherapy
3. Arizona — Board: Arizona Board of Occupational Therapy Examiners — http://ot.az.gov
4. Arkansas — Board: Arkansas State Medical Board — http://www.armedicalboard.org/Professionals/OccupationalTherapistandAssistant.aspx
5. California — Board: California Board of Occupational Therapy — http://www.bot.ca.gov/
6. Colorado — Board: DORA — http://www.colorado.gov/DORA/Occupational_Therapy
7. Connecticut — Board: DPH — https://portal.ct.gov/DPH
8. Delaware — Board: Division of Professional Regulation — https://dpr.delaware.gov/boards/occupationaltherapy/
9. District of Columbia — Board: DC Health — https://dchealth.dc.gov/service/occupational-therapy-licensing
10. Florida — Board: Florida Board of OT — https://floridasoccupationaltherapy.gov/
11. Georgia — Board: Secretary of State PLB — https://sos.ga.gov/PLB/acrobat/Forms/38%20Reference%20-%20Occupational%20Therapy.pdf
12. Hawaii — Board: DCCA PVL — https://cca.hawaii.gov/pvl/
13. Idaho — Board: DOPL — https://dopl.idaho.gov/

Respond with a JSON array. Each element must follow this schema exactly:

{
  "state": "Alabama",
  "state_abbr": "AL",
  "vertical": "ot",
  "profession": "Occupational Therapist",
  "board_url_used": "http://www.ot.alabama.gov/fees.html",
  "research_timestamp": "2026-03-20T00:00:00Z",
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
      "source_quote": "Endorsement Application Fee: $150.00",
      "confidence": "HIGH"
    }
  }
}

Rules:
- Only use official .gov or official board websites as sources
- value must be just the number (no $ sign) for dollar amounts
- If you cannot find a fee, set value to "NOT_PUBLISHED"
- confidence must be HIGH (found on fee schedule), MEDIUM (inferred from related page), or LOW (uncertain)
- Include source_url and source_quote for every field
```

---

## BATCH 2: OT States I–M (13 states)

```
You are researching OCCUPATIONAL THERAPIST licensing fees for U.S. state boards. Use Google Search to find the current fee schedules on each state board's official website.

For each state below, find these 3 data points:
- quick_facts.total_fee: The total endorsement/reciprocity application fee
- quick_facts.renewal_fee: The license renewal fee
- fees_endorsement.total_estimated_cost: The total estimated cost for endorsement

STATES:
1. Illinois — https://idfpr.illinois.gov/profs/ot.asp
2. Indiana — https://www.in.gov/pla/professions/occupational-therapy/
3. Iowa — https://www.idph.iowa.gov/
4. Kansas — https://www.ksbha.org/
5. Kentucky — https://bot.ky.gov/
6. Louisiana — https://www.lsbme.la.gov/
7. Maine — https://www.maine.gov/pfr/professionallicensing/
8. Maryland — https://health.maryland.gov/botp/Pages/index.aspx
9. Massachusetts — https://www.mass.gov/orgs/board-of-registration-of-allied-health-professionals
10. Michigan — https://www.michigan.gov/lara/bureau-list/bpl/occ/professions/occupational-therapists
11. Minnesota — https://mn.gov/boards/medical-practice/
12. Mississippi — https://www.ot.ms.gov/
13. Missouri — https://pr.mo.gov/occtherp.asp

Respond with a JSON array. Each element must follow the same schema as Batch 1 above — use vertical "ot", profession "Occupational Therapist". value = number only for fees. confidence = HIGH/MEDIUM/LOW. Include source_url and source_quote.
```

---

## BATCH 3: OT States M–O (13 states)

```
You are researching OCCUPATIONAL THERAPIST licensing fees for U.S. state boards. Use Google Search to find the current fee schedules on each state board's official website.

For each state below, find these 3 data points:
- quick_facts.total_fee: The total endorsement/reciprocity application fee
- quick_facts.renewal_fee: The license renewal fee
- fees_endorsement.total_estimated_cost: The total estimated cost for endorsement

STATES:
1. Montana — https://boards.bsd.dli.mt.gov/occupational-therapists
2. Nebraska — https://dhhs.ne.gov/licensure/Pages/Licensing-Home-Page.aspx
3. Nevada — https://bop.nv.gov/
4. New Hampshire — https://www.oplc.nh.gov/occupational-therapy
5. New Jersey — https://www.njconsumeraffairs.gov/ot
6. New Mexico — https://www.rld.nm.gov/
7. New York — https://www.op.nysed.gov/professions-index/occupational-therapy
8. North Carolina — https://www.ncbot.org/
9. North Dakota — https://www.ndotboard.com/
10. Ohio — https://otptat.ohio.gov/
11. Oklahoma — https://www.okmedicalboard.org/
12. Oregon — https://www.oregon.gov/otlb
13. Pennsylvania — https://www.dos.pa.gov/ProfessionalLicensing/BoardsCommissions/OccupationalTherapy/Pages/default.aspx

Same schema. vertical "ot", profession "Occupational Therapist". value = number only for fees. confidence = HIGH/MEDIUM/LOW. Include source_url and source_quote.
```

---

## BATCH 4: OT States R–W (12 states)

```
You are researching OCCUPATIONAL THERAPIST licensing fees for U.S. state boards. Use Google Search to find the current fee schedules on each state board's official website.

For each state below, find these 3 data points:
- quick_facts.total_fee: The total endorsement/reciprocity application fee
- quick_facts.renewal_fee: The license renewal fee
- fees_endorsement.total_estimated_cost: The total estimated cost for endorsement

STATES:
1. Rhode Island — https://health.ri.gov/licenses/
2. South Carolina — https://llr.sc.gov/ot/
3. South Dakota — https://doh.sd.gov/licensing-and-records/boards/medical/
4. Tennessee — https://www.tn.gov/health/health-program-areas/health-professional-boards/ot-board.html
5. Texas — https://ptot.texas.gov/
6. Utah — https://dopl.utah.gov/ot/
7. Vermont — https://sos.vermont.gov/opr/
8. Virginia — https://www.dhp.virginia.gov/medicine/
9. Washington — https://doh.wa.gov/licenses-permits-and-certificates/professions-new-renew-702
10. West Virginia — https://wvbot.org/
11. Wisconsin — https://dsps.wi.gov/
12. Wyoming — https://occupationaltherapy.wyo.gov/

Same schema. vertical "ot", profession "Occupational Therapist". value = number only for fees. confidence = HIGH/MEDIUM/LOW. Include source_url and source_quote.
```

---

## BATCH 5: Pharm + Pharmacist (background_check_fee)

```
You are researching PHARMACY TECHNICIAN and PHARMACIST licensing fees for U.S. state boards. Use Google Search to find the current fee schedules on each state board's official website.

For each state below, find this data point:
- fees_endorsement.background_check_fee: The background check / fingerprint fee for endorsement applicants

STATES (Pharmacy Technician):
1. Arizona — https://pharmacy.az.gov/technician-license-information
2. California — https://www.pharmacy.ca.gov/applicants/tch.shtml
3. Florida — https://floridaspharmacy.gov/registered-pharmacy-technician/
4. Illinois — https://idfpr.illinois.gov
5. Montana — https://boards.bsd.dli.mt.gov/pharmacy/license-information/pharmacy-technician
6. New York — https://www.op.nysed.gov/professions/registered-pharmacy-technicians/license-application-forms
7. North Carolina — https://www.ncbop.org/pharmacy-technicians.html
8. Ohio — https://www.pharmacy.ohio.gov/licensing/techs/registeredtech
9. Pennsylvania — https://www.pa.gov/agencies/dos/department-and-offices/bpoa/boards-commissions/pharmacy/pharmacy-technician-registration-snapshot
10. Texas — https://www.pharmacy.texas.gov/applicants/tech.asp
11. Washington — https://doh.wa.gov/licenses-permits-and-certificates/professions-new-renew-or-update/pharmacy-professions/licensing-information

Use vertical "pharm", profession "Pharmacy Technician". Same schema. value = number only for fees. confidence = HIGH/MEDIUM/LOW. Include source_url and source_quote.
```

---

## BATCH 6: Dietitian + LPN (mixed fields)

```
You are researching healthcare professional licensing fees for U.S. state boards. Use Google Search to find the current fee schedules on each state board's official website.

STATES:

1. Massachusetts — Licensed Practical Nurse — Board of Registration in Nursing
   URL: https://www.mass.gov/how-to/apply-for-a-nursing-license-by-reciprocity
   Find: quick_facts.renewal_fee

2. Arizona — Dietitian — Board: N/A, Title Protection State
   URL: https://www.azsos.gov/public-services/registrations-filings/dietitian-registration
   Find: quick_facts.renewal_fee, quick_facts.renewal_cycle

3. California — Dietitian — Dietetics Licensing
   URL: https://www.cdph.ca.gov/
   Find: quick_facts.renewal_fee

4. Montana — Dietitian
   URL: https://boards.bsd.dli.mt.gov/
   Find: quick_facts.renewal_fee, quick_facts.license_duration

Respond with a JSON array. Each element must include state, state_abbr, vertical (use "lpn" or "dietitian"), profession, board_url_used, research_timestamp, and fields with value/source_url/source_quote/confidence.
```
