import re

from utils.constant import LABEL_SPECIFICATION


def label_rule_for_company(text: str) -> str:
    """Labeling rule for companies.

    Args:
        text (str): Text from posts.

    Returns:
        str: Raw company match.
    """
    match = re.search(LABEL_SPECIFICATION["RE_COMPANY_PRIMARY"], text)
    if not match:
        match = re.search(LABEL_SPECIFICATION["RE_COMPANY_SECONDARY"], text)
    if match:
        text = match.group("label").strip()
        if len(text) > 1:
            return text
        else:
            return ""
    return ""


def label_rule_for_others(text: str, label_type: str) -> str:
    """Labeling rule for titles.

    Args:
        text (str): Text from posts.

    Returns:
        str: Raw `label` match.
    """
    match = re.search(LABEL_SPECIFICATION[f"RE_{label_type.upper()}"], text)
    if match:
        return match.group("label").strip()
    return ""
