from enum import StrEnum
import json
import os

import httpx
from openai import OpenAI


class Provider(StrEnum):
    GITHUB_MODELS = "github_models"
    LM_STUDIO = "lm_studio"
    ZAI = "zai"


LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_MODEL = "openai/gpt-oss-20b"
GITHUB_MODELS_URL = "https://models.github.ai/inference"
GITHUB_MODELS_MODEL = "openai/gpt-4o"
ZAI_MODELS_URL = "https://api.z.ai/api/coding/paas/v4"
ZAI_MODEL = "glm-4.6"


def get_provider_info() -> tuple[Provider, str, str]:
    provider_env = os.environ.get("LLM_PROVIDER", "").lower()
    if provider_env == "github_models":
        return Provider.GITHUB_MODELS, GITHUB_MODELS_URL, GITHUB_MODELS_MODEL
    elif provider_env == "zai":
        return Provider.ZAI, ZAI_MODELS_URL, ZAI_MODEL
    return Provider.LM_STUDIO, LM_STUDIO_URL, LM_STUDIO_MODEL


def last_fetched_info(file_with_ids: str) -> tuple[int | None, str | None]:
    """
    Used to fetch the last processed id and its timestamp from jsonl records.
    Returns a tuple of (id, created_at). Returns (None, None) if file doesn't exist.
    """
    if not os.path.exists(file_with_ids):
        return None, None

    _last_id = None
    _created_at = None
    with open(file_with_ids, "r") as f:
        for line in f:
            data = json.loads(line)
            _last_id = data.get("id")
            _created_at = data.get("created_at")
            break

    return _last_id, _created_at


def get_llm_output(prompt: str) -> str | None:
    """
    LLM based processing for data parsing and sanitization from leetcode comp posts.
    Uses LM Studio for processing data in bulk when syncing for the first time.
    Uses Github Models (free tier credits) to parse the new data during sync operations.
    """
    provider, url, model = get_provider_info()

    if provider == Provider.GITHUB_MODELS or provider == Provider.ZAI:
        api_key = (
            os.environ["GITHUB_TOKEN"]
            if provider == Provider.GITHUB_MODELS
            else os.environ["ZAI_API_KEY"]
        )
        client = OpenAI(base_url=url, api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            temperature=0.3,
            max_tokens=4096,
            top_p=1,
            messages=[
                {
                    "role": "system",
                    "content": "You are expert at parsing compenstaion related posts from leetcode discuss forum.",
                },
                {"role": "user", "content": prompt},
            ],
            reasoning_effort="none",
        )
        return response.choices[0].message.content
    elif provider == Provider.LM_STUDIO:
        # TODO: Need to set the thinking budget here; thinks for really long at times :/
        payload = {
            "model": model,
            "temperature": 0.3,
            "messages": [{"role": "user", "content": prompt}],
        }
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    raise KeyError(f"Unkown provider {provider}")
