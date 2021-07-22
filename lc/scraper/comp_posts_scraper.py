import time
from typing import List, Dict

from loguru import logger
from selenium import webdriver

from utils.constant import BROWSER_EXEC_PATH


browser = webdriver.Chrome(executable_path=BROWSER_EXEC_PATH)


def _get_posts(browser: webdriver.Chrome) -> List[Dict[str, str]]:
    """Posts from selenium browser element.

    Args:
        browser (webdriver.Chrome): Selenium webdriver.
    """
    post_hrefs = []
    for e in browser.find_elements_by_class_name("topic-title-wrapper__27Nt"):
        for e_url, e_time in zip(
            e.find_elements_by_class_name("title-link__1ay5"),
            e.find_elements_by_class_name("topic-info__tdz0"),
        ):
            post_hrefs.append(
                {
                    "post_id": e_url.get_attribute("href").split("/")[-2],
                    "text": e_url.text,
                    "href": e_url.get_attribute("href"),
                    "time": e_time.text,
                }
            )
    return post_hrefs


def get_compensation_posts(url: str) -> List[Dict[str, str]]:
    """Compensation posts from the current page.

    Args:
        url (str): A compensation page.
    """
    try:
        browser.get(url)
        time.sleep(5)
        post_hrefs = _get_posts(browser)
        if not post_hrefs:
            time.sleep(10)
            logger.info(f"sleeping extra for {url}")
            post_hrefs = _get_posts(browser)
        return post_hrefs
    except Exception as e:
        logger.error(f"ERR: {e}")
        raise Exception(e)
    return []
