import json
from random import shuffle

from datasets import load_dataset, load_metric
from loguru import logger
import numpy as np
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    TrainingArguments,
    Trainer,
)

from ner.label_rules import LABEL_SPECIFICATION
from ner.label_prep import _get_ner_tagging_data, get_label_mapping
from utils.constant import NER_DATA_DIR


tokenizer = AutoTokenizer.from_pretrained("distilroberta-base")
data_collator = DataCollatorForTokenClassification(tokenizer)
model = AutoModelForTokenClassification.from_pretrained(
    "distilroberta-base", num_labels=len(LABEL_SPECIFICATION) * 2 + 1
)

LABEL_MAP = get_label_mapping()
LABEL_LIST = list(LABEL_MAP.keys())
args = TrainingArguments(
    "test-ner",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
)
METRIC = load_metric("seqeval")
OTHER_TAG = "O"
SEP_TEXT_START_ID = 0
SEP_TEXT_END_ID = 2
ATTENTION_MASK = 1
NONE = -100
MAX_LEN = 512


def _get_ner_data():
    """Data for NER models."""
    tagging_data = _get_ner_tagging_data()
    label_map = get_label_mapping()
    all_word_ids = {"input_ids": [], "attention_mask": [], "labels": []}

    for d in tagging_data["tags"]:
        sample_word_ids = {"input_ids": [], "attention_mask": [], "labels": []}
        for text, tag in d:
            word_ids = tokenizer(text)
            if tag == "O":
                tags = [0] * (len(word_ids["input_ids"]) - 2)
            else:
                if len(word_ids["input_ids"]) > 3:
                    tags = [label_map[f"B-{tag.upper()}"]] + [
                        label_map[f"I-{tag.upper()}"]
                    ] * (len(word_ids["input_ids"]) - 3)
                else:
                    tags = [label_map[f"B-{tag.upper()}"]]
            sample_word_ids["input_ids"] += word_ids["input_ids"][1:-1]
            sample_word_ids["attention_mask"] += word_ids["attention_mask"][
                1:-1
            ]
            sample_word_ids["labels"] += tags
        all_word_ids["input_ids"].append(
            [SEP_TEXT_START_ID]
            + sample_word_ids["input_ids"]
            + [SEP_TEXT_END_ID]
        )
        all_word_ids["attention_mask"].append(
            [ATTENTION_MASK]
            + sample_word_ids["attention_mask"]
            + [ATTENTION_MASK]
        )
        all_word_ids["labels"].append(
            [NONE] + sample_word_ids["labels"] + [NONE]
        )

    return all_word_ids


def prepare_training_and_validation_data(val_pct: int = 10):
    """Prepares training and validation data for NER model.

    Args:
        val_pct (int): Percentage of data for validation.
    """
    word_ids = _get_ner_data()
    ixs = list(range(len(word_ids["input_ids"])))
    shuffle(ixs)
    n_val = len(ixs) * val_pct // 100
    data = {
        "train": {"input_ids": [], "attention_mask": [], "labels": []},
        "validation": {"input_ids": [], "attention_mask": [], "labels": []},
    }
    n_skip = 0
    for i, ix in enumerate(ixs):
        if len(word_ids["input_ids"][ix]) > MAX_LEN:
            n_skip += 1
            continue
        if i < n_val:
            data["validation"]["input_ids"].append(word_ids["input_ids"][ix])
            data["validation"]["attention_mask"].append(
                word_ids["attention_mask"][ix]
            )
            data["validation"]["labels"].append(word_ids["labels"][ix])
        else:
            data["train"]["input_ids"].append(word_ids["input_ids"][ix])
            data["train"]["attention_mask"].append(
                word_ids["attention_mask"][ix]
            )
            data["train"]["labels"].append(word_ids["labels"][ix])
    train_data = {"data": data["train"]}
    val_data = {"data": data["validation"]}
    with open(NER_DATA_DIR + "ner_data_train.json", "w") as f:
        json.dump(train_data, f)
    with open(NER_DATA_DIR + "ner_data_val.json", "w") as f:
        json.dump(val_data, f)

    logger.info("data prep complete!")
    logger.info(
        f"train: {len(data['train']['input_ids'])}; "
        f"val: {len(data['validation']['input_ids'])}; "
        f"n_skip: {n_skip}"
    )


def compute_metrics(p):
    """Precision, Recall and F1 for NER model."""
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    # Remove ignored index (special tokens)
    true_predictions = [
        [LABEL_LIST[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [LABEL_LIST[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    results = METRIC.compute(
        predictions=true_predictions, references=true_labels
    )
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"],
    }


def train_ner():
    """Trains NER on leetocode compensations data."""
    prepare_training_and_validation_data()
    train_data = load_dataset(
        "json", data_files=NER_DATA_DIR + "ner_data_train.json", field="data"
    )
    val_data = load_dataset(
        "json", data_files=NER_DATA_DIR + "ner_data_val.json", field="data"
    )
    logger.info(
        f"train: {train_data['train'].num_rows}; "
        f"val: {val_data['train'].num_rows}"
    )
    trainer = Trainer(
        model,
        args,
        train_dataset=train_data["train"],
        eval_dataset=val_data["train"],
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.evaluate()

    predictions, labels, _ = trainer.predict(val_data)
    predictions = np.argmax(predictions, axis=2)

    # Remove ignored index (special tokens)
    true_predictions = [
        [LABEL_LIST[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [LABEL_LIST[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    results = METRIC.compute(
        predictions=true_predictions, references=true_labels
    )
    return results
