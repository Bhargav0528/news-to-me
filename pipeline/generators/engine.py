"""LLM engine adapters for the News To Me production pipeline."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Protocol

import requests
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    """Runtime configuration for supported LLM providers."""

    provider: str = os.getenv("LLM_PROVIDER", "openrouter")
    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-preview-05-20")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest")


class LLMAdapter(Protocol):
    """Protocol for provider-specific structured generation adapters."""

    def generate_json(self, system_prompt: str, user_content: str) -> dict[str, Any]:
        """Generate a JSON object for the given prompt pair."""


class OpenRouterAdapter:
    """Structured JSON generation via the OpenRouter API."""

    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        if not config.openrouter_api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required for OpenRouter runs")

    def generate_json(self, system_prompt: str, user_content: str, max_retries: int = 3) -> dict[str, Any]:
        """Call OpenRouter and parse the JSON response."""
        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.config.openrouter_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.openrouter_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.config.openrouter_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Return valid JSON only.\n\n{user_content}"},
                        ],
                        "temperature": 0.1,
                        "max_tokens": 8000,
                    },
                    timeout=90,
                )
                response.raise_for_status()
                payload = response.json()
                message = payload.get("choices", [{}])[0].get("message", {})
                text = message.get("content") or ""
                if not text:
                    finish = payload.get("choices", [{}])[0].get("finish_reason")
                    raise RuntimeError(f"Empty response. finish_reason={finish}, refusal={message.get('refusal')}")
                # Some models wrap JSON in markdown fences - strip those
                text = text.strip()
                if text.startswith("```"):
                    lines = text.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    text = "\n".join(lines)
                return json.loads(text)
            except (requests.exceptions.HTTPError, json.JSONDecodeError, RuntimeError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
        raise RuntimeError(f"OpenRouter failed after {max_retries} attempts: {last_error}")


class OpenAIResponsesAdapter:
    """Structured JSON generation via the OpenAI Responses API."""

    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        if not config.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI runs")

    def generate_json(self, system_prompt: str, user_content: str) -> dict[str, Any]:
        """Call OpenAI and parse the first JSON response payload."""
        response = requests.post(
            f"{self.config.openai_base_url.rstrip('/')}/responses",
            headers={
                "Authorization": f"Bearer {self.config.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config.openai_model,
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
    if config.provider == "openrouter":
        return OpenRouterAdapter(config)
    if config.provider == "openai":
        return OpenAIResponsesAdapter(config)
    if config.provider == "anthropic":
        return AnthropicMessagesAdapter(config)
    raise ValueError(f"Unsupported provider: {config.provider}")