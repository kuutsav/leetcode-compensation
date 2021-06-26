import re

from ner.label_rules import LABEL_SPECIFICATION


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
