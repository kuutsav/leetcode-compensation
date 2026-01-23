"""
The final transform step that helps create the "ready-to-consume" data for the ui.
Does a little filtering, capitalization and basic processing of the llm parsed data
(PARSED_FILE; data/parsed_posts.jsonl) so that the records are easy to consume in the
client facing ui (index.html).
"""

from enum import StrEnum
import json

from leetcomp import DATA_DIR, PARSED_FILE, FINAL_DATA_FILE


class InvalidRecReason(StrEnum):
    NON_COMP = "Non Comp"
    NON_INR = "Non INR"
    MISSING_FIELDS = "Misssing Fields"


def load_entity_mappings(entities: list[str]) -> dict[str, dict[str, str]]:
    entity_map = {}
    for entity in entities:
        with open(f"{DATA_DIR}/{entity}_map.json", "r") as f:
            entity_map[entity] = json.load(f)
    return entity_map


def capitalize_role(role: str) -> str:
    # for example; sse -> SSE, sdet -> SDET
    if len(role) <= 4 and " " not in role:
        return role.upper()

    # for example; smts 1 -> SMTS 1, ic 4 -> IC 4
    parts = role.split()
    if len(parts) == 2:
        word, num = parts
        if 2 <= len(word) <= 4 and num.isdigit():
            return f"{word.upper()} {num}"

    return role.title()


def is_valid_record(rec: dict) -> tuple[bool, str]:
    if not rec.get("compensation-post", False):
        return False, InvalidRecReason.NON_COMP

    # TODO: We need to preserve the remote offers for India in EUR or USD
    if rec.get("currency") != "INR":
        return False, InvalidRecReason.NON_INR

    # Loosened criteria: role-normalized is now optional (will default to "N/A")
    required = ["id", "created_at", "company-normalized"]
    if not all(key in rec for key in required):
        return False, InvalidRecReason.MISSING_FIELDS

    return True, ""


def transform_record(rec: dict, entity_map: dict[str, dict[str, str]]) -> dict:
    company_raw = rec.get("company-normalized", "")
    role_raw = rec.get("role-normalized", "")
    location_raw = rec.get("location", "")

    # Use map value directly if found, otherwise apply our capitalization
    company = entity_map["company"].get(company_raw.lower()) or company_raw.title()
    role = entity_map["role"].get(role_raw.lower()) or capitalize_role(role_raw)
    location = (
        entity_map["location"].get(location_raw.lower()) or location_raw.title()
        if location_raw
        else ""
    )

    yoe = rec.get("yoe")
    base = rec.get("base")
    total = rec.get("total") or rec.get("total-calculated")

    return {
        "id": rec["id"],
        "date": rec["created_at"],
        "location": location,
        "company": company or "N/A",
        "role": role or "N/A",
        "yoe": yoe,  # Keep as null for proper sorting/charting in JS
        "base": base,  # Keep as null for proper sorting/charting in JS
        "total": total,  # Keep as null for proper sorting/charting in JS
    }


def print_stats(stats: dict) -> None:
    total = stats["total"]
    processed = stats["processed"]
    dropped = sum(stats[reason] for reason in InvalidRecReason)

    print("Processing Stats...")
    print(f"Total posts processed: {total}")
    print(f"Successfully included: {processed}")
    print("\nDropped posts breakdown:")

    for reason in InvalidRecReason:
        count = stats[reason]
        print(f" ⤷ {reason}: {count} ({count / total * 100:.1f}%)")

    print(f"\nTotal dropped: {dropped} ({dropped / total * 100:.1f}%)")


def create_final_data(parsed_file: str = PARSED_FILE, output_file: str = FINAL_DATA_FILE):
    """
    Creates final data for the ui by only keeping the records of interest for the table
    and charts in the ui as well as maps the entities like companies, roles, etc. to
    sanitized and normalized values based on data normalization done by processing
    these raw entities in bulk in the past.
    """

    print("Loading entity mappings...")
    entity_map = load_entity_mappings(["company", "role", "location"])

    stats = {
        "total": 0,
        "processed": 0,
        **{reason: 0 for reason in InvalidRecReason},
    }
    final_data = []

    print(f"Processing {parsed_file}...")
    with open(parsed_file, "r") as f:
        for line in f:
            rec = json.loads(line)
            stats["total"] += 1

            valid, reason = is_valid_record(rec)
            if not valid:
                stats[reason] += 1
                continue

            final_data.append(transform_record(rec, entity_map))
            stats["processed"] += 1

    with open(output_file, "w") as f:
        json.dump(final_data, f, indent=2)

    print_stats(stats)
    print(f"Final data saved to {output_file}")
