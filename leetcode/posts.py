import argparse
from datetime import datetime, timedelta
import json
import os
import time

from loguru import logger
from selenium import webdriver

from leetcode.scraper import compensation_post_text, compensation_posts
from leetcode.utils.commons import load_json, save_json
from leetcode.utils.constants import (
    CACHE_DIR,
    DEFAULT_POST_DATE,
    LAST_PAGE_NO,
    LEETCODE_POSTS_URL,
    OUTPUT_DATE_FMT,
    POSTS_DIR,
    POSTS_METADATA_F,
    TOTAL_RETRIES,
)

driver = webdriver.Chrome()


def datetime_from_posts_date(date: str) -> str:
    if ":" in date:
        return datetime.strptime(date, "%B %d, %Y %I:%M %p").strftime(OUTPUT_DATE_FMT)
    elif "ago" in date:
        if "hour" in date or "minute" in date:
            return datetime.now().strftime(OUTPUT_DATE_FMT)
        else:
            n_days_ago = date.split(" ")[0]
            n_days_ago = 1 if n_days_ago == "a" else int(n_days_ago)
            return (datetime.now() - timedelta(days=n_days_ago)).strftime(OUTPUT_DATE_FMT)

    return DEFAULT_POST_DATE


def page_metadata_in_cache(page_no: int) -> bool:
    return os.path.exists(CACHE_DIR / f"page_{page_no}_meta.json")


def page_metadata_from_cache(page_no: int) -> list[dict[str, str]]:
    return load_json(CACHE_DIR / f"page_{page_no}_meta.json")


def cache_page_metadata(page_no: int, page_metadata: list[dict[str, str]]) -> None:
    save_json(page_metadata, CACHE_DIR / f"page_{page_no}_meta.json")


def post_in_cache(post_id: str) -> bool:
    return os.path.exists(CACHE_DIR / f"{post_id}.txt")


def post_from_cache(post_id: str) -> str:
    return load_json(CACHE_DIR / f"{post_id}.txt")


def cache_post(post_id: str, post: str) -> None:
    save_json(post, CACHE_DIR / f"{post_id}.txt")


def posts_metadata_by_page(page_no: int) -> list[dict[str, str]]:
    nth_try, page_posts_metadata = 1, []

    while nth_try < TOTAL_RETRIES and not page_posts_metadata:
        time.sleep(0.5 + nth_try)
        if page_metadata_in_cache(page_no):
            logger.info(f"metadata found in cache, page no: {page_no}")
            return page_metadata_from_cache(page_no)
        page_posts_metadata = compensation_posts(page_no)
        if not page_posts_metadata:
            logger.warning(f"retrying page: {page_no} [try-no-{nth_try}]")
        else:
            cache_page_metadata(page_no, page_posts_metadata)
        nth_try += 1
    if not page_posts_metadata:
        logger.error(f"failed page: {page_no}")

    return page_posts_metadata


def posts_metadata(till_date: str) -> list[dict[str, str]]:
    page_no, posts_metadata = 1, []

    while page_no < LAST_PAGE_NO:
        logger.info(f"fetching posts metadata, page no: {page_no}")
        page_posts_metadata = posts_metadata_by_page(page_no)
        for metadata in page_posts_metadata:
            metadata["page_no"] = page_no
        posts_metadata += page_posts_metadata

        page_no += 1

        if posts_metadata:
            last_date = datetime_from_posts_date(posts_metadata[-1]["date"])
            if last_date < till_date:
                break

    return posts_metadata


def load_metadata() -> list[dict[str, str]]:
    with open(POSTS_METADATA_F, "r") as f:
        posts_metadata = json.load(f)
    return posts_metadata


def save_metadata(posts_metadata: list[dict[str, str]]) -> None:
    with open(POSTS_METADATA_F, "w") as f:
        json.dump(posts_metadata, f)


def update_posts_metadata(new_posts_metadata: list[dict[str, str]]) -> None:
    if os.path.exists(POSTS_METADATA_F):
        posts_metadata = load_metadata()
        posts_metadata.update({post["post_id"]: post for post in new_posts_metadata})
        save_metadata(posts_metadata)
    else:
        save_metadata({post["post_id"]: post for post in new_posts_metadata})


def post_text(post_id: str) -> str:
    nth_try, post_text = 1, ""

    while nth_try < TOTAL_RETRIES and not post_text:
        time.sleep(0.5 + nth_try)
        post_text = compensation_post_text(LEETCODE_POSTS_URL.format(post_id))
        if not post_text:
            logger.warning(f"retrying post: {post_id} [try-no-{nth_try}]")
        nth_try += 1
    if not post_text:
        logger.error(f"failed post: {post_id}")

    return post_text


def get_and_save_posts(post_ids: list[str]) -> None:
    for post_id in post_ids:
        logger.info(f"fetching post text: {post_id}")
        if post_in_cache(post_id):
            logger.info(f"post found in cache, post id: {post_id}")
            text = post_from_cache(post_id)
        else:
            text = post_text(post_id)
            cache_post(post_id, text)
        with open(POSTS_DIR / f"{post_id}.txt", "w") as f:
            f.write(text)


if __name__ == "__main__":
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument("--till_date", type=str, help="Date(Y/m/d) till we need to fetch the posts info")
    my_parser.add_argument(
        "--posts_meta", type=str, default="T", help="Fetch posts metadata if True else fetch posts text"
    )
    args = my_parser.parse_args()
    fetch_only_posts_meta = args.posts_meta.lower()[0] == "t"

    if fetch_only_posts_meta:
        if not args.till_date:
            raise ValueError("--till_date arg is needed to fetch posts metadata")
        logger.info(f"fetching posts metadata till date: {args.till_date}")
        new_posts_metadata = posts_metadata(till_date=args.till_date)
        logger.info(f"updating posts metadata: {len(new_posts_metadata)} new records")
        update_posts_metadata(new_posts_metadata)

    else:
        logger.info("fetching updated posts texts")
        updated_posts_metadata = load_metadata()
        old_posts = set([str(f.split(".")[0]) for f in os.listdir(POSTS_DIR)])
        missing_post_ids = [p for p in updated_posts_metadata if p not in old_posts]
        logger.info(f"# updated posts: {len(updated_posts_metadata)} # missing posts: {len(missing_post_ids)}")

        get_and_save_posts(missing_post_ids)
