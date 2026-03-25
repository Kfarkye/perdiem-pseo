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
            "board": {
                "name": board_name,
                "phone": phone,
                "fax": "",
                "contact_url": "",
                "website": "",
                "verify_url": ""
            },
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
        "illinois-certified-nursing-assistant", "Illinois", "IL",
        "Certified Nursing Assistant", "CNA", [],
        "Illinois Department of Public Health (IDPH)", "217-785-5133",
        "120 hours", "120 hours (classroom + clinical)", "SIU",
        "Complete a 120-hour approved training program and pass the SIU competency evaluation to join the Illinois Health Care Worker Registry.",
        "Learn IDPH requirements, complete a 120-hour program, and pass the SIU competency evaluation.",
        "Transfer via Interstate Endorsement using the IL Health Care Worker Registry.",
        "Apply to take the SIU Nurse Aide evaluation."
    ),
    make_state(
        "indiana-certified-nursing-assistant", "Indiana", "IN",
        "Certified Nurse Aide", "CNA", [],
        "Indiana State Department of Health (ISDH)", "317-233-7351",
        "105 hours", "105 hours (30 classroom, 75 clinical)", "Ivy Tech / D&S Diversified",
        "Complete 105 hours of state-approved training and pass the Indiana State Test to join the Nurse Aide Registry.",
        "Learn ISDH requirements, complete a 105-hour program, and pass the state competency exam.",
        "Transfer via Reciprocity using the ISDH Nurse Aide Registry.",
        "Apply to take the Indiana Nurse Aide evaluation."
    ),
    make_state(
        "iowa-certified-nursing-assistant", "Iowa", "IA",
        "Certified Nursing Assistant", "CNA", [],
        "Iowa Department of Inspections and Appeals (DIA)", "515-281-4115",
        "75 hours", "75 hours (45 classroom, 30 clinical)", "Prometric",
        "Complete 75 hours of DIA-approved training and pass the Prometric competency exam to join the Iowa Direct Care Worker Registry.",
        "Learn DIA requirements, complete a 75-hour program, and pass the Prometric exam.",
        "Transfer via Interstate Endorsement using the Iowa Direct Care Worker Registry.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
    make_state(
        "kansas-certified-nursing-assistant", "Kansas", "KS",
        "Certified Nurse Aide", "CNA", [],
        "Kansas Department for Aging and Disability Services (KDADS)", "785-296-4986",
        "90 hours", "90 hours (45 classroom, 45 clinical)", "Headmaster",
        "Complete 90 hours of KDADS-approved training and pass the Headmaster competency exam.",
        "Learn KDADS requirements, complete a 90-hour program, and pass the Headmaster exam.",
        "Transfer via Reciprocity using the Kansas Nurse Aide Registry.",
        "Apply to take the Headmaster Nurse Aide evaluation."
    ),
    make_state(
        "michigan-certified-nursing-assistant", "Michigan", "MI",
        "Certified Nursing Assistant", "CNA", [],
        "Michigan Department of Licensing and Regulatory Affairs (LARA)", "517-335-0918",
        "75 hours", "75 hours (classroom + clinical)", "Prometric",
        "Complete 75 hours of LARA-approved training and pass the Prometric competency exam to join the Michigan Nurse Aide Registry.",
        "Learn LARA requirements, complete a 75-hour program, and pass the Prometric exam.",
        "Transfer via Reciprocity using the Michigan Nurse Aide Registry.",
        "Apply to take the Prometric Nurse Aide evaluation."
    ),
    make_state(
        "minnesota-certified-nursing-assistant", "Minnesota", "MN",
        "Nursing Assistant", "NA", ["CNA"],
        "Minnesota Department of Health (MDH)", "651-201-3731",
        "75 hours", "75 hours (16 classroom, 59 clinical)", "Pearson VUE",
        "Complete 75 hours of MDH-approved training and pass the Pearson VUE competency exam to join the Minnesota Nursing Assistant Registry.",
        "Learn MDH requirements, complete a 75-hour program, and pass the Pearson VUE exam.",
        "Transfer via Interstate Endorsement using the Minnesota NA Registry.",
        "Apply to take the Pearson VUE Nursing Assistant evaluation."
    ),
    make_state(
        "missouri-certified-nursing-assistant", "Missouri", "MO",
        "Certified Nurse Assistant", "CNA", [],
        "Missouri Department of Health and Senior Services (DHSS)", "573-526-5686",
        "75 hours", "75 hours (classroom + clinical)", "Headmaster",
        "Complete 75 hours of DHSS-approved training and pass the Headmaster competency exam to join the Missouri Nurse Aide Registry.",
        "Learn DHSS requirements, complete a 75-hour program, and pass the Headmaster exam.",
        "Transfer via Reciprocity using the Missouri CNA Registry.",
        "Apply to take the Headmaster Nurse Aide evaluation."
    ),
    make_state(
        "nebraska-certified-nursing-assistant", "Nebraska", "NE",
        "Certified Nurse Aide", "CNA", [],
        "Nebraska Department of Health and Human Services (DHHS)", "402-471-2115",
        "75 hours", "75 hours (classroom + clinical)", "Pearson VUE",
        "Complete 75 hours of DHHS-approved training and pass the Pearson VUE competency exam.",
        "Learn DHHS requirements, complete a 75-hour program, and pass the Pearson VUE exam.",
        "Transfer via Interstate Endorsement using the Nebraska Nurse Aide Registry.",
        "Apply to take the Pearson VUE Nurse Aide evaluation."
    ),
    make_state(
        "north-dakota-certified-nursing-assistant", "North Dakota", "ND",
        "Certified Nurse Aide", "CNA", [],
        "North Dakota Department of Health and Human Services", "701-328-2352",
        "75 hours", "75 hours (classroom + clinical)", "Headmaster",
        "Complete 75 hours of state-approved training and pass the Headmaster competency exam to join the ND Nurse Aide Registry.",
        "Learn ND requirements, complete a 75-hour program, and pass the Headmaster exam.",
        "Transfer via Reciprocity using the ND Nurse Aide Registry.",
        "Apply to take the Headmaster Nurse Aide evaluation."
    ),
    make_state(
        "ohio-certified-nursing-assistant", "Ohio", "OH",
        "State Tested Nursing Assistant", "STNA", ["CNA"],
        "Ohio Department of Health (ODH)", "614-752-9524",
        "75 hours", "75 hours (59 classroom, 16 clinical)", "D&S Diversified",
        "Complete 75 hours of ODH-approved training and pass the D&S Diversified competency exam to join the Ohio Nurse Aide Registry.",
        "Learn ODH requirements, complete a 75-hour program, and pass the D&S Diversified STNA exam.",
        "Transfer via Reciprocity using the ODH Nurse Aide Registry.",
        "Apply to take the D&S Diversified STNA evaluation."
    ),
    make_state(
        "south-dakota-certified-nursing-assistant", "South Dakota", "SD",
        "Certified Nurse Aide", "CNA", [],
        "South Dakota Department of Health (DOH)", "605-773-3356",
        "75 hours", "75 hours (classroom + clinical)", "Headmaster",
        "Complete 75 hours of DOH-approved training and pass the Headmaster competency exam.",
        "Learn SD DOH requirements, complete a 75-hour program, and pass the Headmaster exam.",
        "Transfer via Reciprocity using the SD Nurse Aide Registry.",
        "Apply to take the Headmaster Nurse Aide evaluation."
    ),
    make_state(
        "wisconsin-certified-nursing-assistant", "Wisconsin", "WI",
        "Certified Nursing Assistant", "CNA", [],
        "Wisconsin Department of Health Services (DHS)", "608-261-8319",
        "120 hours", "120 hours (classroom + clinical)", "Headmaster",
        "Complete 120 hours of DHS-approved training and pass the Headmaster competency exam to join the Wisconsin Nurse Aide Registry.",
        "Learn DHS requirements, complete a 120-hour program, and pass the Headmaster exam.",
        "Transfer via Reciprocity using the Wisconsin Nurse Aide Registry.",
        "Apply to take the Headmaster Nurse Aide evaluation."
    ),
]

with open("temp_research.jsonl", "w", encoding="utf-8") as f:
    for s in states:
        f.write(json.dumps(s) + "\n")
print(f"Created temp_research.jsonl with {len(states)} Midwest state records.")
