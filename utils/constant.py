from loguru import logger

import os
import re

UTILS_PATH = os.path.dirname(os.path.realpath(__file__))
BROWSER_EXEC_PATH = f"{UTILS_PATH}/chromedriver"
if not os.path.exists(BROWSER_EXEC_PATH):
    logger.error("chromedriver not present in utils path")
    raise FileNotFoundError("chromedriver not present in the utils path")

MISSING_TEXT = "n/a"
TOTAL_RETRIES = 3
LAST_PAGE_NO = 274

POSTS_META_FNAME = "posts_meta"

DATA_DIR = "data/posts/"
META_DIR = "data/meta/"
MAPPING_DIR = "data/mappings/"
OUT_DIR = "data/out/"

LEETCODE_COMPENSATIONS_URL = "https://leetcode.com/discuss/compensation?currentPage={}&orderBy=newest_to_oldest&query="
LEETCODE_POSTS_URL = "https://leetcode.com/discuss/compensation/{}"

LABEL_SPECIFICATION = {
    "RE_COMPANY_PRIMARY": re.compile(
        r"company\s?[:-]-?\s?(?P<label>[&\w\.\-\(\)\, ]+)"
    ),
    "RE_COMPANY_SECONDARY": re.compile(r"\scompany (?P<label>[&\w\.\- ]+)"),
    "RE_TITLE": re.compile(
        r"title\s?(/level)?\s?[:-]-?\s?(?P<label>[&\w\.\-\/\+\# ]+)"
    ),
    "RE_YOE": re.compile(
        r"((yrs|years\sof\s)(experience|exp)|yoe)\s?[:-]-?\s?(?P<label>[\w\.\+\~\-\, ]+)"
    ),
    "RE_SALARY": re.compile(
        r"(salary|base|base pay)\s?[:-]-?\s?(?P<label>[\w\,\₹\$\.\/\- ]+)\s"
    ),
    "RE_LOCATION": re.compile(r"\slocation\s?[:-]-?\s?(?P<label>[\w\, ]+)"),
}
YOE_SPECIFICATION = [
    re.compile(r"^(\~\s?)?(?P<years>\d{1,2}(\.\d{1,2})?)\s?\+?$"),
    re.compile(
        r"^(\~\s?)?(?P<years>\d{1,2}(\.\d{1,2})?)\+?\s?(years|year|yrs|yr|yoe|y)((\sand)? (?P<months>\d{1,2})\s?(months?|m))?"
    ),
    re.compile(r"^(?P<months>\d{1,2}) (months?)"),
]

MIN_SALARY = 250000
MAX_BASE_LPA = 100
MAX_SALARY = MAX_BASE_LPA * 100000
MONTHLY_SALARY_INDICATORS = [
    "per month",
    "pm",
    "p.m",
    "p.m.",
    "/month",
    "/ month",
]
