from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class GroqConfig:
    api_key: str | None = None
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.35
    max_tokens: int = 900
    timeout: int = 45


class GroqClient:
    """Minimal Groq API client using the OpenAI-compatible chat completions endpoint.

    The app works without an API key by returning a clear fallback response.
    Configure with environment variables:
      - GROQ_API_KEY
      - GROQ_MODEL, optional. Default: llama-3.3-70b-versatile
    """

    endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, config: GroqConfig | None = None):
        api_key = os.getenv("GROQ_API_KEY")
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.config = config or GroqConfig(api_key=api_key, model=model)

    @property
    def is_configured(self) -> bool:
        return bool(self.config.api_key)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if not self.is_configured:
            return self._missing_key_response()

        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.config.temperature,
            "max_completion_tokens": self.config.max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.HTTPError as exc:
            try:
                detail = response.json()
            except Exception:
                detail = response.text[:500]
            return (
                "### Groq Analyst unavailable\n\n"
                f"The Groq API returned an HTTP error: `{exc}`.\n\n"
                f"Details: `{detail}`\n\n"
                "The local deterministic analyst remains available as fallback."
            )
        except Exception as exc:
            return (
                "### Groq Analyst unavailable\n\n"
                f"Could not call Groq: `{exc}`.\n\n"
                "Check your internet connection, `GROQ_API_KEY`, and selected `GROQ_MODEL`."
            )

    @staticmethod
    def _missing_key_response() -> str:
        return (
            "### Groq Analyst not configured\n\n"
            "To enable the real AI Analyst, set your API key before running Streamlit:\n\n"
            "```powershell\n"
            "$env:GROQ_API_KEY=\"your_api_key_here\"\n"
            "$env:GROQ_MODEL=\"llama-3.3-70b-versatile\"\n"
            "streamlit run app.py\n"
            "```\n\n"
            "Without the key, the app continues to work using the local rules-based Chief Analyst."
        )
