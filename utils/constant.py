BROWSER_EXEC_PATH = (
    "/Users/kuutsav/Documents/leetcode-compensation/chromedriver"
)

TOTAL_RETRIES = 3
LAST_PAGE_NO = 274

POSTS_META_FNAME = "posts_meta"

DATA_DIR = "data/posts/"
META_DIR = "data/meta/"
MAPPING_DIR = "data/mappings/"

LEETCODE_COMPENSATIONS_URL = "https://leetcode.com/discuss/compensation?currentPage={}&orderBy=newest_to_oldest&query="
LEETCODE_POSTS_URL = "https://leetcode.com/discuss/compensation/{}"

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

YOE_SPECIFICATION = [
    r"^(\~\s?)?(?P<years>\d{1,2}(\.\d{1,2})?)\s?\+?$",
    r"^(\~\s?)?(?P<years>\d{1,2}(\.\d{1,2})?)\+?\s?(years|year|yrs|yr|yoe|y)((\sand)? (?P<months>\d{1,2})\s?(months?|m))?",
    r"^(?P<months>\d{1,2}) (months?)",
]
