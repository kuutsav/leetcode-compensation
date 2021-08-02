import json
import os
import re

from loguru import logger
import pandas as pd

from info.label_rules import label_rule_for_company, label_rule_for_others
from utils.constant import DATA_DIR, META_DIR, POSTS_META_FNAME


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
                    posts_meta[post_id]["href"],
                    posts_meta[post_id]["title"],
                    label_rule_for_company(formatted_txt),
                    label_rule_for_others(formatted_txt, "title"),
                    label_rule_for_others(formatted_txt, "yoe"),
                    label_rule_for_others(formatted_txt, "salary"),
                    label_rule_for_others(formatted_txt, "location"),
                )
            )

    df = pd.DataFrame(data, dtype="str")
    cols = [
        "href",
        "post_title",
        "company",
        "title",
        "yoe",
        "salary",
        "location",
    ]
    df.columns = cols

    logger.info(f"n records: {df.shape[0]}")
    if missing_post_ids:
        logger.warning(f"missing post_ids: {missing_post_ids}")

    return df
