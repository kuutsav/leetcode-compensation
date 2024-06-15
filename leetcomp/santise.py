import json
from typing import Any

from leetcomp.prompts import COMPANY_CLUSTER_PROMPT, ROLE_CLUSTER_PROMPT
from leetcomp.utils import config


def cluster_companies_prompt(records: list[dict[Any, Any]]) -> str:
    companies = [r["company"].lower() for r in records if r["company"].strip()]
    unique_companies = "\n".join(sorted(set(companies)))
    prompt = COMPANY_CLUSTER_PROMPT.substitute(companies=unique_companies)
    return prompt


def cluster_roles_prompt(records: list[dict[Any, Any]]) -> str:
    roles = [r["role"].lower() for r in records if r["role"].strip()]
    unique_roles = "\n".join(sorted(set(roles)))
    prompt = ROLE_CLUSTER_PROMPT.substitute(roles=unique_roles)
    return prompt


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Sanitise parsed LeetCode Compensations posts."
    )
    parser.add_argument(
        "--json_path",
        type=str,
        default=config["app"]["data_dir"] / "parsed_comps.json",
        help="Path to the file where parsed posts are stored in JSON format.",
    )
    args = parser.parse_args()

    with open(args.json_path, "r") as f:
        records = json.load(f)

    cluster_roles_prompt_ = cluster_roles_prompt(records)
    print(cluster_roles_prompt_)
