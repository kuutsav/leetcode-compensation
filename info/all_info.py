from typing import Tuple

from ner.label_prep import _get_ner_tagging_data
from info.clean_info import get_clean_inr_salary, get_clean_location


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
            if tag == "location":
                loc = get_clean_location(text)
            elif tag == "salary":
                salary = get_clean_inr_salary(text)
                valid_salary, final_salary = filter_salary(text, salary)
        if loc and salary and valid_salary:
            if loc["india"] == 1.0:
                clean_info.append((loc["clean_location"], salary))


if __name__ == "__main__":
    get_all_info()
