import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from leetcode.utils.commons import load_json
from leetcode.utils.constants import MAPPINGS_DIR

company_mapping = load_json(MAPPINGS_DIR / "lc_company.json")
companies = list(company_mapping.keys())
cv_company = CountVectorizer(analyzer="char")
base_companies = cv_company.fit_transform(companies)

title_mapping = load_json(MAPPINGS_DIR / "lc_title.json")
titles = list(title_mapping.keys())
cv_title = CountVectorizer(analyzer="char")
base_titles = cv_title.fit_transform(titles)


def company_suggestions(unmapped_companies: dict) -> dict:
    unmapped_vecs = cv_company.transform(list(unmapped_companies.keys()))
    scores = cosine_similarity(unmapped_vecs, base_companies)
    reco_ixs = np.argmax(scores, axis=1)
    for c, reco_ix in zip(unmapped_companies, reco_ixs):
        unmapped_companies[c]["company"] = company_mapping[companies[reco_ix]]["company"]
    return unmapped_companies


def title_suggestions(unmapped_titles: dict) -> dict:
    unmapped_vecs = cv_title.transform(list(unmapped_titles.keys()))
    scores = cosine_similarity(unmapped_vecs, base_titles)
    reco_ixs = np.argmax(scores, axis=1)
    for c, reco_ix in zip(unmapped_titles, reco_ixs):
        unmapped_titles[c]["title"] = title_mapping[titles[reco_ix]]["title"]
    return unmapped_titles
