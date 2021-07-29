import argparse
from datetime import datetime
import json
from pathlib import Path
import time

from loguru import logger

from lc.scraper.post_meta_scraper import (
    driver,
    get_compensation_posts,
)
from utils.constant import (
    LAST_PAGE_NO,
    META_DIR,
    POSTS_META_FNAME,
    TOTAL_RETRIES,
)
from utils.utils import get_datetime_from_date

logger.add(f"data/logs/{POSTS_META_FNAME}.log")

my_parser = argparse.ArgumentParser()
my_parser.add_argument("--till_date", type=str, required=True)
args = my_parser.parse_args()
till_datetime = datetime.strptime(args.till_date, "%Y/%m/%d")


# get all the meta info from leetcode compensations page.
all_posts = []
page_no = 1
while True and page_no <= LAST_PAGE_NO:
    posts = get_compensation_posts(page_no)
    if not posts:
        logger.warning(f"sleeping extra for page no: {page_no}")
        sleep_for = 0.5
        n_tries = 0
        while not posts and n_tries < TOTAL_RETRIES:
            time.sleep(sleep_for)
            posts = get_compensation_posts(page_no)
            sleep_for += 0.5
            n_tries += 1
        if not posts:
            logger.error(f"failed page no: {page_no}")
            page_no += 1
            continue
    logger.info(f"page no: {page_no} | # posts: {len(posts)}")
    for p in posts:
        p["page_no"] = page_no
    all_posts += posts
    last_date = get_datetime_from_date(posts[-1]["date"])
    if last_date < till_datetime:
        break
    page_no += 1


# save data
posts_meta_path = Path(META_DIR) / f"{POSTS_META_FNAME}.json"
if posts_meta_path.exists():
    with open(posts_meta_path, "r") as f:
        data = json.load(f)
    with open(posts_meta_path, "w") as f:
        data.update({post["post_id"]: post for post in all_posts})
        json.dump(data, f)
else:
    with open(posts_meta_path, "w") as f:
        json.dump({post["post_id"]: post for post in all_posts}, f)


driver.__exit__()
