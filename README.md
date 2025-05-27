# LLM Client Toolkit

## Table of Contents

* [Overview](#overview)
* [Technical Architecture](#technical-architecture)
* [Installation](#installation)

  * [Using **uv** (recommended)](#using-uv-recommended)
  * [Using `pip` / virtual‑env](#using-pip--virtualenv)
* [Quick Start](#quick-start)
* [Troubleshooting](#troubleshooting)
* [Directory Tree](#directory-tree)
* [Contributing — Bugs & Feature Requests](#contributing--bugs--feature-requests)
* [Technologies Used](#technologies-used)


## Overview

`llm_client` is a **framework‑agnostic**, easily extensible toolkit that wraps any Large‑Language‑Model backend—OpenAI, Anthropic, local models, etc.—behind a single, clean interface.

It is designed for developers who want:

* **Sync & async** support out‑of‑the‑box.
* **Parser‑driven retries** that auto‑repair malformed model output.
* Drop‑in **adapters** for LangChain, Llama‑Index, Pydantic‑AI and friends.
* A **Pydantic‑powered configuration** system you can load from `config.yaml`, environment variables, or code.

> **Why do I need this?**  If you have ever peppered your codebase with ad‑hoc OpenAI calls, copy‑pasted retry loops, or fought with schema validation, `llm_client` gives you a reusable core so you can focus on *product* rather than plumbing.


## Technical Architecture

| Layer               | Responsibility                                                                            | Key Files                      |
| ------------------- | ----------------------------------------------------------------------------------------- | ------------------------------ |
| **Configuration**   | Strongly‑typed values loaded from YAML / env                                              | `llm_client/config.py`         |
| **Core Client**     | Abstract `LLMClient` with sync `generate()` and async `agenerate()`                       | `llm_client/base.py`           |
| **Back‑ends**       | Concrete clients (e.g. `OpenAILLMClient`) that implement a single `_acomplete()` method   | `llm_client/openai_backend.py` |
| **Parsing**         | Strategy objects that turn raw text → structured data (`JsonParser`, `PydanticParser`, …) | `llm_client/parsing.py`        |
| **Retry Decorator** | Wraps any client with parser‑aware retries                                                | `llm_client/retry.py`          |
| **Adapters**        | Optional helpers that convert an `LLMClient` into LangChain/LlamaIndex objects            | `llm_client/adapters.py`       |


## Installation

`llm_client` works with **Python 3.10 – 3.13**.

### Using **uv** (recommended)

[`uv`](https://docs.astral.sh/uv/getting-started/features/#projects) is a super‑fast Rust replacement for `pip` + `virtualenv`. It creates deterministic lock files and dramatically speeds up installs.

```bash
# 1 — Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2 — Create & activate a virtualenv (optional)
uv venv .venv
source .venv/bin/activate 

# 3 — Lock and sync project dependencies
uv lock                          # generates uv.lock if missing
uv sync                          # installs deps exactly as in uv.lock
```

### Using `pip` / virtual‑env

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt # will be generated from uv.lock if you prefer pip
```

> **Note**  If you plan to use OpenAI or Grok, remember to export your key:
>
> ```bash
> export OPENAI_API_KEY="sk‑..."
> ```

---

## Quick Start

```python
from llm_client import (
    LLMConfig,
    OpenAILLMClient,
    RetryLLMClient,
    JsonParser,
)

cfg    = LLMConfig.from_yaml("config.yaml")
base   = OpenAILLMClient(cfg)
client = RetryLLMClient(base, JsonParser())

answer = client.generate("Return a JSON greet: {\"greeting\": \"...\"}")
print(answer)
```

Async usage:

```python
import asyncio
from llm_client import OpenAILLMClient, LLMConfig

async def main():
    cfg = LLMConfig.from_env()
    async with OpenAILLMClient(cfg) as llm:
        print(await llm.agenerate("Hi! Who are you?"))

asyncio.run(main())
```

Need LangChain? Just adapt:

```python
from llm_client import OpenAILLMClient, LLMConfig
from llm_client.adapters import to_langchain

lc_chat = to_langchain(OpenAILLMClient(LLMConfig.from_env()))
print(lc_chat.invoke("Summarise this repo in two bullets"))
```

---

## Configuration (`config.yaml`) & Environment Variables

`config.yaml` is the single place to tweak **model**, **generation parameters**, and **retry behaviour**.  Typical keys:

```yaml
# Model & generation
model: "gpt-4o-mini"
temperature: 0.7
max_tokens: 1024

# Retry wrapper
retry_count: 3

# Transport — `api_key` is OPTIONAL here
# Prefer loading secrets from the environment for safety
api_key: ""   # leave blank or delete this key
```

> **Why env vars for secrets?**
> Hard‑coding your OpenAI key (or any credential) into a repo is a security risk. By keeping `api_key` empty the client will automatically fall back to the `OPENAI_API_KEY` environment variable.

### Exporting the key

```bash
# macOS/Linux
export OPENAI_API_KEY="sk‑…"

# Windows PowerShell
setx OPENAI_API_KEY "sk‑…"
```

### Example usage in code

```python
from llm_client import LLMConfig, OpenAILLMClient

cfg = LLMConfig.from_yaml("config.yaml")  # `api_key` is resolved from env
client = OpenAILLMClient(cfg)
print(client.generate("Say hi as JSON {\"greeting\":\"...\"}"))
```

---

## Troubleshooting

| Symptom                         | Fix                                                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| *`ModuleNotFoundError: openai`* | `pip install openai` or `uv pip install openai`                                                                    |
| Parser keeps failing            | Increase `retry_count` in `config.yaml` or improve your prompt so the output actually matches the expected schema. |
| Timeouts on large payloads      | Bump `timeout` in `config.yaml` or stream tokens (planned feature).                                                |

If you hit something gnarlier, feel free to open an [issue](https://github.com/nehalvaghasiya/llm-client-toolkit/issues).



## Optional Adapters (LangChain, LlamaIndex, Pydantic‑AI, …)

The **core package** has *no hard dependency* on external framework SDKs. If you want to use the convenience wrappers in `llm_client.adapters`, install the matching library yourself:

| Adapter helper     | Extra dependency                         | Install command                |
| ------------------ | ---------------------------------------- | ------------------------------ |
| `to_langchain()`   | `langchain` (or `langchain-openai`)      | `pip install langchain-openai` |
| `to_llamaindex()`  | `llama-index` >= 0.10                    | `pip install llama-index`      |
| `to_pydantic_ai()` | `pydantic-ai` (hypothetical placeholder) | `pip install "pydantic-ai-slim[openai]"`      |

If an adapter is invoked without the required package present, an `ImportError` will be raised with guidance on what to install.


## Directory Tree

```text
llm_project/
├── llm_client/                # Reusable Python package
│   ├── __init__.py            # Public re‑exports
│   ├── base.py                # Abstract client + helpers
│   ├── config.py              # Pydantic model & YAML loader
│   ├── parsing.py             # Parsers + ParserError
│   ├── openai_backend.py      # Async OpenAI implementation
│   ├── retry.py               # Parser‑aware retry decorator
│   └── adapters.py            # LangChain / LlamaIndex utilities
├── examples/                  # Ready‑to‑run demos
│   ├── demo_sync.py
│   └── demo_async.py
├── configs/
│   └── config.yaml            # Default settings (copy & edit)
├── uv.lock                    # Exact dependency versions (auto‑generated)
├── requirements.txt           # Generated from uv.lock for pip users
└── README.md                  # You are here 📖
```

## Contributing — Bugs & Feature Requests

Spotted a bug, need another backend, or fancy streaming‑token support?

* **Bug?**  [Open an issue](https://github.com/nehalvaghasiya/llm-client-toolkit/issues) with a minimal, reproducible example.
* **Feature?**  Describe the use‑case; PRs are welcome once we agree on the scope.

