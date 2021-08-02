import json
import re

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.constant import MAPPING_DIR, MISSING_TEXT

# mapping data
with open(f"{MAPPING_DIR}/lc_company.json", "r") as f:
    COMPANY_MAPPING = json.load(f)
    COMPANIES = list(COMPANY_MAPPING.keys())
with open(f"{MAPPING_DIR}/lc_title.json", "r") as f:
    TITLE_MAPPING = json.load(f)
    TITLES = list(TITLE_MAPPING.keys())

# base features
cv_company = CountVectorizer(analyzer="char")
base_companies = cv_company.fit_transform(COMPANIES)
cv_title = CountVectorizer(analyzer="char")
base_titles = cv_title.fit_transform(TITLES)


def get_company_suggestions(unmapped_companies: dict) -> dict:
    """Suggestions for unmapped companies.

    Args:
        unmapped_companies (dict): Unmapped companies.

    Returns:
        dict: Suggestions.
    """
    unmapped_vecs = cv_company.transform(list(unmapped_companies.keys()))
    scores = cosine_similarity(unmapped_vecs, base_companies)
    reco_ixs = np.argmax(scores, axis=1)
    for c, reco_ix in zip(unmapped_companies, reco_ixs):
        unmapped_companies[c]["company"] = COMPANY_MAPPING[COMPANIES[reco_ix]]["company"]
    return unmapped_companies


def get_title_suggestions(unmapped_titles: dict) -> dict:
    """Suggestions for unmapped titles.

    Args:
        unmapped_titles (dict): Unmapped titles.

    Returns:
        dict: Suggestions.
    """
    unmapped_vecs = cv_title.transform(list(unmapped_titles.keys()))
    scores = cosine_similarity(unmapped_vecs, base_titles)
    reco_ixs = np.argmax(scores, axis=1)
    for c, reco_ix in zip(unmapped_titles, reco_ixs):
        unmapped_titles[c]["title"] = TITLE_MAPPING[TITLES[reco_ix]]["title"]
    return unmapped_titles
