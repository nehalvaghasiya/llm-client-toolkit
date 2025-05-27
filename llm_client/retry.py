import re
from typing import List

from .base import LLMClient, Message
from .parsing import Parser, ParserError

__all__ = ["RetryLLMClient"]


class RetryLLMClient(LLMClient):
    """
    Decorator that retries an inner client until a Parser succeeds
    or the retry budget is exhausted.
    """

    REPAIR_INSTRUCTION = (
        "Your previous answer did not match the required format. "
        "Please output *only* the valid content."
    )

    def __init__(self, inner: LLMClient, parser: Parser):
        super().__init__(inner.config)
        self._inner = inner
        self._parser = parser

    async def _acomplete(self, messages: List[Message]) -> str:
        exceptions: List[str] = []
        for attempt in range(self.config.retry_count + 1):
            raw = await self._inner._acomplete(messages)
            
            # Strip code fences like ```json ... ``` or ```
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.IGNORECASE)

            try:
                self._parser.parse(cleaned)
                return raw
            except ParserError as exc:
                self.log.warning(
                    "Parse failed on attempt %d/%d: %s",
                    attempt + 1,
                    self.config.retry_count,
                    exc,
                )
                exceptions.append(str(exc))
                messages.append({"role": "system", "content": self.REPAIR_INSTRUCTION})

        raise ParserError(
            "All retries exhausted. Last errors:\n" + "\n".join(exceptions)
        )
