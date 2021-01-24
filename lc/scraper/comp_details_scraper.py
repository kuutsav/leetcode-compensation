import json
import time
from typing import Dict, List

from loguru import logger
from selenium import webdriver

from utils.constant import BROWSER_EXEC_PATH, DATA_DIR


browser = webdriver.Chrome(executable_path=BROWSER_EXEC_PATH)


def _get_post_details(browser: webdriver.Chrome) -> List[Dict[str, str]]:
    """Posts from selenium browser element.

    Args:
        browser (webdriver.Chrome): Selenium webdriver.
    """
    elem = browser.find_elements_by_class_name("content-area__2vnF")
    post_text = "\n".join([e.text for e in elem])
    return post_text


def get_compenstation_post_details(url: str) -> str:
    """Details from the compensation post.

    Args:
        url (str): `url` of the post.

    Returns:
        dict: Post details.
    """
    try:
        browser.get(url)
        time.sleep(5)
        post_text = _get_post_details(browser)
        if not post_text:
            time.sleep(2)
            logger.info(f"sleeping extra for {url}")
            post_text = _get_post_details(browser)
        if post_text:
            with open(DATA_DIR + f"{url.split('/')[-2]}.json", "w") as f:
                json.dump({"text": post_text}, f)
            return post_text
        else:
            logger.warning(f"ERR_URL - {url}")
            return ""
    except Exception as e:
        logger.error(f"ERR: {e}")
        raise Exception(e)
    return ""
