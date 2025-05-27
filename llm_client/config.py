from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """
    Pydantic-powered configuration model.
    Unknown keys are preserved so backend-specific options pass through untouched.
    """

    # core knobs
    model: str = Field(..., description="Backend model name, e.g. 'gpt-4o-mini'")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1024, gt=0)

    # transport / auth
    api_key: Optional[str] = Field(
        default=None,
        env="OPENAI_API_KEY",
        description="If omitted we fall back to env var OPENAI_API_KEY",
    )
    base_url: Optional[str] = Field(
        default=None,
        env="OPENAI_BASE_URL",
        description="Override for custom gateways / proxies (e.g. Azure, local)",
    )
    timeout: Optional[int] = Field(30, gt=0, description="HTTP timeout (seconds)")

    # retry logic (used by RetryLLMClient)
    retry_count: int = Field(3, ge=0)

    class Config:
        extra = "allow"
        frozen = True

    @classmethod
    def from_yaml(cls, path: str | Path) -> "LLMConfig":
        data = yaml.safe_load(Path(path).read_text()) or {}
        return cls(**data)

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Bare-bones config that relies entirely on environment variables."""
        return cls(model="gpt-4o-mini")  # minimum required field
