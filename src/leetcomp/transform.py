import json

from leetcomp import PARSED_FILE, FINAL_DATA_FILE


def load_entity_mappings():
    with open("data/company_map.json", "r") as f:
        company_map = json.load(f)
    with open("data/role_map.json", "r") as f:
        role_map = json.load(f)
    with open("data/location_map.json", "r") as f:
        location_map = json.load(f)
    return company_map, role_map, location_map


def capitalize_role(role: str) -> str:
    if len(role) <= 4 and " " not in role:
        return role.upper()

    parts = role.split()
    if len(parts) == 2:
        word, num = parts
        if 3 <= len(word) <= 4 and num.isdigit():
            return f"{word.upper()} {num}"

    return role.title()


def is_valid_record(rec: dict) -> tuple[bool, str]:
    if not rec.get("compensation-post", False):
        return False, "non_comp"

    if rec.get("currency") != "INR":
        return False, "non_inr"

    required = ["id", "created_at", "company-normalized", "role-normalized"]
    if not all(key in rec for key in required):
        return False, "missing_fields"

    return True, ""


def transform_record(rec: dict, company_map: dict, role_map: dict, location_map: dict) -> dict:
    company_raw = rec.get("company-normalized", "")
    role_raw = rec.get("role-normalized", "")
    location_raw = rec.get("location", "")

    company = company_map.get(company_raw, company_raw).title()
    role = role_map.get(role_raw, capitalize_role(role_raw))
    location = location_map.get(location_raw, location_raw).title() if location_raw else ""

    return {
        "id": rec["id"],
        "date": rec["created_at"],
        "location": location,
        "company": company,
        "role": role,
        "yoe": rec.get("yoe"),
        "base": rec.get("base"),
        "total": rec.get("total") or rec.get("total-calculated"),
    }


def print_stats(total: int, processed: int, non_comp: int, non_inr: int, missing: int):
    dropped = non_comp + non_inr + missing
    print("\n" + "=" * 50)
    print("PROCESSING STATISTICS")
    print("=" * 50)
    print(f"Total posts processed: {total}")
    print(f"✓ Successfully included: {processed}")
    print("\nDropped posts breakdown:")
    print(f"  • Non-compensation related: {non_comp} ({non_comp / total * 100:.1f}%)")
    print(f"  • Non-INR currency: {non_inr} ({non_inr / total * 100:.1f}%)")
    print(f"  • Missing required fields: {missing} ({missing / total * 100:.1f}%)")
    print(f"\nTotal dropped: {dropped} ({dropped / total * 100:.1f}%)")
    print("=" * 50)


def create_final_data(parsed_file: str = PARSED_FILE, output_file: str = FINAL_DATA_FILE):
    print("Loading entity mappings...")
    company_map, role_map, location_map = load_entity_mappings()

    stats = {"total": 0, "processed": 0, "non_comp": 0, "non_inr": 0, "missing": 0}
    final_data = []

    print(f"Processing {parsed_file}...")
    with open(parsed_file, "r") as f:
        for line in f:
            rec = json.loads(line)
            stats["total"] += 1

            valid, reason = is_valid_record(rec)
            if not valid:
                if reason == "non_comp":
                    stats["non_comp"] += 1
                elif reason == "non_inr":
                    stats["non_inr"] += 1
                else:
                    stats["missing"] += 1
                continue

            final_data.append(transform_record(rec, company_map, role_map, location_map))
            stats["processed"] += 1

    with open(output_file, "w") as f:
        json.dump(final_data, f, indent=2)

    print_stats(
        stats["total"],
        stats["processed"],
        stats["non_comp"],
        stats["non_inr"],
        stats["missing"],
    )
    print(f"✓ Final data saved to {output_file}")


if __name__ == "__main__":
    create_final_data()
