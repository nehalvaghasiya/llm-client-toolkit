import logging
import os
from typing import List

import openai

from .base import LLMClient, Message
from .config import LLMConfig

__all__ = ["OpenAILLMClient"]

api_key = os.getenv("OPENAI_API_KEY")


class OpenAILLMClient(LLMClient):
    """Tiny async wrapper around openai.AsyncOpenAI."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.log.setLevel(logging.INFO)
        self._openai = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=config.base_url,
            timeout=config.timeout,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._openai.close()
    
    async def _acomplete(self, messages: List[Message]) -> str:
        self.log.debug("Sending %d msg(s) to OpenAI", len(messages))
        resp = await self._openai.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return resp.choices[0].message.content
