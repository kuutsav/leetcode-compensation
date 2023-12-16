from pathlib import Path
import re

POSTS_TO_DROP = ["884535"]
MISSING_TEXT = "n/a"
MISSING_NUMERIC = -1
OUTPUT_DATE_FMT = "%Y/%m/%d"
DEFAULT_POST_DATE = "1900/01/01"
TOTAL_RETRIES = 3
LAST_PAGE_NO = 500

DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / ".cache"
POSTS_DIR = DATA_DIR / "posts"
POSTS_METADATA_F = DATA_DIR / "meta/posts_meta.json"
MAPPINGS_DIR = DATA_DIR / "mappings"
OUTPUT_DIR = DATA_DIR / "out"
IMGS_DIR = DATA_DIR / "imgs"
REPORTS_DIR = DATA_DIR / "reports"

LEETCODE_COMPENSATIONS_URL = "https://leetcode.com/discuss/compensation?currentPage={}&orderBy=newest_to_oldest&query="
LEETCODE_POSTS_URL = "https://leetcode.com/discuss/compensation/{}"

LABEL_SPECIFICATION = {
    "RE_COMPANY_PRIMARY": re.compile(r"company\s?[:-]-?\s?(?P<label>[&\w\.\-\(\)\, ]+)"),
    "RE_COMPANY_SECONDARY": re.compile(r"\scompany (?P<label>[&\w\.\- ]+)"),
    "RE_TITLE": re.compile(r"title\s?(/level)?\s?[:-]-?\s?(?P<label>[&\w\.\-\/\+\# ]+)"),
    "RE_YOE": re.compile(r"((yrs|years\sof\s)(experience|exp)|yoe)\s?[:-]-?\s?(?P<label>[\w\.\+\~\-\, ]+)"),
    "RE_SALARY": re.compile(r"(salary|base|base pay)\s?[:-]-?\s?(?P<label>[\w\,\₹\$\.\/\- ]+)\s"),
    "RE_LOCATION": re.compile(r"\slocation\s?[:-]-?\s?(?P<label>[\w\, ]+)"),
    "RE_SALARY_TOTAL": re.compile(
        r"\ntot?al (1st year\s)?(comp[e|a]nsation|comp|ctc)(\sfor 1st year)?(\s?\(\s?(salary|base).+?\))?(?P<label>.+)"
    ),
}

YOE_SPECIFICATION = [
    (re.compile(r"^((?P<years>\d{1,2}(\.\d{1,2})?)(years?|yrs?))?((?P<months>\d{1,2})(months?|mnths?|m))"), 1),
    (re.compile(r"^(?P<years>\d{1,2}(\.\d{1,2})?)(years?|yrs?|yoe)"), 1),
    (re.compile(r"^almost(?P<years>\d{1,2}(\.\d{1,2})?)"), 1),
    (re.compile(r"(?P<years>fresh*|none|nil|na|newgrad|nofulltime|202[01]graduate)"), 0),
    (re.compile(r"^(?P<weeks>\d{1,2})(weeks)"), 0),
    (re.compile(r"^(?P<years>\d{1,2}(\.\d{1,2})?)"), 1),
]

TOTAL_SALARY_SPECIFICATION = [
    (re.compile(r"\d{6,8}"), 1),
    (re.compile(r"(\d{1,3}\.\d{1,3})(lpa|lacks|l)"), 100000),
    (re.compile(r"(\d{1,3})(lpa|lacks|l)"), 100000),
]

# fmt: off
SALARY_SPECIFICATION = [
    (re.compile(r"(?P<per_month>([\w\.\s]+)(month|pm|p\.m\.?))$"), 1),
    (re.compile(r"(inr\.?|rs\.?|ctc|base)?(?P<lakhs>\d{1,2}(\.\d{1,2})?)(lpa|lakhs?|lacs?|l|base|basepay|fixed)"), 100000),
    (re.compile(r"(inr\.?|rs\.?|ctc|base)?(?P<lakhs>\d{6,7}(\.\d{1,2})?)(\-)?(lpa|lakhs?|lacs?|base|perannum|ctc|fixed|rupees|peranum|peryear)"), 1),
    (re.compile(r"^(inr\.?|rs\.?|ctc|base)?(?P<lakhs>\d{6,7}(\.\d{1,2})?)(\-)?$"), 1),
    (re.compile(r"^(?P<lakhs>\d{6,7})(\-)?(inr\.?|rs\.?|ctc|base)?$"), 1),
    (re.compile(r"^(?P<lakhs>\d{1,2}(\.\d{1,2})?)$"), 100000),
    (re.compile(r"(?P<lakhs>[1-9]?\d0{5})"), 1),
]
# fmt: on
