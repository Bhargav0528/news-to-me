from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol

import requests


@dataclass
class ModelConfig:
    provider: str = os.getenv("LLM_PROVIDER", "openai")
    model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    api_key: str | None = os.getenv("OPENAI_API_KEY")
    base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")


class LLMAdapter(Protocol):
    def generate_json(self, system_prompt: str, user_content: str) -> dict[str, Any]: ...


class OpenAIResponsesAdapter:
    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        if not config.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for live runs")

    def generate_json(self, system_prompt: str, user_content: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.config.base_url.rstrip('/')}/responses",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config.model,
                "input": [
                    {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                    {"role": "user", "content": [{"type": "input_text", "text": user_content}]},
                ],
                "text": {"format": {"type": "json_object"}},
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        text = payload["output"][0]["content"][0]["text"]
        return json.loads(text)


def build_adapter(config: ModelConfig | None = None) -> LLMAdapter:
    config = config or ModelConfig()
    if config.provider == "openai":
        return OpenAIResponsesAdapter(config)
    raise ValueError(f"Unsupported provider: {config.provider}")
