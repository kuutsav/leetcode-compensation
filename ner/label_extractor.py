import re
from typing import List, Tuple

from termcolor import colored

from ner.label_rules import LABEL_SPECIFICATION
from utils.utils import get_clean_posts_iter


def get_labels(text: str):
    """All labels from text.

    Args:
        text (str): Input text.
    """
    label_spans = {"_text": text}

    for label, re_pattern in LABEL_SPECIFICATION.items():
        for m in re.finditer(re_pattern, text):
            n = len(m.groups())
            label_type = label.split("_")[-1].lower()
            if label_type not in label_spans:
                label_spans[label_type] = []
            label_spans[label_type].append(
                {"text": m.groups()[-1].strip(), "span": m.span(n)}
            )

    return label_spans


def get_ner_printable_text(tagged_texts: List[Tuple[str, str]]):
    """NER printable text.

    Args:
        tagged_texts (List[Tuple[str, str]]): List of tagged texts.
    """
    markdown_text = ""
    for tt in tagged_texts:
        if tt[1] == "O":
            markdown_text += tt[0]
        else:
            colored_text = colored(tt[0], "red", "on_yellow", attrs=["bold"])
            colored_label = colored(tt[1], attrs=["bold"])
            markdown_text += f"[{colored_text}:{colored_label}]"
    return markdown_text


def get_ner_tagging_data():
    """Data for ner tokenzier."""
    ents = {k.split("_")[1].lower(): [] for k in LABEL_SPECIFICATION}
    tagging_data = []

    for clean_post in get_clean_posts_iter():
        labels = get_labels(clean_post)
        for k in labels:
            if not k[0] == "_":
                for v in labels[k]:
                    if v["text"]:
                        ents[k].append(v["text"])

        sorted_spans = []
        for label, value in labels.items():
            if label != "_text":
                for v in value:
                    sorted_spans.append([v["span"], label])
        sorted_spans = sorted(sorted_spans, key=lambda x: x[0][0])

        start_ix = 0
        text = labels["_text"]
        tagged_texts = []
        for span in sorted_spans:
            end_ix = span[0][0]
            # fmt: off
            tagged_texts.append((text[start_ix: end_ix], "O"))
            tagged_texts.append((text[end_ix: span[0][1]], span[1]))
            # fmt: on
            start_ix = span[0][1]
        tagged_texts.append((text[start_ix:], "O"))
        tagging_data.append(tagged_texts)

    return {"tags": tagging_data, "meta": ents}
