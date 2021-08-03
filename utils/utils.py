from datetime import datetime, timedelta

from info.all_info import get_clean_records_for_india
from utils.constant import OUT_DATE_FORMAT


def get_datetime_from_date(date: str) -> datetime:
    """Returns a `datetime.datetime` object from a leetcode comps post date.

    Args:
        date (str): Date of the `post`.

    Returns:
        datetime: `datetime.datetime` from the `post`.
    """
    if ":" in date:
        return datetime.strptime(date, "%B %d, %Y %I:%M %p").strftime(OUT_DATE_FORMAT)
    elif "ago" in date:
        if "hour" in date or "minute" in date:
            return datetime.now().strftime(OUT_DATE_FORMAT)
        else:
            n_days_ago = date.split(" ")[0]
            n_days_ago = 1 if n_days_ago == "a" else int(n_days_ago)
            return (datetime.now() - timedelta(days=n_days_ago)).strftime(OUT_DATE_FORMAT)

    return "1900/01/01"

# def sample_for_readme(n: int=3) -> None:
#     """Sample posts and entities for README.

#     Args:
#         n (int, optional): # samples.
#     """
#     df = get_clean_records_for_india()
#     sample_df = df[["post_title", "href", "date", "company", "title", "yoe",
#                     "salary", "location", "post"]].sample(3)
#     for r in sample_df.iterrows():
#         r = r[1]
#         print(f'title : {r["post_title"]}<br>')
#         print(f'url : {r["href"]}<br>')
#         print(f'company : `{r["company"]}`<br>')
#         print(f'title : `{r["title"]}`<br>')
#         print(f'yoe : `{r["yoe"]}` years<br>')
#         print(f'salary : `₹ {r["salary"]}`<br>')
#         print(f'location : `{r["location"]}`<br>')
#         print(f'`post`\n{r["post"]}<br>')
#         print('---')
