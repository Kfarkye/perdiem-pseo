#!/usr/bin/env python3
"""Enrich CNA production JSON (database/json/) with Batch 1 research data.

Applies official exam portals, registry URLs, transfer forms, and background
check details from the enrichment research to the 10 Batch 1 states:
FL, NY, PA, IL, OH, GA, NJ, VA, WA, MA

Does NOT change the schema — only fills in missing or generic values
with state-specific, source-backed data.
"""
from __future__ import annotations

import json
from pathlib import Path

CNA_JSON_DIR = Path(__file__).resolve().parent / "cna-pseo" / "database" / "json"

# Batch 1 enrichment data keyed by state slug
ENRICHMENTS: dict[str, dict] = {
    "florida": {
        "board": {
            "phone": "(850) 488-0595",
            "url": "https://floridasnursing.gov/",
            "email": "See board website",
        },
        "reciprocity": {
            "board_url": "https://floridasnursing.gov/",
            "endorsement_url": "https://flhealthsource.gov",
            "notes": "Out-of-state CNAs apply for endorsement through the FL Health Source online portal. A Level II LiveScan background check is required. No state exam retake if approved.",
        },
        "fingerprints": {
            "method_in_state": "LiveScan (Level II — AHCA Clearinghouse)",
            "method_out_of_state": "AHCA Clearinghouse (CHAI) at flclearinghouse.com — ORI: EDOH0380Z",
            "vendor": "AHCA / FDLE",
            "vendor_url": "https://www.flclearinghouse.com",
        },
        "board_verification_sources": {
            "registry": "https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders",
            "exam_portal": "https://www.prometric.com/nurseaide/fl",
            "application_portal": "https://www.flhealthsource.gov",
            "transfer_portal": "https://www.flhealthsource.gov",
        },
        "steps_override": [
            {
                "title": "Complete a State-Approved Training Program",
                "description": "Florida requires a state-approved CNA training program. Florida also offers a unique 'Challenger Route' allowing individuals 18+ with a high school diploma to sit for the exam without formal training.",
            },
            {
                "title": "Pass Background Screening",
                "description": "All applicants must pass a Level II LiveScan background check through the AHCA Clearinghouse (ORI: EDOH0380Z).",
            },
            {
                "title": "Register for the State Competency Exam",
                "description": "Register through Prometric at prometric.com/nurseaide/fl. The exam has both a written and skills component.",
            },
            {
                "title": "Submit Application via FL Health Source",
                "description": "Apply online at flhealthsource.gov to be added to the Florida Nurse Aide Registry.",
            },
        ],
        "documents_override": [
            {"item": "Proof of Training", "detail": "Certificate from your state-approved CNA program, or high school diploma/GED if using the Challenger Route."},
            {"item": "Prometric Exam Results", "detail": "Official results from your Prometric competency exam."},
            {"item": "Level II Background Screening", "detail": "Completed via AHCA Clearinghouse (flclearinghouse.com) using ORI: EDOH0380Z."},
        ],
        "faqs_override": [
            {"question": "Can I challenge the CNA exam in Florida without training?", "answer": "Yes. Florida's Challenger Route lets individuals 18 or older with a high school diploma take the CNA exam without completing a formal training program."},
            {"question": "Who administers the Florida CNA exam?", "answer": "The Florida CNA competency exam is administered by Prometric. Register at prometric.com/nurseaide/fl."},
            {"question": "How do I verify a Florida CNA license?", "answer": "Use the FL DOH MQA Provider Search at mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders."},
            {"question": "How do I transfer my CNA to Florida?", "answer": "Apply for endorsement through the FL Health Source portal (flhealthsource.gov). You must hold an active out-of-state CNA certificate and pass a Level II background check."},
            {"question": "How long does Florida CNA endorsement take?", "answer": "Most endorsement applications are processed in 2 to 4 weeks once your file is complete."},
        ],
    },
    "new-york": {
        "reciprocity": {
            "board_url": "https://www.health.ny.gov/professionals/nursing_home_administrator/nha_cna.htm",
            "endorsement_url": "https://www.prometric.com/nurseaide/ny",
            "notes": "Contact Prometric at the NY Nurse Aide portal to apply for reciprocity. Phone verification available 24/7 at 1-800-918-8818.",
        },
        "board_verification_sources": {
            "registry": "https://www.prometric.com/nurseaide/ny",
            "exam_portal": "https://www.prometric.com/nurseaide/ny",
            "info_page": "https://www.health.ny.gov/professionals/nursing_home_administrator/nha_cna.htm",
        },
        "faqs_override": [
            {"question": "Who administers the New York CNA exam?", "answer": "The NYS Nurse Aide exam is administered by Prometric. Register at prometric.com/nurseaide/ny."},
            {"question": "How do I verify a New York CNA?", "answer": "Use the Prometric NY Nurse Aide Registry portal or call the 24/7 IVR line at 1-800-918-8818."},
            {"question": "How do I transfer my CNA to New York?", "answer": "Contact Prometric at the NY Nurse Aide Portal to apply for reciprocity."},
            {"question": "How long does New York CNA endorsement take?", "answer": "Most endorsement applications take 2 to 4 weeks. Contact the registry for current timelines."},
        ],
    },
    "pennsylvania": {
        "reciprocity": {
            "endorsement_url": "https://www.credentia.com/test-takers/pa",
            "notes": "Pennsylvania handles CNA reciprocity through Credentia's CNA365 platform. Reciprocity applications can be submitted online via CNA365 or by mail. No fee for reciprocity.",
            "endorsement_fee": 0,
        },
        "board_verification_sources": {
            "registry": "https://www.credentia.com",
            "exam_portal": "https://www.credentia.com/test-takers/pa",
        },
        "faqs_override": [
            {"question": "Who administers the Pennsylvania CNA exam?", "answer": "The PA nurse aide competency exam is administered by Credentia. Register at credentia.com/test-takers/pa."},
            {"question": "How do I transfer my CNA to Pennsylvania?", "answer": "Submit a reciprocity application through Credentia's CNA365 platform online, or mail the NNAAP Registration Application for Enrollment by Reciprocity to: Credentia – PA Nurse Aide Registry, PO Box 13785, Philadelphia, PA 19101-3785."},
            {"question": "Is PA CNA reciprocity free?", "answer": "Yes, Pennsylvania CNA reciprocity is free."},
            {"question": "How do I verify a Pennsylvania CNA?", "answer": "Use the Credentia CNA365 platform or call Credentia support at (888) 204-6249. You can also call PA DOH at (800) 852-0518."},
        ],
        "fees_endorsement_override": {
            "app_fee": "$0",
            "total_estimated_cost": "$0",
        },
    },
    "illinois": {
        "reciprocity": {
            "endorsement_url": "https://www.nurseaidetesting.com",
            "endorsement_fee": 25,
            "notes": "Illinois reciprocity is handled through SIU-C Nurse Aide Testing. Submit the Out-of-State CNA Application with a $25 money order. A written competency retest is usually required.",
        },
        "board_verification_sources": {
            "registry": "https://hcwr.illinois.gov",
            "exam_portal": "https://www.nurseaidetesting.com",
            "info_page": "https://dph.illinois.gov/topics-services/health-care-regulation/nurse-aide-program.html",
        },
        "faqs_override": [
            {"question": "Who administers the Illinois CNA exam?", "answer": "The Illinois nurse aide exam is administered by SIU-C (Southern Illinois University Carbondale) via nurseaidetesting.com."},
            {"question": "How do I transfer my CNA to Illinois?", "answer": "Submit the Out-of-State CNA Application on nurseaidetesting.com with a $25 money order payable to SIU-C. A written competency retest is usually required."},
            {"question": "How do I verify an Illinois CNA?", "answer": "Search the Illinois Health Care Worker Registry (HCWR) at hcwr.illinois.gov or call (844) 789-3676 (M-F 8:30am-5pm CT)."},
        ],
        "fees_endorsement_override": {
            "app_fee": "$25",
            "total_estimated_cost": "$25",
        },
    },
    "ohio": {
        "reciprocity": {
            "endorsement_url": "https://ohio.gov",
            "endorsement_fee": 0,
            "notes": "Ohio uses Form HEA 6907 (Nurse Aide Registry Request for Reciprocity). Submit by mail to Ohio Dept of Health, Nurse Aide Registry, 246 N. High Street, Attn: NAR, Columbus, OH 43215, or fax to (614) 564-2461, or email NAR@odh.ohio.gov. No fee. Note: Ohio is transitioning from 'STNA' to 'CNA' terminology as of October 2024.",
        },
        "board_verification_sources": {
            "registry": "https://nurseaideinquiry.odh.ohio.gov",
            "exam_portal": "https://www.hdmaster.com",
        },
        "faqs_override": [
            {"question": "Who administers the Ohio CNA/STNA exam?", "answer": "The Ohio nurse aide exam is administered by D&S Headmaster. Contact them at (877) 851-2355 or visit hdmaster.com."},
            {"question": "How do I transfer my CNA to Ohio?", "answer": "Submit Form HEA 6907 (Reciprocity Request) by mail, fax (614-564-2461), or email (NAR@odh.ohio.gov). There is no fee for Ohio CNA reciprocity."},
            {"question": "Is Ohio calling it CNA or STNA?", "answer": "Ohio is transitioning from 'STNA' (State Tested Nursing Assistant) to 'CNA' terminology as of October 24, 2024. Some forms may still use STNA."},
            {"question": "How do I verify an Ohio CNA?", "answer": "Use the Ohio Nurse Aide Registry Inquiry at nurseaideinquiry.odh.ohio.gov or call (800) 582-5908."},
        ],
        "fees_endorsement_override": {
            "app_fee": "$0",
            "total_estimated_cost": "$0",
        },
    },
    "georgia": {
        "reciprocity": {
            "endorsement_url": "https://www.credentia.com/test-takers/ga",
            "notes": "Georgia CNA reciprocity is managed through the Credentia CNA365 platform.",
        },
        "board_verification_sources": {
            "registry": "https://www.mmis.georgia.gov/portal_nar/",
            "exam_portal": "https://www.credentia.com/test-takers/ga",
        },
        "faqs_override": [
            {"question": "Who administers the Georgia CNA exam?", "answer": "The Georgia nurse aide exam is administered by Credentia. Register at credentia.com/test-takers/ga."},
            {"question": "How do I verify a Georgia CNA?", "answer": "Use the Georgia CareConnect portal (Alliant Health Solutions) at mmis.georgia.gov/portal_nar/ or search on georgia.gov."},
        ],
    },
    "new-jersey": {
        "reciprocity": {
            "endorsement_url": "https://www.nj.gov/health/healthfacilities/certification-nurse-aide/",
            "notes": "Contact NJ DOH at (866) 561-5914 or CNA@doh.nj.gov, or PSI at (877) 774-4243 for reciprocity applications.",
        },
        "board_verification_sources": {
            "registry": "https://www.psiexams.com",
            "exam_portal": "https://candidate.psiexams.com",
            "info_page": "https://www.nj.gov/health/healthfacilities/certification-nurse-aide/",
        },
        "faqs_override": [
            {"question": "Who administers the New Jersey CNA exam?", "answer": "The NJ Nurse Aide exam is administered by PSI. Schedule at psiexams.com or call 1-800-733-9267."},
            {"question": "How do I transfer my CNA to New Jersey?", "answer": "Contact the NJ DOH at (866) 561-5914 or email CNA@doh.nj.gov, or contact PSI at (877) 774-4243 / njna@psionline.com."},
        ],
    },
    "virginia": {
        "reciprocity": {
            "endorsement_url": "https://www.credentia.com/test-takers/va",
            "notes": "Virginia CNA endorsement is handled through the Credentia CNA365 platform or the VA Board of Nursing.",
        },
        "board_verification_sources": {
            "registry": "https://dhp.virginiainteractive.org/Lookup/Index",
            "exam_portal": "https://www.credentia.com/test-takers/va",
            "board_page": "https://www.dhp.virginia.gov/nursing/nursing-education/nurse-aide/",
        },
        "faqs_override": [
            {"question": "Who administers the Virginia CNA exam?", "answer": "The VA nurse aide exam is administered by Credentia. Register at credentia.com/test-takers/va."},
            {"question": "How do I verify a Virginia CNA?", "answer": "Use the DHP License Lookup at dhp.virginiainteractive.org/Lookup/Index or contact VBON at (804) 367-4515 or nurseaide@dhp.virginia.gov."},
        ],
    },
    "washington": {
        "reciprocity": {
            "endorsement_url": "https://doh.wa.gov/licenses-permits-and-certificates/professions-new-renew-702/nursing-assistant",
            "notes": "Washington uses the NAC Application Packet for endorsement. The endorsement section of the packet covers out-of-state transfers. An Authorization to Test may be required.",
        },
        "board_verification_sources": {
            "registry": "https://fortress.wa.gov/doh/providercredentialsearch/",
            "exam_portal": "https://www.credentia.com/test-takers/wa",
            "info_page": "https://doh.wa.gov/licenses-permits-and-certificates/professions-new-renew-702/nursing-assistant",
        },
        "faqs_override": [
            {"question": "Who administers the Washington NAC exam?", "answer": "The WA Nursing Assistant Certified exam is administered by Credentia. Register at credentia.com/test-takers/wa."},
            {"question": "How do I verify a Washington CNA/NAC?", "answer": "Use the WA DOH Provider Credential Search at fortress.wa.gov/doh/providercredentialsearch/. Search for credential type 'Nursing Assistant Certification – NC'."},
        ],
    },
    "massachusetts": {
        "reciprocity": {
            "endorsement_url": "https://www.mass.gov/nurse-aide-testing",
            "notes": "Contact the MA DPH Nurse Aide Testing Office at (781) 979-4010 or 1-800-962-4337 for reciprocity. A CORI (Criminal Offender Record Information) background check is required.",
        },
        "board_verification_sources": {
            "registry": "https://nars.dph.mass.gov",
            "exam_portal": "https://www.hdmaster.com",
            "info_page": "https://www.mass.gov/nurse-aide-testing",
        },
        "faqs_override": [
            {"question": "Who administers the Massachusetts CNA exam?", "answer": "The MA CNA exam is administered by D&S Headmaster. Contact them at (888) 401-0462 or visit hdmaster.com (Massachusetts CNA section)."},
            {"question": "How do I transfer my CNA to Massachusetts?", "answer": "Contact the MA DPH Nurse Aide Testing Office at (781) 979-4010 or 1-800-962-4337 for reciprocity applications. A CORI background check is required."},
            {"question": "How do I verify a Massachusetts CNA?", "answer": "Use the NARIS (Nurse Aide Registry Information System) at nars.dph.mass.gov or call (617) 753-8144 / email nars@mass.gov."},
        ],
    },
}


