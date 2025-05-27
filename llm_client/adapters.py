"""
Thin wrappers that turn any LLMClient instance into LangChain / LlamaIndex / Pydantic-AI
objects without adding a hard dependency to *base* classes.
"""
import os

from .base import LLMClient

api_key = os.getenv("OPENAI_API_KEY")

def to_langchain(client: LLMClient):
    from langchain_openai import ChatOpenAI

    cfg = client.config
    return ChatOpenAI(
        model_name=cfg.model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        openai_api_key=api_key,
        openai_api_base=cfg.base_url,
    )


def to_llamaindex(client: LLMClient):
    from llama_index.llms.openai import OpenAI

    cfg = client.config
    return OpenAI(model=cfg.model, temperature=cfg.temperature, api_key=api_key)


def to_pydantic_ai(client: LLMClient):
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider

    cfg = client.config
    return OpenAIModel(cfg.model, provider=OpenAIProvider(api_key=api_key))
