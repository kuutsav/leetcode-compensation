import json
import os
import re

from loguru import logger
import pandas as pd

from info.clean_info import (
    clean_company,
    clean_location,
    clean_salary,
    clean_salary_total,
    clean_title,
    clean_yoe,
    get_clean_text,
)
from info.label_rules import label_rule_for_company, label_rule_for_others
from info.suggestions import get_company_suggestions, get_title_suggestions
from utils.constant import (
    DATA_DIR, MAPPING_DIR,
    META_DIR,
    MISSING_NUMERIC,
    MISSING_TEXT,
    POSTS_META_FNAME
)
from utils.utils import get_datetime_from_date


def _save_unmapped_labels(df: pd.DataFrame, label: str, suggest: bool=False) -> dict:
    """Saves unmapped labels for manual labeling.

    Args:
        df (pd.DataFrame): Input df with labels.
        label (str): Label to filter.

    Returns:
        dict: Unmapped labels.
    """
    unmapped_txts = set(df[df[label] == MISSING_TEXT][f"raw_{label}"].values.tolist())
    unmapped_labels = {}
    for txt in unmapped_txts:
        if txt:
            clean_txt = get_clean_text(txt)
            if clean_txt in unmapped_labels:
                unmapped_labels[clean_txt]["count"] += 1
            else:
                unmapped_labels[clean_txt] = {label: "", "count": 1}
    
    if suggest:
        if label == "company":
            unmapped_labels = get_company_suggestions(unmapped_labels)
        elif label == "title":
            unmapped_labels = get_title_suggestions(unmapped_labels)
    
    logger.warning(f"{len(unmapped_labels)} unmapped {label} saved")

    with open(f"{MAPPING_DIR}/unmapped_{label}.json", "w") as f:
        json.dump(unmapped_labels, f)


def get_raw_records() -> pd.DataFrame:
    """Raw records with entities extracted using rules.

    Returns:
        pd.DataFrame: Records in a pandas dataframe.
    """
    with open(f"{META_DIR}/{POSTS_META_FNAME}.json", "r") as f:
        posts_meta = json.load(f)

    data = []
    missing_post_ids = []
    for f in os.listdir(DATA_DIR):
        post_id = f.split(".")[0]
        if post_id not in posts_meta:
            missing_post_ids.append(post_id)
            continue
        with open(f"{DATA_DIR}/{f}", "r") as f:
            txt = f.read()
            formatted_txt = re.sub(r"\s{2,}", " ", txt.lower())
            data.append(
                (
                    posts_meta[post_id]["href"], posts_meta[post_id]["title"],
                    get_datetime_from_date(posts_meta[post_id]["date"]), txt,
                    label_rule_for_company(formatted_txt),
                    label_rule_for_others(formatted_txt, "title"),
                    label_rule_for_others(formatted_txt, "yoe"),
                    label_rule_for_others(formatted_txt, "salary"),
                    label_rule_for_others(formatted_txt, "salary_total"),
                    label_rule_for_others(formatted_txt, "location"),
                )
            )

    df = pd.DataFrame(data, dtype="str",
                      columns=["href", "post_title", "date", "post", "raw_company",
                               "raw_title", "raw_yoe", "raw_salary", "raw_salary_total",
                               "raw_location"])

    logger.info(f"n records: {df.shape[0]}")
    if missing_post_ids:
        logger.warning(f"missing post_ids: {missing_post_ids}")

    return df


def get_clean_records_for_india() -> pd.DataFrame:
    """Posts along with the extracted info(filtered for `India`).

    Returns:
        pd.DataFrame: Records with labels in a pandas dataframe.
    """
    df = get_raw_records()
    df["company"] = df["raw_company"].apply(lambda x: clean_company(x))
    df["title"] = df["raw_title"].apply(lambda x: clean_title(x))
    df["location"] = df["raw_location"].apply(lambda x: clean_location(x))
    df["yoe"] = df["raw_yoe"].apply(lambda x: clean_yoe(x))
    df["salary"] = df["raw_salary"].apply(lambda x: clean_salary(x))
    df["salary_total"] = df["raw_salary_total"].apply(lambda x: clean_salary_total(x))
    # unmapped labels
    _save_unmapped_labels(df, "company", True)
    _save_unmapped_labels(df, "title", True)
    # remove rows not from india
    n_rows_before = df.shape[0]
    df = df[df["location"] != MISSING_TEXT]
    n_rows_dropped = n_rows_before - df.shape[0]
    if n_rows_dropped:
        logger.warning(f"{n_rows_dropped} rows dropped(location!=india)")
    # remove rows with missing company or yoe
    n_rows_before = df.shape[0]
    df = df[(df["company"] != MISSING_TEXT) & (df["salary"] != MISSING_NUMERIC)]
    n_rows_dropped = n_rows_before - df.shape[0]
    if n_rows_dropped:
        logger.warning(f"{n_rows_dropped} rows dropped(incomplete info)")
    # remove internships(some escape the per/month filter in salary regex speficification)
    n_rows_before = df.shape[0]
    df = df[~df["raw_title"].apply(lambda x: "intern" in x)]
    n_rows_dropped = n_rows_before - df.shape[0]
    if n_rows_dropped:
        logger.warning(f"{n_rows_dropped} rows dropped(internships)")
    # remove salary_total where salary_ctc < salary
    df.loc[df["salary_total"]<df["salary"], "salary_total"] = MISSING_NUMERIC
    return df
