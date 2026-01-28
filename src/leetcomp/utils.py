from enum import StrEnum
import json
import os
import time

import httpx
from openai import OpenAI
from openai import RateLimitError


class Provider(StrEnum):
    GITHUB_MODELS = "github_models"
    LM_STUDIO = "lm_studio"
    ZAI = "zai"


_PROVIDER_CONFIG = {
    Provider.GITHUB_MODELS: {
        "url": "https://models.github.ai/inference",
        "model": "openai/gpt-4o",
        "api_key_env": "GITHUB_TOKEN",
    },
    Provider.LM_STUDIO: {
        "url": "http://localhost:1234/v1/chat/completions",
        "model": "openai/gpt-oss-20b",
        "api_key_env": None,
    },
    Provider.ZAI: {
        "url": "https://api.z.ai/api/coding/paas/v4",
        "model": "glm-4.6",
        "api_key_env": "ZAI_API_KEY",
    },
}


def get_provider_info() -> tuple[Provider, str, str]:
    provider_env = os.environ.get("LLM_PROVIDER", "").lower()
    match provider_env:
        case Provider.GITHUB_MODELS.value:
            provider = Provider.GITHUB_MODELS
        case Provider.ZAI.value:
            provider = Provider.ZAI
        case _:
            provider = Provider.LM_STUDIO

    config = _PROVIDER_CONFIG[provider]
    return provider, config["url"], config["model"]


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
    config = _PROVIDER_CONFIG[provider]

    match provider:
        case Provider.LM_STUDIO:
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

        case Provider.GITHUB_MODELS | Provider.ZAI:
            api_key = os.environ[config["api_key_env"]]
            client = OpenAI(base_url=url, api_key=api_key)
            backoff_delays = [5, 10, 15]
            for attempt, delay in enumerate(backoff_delays, 1):
                try:
                    response = client.chat.completions.create(
                        model=model,
                        temperature=0.3,
                        max_tokens=4096,
                        top_p=1,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are expert at parsing compensation related posts from leetcode discuss forum.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        reasoning_effort="none",
                    )
                    return response.choices[0].message.content
                except RateLimitError as e:
                    if attempt < len(backoff_delays):
                        time.sleep(delay)
                    else:
                        raise

    raise KeyError(f"Unknown provider {provider}")
