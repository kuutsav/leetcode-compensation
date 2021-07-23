BROWSER_EXEC_PATH = (
    "/Users/kuutsav/Documents/leetcode-compensation/chromedriver"
)

DATA_DIR = "data/posts/"
STATS_DIR = "data/stats/"
NER_DATA_DIR = "data/ner/"
MAPPING_DIR = "data/mappings/"

URL = "https://leetcode.com/discuss/compensation?currentPage={}&orderBy=newest_to_oldest&query="

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
    "^(\~\s?)?(?P<years>\d{1,2}(\.\d{1,2})?)\s?\+?$",
    "^(\~\s?)?(?P<years>\d{1,2}(\.\d{1,2})?)\+?\s?(years|year|yrs|yr|yoe|y)((\sand)? (?P<months>\d{1,2})\s?(months?|m))?",
    "^(?P<months>\d{1,2}) (months?)",
]
