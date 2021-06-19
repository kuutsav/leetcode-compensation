import time
from typing import List, Dict

from loguru import logger
from selenium import webdriver


browser = webdriver.Chrome(
    executable_path="/Users/kuutsav/Documents/leetcode-compensation/chromedriver"
)


def get_compensation_posts(url: str) -> List[Dict[str, str]]:
    """Compensation posts from the current page.

    Args:
        url (str): A compensation page.
    """
    try:
        browser.get(url)
        time.sleep(5)
        elem = browser.find_elements_by_class_name("title-link__1ay5")
        post_hrefs = [
            {"title": e.text, "href": e.get_attribute("href")} for e in elem
        ]
        if not post_hrefs:
            time.sleep(10)
            logger.info(f"sleeping extra for {url}")
            post_hrefs = [
                {"title": e.text, "href": e.get_attribute("href")} for e in elem
            ]
        return post_hrefs
    except Exception as e:
        logger.error(f"ERR: {e}")
        raise Exception(e)
    return []
