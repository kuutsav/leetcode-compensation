import os
import re

from loguru import logger
import pandas as pd

from leetcode import clean_info, suggestions
from leetcode.label_rules import label_rule_for_company, label_rule_for_others
from leetcode.utils.commons import datetime_from_posts_date, load_json, save_json
from leetcode.utils.constants import (
    POSTS_DIR,
    POSTS_METADATA_F,
    MAPPINGS_DIR,
    MISSING_NUMERIC,
    MISSING_TEXT,
    POSTS_TO_DROP,
)


def _save_unmapped_labels(df: pd.DataFrame, label: str, suggest: bool = False) -> None:
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
            clean_txt = clean_info.clean_text(txt)
            if clean_txt in unmapped_labels:
                unmapped_labels[clean_txt]["count"] += 1
            else:
                unmapped_labels[clean_txt] = {label: "", "count": 1}

    if suggest:
        if label == "company":
            unmapped_labels = suggestions.company_suggestions(unmapped_labels)
        elif label == "title":
            unmapped_labels = suggestions.title_suggestions(unmapped_labels)

    logger.warning(f"{len(unmapped_labels)} unmapped {label} saved")

    save_json(unmapped_labels, f"{MAPPINGS_DIR}/unmapped_{label}.json")


def get_raw_records() -> pd.DataFrame:
    """Raw records with entities extracted using rules.

    Returns:
        pd.DataFrame: Records in a pandas dataframe.
    """
    posts_meta, data, missing_post_ids = load_json(POSTS_METADATA_F), [], []

    for f in os.listdir(POSTS_DIR):
        post_id = f.split(".")[0]
        if post_id not in posts_meta:
            missing_post_ids.append(post_id)
            continue
        with open(POSTS_DIR / f, "r") as f:
            txt = f.read()
            formatted_txt = re.sub(r"\s{2,}", " ", txt.lower())
            data.append(
                (
                    post_id,
                    posts_meta[post_id]["href"],
                    posts_meta[post_id]["title"],
                    datetime_from_posts_date(posts_meta[post_id]["date"]),
                    txt,
                    label_rule_for_company(formatted_txt),
                    label_rule_for_others(formatted_txt, "title"),
                    label_rule_for_others(formatted_txt, "yoe"),
                    label_rule_for_others(formatted_txt, "salary"),
                    label_rule_for_others(formatted_txt, "salary_total"),
                    label_rule_for_others(formatted_txt, "location"),
                )
            )

    # fmt: off
    df = pd.DataFrame(
        data, dtype="str",
        columns=[
            "post_id", "href", "post_title", "date", "post", "raw_company",
            "raw_title","raw_yoe", "raw_salary", "raw_salary_total", "raw_location"
        ],
    )
    # fmt: on

    logger.info(f"n records: {df.shape[0]}")

    if missing_post_ids:
        logger.warning(f"n missing post_ids: {len(missing_post_ids)}, {missing_post_ids[:10]} ...")

    return df


def get_clean_records_for_india() -> pd.DataFrame:
    """Posts along with the extracted info(filtered for `India`).

    Returns:
        pd.DataFrame: Records with labels in a pandas dataframe.
    """
    df = get_raw_records()

    df["company"] = df["raw_company"].apply(lambda x: clean_info.clean_company(x))
    df["title"] = df["raw_title"].apply(lambda x: clean_info.clean_title(x))
    df["location"] = df["raw_location"].apply(lambda x: clean_info.clean_location(x))
    df["yoe"] = df["raw_yoe"].apply(lambda x: clean_info.clean_yoe(x))
    df["salary"] = df["raw_salary"].apply(lambda x: clean_info.clean_salary(x))
    df["salary_total"] = df["raw_salary_total"].apply(lambda x: clean_info.clean_salary_total(x))

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
    df.loc[df["salary_total"] < df["salary"], "salary_total"] = MISSING_NUMERIC

    # remove wrong info (marked manually)
    df = df.loc[~df["post_id"].isin(POSTS_TO_DROP), :]

    return df
