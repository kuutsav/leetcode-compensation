import re
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.constant import BROWSER_EXEC_PATH, LEETCODE_COMPENSATIONS_URL

# stop loading the page when posts are available
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"

driver = webdriver.Chrome(
    executable_path=BROWSER_EXEC_PATH, desired_capabilities=capa
)
wait = WebDriverWait(driver, 20)


def _get_info_from_post(
    href_obj: webdriver.remote.webelement.WebElement,
    time_obj: webdriver.remote.webelement.WebElement,
) -> Dict[str, str]:
    """Information from post object for the `post` class.

    Args:
        href_obj ([webdriver.remote.webelement.WebElement]): Href object.
        time_obj ([webdriver.remote.webelement.WebElement]): Time object.

    Returns:
        Dict[str, str]: Meta information for a `post`.
    """
    href = href_obj.get_attribute("href")
    return {
        "post_id": href.split("/")[-2],
        "href": href,
        "title": href_obj.text,
        "date": re.findall(r"created at: (.+)(?=\|)", time_obj.text)[0].strip(),
    }


def _get_posts() -> List[Dict[str, str]]:
    """Posts from selenium browser element.

    Returns:
        List[Dict[str, str]]: Meta information from the `posts` from a
        `leetcode compensations` page.
    """
    post_hrefs = []
    for e in driver.find_elements_by_class_name("topic-title-wrapper__27Nt"):
        for e_url, e_time in zip(
            e.find_elements_by_class_name("title-link__1ay5"),
            e.find_elements_by_class_name("topic-info__tdz0"),
        ):
            post_hrefs.append(_get_info_from_post(e_url, e_time))
    return post_hrefs


def get_compensation_posts(page_no: int) -> List[Dict[str, str]]:
    """Compensation posts from the current page.

    Args:
        page_no (int): A `leetcode compensations` page.

    Returns:
        List[Dict[str, str]]: List of information from the `posts`.
    """
    driver.get(LEETCODE_COMPENSATIONS_URL.format(page_no))
    wait.until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "topic-title-wrapper__27Nt")
        )
    )
    driver.execute_script("window.stop();")
    return _get_posts()
