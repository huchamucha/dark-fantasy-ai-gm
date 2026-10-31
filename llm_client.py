import json
import re
from typing import Any

import httpx


class LMStudioClient:
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def ask(self, prompt: str, *, temperature: float = 0.7, max_tokens: int = 700) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()

        payload_json = response.json()
        if "choices" not in payload_json or not payload_json["choices"]:
            raise ValueError(f"LM Studio returned an unexpected payload: {payload_json}")

        return str(payload_json["choices"][0]["message"]["content"]).strip()


def extract_json_object(text: str) -> str:
    if not text:
        return "{}"

    text = text.strip()
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        return match.group(0)

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]

    return "{}"


def parse_json_response(raw: str) -> dict[str, Any]:
    if raw is None:
        return {}

    text = str(raw).strip()
    if not text:
        return {}

    candidate = extract_json_object(text)
    candidate = candidate.replace("True", "true")
    candidate = candidate.replace("False", "false")
    candidate = candidate.replace("None", "null")
    candidate = candidate.replace("'", '"')

    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
        return {"raw": parsed}
    except json.JSONDecodeError:
        return {"raw": raw}
