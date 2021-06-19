import json
from typing import Tuple

from loguru import logger

from lc.scraper.comp_posts_scraper import get_compensation_posts
from lc.scraper.comp_details_scraper import get_compenstation_post_details


stats_dir = "stats/"
URL = "https://leetcode.com/discuss/compensation?currentPage={}&orderBy=hot&query="
N_PAGES = 243


def get_comps(page_range: Tuple[int, int]):
    """Get compensation details.

    Args:
        page_range (Tuple): Range of compensation pages.
    """
    post_data = {}
    for page_ix in range(*page_range):
        url = URL.format(page_ix)
        post_data[page_ix] = {"n_posts": 0, "n_success": 0}
        post_hrefs = get_compensation_posts(url)
        if post_hrefs:
            logger.info(f"{url} - {len(post_hrefs)} posts")
            post_data[page_ix]["n_posts"] = len(post_hrefs)
        else:
            logger.warning(f"ERR_URL - {url}")
            continue
        for href in post_hrefs:
            post_text = get_compenstation_post_details(href["href"])
            if post_text:
                post_data[page_ix]["n_success"] += 1
        logger.info(f"page: {page_ix} | {post_data[page_ix]}")

    # store stats
    with open(stats_dir + "posts.json", "w") as f:
        json.dump(post_data, f)


if __name__ == "__main__":
    get_comps((1, N_PAGES + 1))
