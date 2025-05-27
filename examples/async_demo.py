import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm_client import LLMConfig, OpenAILLMClient


async def main() -> None:
    cfg = LLMConfig.from_yaml("configs/config.yaml")
    
    async with OpenAILLMClient(cfg) as llm:
        response = await llm.agenerate('Tell me a joke, reply JSON {"joke": "..."}')
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
