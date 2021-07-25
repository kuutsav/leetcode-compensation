import pandas as pd

from info.clean_info import (
    filter_salary,
    get_clean_company,
    get_clean_inr_salary,
    get_clean_location,
    get_clean_title,
    get_yoe,
)
from ner.label_prep import _get_ner_tagging_data


def get_all_info():
    """Clean info from posts."""
    clean_info = []
    for d in _get_ner_tagging_data()["tags"]:
        loc, salary, yoe = "", "", -1
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
            elif tag == "yoe":
                yoe = get_yoe(text)
        if comp and title and loc and salary and valid_salary:
            if loc["india"]:
                loc = loc["clean_location"]
            else:
                loc = "n/a"
            clean_info.append((comp, title, loc, salary, yoe, d))

    return clean_info


def get_info_df():
    """DataFrame of all the info."""
    df = pd.DataFrame(
        get_all_info(),
        columns=[
            "company",
            "title",
            "location",
            "salary",
            "yoe",
            "original_text",
        ],
    )
    df["original_text"] = [
        "".join(txt for txt, _ in txt_tag) for txt_tag in df["original_text"]
    ]
    return df
