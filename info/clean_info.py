import json
import re

from utils.constant import MAPPING_DIR, MISSING_TEXT

# mapping data
with open(f"{MAPPING_DIR}/lc_company.json", "r") as f:
    COMPANY_MAPPING = json.load(f)
with open(f"{MAPPING_DIR}/lc_title.json", "r") as f:
    TITLE_MAPPING = json.load(f)


def clean_company(company_text: str) -> str:
    """Raw company standardization.

    Args:
        text (str): Raw company match.

    Returns:
        str: Final company string.
    """
    return COMPANY_MAPPING.get(
        "".join(re.findall(r"\w+", company_text)), {"company": MISSING_TEXT}
    )["company"]


def clean_title(title_text: str) -> str:
    """Raw title standardization.

    Args:
        title_text (str): Raw title string.

    Returns:
        str: Final title string.
    """
    return TITLE_MAPPING.get(
        "".join(re.findall(r"\w+", title_text)), {"title": MISSING_TEXT}
    )["title"]
