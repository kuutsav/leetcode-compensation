from functools import lru_cache

from bs4 import BeautifulSoup
from loguru import logger
import requests
from requests.exceptions import HTTPError


URL = "https://leetcode.com/discuss/compensation?currentPage=1&orderBy=hot&query="


def get_compensation_posts(url: str):
    """Compensation posts from the current page.

    Args:
        url (str): A compensation page.
    """
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.text
    except HTTPError as http_err:
        logger.error(f"HTTP_ERR: {http_err}")
        raise HTTPError(http_err)
    except Exception as e:
        logger.error(f"ERR: {e}")
        raise Exception(e)


if __name__ == "__main__":
    print(get_compensation_posts(URL))