def enrich_record(data: dict, enrichment: dict) -> dict:
    """Apply enrichment data to a production CNA JSON record."""

    # Update board fields
    if "board" in enrichment:
        for k, v in enrichment["board"].items():
            data["board"][k] = v

    # Update reciprocity fields
    if "reciprocity" in enrichment:
        for k, v in enrichment["reciprocity"].items():
            data["reciprocity"][k] = v

    # Update fingerprints
    if "fingerprints" in enrichment:
        for k, v in enrichment["fingerprints"].items():
            data["fingerprints"][k] = v

    # Add board verification sources
    if "board_verification_sources" in enrichment:
        data["board_verification_sources"] = enrichment["board_verification_sources"]

    # Override steps if provided
    if "steps_override" in enrichment:
        data["steps"] = enrichment["steps_override"]

    # Override documents if provided
    if "documents_override" in enrichment:
        data["documents"] = enrichment["documents_override"]

    # Override FAQs if provided
    if "faqs_override" in enrichment:
        data["faqs"] = enrichment["faqs_override"]

    # Override fees_endorsement fields
    if "fees_endorsement_override" in enrichment:
        for k, v in enrichment["fees_endorsement_override"].items():
            data["fees_endorsement"][k] = v

    # Update timestamps
    data["last_updated"] = "2026-03-24"
    data["last_verified_date"] = "2026-03-24"

    return data


def main() -> None:
    updated = 0
    for state_slug, enrichment in ENRICHMENTS.items():
        json_file = CNA_JSON_DIR / f"{state_slug}-cna.json"
        if not json_file.exists():
            print(f"  ⚠ SKIP: {json_file.name} not found")
            continue

        data = json.loads(json_file.read_text(encoding="utf-8"))
        data = enrich_record(data, enrichment)
        json_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        updated += 1
        print(f"  ✓ {json_file.name}")

    print(f"\n[enrich] Updated {updated}/{len(ENRICHMENTS)} CNA records with Batch 1 data.")


if __name__ == "__main__":
    main()
