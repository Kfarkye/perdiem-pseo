import json
from pathlib import Path

states_data = [
    {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": "alabama-certified-nursing-assistant",
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {"entity_key": "al::cna", "default_variant": "becoming"},
        "state": {"name": "Alabama", "abbr": "AL"},
        "profession": {"key": "cna", "display_label": "Certified Nurse Aide", "short_label": "CNA", "aliases": ["N.A."]},
        "container": {"label": "Becoming a CNA in Alabama", "label_source": "google_autocomplete", "intro": "Complete 120 hours of training and pass the Prometric competency exam to join the Alabama Nurse Aide Registry.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Standard intent"},
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {"key": "becoming", "label": "Becoming", "label_source": "google_autocomplete", "description": "How to become a CNA in AL.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Task variant"},
                {"key": "state_application", "label": "State Application", "label_source": "search_console_intent", "description": "Apply for the Alabama Prometric exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Application intent"},
                {"key": "transfer", "label": "Transfer", "label_source": "google_autocomplete", "description": "Transfer an active out-of-state CNA to Alabama.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Reciprocity intent"}
            ]
        },
        "shared_facts": {
            "board": {
                "name": "Alabama Department of Public Health (ADPH)",
                "phone": "334-206-5169",
                "fax": "",
                "contact_url": "mailto:NARegistry@adph.state.al.us",
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
                "hero": {"title": "Becoming a CNA in Alabama", "dek": "Learn ADPH requirements, complete a 120-hour program, and pass the Prometric exam."},
                "seo": {"title": "How to Become a CNA in Alabama", "description": "Step-by-step guide to the 120-hour training requirement and testing.", "target_queries": []},
                "faq_heading": "Common Questions",
                "cards": [{"key": "training_hours", "label": "Required Training", "value": "120 hours", "status": "confirmed"}],
                "sections": [], "faq": []
            },
            "state_application": {
                "hero": {"title": "Alabama CNA State Exam Application", "dek": "Apply to take the evaluation via Prometric."},
                "seo": {"title": "Alabama CNA Exam Application", "description": "Apply for AL CNA testing.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": []
            },
            "transfer": {
                "hero": {"title": "Transfer a CNA License to Alabama", "dek": "Transfer via Reciprocity using the ADPH Nurse Aide Registry."},
                "seo": {"title": "Transfer CNA License to Alabama", "description": "Transfer your active out-of-state CNA to AL.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": [],
                "temporary_license": {"enabled": False, "hero": {"title": "", "dek": ""}, "cards": [], "sections": []}
            }
        },
        "validation_notes": {"materially_distinct_variant_warning": "", "uncertain_fields": [], "source_backed_only": True}
    },
    {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": "arkansas-certified-nursing-assistant",
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {"entity_key": "ar::cna", "default_variant": "becoming"},
        "state": {"name": "Arkansas", "abbr": "AR"},
        "profession": {"key": "cna", "display_label": "Certified Nursing Assistant", "short_label": "CNA", "aliases": []},
        "container": {"label": "Becoming a CNA in Arkansas", "label_source": "google_autocomplete", "intro": "Complete 90 hours of training and pass the Prometric exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Standard intent"},
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {"key": "becoming", "label": "Becoming", "label_source": "google_autocomplete", "description": "How to become a CNA in AR.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Task variant"},
                {"key": "state_application", "label": "State Application", "label_source": "search_console_intent", "description": "Apply for the exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Application intent"},
                {"key": "transfer", "label": "Transfer", "label_source": "google_autocomplete", "description": "Transfer an active out-of-state CNA.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Reciprocity intent"}
            ]
        },
        "shared_facts": {
            "board": {
                "name": "Arkansas Office of Long Term Care (OLTC)",
                "phone": "501-682-8430",
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
                "hero": {"title": "Becoming a CNA in Arkansas", "dek": "Learn OLTC requirements, complete a 90-hour program, and pass the Prometric exam."},
                "seo": {"title": "How to Become a CNA in Arkansas", "description": "Step-by-step guide.", "target_queries": []},
                "faq_heading": "Common Questions",
                "cards": [{"key": "training_hours", "label": "Required Training", "value": "90 hours", "status": "confirmed"}],
                "sections": [], "faq": []
            },
            "state_application": {
                "hero": {"title": "Arkansas CNA State Exam Application", "dek": "Apply to take the evaluation."},
                "seo": {"title": "Arkansas CNA Exam Application", "description": "Apply for AR CNA testing.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": []
            },
            "transfer": {
                "hero": {"title": "Transfer a CNA License to Arkansas", "dek": "Transfer via Reciprocity using Form 9110."},
                "seo": {"title": "Transfer CNA License to Arkansas", "description": "Transfer your active out-of-state CNA to AR.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": [],
                "temporary_license": {"enabled": False, "hero": {"title": "", "dek": ""}, "cards": [], "sections": []}
            }
        },
        "validation_notes": {"materially_distinct_variant_warning": "", "uncertain_fields": [], "source_backed_only": True}
    },
    {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": "georgia-certified-nursing-assistant",
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {"entity_key": "ga::cna", "default_variant": "becoming"},
        "state": {"name": "Georgia", "abbr": "GA"},
        "profession": {"key": "cna", "display_label": "Certified Nurse Aide", "short_label": "CNA", "aliases": []},
        "container": {"label": "Becoming a CNA in Georgia", "label_source": "google_autocomplete", "intro": "Complete 85 hours of state-approved training and pass the Credentia competency exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Standard intent"},
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {"key": "becoming", "label": "Becoming", "label_source": "google_autocomplete", "description": "How to become a CNA in GA.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Task variant"},
                {"key": "state_application", "label": "State Application", "label_source": "search_console_intent", "description": "Apply for the Credentia exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Application intent"},
                {"key": "transfer", "label": "Transfer", "label_source": "google_autocomplete", "description": "Transfer an active out-of-state CNA to Georgia.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Reciprocity intent"}
            ]
        },
        "shared_facts": {
            "board": {
                "name": "Georgia Department of Community Health",
                "phone": "800-414-4358",
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
                "hero": {"title": "Becoming a CNA in Georgia", "dek": "Learn DCH requirements, complete an 85-hour program, and pass the Credentia exam."},
                "seo": {"title": "How to Become a CNA in Georgia", "description": "Step-by-step guide.", "target_queries": []},
                "faq_heading": "Common Questions",
                "cards": [{"key": "training_hours", "label": "Required Training", "value": "85 hours", "status": "confirmed"}],
                "sections": [], "faq": []
            },
            "state_application": {
                "hero": {"title": "Georgia CNA State Exam Application", "dek": "Apply to take the Credentia Nurse Aide evaluation."},
                "seo": {"title": "Georgia CNA Exam Application", "description": "Apply for GA CNA testing.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": []
            },
            "transfer": {
                "hero": {"title": "Transfer a CNA License to Georgia", "dek": "Transfer via Reciprocity using the Nurse Aide Registry."},
                "seo": {"title": "Transfer CNA License to Georgia", "description": "Transfer your active out-of-state CNA to GA.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": [],
                "temporary_license": {"enabled": False, "hero": {"title": "", "dek": ""}, "cards": [], "sections": []}
            }
        },
        "validation_notes": {"materially_distinct_variant_warning": "", "uncertain_fields": [], "source_backed_only": True}
    },
    {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": "kentucky-certified-nursing-assistant",
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {"entity_key": "ky::cna", "default_variant": "becoming"},
        "state": {"name": "Kentucky", "abbr": "KY"},
        "profession": {"key": "cna", "display_label": "State Registered Nurse Aide", "short_label": "SRNA", "aliases": ["CNA"]},
        "container": {"label": "Becoming an SRNA in Kentucky", "label_source": "google_autocomplete", "intro": "Complete 75 hours of state-approved training and pass the KCTCS competency exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Standard intent"},
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {"key": "becoming", "label": "Becoming", "label_source": "google_autocomplete", "description": "How to become an SRNA in KY.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Task variant"},
                {"key": "state_application", "label": "State Application", "label_source": "search_console_intent", "description": "Apply for the KCTCS exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Application intent"},
                {"key": "transfer", "label": "Transfer", "label_source": "google_autocomplete", "description": "Transfer an active out-of-state list to Kentucky.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Reciprocity intent"}
            ]
        },
        "shared_facts": {
            "board": {
                "name": "Kentucky Board of Nursing",
                "phone": "502-429-3300",
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
                "hero": {"title": "Becoming an SRNA in Kentucky", "dek": "Learn KBN requirements, complete a 75-hour program, and pass the state exam."},
                "seo": {"title": "How to Become an SRNA in Kentucky", "description": "Step-by-step guide.", "target_queries": []},
                "faq_heading": "Common Questions",
                "cards": [{"key": "training_hours", "label": "Required Training", "value": "75 hours", "status": "confirmed"}],
                "sections": [], "faq": []
            },
            "state_application": {
                "hero": {"title": "Kentucky State Exam Application", "dek": "Apply to take the SRNA evaluation via KCTCS."},
                "seo": {"title": "Kentucky SRNA Exam Application", "description": "Apply for KY testing.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": []
            },
            "transfer": {
                "hero": {"title": "Transfer a CNA License to Kentucky", "dek": "Transfer via Reciprocity using the KBN Portal."},
                "seo": {"title": "Transfer CNA License to Kentucky", "description": "Transfer your active out-of-state CNA/SRNA to KY.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": [],
                "temporary_license": {"enabled": False, "hero": {"title": "", "dek": ""}, "cards": [], "sections": []}
            }
        },
        "validation_notes": {"materially_distinct_variant_warning": "", "uncertain_fields": [], "source_backed_only": True}
    },
    {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": "louisiana-certified-nursing-assistant",
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {"entity_key": "la::cna", "default_variant": "becoming"},
        "state": {"name": "Louisiana", "abbr": "LA"},
        "profession": {"key": "cna", "display_label": "Certified Nursing Assistant", "short_label": "CNA", "aliases": []},
        "container": {"label": "Becoming a CNA in Louisiana", "label_source": "google_autocomplete", "intro": "Complete 80 hours of state-approved training and pass the Prometric exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Standard intent"},
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {"key": "becoming", "label": "Becoming", "label_source": "google_autocomplete", "description": "How to become a CNA in LA.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Task variant"},
                {"key": "state_application", "label": "State Application", "label_source": "search_console_intent", "description": "Apply for the Prometric exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Application intent"},
                {"key": "transfer", "label": "Transfer", "label_source": "google_autocomplete", "description": "Transfer an active out-of-state CNA to Louisiana.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Reciprocity intent"}
            ]
        },
        "shared_facts": {
            "board": {
                "name": "Louisiana Department of Health",
                "phone": "225-342-0138",
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
                "hero": {"title": "Becoming a CNA in Louisiana", "dek": "Learn LDH requirements, complete an 80-hour program, and pass the Prometric exam."},
                "seo": {"title": "How to Become a CNA in Louisiana", "description": "Step-by-step guide.", "target_queries": []},
                "faq_heading": "Common Questions",
                "cards": [{"key": "training_hours", "label": "Required Training", "value": "80 hours", "status": "confirmed"}],
                "sections": [], "faq": []
            },
            "state_application": {
                "hero": {"title": "Louisiana CNA State Exam Application", "dek": "Apply to take the Prometric Nurse Aide evaluation."},
                "seo": {"title": "Louisiana CNA Exam Application", "description": "Apply for LA testing.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": []
            },
            "transfer": {
                "hero": {"title": "Transfer a CNA License to Louisiana", "dek": "Transfer via Reciprocity using the Route 8 application."},
                "seo": {"title": "Transfer CNA License to Louisiana", "description": "Transfer your active out-of-state CNA to LA.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": [],
                "temporary_license": {"enabled": False, "hero": {"title": "", "dek": ""}, "cards": [], "sections": []}
            }
        },
        "validation_notes": {"materially_distinct_variant_warning": "", "uncertain_fields": [], "source_backed_only": True}
    },
    {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": "mississippi-certified-nursing-assistant",
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {"entity_key": "ms::cna", "default_variant": "becoming"},
        "state": {"name": "Mississippi", "abbr": "MS"},
        "profession": {"key": "cna", "display_label": "Certified Nurse Aide", "short_label": "CNA", "aliases": []},
        "container": {"label": "Becoming a CNA in Mississippi", "label_source": "google_autocomplete", "intro": "Complete 75 hours of state-approved training and pass the Credentia exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Standard intent"},
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {"key": "becoming", "label": "Becoming", "label_source": "google_autocomplete", "description": "How to become a CNA in MS.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Task variant"},
                {"key": "state_application", "label": "State Application", "label_source": "search_console_intent", "description": "Apply for the Credentia exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Application intent"},
                {"key": "transfer", "label": "Transfer", "label_source": "google_autocomplete", "description": "Transfer an active out-of-state CNA to Mississippi.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Reciprocity intent"}
            ]
        },
        "shared_facts": {
            "board": {
                "name": "Mississippi State Department of Health",
                "phone": "601-364-1100",
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
                "hero": {"title": "Becoming a CNA in Mississippi", "dek": "Learn MSDH requirements, complete a 75-hour program, and pass the Credentia exam."},
                "seo": {"title": "How to Become a CNA in Mississippi", "description": "Step-by-step guide.", "target_queries": []},
                "faq_heading": "Common Questions",
                "cards": [{"key": "training_hours", "label": "Required Training", "value": "75 hours", "status": "confirmed"}],
                "sections": [], "faq": []
            },
            "state_application": {
                "hero": {"title": "Mississippi CNA State Exam Application", "dek": "Apply to take the Credentia Nurse Aide evaluation."},
                "seo": {"title": "Mississippi CNA Exam Application", "description": "Apply for MS CNA testing.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": []
            },
            "transfer": {
                "hero": {"title": "Transfer a CNA License to Mississippi", "dek": "Transfer via Reciprocity using the Nurse Aide Registry."},
                "seo": {"title": "Transfer CNA License to Mississippi", "description": "Transfer your active out-of-state CNA to MS.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": [],
                "temporary_license": {"enabled": False, "hero": {"title": "", "dek": ""}, "cards": [], "sections": []}
            }
        },
        "validation_notes": {"materially_distinct_variant_warning": "", "uncertain_fields": [], "source_backed_only": True}
    },
    {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": "south-carolina-certified-nursing-assistant",
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {"entity_key": "sc::cna", "default_variant": "becoming"},
        "state": {"name": "South Carolina", "abbr": "SC"},
        "profession": {"key": "cna", "display_label": "Certified Nursing Assistant", "short_label": "CNA", "aliases": []},
        "container": {"label": "Becoming a CNA in South Carolina", "label_source": "google_autocomplete", "intro": "Complete 100 hours of state-approved training and pass the Credentia exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Standard intent"},
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {"key": "becoming", "label": "Becoming", "label_source": "google_autocomplete", "description": "How to become a CNA in SC.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Task variant"},
                {"key": "state_application", "label": "State Application", "label_source": "search_console_intent", "description": "Apply for the Credentia exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Application intent"},
                {"key": "transfer", "label": "Transfer", "label_source": "google_autocomplete", "description": "Transfer an active out-of-state CNA to South Carolina.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Reciprocity intent"}
            ]
        },
        "shared_facts": {
            "board": {
                "name": "SC Department of Health and Environmental Control",
                "phone": "803-898-3432",
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
                "hero": {"title": "Becoming a CNA in South Carolina", "dek": "Learn DHEC requirements, complete a 100-hour program, and pass the Credentia exam."},
                "seo": {"title": "How to Become a CNA in South Carolina", "description": "Step-by-step guide.", "target_queries": []},
                "faq_heading": "Common Questions",
                "cards": [{"key": "training_hours", "label": "Required Training", "value": "100 hours", "status": "confirmed"}],
                "sections": [], "faq": []
            },
            "state_application": {
                "hero": {"title": "South Carolina CNA State Exam Application", "dek": "Apply to take the Credentia evaluation."},
                "seo": {"title": "South Carolina CNA Exam Application", "description": "Apply for SC testing.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": []
            },
            "transfer": {
                "hero": {"title": "Transfer a CNA License to South Carolina", "dek": "Transfer via Reciprocity using the Nurse Aide Registry."},
                "seo": {"title": "Transfer CNA License to South Carolina", "description": "Transfer your active out-of-state CNA to SC.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": [],
                "temporary_license": {"enabled": False, "hero": {"title": "", "dek": ""}, "cards": [], "sections": []}
            }
        },
        "validation_notes": {"materially_distinct_variant_warning": "", "uncertain_fields": [], "source_backed_only": True}
    },
    {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": "tennessee-certified-nursing-assistant",
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {"entity_key": "tn::cna", "default_variant": "becoming"},
        "state": {"name": "Tennessee", "abbr": "TN"},
        "profession": {"key": "cna", "display_label": "Certified Nursing Assistant", "short_label": "CNA", "aliases": []},
        "container": {"label": "Becoming a CNA in Tennessee", "label_source": "google_autocomplete", "intro": "Complete 75 hours of state-approved training and pass the Headmaster exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Standard intent"},
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {"key": "becoming", "label": "Becoming", "label_source": "google_autocomplete", "description": "How to become a CNA in TN.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Task variant"},
                {"key": "state_application", "label": "State Application", "label_source": "search_console_intent", "description": "Apply for the Headmaster exam.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Application intent"},
                {"key": "transfer", "label": "Transfer", "label_source": "google_autocomplete", "description": "Transfer an active out-of-state CNA to Tennessee.", "evidence_considered": [], "rejected_alternatives": [], "selection_reason": "Reciprocity intent"}
            ]
        },
        "shared_facts": {
            "board": {
                "name": "Tennessee Department of Health",
                "phone": "615-532-5171",
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
                "hero": {"title": "Becoming a CNA in Tennessee", "dek": "Learn TDH requirements, complete a 75-hour program, and pass the Headmaster exam."},
                "seo": {"title": "How to Become a CNA in Tennessee", "description": "Step-by-step guide.", "target_queries": []},
                "faq_heading": "Common Questions",
                "cards": [{"key": "training_hours", "label": "Required Training", "value": "75 hours", "status": "confirmed"}],
                "sections": [], "faq": []
            },
            "state_application": {
                "hero": {"title": "Tennessee CNA State Exam Application", "dek": "Apply to take the Headmaster evaluation."},
                "seo": {"title": "Tennessee CNA Exam Application", "description": "Apply for TN testing.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": []
            },
            "transfer": {
                "hero": {"title": "Transfer a CNA License to Tennessee", "dek": "Transfer via Reciprocity using the Nurse Aide Registry."},
                "seo": {"title": "Transfer CNA License to Tennessee", "description": "Transfer your active out-of-state CNA to TN.", "target_queries": []},
                "faq_heading": "", "cards": [], "sections": [], "faq": [],
                "temporary_license": {"enabled": False, "hero": {"title": "", "dek": ""}, "cards": [], "sections": []}
            }
        },
        "validation_notes": {"materially_distinct_variant_warning": "", "uncertain_fields": [], "source_backed_only": True}
    }
]

with open("temp_research.jsonl", "w", encoding="utf-8") as f:
    for state in states_data:
        f.write(json.dumps(state) + "\n")
print(f"Created temp_research.jsonl with {len(states_data)} state records.")
