from enum import StrEnum
import json
import os

import httpx
from openai import OpenAI


class Provider(StrEnum):
    GITHUB_MODELS = "github_models"
    LM_STUDIO = "lm_studio"


LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
GITHUB_MODELS_URL = "https://models.github.ai/inference"


def get_llm_output(prompt: str, provider: Provider = Provider.LM_STUDIO) -> str | None:
    if provider == Provider.LM_STUDIO:
        # TODO: Need to set the thinking budget here; thinks for really long at times :/
        payload = {
            "model": "openai/gpt-oss-20b",
            "temperature": 0.3,
            "messages": [{"role": "user", "content": prompt}],
        }
        with httpx.Client(timeout=120.0) as client:
            response = client.post(LM_STUDIO_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    elif provider == Provider.GITHUB_MODELS:
        client = OpenAI(base_url=GITHUB_MODELS_URL, api_key=os.environ["GITHUB_TOKEN"])
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            temperature=0.3,
            max_tokens=4096,
            top_p=1,
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    raise KeyError(f"Unkown provider {provider}")


def last_fetched_id(file_with_ids: str) -> int | None:
    if not os.path.exists(file_with_ids):
        return None

    _last_id = None
    with open(file_with_ids, "r") as f:
        for line in f:
            _last_id = json.loads(line)["id"]
            break

    return _last_id


# if __name__ == "__main__":
#     print(get_llm_output("1+1=", Provider.GITHUB_MODELS))
