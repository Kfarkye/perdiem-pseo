"""Apply board-verified pharmacy technician data into state JSON files."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_DIR = ROOT / "database" / "json"
BOARD_DATA_FILE = ROOT / "database" / "board_verified" / "pharmacy-technician-board-data.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def update_faq_answers(faqs: list[dict], faq_answers: dict) -> None:
    cost_answer = faq_answers.get("cost")
    timeline_answer = faq_answers.get("timeline")

    for faq in faqs:
        question = str(faq.get("question", "")).lower()

        if cost_answer and ("how much" in question or "cost" in question or "fee" in question):
            faq["answer"] = cost_answer

        if timeline_answer and ("how long" in question or "processing" in question or "timeline" in question):
            faq["answer"] = timeline_answer


def apply_override(slug: str, override: dict) -> None:
    json_path = JSON_DIR / f"{slug}.json"
    if not json_path.exists():
        raise FileNotFoundError(f"Missing state JSON for override: {slug}")

    data = load_json(json_path)

    verified_date = override["verified_date"]
    board_source_url = override["board_source_url"]

    data["last_verified_date"] = verified_date
    data["last_updated"] = verified_date
    data["board_source_url"] = board_source_url
    data["board_verification"] = override.get("board_verification", {})
    data["board_verification_sources"] = override.get("sources", {})

    if "quick_facts" in override:
        data.setdefault("quick_facts", {}).update(override["quick_facts"])

    if "fees_endorsement" in override:
        data.setdefault("fees_endorsement", {}).update(override["fees_endorsement"])

    reciprocity_override = override.get("reciprocity", {})
    if reciprocity_override:
        data.setdefault("reciprocity", {}).update(reciprocity_override)

    data.setdefault("reciprocity", {})["board_url"] = reciprocity_override.get(
        "board_url",
        board_source_url,
    )
    data["reciprocity"]["endorsement_url"] = reciprocity_override.get(
        "endorsement_url",
        board_source_url,
    )

    update_faq_answers(data.setdefault("faqs", []), override.get("faq_answers", {}))
    save_json(json_path, data)


def main() -> None:
    board_data = load_json(BOARD_DATA_FILE)
    states = board_data.get("states", {})

    if not states:
        raise SystemExit("No board-verified state overrides found.")

    for slug, override in states.items():
        apply_override(slug, override)

    print(f"Applied board-verified overrides to {len(states)} pharmacy technician state files.")


if __name__ == "__main__":
    main()
