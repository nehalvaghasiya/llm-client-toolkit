from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm_client import (
    JsonParser,
    LLMConfig,
    OpenAILLMClient,
    RetryLLMClient,
)

cfg = LLMConfig.from_yaml("configs/config.yaml")
base = OpenAILLMClient(cfg)
client = RetryLLMClient(base, JsonParser())

print(client.generate('Say hello as JSON {"greeting": "..."}'))
