import json
from pathlib import Path

states_data = [
    {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": "connecticut-certified-nursing-assistant",
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {
            "entity_key": "ct::cna",
            "default_variant": "becoming"
        },
        "state": {
            "name": "Connecticut",
            "abbr": "CT"
        },
        "profession": {
            "key": "cna",
            "display_label": "Certified Nurse Aide",
            "short_label": "CNA",
            "aliases": ["C.N.A."]
        },
        "container": {
            "label": "Becoming a CNA in Connecticut",
            "label_source": "google_autocomplete",
            "intro": "Complete 100 hours of state-approved training, pass the Prometric competency exam, and get listed on the Connecticut DPH Nurse Aide Registry.",
            "evidence_considered": ["High search volume for 'how to become a cna in ct'"],
            "rejected_alternatives": [],
            "selection_reason": "Matches top informational query."
        },
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {
                    "key": "becoming",
                    "label": "Becoming",
                    "label_source": "google_autocomplete",
                    "description": "Information on how to become a CNA in CT.",
                    "evidence_considered": [],
                    "rejected_alternatives": [],
                    "selection_reason": "Standard task variant."
                },
                {
                    "key": "state_application",
                    "label": "State Application",
                    "label_source": "search_console_intent",
                    "description": "Apply for the Prometric exam.",
                    "evidence_considered": [],
                    "rejected_alternatives": [],
                    "selection_reason": "Standard application intent."
                },
                {
                    "key": "transfer",
                    "label": "Transfer",
                    "label_source": "google_autocomplete",
                    "description": "Transfer an active out-of-state CNA license to Connecticut.",
                    "evidence_considered": [],
                    "rejected_alternatives": [],
                    "selection_reason": "Standard reciprocity intent."
                }
            ]
        },
        "shared_facts": {
            "board": {
                "name": "Connecticut Department of Public Health (DPH) & Prometric",
                "phone": "866-499-7485",
                "fax": "",
                "contact_url": "mailto:CTCNA@Prometric.com",
                "website": "https://portal.ct.gov/DPH",
                "verify_url": ""
            },
            "last_verified": "2026-03-24",
            "source_count": 3
        },
        "task_signals": [],
        "candidate_supporting_pages": [],
        "variants": {
            "becoming": {
                "hero": {
                    "title": "Becoming a CNA in Connecticut",
                    "dek": "Learn Connecticut DPH requirements, find a 100-hour approved training program, and prepare for the Prometric evaluation."
                },
                "seo": {
                    "title": "How to Become a CNA in Connecticut | DPH Requirements",
                    "description": "Step-by-step guide to getting your CNA license in CT. Learn about the 100-hour training requirement and the Prometric exam.",
                    "target_queries": []
                },
                "faq_heading": "Common Questions",
                "cards": [
                    {
                        "key": "training_hours",
                        "label": "Required Training",
                        "value": "100 hours",
                        "status": "confirmed"
                    }
                ],
                "sections": [],
                "faq": []
            },
            "state_application": {
                "hero": {"title": "Connecticut CNA State Exam Application", "dek": "Apply to take the Nurse Aide competency evaluation via Prometric."},
                "seo": {"title": "Connecticut CNA Exam Application | Prometric Registry Guide", "description": "Apply for CT CNA testing.", "target_queries": []},
                "faq_heading": "",
                "cards": [],
                "sections": [],
                "faq": []
            },
            "transfer": {
                "hero": {"title": "Transfer a CNA License to Connecticut", "dek": "Transfer an active out-of-state CNA to CT via Route 8 Endorsement."},
                "seo": {"title": "Transfer CNA License to Connecticut | CT CNA Endorsement", "description": "Learn how to transfer your active out-of-state CNA license to CT.", "target_queries": []},
                "faq_heading": "",
                "cards": [],
                "sections": [],
                "faq": [],
                "temporary_license": {
                    "enabled": False,
                    "hero": {"title": "", "dek": ""},
                    "cards": [],
                    "sections": []
                }
            }
        },
        "validation_notes": {
            "materially_distinct_variant_warning": "",
            "uncertain_fields": ["transfer reciprocity details"],
            "source_backed_only": True
        }
    },
    {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": "delaware-certified-nursing-assistant",
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {
            "entity_key": "de::cna",
            "default_variant": "becoming"
        },
        "state": {
            "name": "Delaware",
            "abbr": "DE"
        },
        "profession": {
            "key": "cna",
            "display_label": "Certified Nursing Assistant",
            "short_label": "CNA",
            "aliases": ["C.N.A."]
        },
        "container": {
            "label": "Becoming a CNA in Delaware",
            "label_source": "google_autocomplete",
            "intro": "Complete 150 hours of training, pass the Prometric exams, and get listed on the Delaware Nurse Aide Registry via DHCQ.",
            "evidence_considered": [],
            "rejected_alternatives": [],
            "selection_reason": "Matches top informational query."
        },
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {
                    "key": "becoming",
                    "label": "Becoming",
                    "label_source": "google_autocomplete",
                    "description": "Information on how to become a CNA in DE.",
                    "evidence_considered": [],
                    "rejected_alternatives": [],
                    "selection_reason": "Standard task variant."
                },
                {
                    "key": "state_application",
                    "label": "State Application",
                    "label_source": "search_console_intent",
                    "description": "Apply for the DHCQ exam via Prometric.",
                    "evidence_considered": [],
                    "rejected_alternatives": [],
                    "selection_reason": "Standard application intent."
                },
                {
                    "key": "transfer",
                    "label": "Transfer",
                    "label_source": "google_autocomplete",
                    "description": "Transfer an active out-of-state CNA license to Delaware.",
                    "evidence_considered": [],
                    "rejected_alternatives": [],
                    "selection_reason": "Standard reciprocity intent."
                }
            ]
        },
        "shared_facts": {
            "board": {
                "name": "Delaware Division of Health Care Quality (DHCQ)",
                "phone": "302-577-6666",
                "fax": "",
                "contact_url": "mailto:DECNA@prometric.com",
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
                "hero": {
                    "title": "Becoming a CNA in Delaware",
                    "dek": "Learn Delaware DHCQ requirements, complete a 150-hour approved training program, and prepare for the Prometric skills and knowledge tests."
                },
                "seo": {
                    "title": "How to Become a CNA in Delaware | DHCQ Requirements",
                    "description": "Step-by-step guide to getting your CNA license in DE. Learn about the 150-hour training requirement and Prometric testing.",
                    "target_queries": []
                },
                "faq_heading": "Common Questions",
                "cards": [
                    {
                        "key": "training_hours",
                        "label": "Required Training",
                        "value": "150 hours (75 classroom, 75 clinical)",
                        "status": "confirmed"
                    }
                ],
                "sections": [],
                "faq": []
            },
            "state_application": {
                "hero": {"title": "Delaware CNA State Exam Application", "dek": "Apply via Prometric to take the Delaware Nurse Aide competency evaluation."},
                "seo": {"title": "Delaware CNA Exam Application | Prometric Guide", "description": "Apply for DE CNA testing.", "target_queries": []},
                "faq_heading": "",
                "cards": [],
                "sections": [],
                "faq": []
            },
            "transfer": {
                "hero": {"title": "Transfer a CNA License to Delaware", "dek": "Transfer an active out-of-state CNA to DE."},
                "seo": {"title": "Transfer CNA License to Delaware | Reciprocity", "description": "Learn how to transfer your active out-of-state CNA license to DE.", "target_queries": []},
                "faq_heading": "",
                "cards": [],
                "sections": [],
                "faq": [],
                "temporary_license": {
                    "enabled": False,
                    "hero": {"title": "", "dek": ""},
                    "cards": [],
                    "sections": []
                }
            }
        },
        "validation_notes": {
            "materially_distinct_variant_warning": "",
            "uncertain_fields": ["transfer reciprocity detailed forms"],
            "source_backed_only": True
        }
    },
    {
        "page_type": "license_path_detail",
        "routing": {
            "canonical_slug": "maine-certified-nursing-assistant",
            "variant_param": "path",
            "allowed_variants": ["becoming", "state_application", "transfer"]
        },
        "analytics": {
            "entity_key": "me::cna",
            "default_variant": "becoming"
        },
        "state": {
            "name": "Maine",
            "abbr": "ME"
        },
        "profession": {
            "key": "cna",
            "display_label": "Certified Nursing Assistant",
            "short_label": "CNA",
            "aliases": ["C.N.A."]
        },
        "container": {
            "label": "Becoming a CNA in Maine",
            "label_source": "google_autocomplete",
            "intro": "Complete 180 hours of state-approved training and pass the competency exam to be listed on the Maine Registry of Certified Nursing Assistants.",
            "evidence_considered": [],
            "rejected_alternatives": [],
            "selection_reason": "Matches top informational query."
        },
        "selector": {
            "default_variant": "becoming",
            "variants": [
                {
                    "key": "becoming",
                    "label": "Becoming",
                    "label_source": "google_autocomplete",
                    "description": "Information on how to become a CNA in ME.",
                    "evidence_considered": [],
                    "rejected_alternatives": [],
                    "selection_reason": "Standard task variant."
                },
                {
                    "key": "state_application",
                    "label": "State Application",
                    "label_source": "search_console_intent",
                    "description": "Apply for the Maine registry exam.",
                    "evidence_considered": [],
                    "rejected_alternatives": [],
                    "selection_reason": "Standard application intent."
                },
                {
                    "key": "transfer",
                    "label": "Transfer",
                    "label_source": "google_autocomplete",
                    "description": "Transfer an active out-of-state CNA license to Maine.",
                    "evidence_considered": [],
                    "rejected_alternatives": [],
                    "selection_reason": "Standard reciprocity intent."
                }
            ]
        },
        "shared_facts": {
            "board": {
                "name": "Maine Registry of Certified Nursing Assistants",
                "phone": "",
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
                "hero": {
                    "title": "Becoming a CNA in Maine",
                    "dek": "Learn Maine CNA Registry requirements, complete a robust 180-hour training program, and prepare for the state evaluation."
                },
                "seo": {
                    "title": "How to Become a CNA in Maine | Registry Requirements",
                    "description": "Step-by-step guide to getting your CNA license in ME. Learn about the 180-hour training requirement and testing.",
                    "target_queries": []
                },
                "faq_heading": "Common Questions",
                "cards": [
                    {
                        "key": "training_hours",
                        "label": "Required Training",
                        "value": "180 hours (90 theory, 20 lab, 70 clinical)",
                        "status": "confirmed"
                    }
                ],
                "sections": [],
                "faq": []
            },
            "state_application": {
                "hero": {"title": "Maine CNA State Exam Application", "dek": "Apply to take the Maine Nurse Aide competency evaluation."},
                "seo": {"title": "Maine CNA Exam Application | Registry Guide", "description": "Apply for ME CNA testing.", "target_queries": []},
                "faq_heading": "",
                "cards": [],
                "sections": [],
                "faq": []
            },
            "transfer": {
                "hero": {"title": "Transfer a CNA License to Maine", "dek": "Contact the Maine Department of Education for bridging requirements to transfer an out-of-state CNA."},
                "seo": {"title": "Transfer CNA License to Maine | Reciprocity", "description": "Learn how to transfer your active out-of-state CNA license to ME.", "target_queries": []},
                "faq_heading": "",
                "cards": [],
                "sections": [],
                "faq": [],
                "temporary_license": {
                    "enabled": False,
                    "hero": {"title": "", "dek": ""},
                    "cards": [],
                    "sections": []
                }
            }
        },
        "validation_notes": {
            "materially_distinct_variant_warning": "",
            "uncertain_fields": ["board phone and URL", "exact reciprocal forms"],
            "source_backed_only": True
        }
    }
]

with open("temp_research.jsonl", "a", encoding="utf-8") as f:
    for state in states_data:
        f.write(json.dumps(state) + "\n")
print(f"Appended {len(states_data)} state records to temp_research.jsonl")
