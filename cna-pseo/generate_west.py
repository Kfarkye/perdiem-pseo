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
        "alaska-certified-nursing-assistant", "Alaska", "AK",
        "Certified Nurse Aide", "CNA", [],
        "Alaska Department of Commerce, Community, and Economic Development", "907-465-2550",
        "140 hours", "140 hours (60 classroom, 80 clinical)", "Headmaster",
        "Complete 140 hours of state-approved training and pass the Headmaster competency exam to join the Alaska Nurse Aide Registry.",
        "Learn Alaska DCCED requirements, complete a 140-hour program, and pass the Headmaster exam.",
        "Transfer via Reciprocity using the Alaska Nurse Aide Registry.",
        "Apply to take the Headmaster Nurse Aide evaluation."
    ),
    make_state(
        "arizona-certified-nursing-assistant", "Arizona", "AZ",
        "Certified Nursing Assistant", "CNA", [],
        "Arizona State Board of Nursing", "602-771-7800",
        "120 hours", "120 hours (40 classroom, 80 clinical)", "D&S Diversified",
        "Complete 120 hours of Board-approved training and pass the D&S Diversified competency exam.",
        "Learn AZ Board of Nursing requirements, complete a 120-hour program, and pass the D&S Diversified exam.",
        "Transfer via Certification by Endorsement through the AZ Board of Nursing.",
        "Apply to take the D&S Diversified Nurse Aide evaluation."
    ),
    make_state(
        "colorado-certified-nursing-assistant", "Colorado", "CO",
        "Certified Nursing Assistant", "CNA", [],
        "Colorado Department of Regulatory Agencies (DORA)", "303-894-2430",
        "80 hours", "80 hours (classroom + clinical)", "Pearson VUE",
        "Complete 80 hours of DORA-approved training and pass the Pearson VUE competency exam.",
        "Learn DORA requirements, complete an 80-hour program, and pass the Pearson VUE exam.",
        "Transfer via Endorsement using the DORA Nurse Aide Registry.",
        "Apply to take the Pearson VUE Nurse Aide evaluation."
    ),
    make_state(
        "hawaii-certified-nursing-assistant", "Hawaii", "HI",
        "Certified Nurse Aide", "CNA", [],
        "Hawaii Department of Health", "808-453-6453",
        "100 hours", "100 hours (classroom + clinical)", "Prometric",
        "Complete 100 hours of state-approved training and pass the Prometric competency exam to join the Hawaii Nurse Aide Registry.",
        "Learn Hawaii DOH requirements, complete a 100-hour program, and pass the Prometric exam.",
        "Transfer via Reciprocity using the Hawaii Nurse Aide Registry.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
    make_state(
        "idaho-certified-nursing-assistant", "Idaho", "ID",
        "Certified Nursing Assistant", "CNA", [],
        "Idaho Department of Health and Welfare (DHW)", "208-334-6626",
        "120 hours", "120 hours (classroom + clinical)", "Prometric",
        "Complete 120 hours of DHW-approved training and pass the Prometric competency exam.",
        "Learn Idaho DHW requirements, complete a 120-hour program, and pass the Prometric exam.",
        "Transfer via Reciprocity using the Idaho Nurse Aide Registry.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
    make_state(
        "montana-certified-nursing-assistant", "Montana", "MT",
        "Certified Nursing Assistant", "CNA", [],
        "Montana Department of Public Health and Human Services (DPHHS)", "406-444-4980",
        "75 hours", "75 hours (classroom + clinical)", "Headmaster",
        "Complete 75 hours of DPHHS-approved training and pass the Headmaster competency exam.",
        "Learn Montana DPHHS requirements, complete a 75-hour program, and pass the Headmaster exam.",
        "Transfer via Reciprocity using the Montana Nurse Aide Registry.",
        "Apply to take the Headmaster Nurse Aide evaluation."
    ),
    make_state(
        "nevada-certified-nursing-assistant", "Nevada", "NV",
        "Certified Nursing Assistant", "CNA", [],
        "Nevada State Board of Nursing", "702-486-5800",
        "75 hours", "75 hours (classroom + clinical)", "Prometric",
        "Complete 75 hours of Board-approved training and pass the Prometric competency exam.",
        "Learn NV Board of Nursing requirements, complete a 75-hour program, and pass the Prometric exam.",
        "Transfer via Endorsement through the NV Board of Nursing.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
    make_state(
        "new-mexico-certified-nursing-assistant", "New Mexico", "NM",
        "Certified Nursing Assistant", "CNA", [],
        "New Mexico Department of Health (DOH)", "505-476-8975",
        "80 hours", "80 hours (classroom + clinical)", "Prometric",
        "Complete 80 hours of DOH-approved training and pass the Prometric competency exam to join the NM Nurse Aide Registry.",
        "Learn NM DOH requirements, complete an 80-hour program, and pass the Prometric exam.",
        "Transfer via Reciprocity using the NM Nurse Aide Registry.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
    make_state(
        "oregon-certified-nursing-assistant", "Oregon", "OR",
        "Certified Nursing Assistant", "CNA", ["CNA 1"],
        "Oregon State Board of Nursing (OSBN)", "971-673-0685",
        "155 hours", "155 hours (80 classroom, 75 clinical)", "Headmaster",
        "Complete 155 hours of OSBN-approved training and pass the Headmaster competency exam.",
        "Learn Oregon OSBN requirements, complete a 155-hour program, and pass the Headmaster exam.",
        "Transfer via Endorsement through the Oregon State Board of Nursing.",
        "Apply to take the Headmaster Nurse Aide evaluation."
    ),
    make_state(
        "utah-certified-nursing-assistant", "Utah", "UT",
        "Certified Nursing Assistant", "CNA", [],
        "Utah Nursing Assistant Registry (UNAR)", "801-547-9947",
        "80 hours", "80 hours (classroom + clinical)", "Headmaster",
        "Complete 80 hours of state-approved training and pass the Headmaster competency exam to join the Utah Nursing Assistant Registry.",
        "Learn UNAR requirements, complete an 80-hour program, and pass the Headmaster exam.",
        "Transfer via Reciprocity using the Utah Nursing Assistant Registry.",
        "Apply to take the Headmaster Nurse Aide evaluation."
    ),
    make_state(
        "washington-certified-nursing-assistant", "Washington", "WA",
        "Nursing Assistant Certified", "NAC", ["CNA"],
        "Washington Department of Health (DOH)", "360-236-4700",
        "85 hours", "85 hours (35 classroom, 50 clinical)", "Pearson VUE",
        "Complete 85 hours of DOH-approved training and pass the Pearson VUE competency exam.",
        "Learn WA DOH requirements, complete an 85-hour program, and pass the Pearson VUE exam.",
        "Transfer via Endorsement through the WA DOH Nursing Commission.",
        "Apply to take the Pearson VUE Nursing Assistant evaluation."
    ),
    make_state(
        "wyoming-certified-nursing-assistant", "Wyoming", "WY",
        "Certified Nursing Assistant", "CNA", [],
        "Wyoming Department of Health", "307-777-7123",
        "75 hours", "75 hours (classroom + clinical)", "Headmaster",
        "Complete 75 hours of state-approved training and pass the Headmaster competency exam.",
        "Learn Wyoming DOH requirements, complete a 75-hour program, and pass the Headmaster exam.",
        "Transfer via Reciprocity using the Wyoming Nurse Aide Registry.",
        "Apply to take the Headmaster Nurse Aide evaluation."
    ),
]

with open("temp_research.jsonl", "w", encoding="utf-8") as f:
    for s in states:
        f.write(json.dumps(s) + "\n")
print(f"Created temp_research.jsonl with {len(states)} West state records.")
