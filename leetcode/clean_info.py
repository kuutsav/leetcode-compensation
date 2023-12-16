import re

from leetcode.utils.commons import load_json
from leetcode.utils.constants import (
    MAPPINGS_DIR,
    MISSING_NUMERIC,
    MISSING_TEXT,
    SALARY_SPECIFICATION,
    TOTAL_SALARY_SPECIFICATION,
    YOE_SPECIFICATION,
)

company_mapping = load_json(MAPPINGS_DIR / "lc_company.json")
title_mapping = load_json(MAPPINGS_DIR / "lc_title.json")
location_mapping = load_json(MAPPINGS_DIR / "lc_location.json")


def clean_text(text: str) -> str:
    return "".join(re.findall(r"\w+", text))


def clean_company(company_text: str) -> str:
    return company_mapping.get(clean_text(company_text), {"company": MISSING_TEXT})["company"]


def clean_title(title_text: str) -> str:
    return title_mapping.get(clean_text(title_text), {"title": MISSING_TEXT})["title"]


def clean_location(location_text: str) -> str:
    clean_loc = clean_text(location_text)
    if clean_loc in location_mapping:
        if location_mapping[clean_loc]["in_india"]:
            loc = location_mapping[clean_loc]["location"]
            return "india" if loc == MISSING_TEXT else loc
    elif "india" in clean_loc.lower():
        return "india"
    return MISSING_TEXT


def _clean_yoe(yoe_text: str) -> str:
    return "".join(re.findall(r"\w[\w\.\-\~\+]*", yoe_text))


def clean_yoe(yoe_text: str) -> float:
    clean_yoe_text = _clean_yoe(yoe_text)
    for pattern, is_numeric_year in YOE_SPECIFICATION:
        match = re.match(pattern, clean_yoe_text)
        if match:
            if not is_numeric_year:
                try:
                    return float(match.group("weeks")) / (4 * 12)
                except Exception:
                    return 0
            years = float(match.group("years")) if match.group("years") else 0
            try:
                years += float(match.group("months")) / 12
            except Exception:
                pass
            return years
    return MISSING_NUMERIC


def _clean_salary(salary_text: str) -> str:
    return "".join(re.findall(r"[\w\.\-]", salary_text))


def clean_salary(salary_text: str) -> float:
    clean_salary_text = _clean_salary(salary_text)
    for pattern, lakhs_multiplier in SALARY_SPECIFICATION:
        match = re.match(pattern, clean_salary_text)
        if match:
            try:
                return float(match.group("lakhs")) * lakhs_multiplier
            except Exception:
                # per month (internships, etc.)
                pass
            break
    return MISSING_NUMERIC


def clean_salary_total(salary_total_text: str) -> float:
    salary_total_text = salary_total_text.replace(",", "").replace(" ", "")
    for pattern, lakhs_multiplier in TOTAL_SALARY_SPECIFICATION:
        match = re.findall(pattern, salary_total_text)
        if match:
            salary = match[-1]
            salary = float(salary) if isinstance(salary, str) else float(salary[0]) * lakhs_multiplier
            return salary
    return MISSING_NUMERIC
