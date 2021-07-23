from typing import Tuple

from ner.label_prep import _get_ner_tagging_data
from info.clean_info import (
    get_clean_company,
    get_clean_inr_salary,
    get_clean_location,
    get_clean_title,
)

import pandas as pd


MIN_SALARY = 250000
MAX_SALARY = 10000000
MONTHLY_SALARY_INDICATORS = [
    "per month",
    "pm",
    "p.m",
    "p.m.",
    "/month",
    "/ month",
]


def filter_salary(salary_text: str, final_salary: float) -> Tuple[bool, float]:
    """Check for valid salaries in LPA(INR).

    Args:
        salary_text (str): Original salary text.
        final_salary (float): Processed salary in LPA(INR).

    Returns:
        Tuple[bool, float]: `is_valid_salary`, salary in LPA(INR).
    """
    for mo in MONTHLY_SALARY_INDICATORS:
        if mo in salary_text:
            return False, -1
    if final_salary >= MIN_SALARY and final_salary <= MAX_SALARY:
        return True, final_salary
    return False, final_salary


def get_all_info():
    """Clean info from posts."""
    clean_info = []
    for d in _get_ner_tagging_data()["tags"]:
        loc, salary = "", ""
        for text, tag in d:
            if tag == "company":
                comp = get_clean_company(text)
            elif tag == "title":
                title = get_clean_title(text)
            elif tag == "location":
                loc = get_clean_location(text)
            elif tag == "salary":
                salary = get_clean_inr_salary(text)
                valid_salary, final_salary = filter_salary(text, salary)
        if comp and title and loc and salary and valid_salary:
            if loc["india"] == 1.0:
                loc = loc["clean_location"]
            else:
                loc = "n/a"
            clean_info.append((comp, title, loc, salary, d))

    return clean_info


def get_info_df():
    """DataFrame of all the info."""
    df = pd.DataFrame(
        get_all_info(),
        columns=["company", "title", "location", "salary", "original_text"],
    )
    df["original_text"] = [
        "".join(txt for txt, _ in txt_tag) for txt_tag in df["original_text"]
    ]
    return df
