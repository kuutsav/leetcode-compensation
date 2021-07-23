import json
import re

import pandas as pd

MAX_BASE_LPA = 100

# Location
df = pd.read_csv("data/mappings/lc_location.csv")
LOCATION_MAPPING = {}
for r in df.iterrows():
    clean_loc = " ".join(re.findall(r"\w+", r[1]["location"]))
    LOCATION_MAPPING[clean_loc] = {
        "clean_location": r[1]["clean_location"],
        "count": r[1]["counts"],
        "india": r[1]["in_india"],
    }

# Company
with open("data/mappings/lc_company.json") as f:
    COMPANY_MAPPING = json.load(f)

# Title
df = pd.read_csv("data/mappings/lc_title.csv", na_filter=False)
TITLE_MAPPING = dict(zip(df["title"], df["clean_title"]))


def get_clean_location(location_text: str) -> str:
    """Clean mapping for location.

    Args:
        location_text (str): Location text.

    Returns:
        str: Clean location.
    """
    clean_loc_text = " ".join(re.findall(r"\w+", location_text))
    return LOCATION_MAPPING.get(clean_loc_text, {"india": "n/a"})


def get_clean_company(company_text: str) -> str:
    """Clean mapping for company.

    Args:
        company_text (str): Company text.

    Returns:
        str: Clean company.
    """
    clean_comp_text = " ".join(re.findall(r"[\w\.\-\&\é ]+", company_text))
    return COMPANY_MAPPING.get(clean_comp_text, "n/a")


def get_clean_title(title_text: str) -> str:
    """Clean mapping for title.

    Args:
        title_text (str): Title text.

    Returns:
        str: Clean title.
    """
    clean_title_text = "".join(re.findall(r"\w+", title_text))
    return TITLE_MAPPING.get(clean_title_text, "n/a")


def get_clean_inr_salary(salary_text: str) -> str:
    """Salary in INR lpa.

    Args:
        s (str): Salary text.

    Returns:
        str: Salary in lakhs per annum.
    """
    salary_text = re.sub(",", "", salary_text)
    salary = ""
    last_span = -1
    for m in re.finditer(r"\d+[\.\d]?", salary_text):
        if last_span > 0:
            if (m.span()[0] - last_span) < 2:
                salary += m.group()
        else:
            salary += m.group()
        last_span = m.span()[1]

    clean_inr = salary
    if clean_inr:
        try:
            clean_inr = float(clean_inr)
        except Exception:
            return 0
    else:
        return 0

    final_salary = clean_inr
    if final_salary:
        if (
            "lpa" in salary_text
            or "lakh" in salary_text
            or re.findall(r"(\d{1,2}.)?\d\s?l", salary_text)
        ):
            if clean_inr < MAX_BASE_LPA:
                final_salary = clean_inr * 100000
        elif "lakh" in salary_text:
            if clean_inr < MAX_BASE_LPA:
                final_salary = clean_inr * 1
        elif re.findall(r"\d\s?k", salary_text) and final_salary < 10000:
            final_salary = clean_inr * 1000
        elif final_salary < MAX_BASE_LPA and (
            "base" in salary_text or "fixed" in salary_text
        ):
            final_salary = final_salary * 100000

    return final_salary
