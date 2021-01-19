import argparse
import json
from typing import Tuple

from loguru import logger

from lc.scraper.comp_posts_scraper import get_compensation_posts
from lc.scraper.comp_details_scraper import get_compenstation_post_details
from utils.constant import STATS_DIR, URL


def get_comps(page_range: Tuple[int, int]):
    """Get compensation details.

    Args:
        page_range (Tuple): Range of compensation pages.
    """
    success_stats = {}
    posts = []
    for page_ix in range(*page_range):
        url = URL.format(page_ix)
        success_stats[page_ix] = {"n_posts": 0, "n_success": 0}
        post_hrefs = get_compensation_posts(url)
        if post_hrefs:
            logger.info(f"{url} - {len(post_hrefs)} posts")
            success_stats[page_ix]["n_posts"] = len(post_hrefs)
            posts += post_hrefs
        else:
            logger.warning(f"ERR_URL - {url}")
            continue
        for href in post_hrefs:
            post_text = get_compenstation_post_details(href["href"])
            if post_text:
                success_stats[page_ix]["n_success"] += 1
        logger.info(f"page: {page_ix} | {success_stats[page_ix]}")
        with open(STATS_DIR + "post_meta.json", "w") as f:
            json.dump(posts, f)

        # store stats
        with open(STATS_DIR + "post_stats.json", "w") as f:
            json.dump(success_stats, f)


if __name__ == "__main__":
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('--start_page', type=int, required=True)
    my_parser.add_argument('--end_page', type=int, required=True)
    args = my_parser.parse_args()
    get_comps((args.start_page, args.end_page))
