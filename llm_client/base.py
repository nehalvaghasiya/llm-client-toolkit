import abc
import asyncio
import logging
from typing import Dict, List, Sequence

from .config import LLMConfig

__all__ = ["Message", "LLMClient"]

Message = Dict[str, str]


class LLMClient(abc.ABC):
    """Framework-agnostic skeleton every concrete backend plugs into."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.log = logging.getLogger(self.__class__.__name__)

    def generate(self, *messages: Message | Sequence[Message] | str) -> str:
        """Synchronous helper (wraps the async path under the hood)."""
        safe_msgs = self._normalize(messages)
        return asyncio.run(self.agenerate(*safe_msgs))

    async def agenerate(self, *messages: Message | Sequence[Message] | str) -> str:
        safe_msgs = self._normalize(messages)
        return await self._acomplete(safe_msgs)

    @abc.abstractmethod
    async def _acomplete(self, messages: List[Message]) -> str:
        raise NotImplementedError

    @staticmethod
    def _normalize(inputs: Sequence[Message | Sequence[Message] | str]) -> List[Message]:
        flat: List[Message] = []
        for item in inputs:
            if isinstance(item, str):
                flat.append({"role": "user", "content": item})
            elif isinstance(item, dict):
                flat.append(item)
            else:
                flat.extend(item)  # assume list/tuple of messages
        return flat
