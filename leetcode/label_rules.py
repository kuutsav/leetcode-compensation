import re

from leetcode.utils.constants import LABEL_SPECIFICATION, MISSING_TEXT


def label_rule_for_company(text: str) -> str:
    match = re.search(LABEL_SPECIFICATION["RE_COMPANY_PRIMARY"], text)
    if not match:
        match = re.search(LABEL_SPECIFICATION["RE_COMPANY_SECONDARY"], text)
    if match:
        text = match.group("label").strip()
        return text if len(text) > 1 else MISSING_TEXT
    return MISSING_TEXT


def label_rule_for_others(text: str, label_type: str) -> str:
    match = re.search(LABEL_SPECIFICATION[f"RE_{label_type.upper()}"], text)
    return match.group("label").strip() if match else MISSING_TEXT
