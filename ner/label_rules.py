import re


RE_COMPANY = r"company\s?[:-]-?\s?([&\w\.\- ]+)"
RE_TITLE = r"title\s?/level?[:-]-?\s?([&\w\.\-\/\+\# ]+)"
RE_YOE = (
    r"\n((yrs|years)\sof\s)?(experience|exp)\s?[:-]-?\s?([\w\.\+\~\-\s]+)\n"
)


def label_rule_for_company(clean_text: str):
    """Labeling rule for companies.

    Args:
        clean_text (str): Clean text from posts.
    """
    return re.findall(RE_COMPANY, clean_text)


def label_rule_for_title(clean_text: str):
    """Labeling rule for titles.

    Args:
        clean_text (str): Clean text from posts.
    """
    return re.findall(RE_TITLE, clean_text)


def label_rule_for_yoe(clean_text: str):
    """Labeling rule for years of exp.

    Args:
        clean_text (str): Clean text from posts.
    """
    return re.findall(RE_YOE, clean_text)
