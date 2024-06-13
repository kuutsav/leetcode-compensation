import json
import os
import random
import re
import time
import tomllib
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable

import ollama
import requests  # type: ignore
from dotenv import load_dotenv

load_dotenv(override=True)


with open("config.toml", "rb") as f:
    config = tomllib.load(f)

config["app"]["data_dir"] = Path(config["app"]["data_dir"])


def ollama_predict(prompt: str) -> str:
    response = ollama.chat(
        model=config["llms"]["ollama_model"],
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]  # type: ignore


def openrouter_predict(prompt: str) -> str:
    response = requests.post(
        url=config["llms"]["openrouter_url"],
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        data=json.dumps(
            {
                "model": config["llms"]["openrouter_model"],
                "messages": [{"role": "user", "content": prompt}],
            }
        ),
    )
    time.sleep(60 / config["llms"]["openrouter_req_per_min"])
    return str(response.json()["choices"][0]["message"]["content"])


def vllm_predict(prompt: str) -> str:
    response = requests.post(
        config["llms"]["vllm_url"],
        json={
            "model": config["llms"]["vllm_model"],
            "prompt": prompt,
            "max_tokens": 256,
            "temperature": 0.3,
        },
    )
    return str(response.json()["choices"][0]["text"])


def get_model_predict(inf_engine: str) -> Callable[[str], str]:
    match inf_engine.lower():
        case "ollama":
            return ollama_predict
        case "openrouter":
            return openrouter_predict
        case "vllm":
            return vllm_predict
        case _:
            raise ValueError("Invalid inference engine")


def retry_with_exp_backoff(retries: int):  # type: ignore[no-untyped-def]
    def decorator(function: Callable):  # type: ignore
        @wraps(function)
        def wrapper(*args, **kwargs):  # type: ignore
            i = 1
            while i <= retries:
                try:
                    return function(*args, **kwargs)
                except Exception as e:
                    sleep_for = random.uniform(2**i, 2 ** (i + 1))
                    err_msg = f"{function.__name__} ({args}, {kwargs}): {e}"
                    print(f"Retry={i} Rest={sleep_for:.1f}s Err={err_msg}")
                    time.sleep(sleep_for)
                    i += 1
                    if i > retries:
                        raise

        return wrapper

    return decorator


def latest_parsed_date(comps_path: str) -> datetime:
    with open(comps_path, "r") as f:
        top_line = json.loads(f.readline())

    return datetime.strptime(
        top_line["creation_date"], config["app"]["date_fmt"]
    )


def parse_json_markdown(json_string: str) -> list[dict[Any, Any]]:
    match = re.search(
        r"""```    # match first occuring triple backticks
        (?:json)?  # zero or one match of string json in non-capturing group
        (.*)```    # greedy match to last triple backticks
        """,
        json_string,
        flags=re.DOTALL | re.VERBOSE,
    )

    if match is None:
        json_str = json_string
    else:
        json_str = match.group(1)

    json_str = json_str.strip()
    try:
        parsed_content = eval(json_str)
    except Exception:
        return []

    return parsed_content  # type: ignore


def sort_and_truncate(comps_path: str, truncate: bool = False) -> None:
    with open(comps_path, "r") as file:
        records = [json.loads(line) for line in file]

    records.sort(
        key=lambda x: datetime.strptime(
            x["creation_date"], config["app"]["date_fmt"]
        ),
        reverse=True,
    )

    if truncate:
        records = records[: config["app"]["max_recs"]]

    with open(comps_path, "w") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    print(f"Sorted {len(records)} records!")


def mapping(map_path: str | Path) -> dict[str, str]:
    with open(map_path, "r") as f:
        data = json.load(f)

    mapping = {}
    for d in data:
        for item in d["cluster"]:
            mapping[item] = d["cluster_name"]

    return mapping
