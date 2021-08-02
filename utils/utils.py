from datetime import datetime, timedelta


def get_datetime_from_date(date: str) -> datetime:
    """Returns a `datetime.datetime` object from a leetcode comps post date.

    Args:
        date (str): Date of the `post`.

    Returns:
        datetime: `datetime.datetime` from the `post`.
    """
    if ":" in date:
        return datetime.strptime(date, "%B %d, %Y %I:%M %p")
    elif "ago" in date:
        if "hour" in date or "minute" in date:
            return datetime.now()
        else:
            n_days_ago = date.split(" ")[0]
            n_days_ago = 1 if n_days_ago == "a" else int(n_days_ago)
            return datetime.now() - timedelta(days=n_days_ago)

    return None
