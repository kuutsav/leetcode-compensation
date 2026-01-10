from enum import StrEnum
import json
import os

import httpx
from openai import OpenAI


class Provider(StrEnum):
    GITHUB_MODELS = "github_models"
    LM_STUDIO = "lm_studio"


LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_MODEL = "openai/gpt-oss-20b"
GITHUB_MODELS_URL = "https://models.github.ai/inference"
GITHUB_MODELS_MODEL = "openai/gpt-4o"


def get_default_provider() -> Provider:
    provider_env = os.environ.get("LLM_PROVIDER", "").lower()
    if provider_env == "github_models":
        return Provider.GITHUB_MODELS
    return Provider.LM_STUDIO


def last_fetched_id(file_with_ids: str) -> int | None:
    """
    Used to fetch the last processed id from jsonl records (raw and processed).
    This heelps in avoiding processing or parsing of the same ids across runs.
    """
    if not os.path.exists(file_with_ids):
        return None

    _last_id = None
    with open(file_with_ids, "r") as f:
        for line in f:
            _last_id = json.loads(line)["id"]
            break

    return _last_id


def get_llm_output(prompt: str, provider: Provider | None = None) -> str | None:
    """
    LLM based processing for data parsing and sanitization from leetcode comp posts.
    Uses LM Studio for processing data in bulk when syncing for the first time.
    Uses Github Models (free tier credits) to parse the new data during sync operations.
    """
    if provider is None:
        provider = get_default_provider()

    if provider == Provider.GITHUB_MODELS:
        client = OpenAI(base_url=GITHUB_MODELS_URL, api_key=os.environ["GITHUB_TOKEN"])
        response = client.chat.completions.create(
            model=GITHUB_MODELS_MODEL,
            temperature=0.3,
            max_tokens=4096,
            top_p=1,
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
    elif provider == Provider.LM_STUDIO:
        # TODO: Need to set the thinking budget here; thinks for really long at times :/
        payload = {
            "model": LM_STUDIO_MODEL,
            "temperature": 0.3,
            "messages": [{"role": "user", "content": prompt}],
        }
        with httpx.Client(timeout=120.0) as client:
            response = client.post(LM_STUDIO_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    raise KeyError(f"Unkown provider {provider}")
