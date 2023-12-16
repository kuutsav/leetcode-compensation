from __future__ import annotations

from datetime import datetime, timedelta
import json

from leetcode.utils.constants import DEFAULT_POST_DATE, OUTPUT_DATE_FMT


def datetime_from_posts_date(date: str) -> str:
    if ":" in date:
        return datetime.strptime(date, "%B %d, %Y %I:%M %p").strftime(OUTPUT_DATE_FMT)
    elif "ago" in date:
        if "hour" in date or "minute" in date:
            return datetime.now().strftime(OUTPUT_DATE_FMT)
        else:
            n_days_ago = date.split(" ")[0]
            n_days_ago = 1 if n_days_ago == "a" else int(n_days_ago)
            return (datetime.now() - timedelta(days=n_days_ago)).strftime(OUTPUT_DATE_FMT)

    return DEFAULT_POST_DATE


def load_json(fname: str) -> dict:
    with open(fname, "r") as f:
        data = json.load(f)
    return data


def save_json(data: dict | list, fname: str) -> None:
    with open(fname, "w") as f:
        json.dump(data, f)
