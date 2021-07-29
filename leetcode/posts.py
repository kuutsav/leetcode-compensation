import os
import json
import time

from loguru import logger

from lc.scraper.post_text_scraper import (
    driver,
    get_text_from_post,
)
from utils.constant import (
    DATA_DIR,
    LEETCODE_POSTS_URL,
    META_DIR,
    POSTS_META_FNAME,
    TOTAL_RETRIES,
)

logger.add("data/logs/posts.log")

# posts scraped already
posts = set([str(f.split(".")[0]) for f in os.listdir(DATA_DIR)])
with open(f"{META_DIR}/{POSTS_META_FNAME}.json", "r") as f:
    posts_meta = json.load(f)
# missing posts
missing_posts = [p for p in posts_meta if p not in posts]

# get all the posts info from leetcode compensations page.
all_posts = []
for post_id in missing_posts:
    url = LEETCODE_POSTS_URL.format(post_id)
    post_text = get_text_from_post(url)
    if not post_text:
        logger.warning(f"sleeping extra for post_id: {post_id}")
        sleep_for = 0.5
        n_tries = 0
        while not post_text and n_tries < TOTAL_RETRIES:
            time.sleep(sleep_for)
            post_text = get_text_from_post(url)
            sleep_for += 0.5
            n_tries += 1
        if not posts:
            logger.error(f"failed post_id: {post_id}")
            continue
    logger.info(f"post_id: {post_id} done!")

    with open(f"{DATA_DIR}/{post_id}.txt", "w") as f:
        f.write(post_text)

driver.__exit__()
