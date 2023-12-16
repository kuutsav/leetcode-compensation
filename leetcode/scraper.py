from __future__ import annotations

import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from leetcode.utils.constants import LEETCODE_COMPENSATIONS_URL

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)


def _post_info(href_obj, time_obj) -> dict[str, str]:
    href = href_obj.get_attribute("href")
    return {
        "post_id": href.split("/")[-2],
        "href": href,
        "title": href_obj.text,
        "date": re.findall(r"created at: (.+)(?=\|)", time_obj.text)[0].strip(),
    }


def _parsed_posts(driver) -> list[dict[str, str]]:
    posts_info = []
    for e in driver.find_elements(By.CLASS_NAME, "topic-title-wrapper__27Nt"):
        for e_url, e_time in zip(
            e.find_elements(By.CLASS_NAME, "title-link__1ay5"), e.find_elements(By.CLASS_NAME, "topic-info__tdz0")
        ):
            posts_info.append(_post_info(e_url, e_time))
    return posts_info


def compensation_posts(page_no: int) -> list[dict[str, str]]:
    driver.get(LEETCODE_COMPENSATIONS_URL.format(page_no))
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "topic-title-wrapper__27Nt")))
    driver.execute_script("window.stop();")
    return _parsed_posts(driver)


def compensation_post_text(url: str) -> str:
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "content-area__2vnF")))
    driver.execute_script("window.stop();")
    elem = driver.find_elements(By.CLASS_NAME, "content-area__2vnF")
    post_text = "\n".join([e.text for e in elem])
    return post_text
