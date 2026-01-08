import asyncio
import os

from leetcomp import PARSED_FILE, PARSED_TEMP_FILE, POSTS_FILE, TEMP_FILE, FINAL_DATA_FILE
from leetcomp.fetch import fetch_posts_in_bulk
from leetcomp.parse import parse_posts_with_llm
from leetcomp.normalize import normalize_all_entities
from leetcomp.transform import create_final_data
from leetcomp.utils import last_fetched_id


def cleanup_temp_files():
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
    if os.path.exists(PARSED_TEMP_FILE):
        os.remove(PARSED_TEMP_FILE)


def sync() -> None:
    # fetch new posts (till the latest fetched id)
    print("Syncing posts...")
    fetch_till_post_id = last_fetched_id(POSTS_FILE)
    if fetch_till_post_id:
        print(f"Fetching till post id: {fetch_till_post_id}")
    asyncio.run(fetch_posts_in_bulk(till_id=fetch_till_post_id))

    # enrich and normalise the posts (for ui)
    print("\nParsing posts...")
    fetch_till_post_id = last_fetched_id(PARSED_FILE)
    if fetch_till_post_id:
        print(f"Parsing till post id: {fetch_till_post_id}")
    parse_posts_with_llm(POSTS_FILE, fetch_till_post_id)

    # normalize entities
    print("\nNormalizing entities...")
    normalize_all_entities(PARSED_FILE)

    # create final data for UI
    print("\nCreating final data...")
    create_final_data(PARSED_FILE, FINAL_DATA_FILE)

    cleanup_temp_files()


if __name__ == "__main__":
    sync()
