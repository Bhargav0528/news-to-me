"""LLM engine adapters for the News To Me production pipeline."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol

import requests


@dataclass
class ModelConfig:
    """Runtime configuration for supported LLM providers."""

    provider: str = os.getenv("LLM_PROVIDER", "openai")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    api_key: str | None = os.getenv("OPENAI_API_KEY")
    base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest")


class LLMAdapter(Protocol):
    """Protocol for provider-specific structured generation adapters."""

    def generate_json(self, system_prompt: str, user_content: str) -> dict[str, Any]:
        """Generate a JSON object for the given prompt pair."""


class OpenAIResponsesAdapter:
    """Structured JSON generation via the OpenAI Responses API."""

    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        if not config.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI runs")

    def generate_json(self, system_prompt: str, user_content: str) -> dict[str, Any]:
        """Call OpenAI and parse the first JSON response payload."""
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


class AnthropicMessagesAdapter:
    """Structured JSON generation via the Anthropic Messages API."""

    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        if not config.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required for Anthropic runs")

    def generate_json(self, system_prompt: str, user_content: str) -> dict[str, Any]:
        """Call Anthropic and parse the JSON text response."""
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.config.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.config.anthropic_model,
                "max_tokens": 2000,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Return valid JSON only.\n\n{user_content}",
                    }
                ],
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        text = "".join(block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text")
        return json.loads(text)


def build_adapter(config: ModelConfig | None = None) -> LLMAdapter:
    """Build an adapter for the configured LLM provider."""
    config = config or ModelConfig()
    if config.provider == "openai":
        return OpenAIResponsesAdapter(config)
    if config.provider == "anthropic":
        return AnthropicMessagesAdapter(config)
    raise ValueError(f"Unsupported provider: {config.provider}")
