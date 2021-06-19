import time

from loguru import logger
from selenium import webdriver


browser = webdriver.Chrome(
    executable_path="/Users/kuutsav/Documents/leetcode-compensation/chromedriver"
)
data_dir = "posts/"


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
        elem = browser.find_elements_by_class_name("content-area__2vnF")
        post_text = "\n".join([e.text for e in elem])
        if not post_text:
            time.sleep(2)
            logger.info(f"sleeping extra for {url}")
            elem = browser.find_elements_by_class_name("content-area__2vnF")
            post_text = "\n".join([e.text for e in elem])
        if post_text:
            with open(data_dir + f"{url.split('/')[-2]}.txt", "w") as f:
                f.write(post_text)
            return post_text
        else:
            logger.warning(f"ERR_URL - {url}")
            return ""
    except Exception as e:
        logger.error(f"ERR: {e}")
        raise Exception(e)
    return ""
