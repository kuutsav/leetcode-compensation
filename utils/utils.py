import json
import os
from random import sample

from utils.constant import DATA_DIR


def get_sample_posts(n: int = 5):
    """Sample compensation posts.

    Args:
        n (int, optional): # sample posts. Defaults to 5.
    """
    posts = os.listdir(DATA_DIR)
    posts_text = ""
    for i, fname in enumerate(sample(posts, n)):
        with open(DATA_DIR + fname) as f:
            post_text = json.load(f)["text"]
            clean_post_text = clean_text(post_text)
            print(
                f"\n{i+1}) ====== original text ======\n{post_text}\n"
                f"\n====== clean text ======\n{clean_post_text}"
            )
            posts_text += f"{'-'*10}{clean_post_text}"
    return posts_text


def clean_text(text: str) -> str:
    """Clean text from leetcode compensations post.

    Args:
        text (str): Text from the post.

    Returns:
        str: Clean text from the post.
    """
    return text.lower()


def get_clean_posts_iter():
    """Generator over the clean posts."""
    for fname in os.listdir(DATA_DIR):
        yield clean_text(json.load(open(DATA_DIR + fname))["text"])
