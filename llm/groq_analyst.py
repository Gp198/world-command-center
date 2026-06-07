from __future__ import annotations

from typing import Any

from llm.groq_client import GroqClient
from llm.prompt_builder import build_system_prompt, build_user_prompt


class GroqAnalyst:
    def __init__(self, client: GroqClient | None = None):
        self.client = client or GroqClient()

    @property
    def is_configured(self) -> bool:
        return self.client.is_configured

    def answer(self, question: str, context: dict[str, Any]) -> str:
        return self.client.complete(
            system_prompt=build_system_prompt(),
            user_prompt=build_user_prompt(question=question, context=context),
        )
