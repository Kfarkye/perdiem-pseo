import json

def make_state(slug, name, abbr, display_label, short_label, aliases,
               board_name, phone, training_hours, training_detail,
               exam_vendor, intro, becoming_dek, transfer_dek, app_dek):
    return {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": slug,
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {"entity_key": f"{abbr.lower()}::cna", "default_variant": "becoming"},
        "state": {"name": name, "abbr": abbr},
        "profession": {"key": "cna", "display_label": display_label, "short_label": short_label, "aliases": aliases},
        "container": {"label": f"Becoming a {short_label} in {name}", "label_source": "google_autocomplete", "intro": intro, "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Standard intent"},
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {"key": "becoming", "label": "Becoming", "label_source": "google_autocomplete", "description": f"How to become a {short_label} in {abbr}.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Task variant"},
                {"key": "state_application", "label": "State Application", "label_source": "search_console_intent", "description": f"Apply for the {exam_vendor} exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Application intent"},
                {"key": "transfer", "label": "Transfer", "label_source": "google_autocomplete", "description": f"Transfer an active out-of-state CNA to {name}.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Reciprocity intent"}
            ]
        },
        "shared_facts": {
            "board": {"name": board_name, "phone": phone, "fax": "", "contact_url": "", "website": "", "verify_url": ""},
            "last_verified": "2026-03-24",
            "source_count": 3
        },
        "task_signals": [],
        "candidate_supporting_pages": [],
        "variants": {
            "becoming": {
                "hero": {"title": f"Becoming a {short_label} in {name}", "dek": becoming_dek},
                "seo": {"title": f"How to Become a {short_label} in {name}", "description": f"Step-by-step guide to {name} {short_label} certification.", "target_queries": []},
                "faq_heading": "Common Questions",
                "cards": [{"key": "training_hours", "label": "Required Training", "value": training_detail, "status": "confirmed"}],
                "sections": [], "faq": []
            },
            "state_application": {
                "hero": {"title": f"{name} {short_label} State Exam Application", "dek": app_dek},
                "seo": {"title": f"{name} {short_label} Exam Application", "description": f"Apply for {abbr} {short_label} testing.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": []
            },
            "transfer": {
                "hero": {"title": f"Transfer a CNA License to {name}", "dek": transfer_dek},
                "seo": {"title": f"Transfer CNA License to {name}", "description": f"Transfer your active out-of-state CNA to {abbr}.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": [],
                "temporary_license": {"enabled": False, "hero": {"title": "", "dek": ""}, "cards": [], "sections": []}
            }
        },
        "validation_notes": {"materially_distinct_variant_warning": "", "uncertain_fields": [], "source_backed_only": True}
    }

states = [
    make_state(
        "district-of-columbia-certified-nursing-assistant", "District of Columbia", "DC",
        "Certified Nursing Assistant", "CNA", [],
        "DC Department of Health", "202-724-4900",
        "75 hours", "75 hours (classroom + clinical)", "Prometric",
        "Complete 75 hours of DC-approved training and pass the Prometric competency exam.",
        "Learn DC DOH requirements, complete a 75-hour program, and pass the Prometric exam.",
        "Transfer via Reciprocity using the DC Nurse Aide Registry.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
    make_state(
        "maryland-certified-nursing-assistant", "Maryland", "MD",
        "Certified Nursing Assistant", "CNA", ["GNA"],
        "Maryland Board of Nursing", "410-585-1900",
        "100 hours", "100 hours (classroom + clinical)", "Pearson VUE",
        "Complete 100 hours of Board-approved training and pass the Pearson VUE competency exam to join the Maryland Nurse Aide Registry.",
        "Learn MD Board of Nursing requirements, complete a 100-hour program, and pass the Pearson VUE exam.",
        "Transfer via Endorsement through the Maryland Board of Nursing.",
        "Apply to take the Pearson VUE Nurse Aide evaluation."
    ),
    make_state(
        "massachusetts-certified-nursing-assistant", "Massachusetts", "MA",
        "Certified Nursing Assistant", "CNA", [],
        "Massachusetts Department of Public Health (DPH)", "617-753-8000",
        "100 hours", "100 hours (75 classroom, 25 clinical)", "Prometric",
        "Complete 100 hours of DPH-approved training and pass the Prometric competency exam.",
        "Learn MA DPH requirements, complete a 100-hour program, and pass the Prometric exam.",
        "Transfer via Reciprocity using the MA Nurse Aide Registry.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
    make_state(
        "new-hampshire-certified-nursing-assistant", "New Hampshire", "NH",
        "Licensed Nursing Assistant", "LNA", ["CNA"],
        "New Hampshire Board of Nursing", "603-271-6282",
        "100 hours", "100 hours (classroom + clinical)", "Prometric",
        "Complete 100 hours of Board-approved training and pass the Prometric competency exam.",
        "Learn NH Board of Nursing requirements, complete a 100-hour program, and pass the Prometric exam.",
        "Transfer via Endorsement through the NH Board of Nursing.",
        "Apply to take the Prometric Nursing Assistant evaluation."
    ),
    make_state(
        "new-jersey-certified-nursing-assistant", "New Jersey", "NJ",
        "Certified Homemaker-Home Health Aide", "CHHA", ["CNA"],
        "New Jersey Department of Health", "609-292-7837",
        "90 hours", "90 hours (classroom + clinical)", "Prometric",
        "Complete 90 hours of NJ DOH-approved training and pass the Prometric competency exam.",
        "Learn NJ DOH requirements, complete a 90-hour program, and pass the Prometric exam.",
        "Transfer via Reciprocity using the NJ Nurse Aide Registry.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
    make_state(
        "new-york-certified-nursing-assistant", "New York", "NY",
        "Certified Nurse Aide", "CNA", [],
        "New York State Department of Health", "518-402-1004",
        "100 hours", "100 hours (classroom + clinical)", "Prometric",
        "Complete 100 hours of DOH-approved training and pass the Prometric competency exam to join the NYS Nurse Aide Registry.",
        "Learn NYS DOH requirements, complete a 100-hour program, and pass the Prometric exam.",
        "Transfer via Reciprocity using the NYS Nurse Aide Registry.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
    make_state(
        "oklahoma-certified-nursing-assistant", "Oklahoma", "OK",
        "Certified Nurse Aide", "CNA", [],
        "Oklahoma State Department of Health (OSDH)", "405-271-6576",
        "75 hours", "75 hours (classroom + clinical)", "Headmaster",
        "Complete 75 hours of OSDH-approved training and pass the Headmaster competency exam.",
        "Learn OSDH requirements, complete a 75-hour program, and pass the Headmaster exam.",
        "Transfer via Reciprocity using the Oklahoma Nurse Aide Registry.",
        "Apply to take the Headmaster Nurse Aide evaluation."
    ),
    make_state(
        "pennsylvania-certified-nursing-assistant", "Pennsylvania", "PA",
        "Certified Nurse Aide", "CNA", [],
        "Pennsylvania Department of Health", "800-852-4549",
        "80 hours", "80 hours (37.5 classroom, 42.5 clinical)", "American Red Cross",
        "Complete 80 hours of PA-approved training and pass the American Red Cross competency exam.",
        "Learn PA DOH requirements, complete an 80-hour program, and pass the American Red Cross exam.",
        "Transfer via Reciprocity using the PA Nurse Aide Registry.",
        "Apply to take the American Red Cross Nurse Aide evaluation."
    ),
    make_state(
        "rhode-island-certified-nursing-assistant", "Rhode Island", "RI",
        "Certified Nursing Assistant", "CNA", [],
        "Rhode Island Department of Health", "401-222-2828",
        "100 hours", "100 hours (classroom + clinical)", "Prometric",
        "Complete 100 hours of RI DOH-approved training and pass the Prometric competency exam.",
        "Learn RI DOH requirements, complete a 100-hour program, and pass the Prometric exam.",
        "Transfer via Reciprocity using the RI Nurse Aide Registry.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
    make_state(
        "vermont-certified-nursing-assistant", "Vermont", "VT",
        "Licensed Nursing Assistant", "LNA", ["CNA"],
        "Vermont Board of Nursing", "802-828-2396",
        "75 hours", "75 hours (classroom + clinical)", "Prometric",
        "Complete 75 hours of Board-approved training and pass the Prometric competency exam.",
        "Learn VT Board of Nursing requirements, complete a 75-hour program, and pass the Prometric exam.",
        "Transfer via Endorsement through the Vermont Board of Nursing.",
        "Apply to take the Prometric Nursing Assistant evaluation."
    ),
    make_state(
        "virginia-certified-nursing-assistant", "Virginia", "VA",
        "Certified Nurse Aide", "CNA", [],
        "Virginia Board of Nursing", "804-367-4515",
        "120 hours", "120 hours (40 classroom, 80 clinical)", "Pearson VUE",
        "Complete 120 hours of Board-approved training and pass the Pearson VUE competency exam.",
        "Learn VA Board of Nursing requirements, complete a 120-hour program, and pass the Pearson VUE exam.",
        "Transfer via Endorsement through the Virginia Board of Nursing.",
        "Apply to take the Pearson VUE Nurse Aide evaluation."
    ),
    make_state(
        "west-virginia-certified-nursing-assistant", "West Virginia", "WV",
        "Certified Nurse Aide", "CNA", [],
        "West Virginia Nurse Aide Program (WVDHHR)", "304-558-0688",
        "120 hours", "120 hours (classroom + clinical)", "Prometric",
        "Complete 120 hours of WVDHHR-approved training and pass the Prometric competency exam.",
        "Learn WV DHHR requirements, complete a 120-hour program, and pass the Prometric exam.",
        "Transfer via Reciprocity using the WV Nurse Aide Registry.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
]

with open("temp_research.jsonl", "w", encoding="utf-8") as f:
    for s in states:
        f.write(json.dumps(s) + "\n")
print(f"Created temp_research.jsonl with {len(states)} Mid-Atlantic/NE/DC state records.")
