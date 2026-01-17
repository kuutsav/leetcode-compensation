import asyncio
import json
import os
from datetime import datetime

from leetcomp import (
    DATA_DIR,
    PARSED_FILE,
    PARSED_TEMP_FILE,
    POSTS_FILE,
    TEMP_FILE,
    FINAL_DATA_FILE,
)
from leetcomp.fetch import fetch_posts_in_bulk
from leetcomp.parse import parse_posts_with_llm
from leetcomp.normalize import normalize_and_save
from leetcomp.transform import (
    create_final_data,
    is_valid_record,
    transform_record,
    load_entity_mappings,
)
from leetcomp.utils import last_fetched_info, get_provider_info


def cleanup_temp_files():
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
    if os.path.exists(PARSED_TEMP_FILE):
        os.remove(PARSED_TEMP_FILE)


def generate_sync_report(till_id: int | None) -> str | None:
    raw_posts: dict[int, dict] = {}
    with open(POSTS_FILE, "r") as f:
        for line in f:
            post = json.loads(line)
            if till_id is not None and post["id"] == till_id:
                break
            raw_posts[post["id"]] = post

    if not raw_posts:
        print("No new posts to report")
        return None

    # load parsed posts (id -> list of parsed offers)
    parsed_posts: dict[int, list[dict]] = {}
    with open(PARSED_FILE, "r") as f:
        for line in f:
            parsed = json.loads(line)
            if till_id is not None and parsed["id"] == till_id:
                break
            post_id = parsed["id"]
            if post_id not in parsed_posts:
                parsed_posts[post_id] = []
            parsed_posts[post_id].append(parsed)

    # load entity mappings for transform
    entity_map = load_entity_mappings(["company", "role", "location"])

    # find records that made it to final, grouped by post
    # structure: {post_id: {"raw": raw_post, "offers": [list of final records]}}
    posts_with_offers: dict[int, dict] = {}
    total_offers_added = 0

    for post_id, offers in parsed_posts.items():
        if post_id not in raw_posts:
            continue
        valid_offers = []
        for parsed in offers:
            valid, _ = is_valid_record(parsed)
            if valid:
                valid_offers.append(transform_record(parsed, entity_map))
                total_offers_added += 1
        if valid_offers:
            posts_with_offers[post_id] = {
                "raw": raw_posts[post_id],
                "offers": valid_offers,
            }

    # generate markdown report
    total_new_posts = len(raw_posts)
    total_posts_with_offers = len(posts_with_offers)

    lines = [
        f"# Sync Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"**{total_new_posts} new posts found, {total_posts_with_offers} posts with {total_offers_added} offers added**",
        "",
        "---",
        "",
    ]

    for i, (post_id, data) in enumerate(posts_with_offers.items(), 1):
        raw = data["raw"]
        offers = data["offers"]

        lines.extend(
            [
                f"## {i}. {raw['title']}",
                "",
                "### Raw Content",
                "```",
                raw.get("content", "No content"),
                "```",
                "",
                "### Parsed Offers",
                "",
                "| Company | Role | YoE | Base | Total | Location |",
                "|---------|------|-----|------|-------|----------|",
            ]
        )

        for offer in offers:
            lines.append(
                f"| {offer['company']} | {offer['role']} | {offer.get('yoe') or '-'} | {offer.get('base') or '-'} | {offer.get('total') or '-'} | {offer.get('location') or '-'} |"
            )

        lines.extend(["", "---", ""])

    # write report
    report_path = f"{DATA_DIR}/sync_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Sync report saved to {report_path}")
    return report_path


def sync() -> None:
    # fetch new posts (till the latest fetched id)
    print("Syncing posts...")
    fetch_till_post_id, fetch_till_timestamp = last_fetched_info(POSTS_FILE)
    if fetch_till_post_id:
        print(f"Fetching till post id: {fetch_till_post_id}")
    if fetch_till_timestamp:
        print(f"Or till timestamp: {fetch_till_timestamp}")
    asyncio.run(
        fetch_posts_in_bulk(
            till_id=fetch_till_post_id, till_timestamp=fetch_till_timestamp
        )
    )

    # enrich and normalise the posts (for ui)
    print("\nParsing posts...")
    fetch_till_post_id, fetch_till_timestamp = last_fetched_info(PARSED_FILE)
    if fetch_till_post_id:
        print(f"Parsing till post id: {fetch_till_post_id}")
    if fetch_till_timestamp:
        print(f"Or till timestamp: {fetch_till_timestamp}")
    parse_posts_with_llm(POSTS_FILE, fetch_till_post_id, fetch_till_timestamp)

    # normalize entities (only new ones)
    print("\nNormalizing entities...")
    provider, url, model = get_provider_info()
    print(f"Using LLM provider: {provider}, model: {model}")
    normalize_and_save(PARSED_FILE, fetch_till_post_id, fetch_till_timestamp)

    # create final data for UI
    print("\nCreating final data...")
    create_final_data(PARSED_FILE, FINAL_DATA_FILE)

    # generate sync report for new records
    print("\nGenerating sync report...")
    generate_sync_report(fetch_till_post_id)

    cleanup_temp_files()


if __name__ == "__main__":
    sync()
