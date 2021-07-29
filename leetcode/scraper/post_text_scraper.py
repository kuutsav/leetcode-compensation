from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.constant import BROWSER_EXEC_PATH

# Stop loading the page when posts are available
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"

driver = webdriver.Chrome(
    executable_path=BROWSER_EXEC_PATH, desired_capabilities=capa
)
wait = WebDriverWait(driver, 20)


def get_text_from_post(url: str) -> str:
    """Text from the offer post.

    Args:
        driver (webdriver.Chrome): Selenium webdriver.
        url (str): A `leetcode compensations` offer post.

    Returns:
        str: Text from the post.
    """
    driver.get(url)
    wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "content-area__2vnF"))
    )
    driver.execute_script("window.stop();")
    elem = driver.find_elements_by_class_name("content-area__2vnF")
    post_text = "\n".join([e.text for e in elem])
    return post_text
