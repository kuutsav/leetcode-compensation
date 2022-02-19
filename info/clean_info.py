import json
import re

from utils.constant import (
    MAPPING_DIR,
    MISSING_NUMERIC,
    MISSING_TEXT,
    SALARY_SPECIFICATION,
    TOTAL_SALARY_SPECIFICATION,
    YOE_SPECIFICATION
)

# mapping data
with open(f"{MAPPING_DIR}/lc_company.json", "r") as f:
    COMPANY_MAPPING = json.load(f)
with open(f"{MAPPING_DIR}/lc_title.json", "r") as f:
    TITLE_MAPPING = json.load(f)
with open(f"{MAPPING_DIR}/lc_location.json", "r") as f:
    LOCATION_MAPPING = json.load(f)


def get_clean_text(text: str) -> str:
    """Alphanumeric text for mapping.

    Args:
        text (str): Input text.

    Returns:
        str: Alphanumeric text.
    """
    return "".join(re.findall(r"\w+", text))


def get_clean_yoe(yoe_text: str) -> str:
    """Cleans the yoe text.
    
    Args:
        yoe_text (str): Raw yoe text.
    
    Returns:
        str: Clean yoe text.
    """
    return "".join(re.findall(r"\w[\w\.\-\~\+]*", yoe_text))


def get_clean_salary(salary_text: str) -> str:
    """Cleans the salary text.
    
    Args:
        salary_text (str): Raw salary text.
    
    Returns:
        str: Clean salary text.
    """
    return "".join(re.findall(r"[\w\.\-]", salary_text))


def clean_company(company_text: str) -> str:
    """Raw company standardization.

    Args:
        text (str): Raw company match.

    Returns:
        str: Final company string.
    """
    return COMPANY_MAPPING.get(
        get_clean_text(company_text), {"company": MISSING_TEXT}
    )["company"]


def clean_title(title_text: str) -> str:
    """Raw title standardization.

    Args:
        title_text (str): Raw title string.

    Returns:
        str: Final title string.
    """
    return TITLE_MAPPING.get(
        get_clean_text(title_text), {"title": MISSING_TEXT}
    )["title"]


def clean_location(location_text: str) -> str:
    """Raw location standardization.

    Args:
        location_text (str): Raw location string.

    Returns:
        str: Final location string.
    """
    clean_loc = get_clean_text(location_text)
    if clean_loc in LOCATION_MAPPING:
        if LOCATION_MAPPING[clean_loc]["in_india"]:
            loc = LOCATION_MAPPING[clean_loc]["location"]
            if loc == MISSING_TEXT:
                return "india"
            else:
                return loc
        else:
            return MISSING_TEXT
    elif "india" in clean_loc.lower():
        return "india"
    else:
        return MISSING_TEXT


def clean_yoe(yoe_text: str) -> float:
    """Raw yoe standardization.

    Args:
        yoe_text (str): Raw yoe string.

    Returns:
        float: Final yoe.
    """
    clean_yoe_text = get_clean_yoe(yoe_text)
    has_match = False
    for pattern, is_numeric_year in YOE_SPECIFICATION:
        match = re.match(pattern, clean_yoe_text)
        if match:
            has_match = True
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
    if not has_match:
        return MISSING_NUMERIC


def clean_salary(salary_text: str) -> float:
    """Raw salary standardization.

    Args:
        salary_text (str): Raw salary string.

    Returns:
        float: Final salary.
    """
    clean_salary_text = get_clean_salary(salary_text)
    has_match = False
    for pattern, lakhs_multiplier in SALARY_SPECIFICATION:
        match = re.match(pattern, clean_salary_text)
        if match:
            has_match = True
            try:
                return float(match.group("lakhs")) * lakhs_multiplier
            except Exception:
                # per month (internships, etc.)
                pass
            break
    return MISSING_NUMERIC


def clean_salary_total(salary_total_text: str) -> float:
    """Raw salary_total standardization.

    Args:
        salary_total_text (str): Raw salary_total string.

    Returns:
        float: Final salary_total.
    """
    has_match = False
    salary_total_text = salary_total_text.replace(",", "").replace(" ", "")
    for pattern, lakhs_multiplier in TOTAL_SALARY_SPECIFICATION:
        match = re.findall(pattern, salary_total_text)
        if match:
            has_match = True
            salary = match[-1]
            if type(salary) == str:
                salary = float(salary)
            else:
                salary = float(salary[0]) * lakhs_multiplier
            return salary
    if not has_match:
        return MISSING_NUMERIC
