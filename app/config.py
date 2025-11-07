from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"


def load_environment() -> None:
    """
    Load environment variables from a local .env file if present.

    This function is safe to call multiple times thanks to dotenv's internal caching.
    """
    load_dotenv(dotenv_path=ENV_PATH, override=False)


@dataclass
class Settings:
    """Central configuration for the invoice comparison agent."""

    openai_api_key: Optional[str]
    model_name: str = "gpt-4o-mini"
    # Temperature kept low for deterministic summaries, adjust via environment if needed
    model_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    @property
    def has_llm(self) -> bool:
        """Return True if an OpenAI API key is available."""
        return bool(self.openai_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load application settings once and cache the result."""
    load_environment()
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )

