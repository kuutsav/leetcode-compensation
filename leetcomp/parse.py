import json
import os
import re
from datetime import datetime
from typing import Any, Generator

from leetcomp.prompts import PARSING_PROMPT
from leetcomp.utils import (
    config,
    get_model_predict,
    latest_parsed_date,
    mapping,
    parse_json_markdown,
    sort_and_truncate,
)

interview_exp_pattern = re.compile(
    r"https://leetcode.com/discuss/interview-experience/\S+"
)

llm_predict = get_model_predict(config["app"]["llm_predictor"])

yoe_map: dict[tuple[int, int], str] = {
    (0, 1): "Entry (0-1)",
    (2, 6): "Mid (2-6)",
    (7, 10): "Senior (7-10)",
    (11, 30): "Senior + (11+)",
}


def post_should_be_parsed(post: dict[Any, Any]) -> bool:
    if "title" not in post:
        print(f" x skipping {post['id']}; no title")
        return False
    if "|" not in post["title"]:
        print(f" x skipping {post['id']}; | not in title")
        return False
    if "vote_count" not in post:
        print(f" x skipping {post['id']}; no vote_count")
        return False
    if post["vote_count"] < 0:
        print(f" x skipping {post['id']}; negative vote_count")
        return False
    return True


def has_crossed_till_date(
    creation_date: str, till_date: datetime | None = None
) -> bool:
    if till_date is None:
        return False

    dt = datetime.strptime(creation_date, config["app"]["date_fmt"])
    return dt <= till_date


def comps_posts_iter(comps_path: str) -> Generator[dict[Any, Any], None, None]:
    with open(comps_path, "r") as f:
        for line in f:
            yield json.loads(line)


def parsed_content_is_valid(
    post_id: str, parsed_content: list[dict[Any, Any]]
) -> bool:
    if not isinstance(parsed_content, list) or not parsed_content:
        return False

    for item in parsed_content:
        try:
            assert isinstance(item, dict), "item is not a dict"

            assert isinstance(
                item["base_offer"], (int, float)
            ), "base_offer is not a number"

            assert (
                config["parsing"]["min_base_offer"]
                <= item["base_offer"]
                <= config["parsing"]["max_base_offer"]
            ), "base_offer out of range"

            assert isinstance(
                item["total_offer"], (int, float)
            ), "total_offer is not a number"

            assert (
                config["parsing"]["min_total_offer"]
                <= item["total_offer"]
                <= config["parsing"]["max_total_offer"]
            ), "total_offer out of range"

            assert isinstance(item["company"], str), "company is not a string"
            assert isinstance(item["role"], str), "role is not a string"
            assert isinstance(item["yoe"], (int, float)), "yoe is not a number"

            if "non_indian" in item:
                assert item["non_indian"] != "yes", "non_indian is yes"

            # offers as amounts are per month, need a modified prompt for these
            assert "intern" not in item["role"].lower(), "intern in role"
        except (KeyError, AssertionError) as e:
            print(f" x skipping {post_id}; invalid content: {str(e)}")
            return False

    return True  # Parsed content is valid if no assertions fail


def extract_interview_exp(content: str) -> str:
    match = interview_exp_pattern.search(content)
    return match.group(0) if match else "N/A"


def get_parsed_posts(
    raw_post: dict[Any, Any], parsed_content: list[dict[Any, Any]]
) -> list[dict[Any, Any]]:
    return [
        {
            "id": raw_post["id"],
            "vote_count": raw_post["vote_count"],
            "comment_count": raw_post["comment_count"],
            "view_count": raw_post["view_count"],
            "creation_date": raw_post["creation_date"],
            "company": item["company"],
            "role": item["role"],
            "yoe": item["yoe"],
            "base_offer": item["base_offer"],
            "total_offer": item["total_offer"],
            "location": item.get("location", "n/a"),
            "interview_exp": extract_interview_exp(raw_post["content"]),
        }
        for item in parsed_content
    ]


def fill_yoe(parsed_content: list[dict[Any, Any]]) -> None:
    if len(parsed_content) > 1:
        for item in parsed_content[1:]:
            item["yoe"] = parsed_content[0]["yoe"]


def parse_posts(
    in_comps_path: str,
    out_comps_path: str,
    parsed_ids: set[int] | None = None,
    till_date: datetime | None = None,
) -> None:
    n_skips = 0
    parsed_ids = parsed_ids or set()

    for i, post in enumerate(comps_posts_iter(in_comps_path), start=1):
        if i % 20 == 0:
            print(f"Processed {i} posts; {n_skips} skips")

        if post["id"] in parsed_ids or not post_should_be_parsed(post):
            n_skips += 1
            continue

        if has_crossed_till_date(post["creation_date"], till_date):
            break

        input_text = f"{post['title']}\n---\n{post['content']}"
        prompt = PARSING_PROMPT.substitute(leetcode_post=input_text)
        response = llm_predict(prompt)
        parsed_content = parse_json_markdown(response)

        if parsed_content_is_valid(post["id"], parsed_content):
            fill_yoe(parsed_content)
            parsed_posts = get_parsed_posts(post, parsed_content)
            with open(out_comps_path, "a") as f:
                for parsed_post in parsed_posts:
                    f.write(json.dumps(parsed_post) + "\n")
        else:
            n_skips += 1


def get_parsed_ids(out_comps_path: str) -> set[int]:
    with open(out_comps_path, "r") as f:
        return {json.loads(line)["id"] for line in f}


def cleanup_record(record: dict[Any, Any]) -> None:
    record.pop("vote_count", None)
    record.pop("comment_count", None)
    record.pop("view_count", None)

    record["creation_date"] = record["creation_date"][:10]
    record["yoe"] = round(record["yoe"])
    record["base"] = round(float(record["base_offer"]), 2)
    record["total"] = round(float(record["total_offer"]), 2)

    record.pop("base_offer", None)
    record.pop("total_offer", None)


def mapped_record(
    item: str,
    mapping: dict[str, str],
    default: str | None = None,
    extras: list[str] | None = None,
) -> str:
    item = item.lower()
    if extras:
        for role_str in extras:
            if role_str in item:
                return role_str.capitalize()

    return mapping.get(item, default or item.capitalize())


def map_location(location: str, location_map: dict[str, str]) -> str:
    location = location.lower()

    if location == "n/a":
        return location_map[location]

    if "(" in location:
        location = location.split("(")[0].strip()

    for sep in [",", "/"]:
        if sep in location:
            locations = [loc.strip().lower() for loc in location.split(sep)]
            location = "/".join(
                [location_map.get(loc, loc.capitalize()) for loc in locations]
            )
            return location

    return location_map.get(location, location.capitalize())


def map_yoe(yoe: int, yoe_map: dict[tuple[int, int], str]) -> str:
    for (start, end), mapped_yoe in yoe_map.items():
        if start <= yoe <= end:
            return mapped_yoe

    return "Senior +"


def jsonl_to_json(jsonl_path: str, json_path: str) -> None:
    company_map = mapping(config["app"]["data_dir"] / "company_map.json")
    role_map = mapping(config["app"]["data_dir"] / "role_map.json")
    location_map = mapping(config["app"]["data_dir"] / "location_map.json")
    records = []

    with open(jsonl_path, "r") as file:
        for line in file:
            record = json.loads(line)
            cleanup_record(record)
            record["company"] = mapped_record(record["company"], company_map)
            role_to_map = "".join(re.findall(r"\w+", record["role"]))
            record["mapped_role"] = mapped_record(
                role_to_map,
                role_map,
                default=record["role"],
                extras=["analyst", "intern", "associate"],
            )
            record["mapped_yoe"] = map_yoe(record["yoe"], yoe_map)
            record["location"] = map_location(record["location"], location_map)
            records.append(record)

    with open(json_path, "w") as file:
        json.dump(records, file, indent=4)

    print(f"Converted {len(records)} records!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse LeetCode Compensations posts."
    )
    parser.add_argument(
        "--in_comps_path",
        type=str,
        default=config["app"]["data_dir"] / "raw_comps.jsonl",
        help="Path to the file to store posts.",
    )
    parser.add_argument(
        "--out_comps_path",
        type=str,
        default=config["app"]["data_dir"] / "parsed_comps.jsonl",
        help="Path to the file to store parsed posts.",
    )
    parser.add_argument(
        "--json_path",
        type=str,
        default=config["app"]["data_dir"] / "parsed_comps.json",
        help="Path to the file to store parsed posts in JSON format.",
    )
    args = parser.parse_args()

    print(f"Parsing comps from {args.in_comps_path}...")

    parsed_ids = (
        get_parsed_ids(args.out_comps_path)
        if os.path.exists(args.out_comps_path)
        else set()
    )
    print(f"Found {len(parsed_ids)} parsed ids...")

    till_date = (
        latest_parsed_date(args.out_comps_path)
        if os.path.exists(args.out_comps_path)
        else None
    )

    parse_posts(args.in_comps_path, args.out_comps_path, parsed_ids, till_date)
    sort_and_truncate(args.out_comps_path, truncate=True)
    jsonl_to_json(args.out_comps_path, args.json_path)
