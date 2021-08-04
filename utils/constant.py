from loguru import logger

import os
import re

UTILS_PATH = os.path.dirname(os.path.realpath(__file__))
BROWSER_EXEC_PATH = f"{UTILS_PATH}/chromedriver"
if not os.path.exists(BROWSER_EXEC_PATH):
    logger.error("chromedriver not present in utils path")
    raise FileNotFoundError("chromedriver not present in the utils path")

MISSING_TEXT = "n/a"
MISSING_NUMERIC = -1
OUT_DATE_FORMAT = "%Y/%m/%d"
TOTAL_RETRIES = 3
LAST_PAGE_NO = 274

POSTS_META_FNAME = "posts_meta"

DATA_DIR = "data/posts/"
META_DIR = "data/meta/"
MAPPING_DIR = "data/mappings/"
OUT_DIR = "data/out/"
IMGS_DIR = "data/imgs/"
REPORTS_DIR = "data/reports/"

LEETCODE_COMPENSATIONS_URL = "https://leetcode.com/discuss/compensation?currentPage={}&orderBy=newest_to_oldest&query="
LEETCODE_POSTS_URL = "https://leetcode.com/discuss/compensation/{}"

LABEL_SPECIFICATION = {
    "RE_COMPANY_PRIMARY": re.compile(r"company\s?[:-]-?\s?(?P<label>[&\w\.\-\(\)\, ]+)"),
    "RE_COMPANY_SECONDARY": re.compile(r"\scompany (?P<label>[&\w\.\- ]+)"),
    "RE_TITLE": re.compile(r"title\s?(/level)?\s?[:-]-?\s?(?P<label>[&\w\.\-\/\+\# ]+)"),
    "RE_YOE": re.compile(r"((yrs|years\sof\s)(experience|exp)|yoe)\s?[:-]-?\s?(?P<label>[\w\.\+\~\-\, ]+)"),
    "RE_SALARY": re.compile(r"(salary|base|base pay)\s?[:-]-?\s?(?P<label>[\w\,\₹\$\.\/\- ]+)\s"),
    "RE_LOCATION": re.compile(r"\slocation\s?[:-]-?\s?(?P<label>[\w\, ]+)"),
}

YOE_SPECIFICATION = [
    (re.compile(r"^((?P<years>\d{1,2}(\.\d{1,2})?)(years?|yrs?))?((?P<months>\d{1,2})(months?|mnths?|m))"), 1),
    (re.compile(r"^(?P<years>\d{1,2}(\.\d{1,2})?)(years?|yrs?|yoe)"), 1),
    (re.compile(r"^almost(?P<years>\d{1,2}(\.\d{1,2})?)"), 1),
    (re.compile(r"(?P<years>fresh*|none|nil|na|newgrad|nofulltime|202[01]graduate)"), 0),
    (re.compile(r"^(?P<weeks>\d{1,2})(weeks)"), 0),
    (re.compile(r"^(?P<years>\d{1,2}(\.\d{1,2})?)"), 1)
]

SALARY_SPECIFICATION = [
    (re.compile(r"(?P<per_month>([\w\.\s]+)(month|pm|p\.m\.?))$"), 1),
    (re.compile(r"(inr\.?|rs\.?|ctc|base)?(?P<lakhs>\d{1,2}(\.\d{1,2})?)(lpa|lakhs?|lacs?|l|base|basepay|fixed)"), 100000),
    (re.compile(r"(inr\.?|rs\.?|ctc|base)?(?P<lakhs>\d{6,7}(\.\d{1,2})?)(\-)?(lpa|lakhs?|lacs?|base|perannum|ctc|fixed|rupees|peranum|peryear)"), 1),
    (re.compile(r"^(inr\.?|rs\.?|ctc|base)?(?P<lakhs>\d{6,7}(\.\d{1,2})?)(\-)?$"), 1),
    (re.compile(r"^(?P<lakhs>\d{6,7})(\-)?(inr\.?|rs\.?|ctc|base)?$"), 1),
    (re.compile(r"^(?P<lakhs>\d{1,2}(\.\d{1,2})?)$"), 100000),
    (re.compile(r"(?P<lakhs>[1-9]?\d0{5})"), 1)
]

MIN_SALARY = 250_000
MAX_SALARY = 1_000_000
