import re


LABEL_SPECIFICATION = {
    "RE_COMPANY": re.compile(r"company\s?[:-]-?\s?([&\w\.\- ]+)"),
    "RE_TITLE": re.compile(r"title\s?/level?[:-]-?\s?([&\w\.\-\/\+\# ]+)"),
    "RE_YOE": re.compile(
        r"\n((yrs|years)\sof\s)?(experience|exp)\s?[:-]-?\s?([\w\.\+\~\-\s]+)\n"
    ),
    "RE_SALARY": re.compile(r"(salary|base)\s?[:-]-?\s?([\w\,\$\.\/\- ]+)\s"),
}


def label_rule_for_company(text: str):
    """Labeling rule for companies.

    Args:
        text (str): Text from posts.
    """
    return re.findall(LABEL_SPECIFICATION["RE_COMPANY"], text)


def label_rule_for_title(text: str):
    """Labeling rule for titles.

    Args:
        text (str): Text from posts.
    """
    return re.findall(LABEL_SPECIFICATION["RE_TITLE"], text)


def label_rule_for_yoe(text: str):
    """Labeling rule for years of exp.

    Args:
        text (str): Text from posts.
    """
    return re.findall(LABEL_SPECIFICATION["RE_YOE"], text)


def label_rule_for_salary(text: str):
    """Labeling rule for salary.

    Args:
        text (str): Text from posts.
    """
    return re.findall(LABEL_SPECIFICATION["RE_SALARY"], text)
