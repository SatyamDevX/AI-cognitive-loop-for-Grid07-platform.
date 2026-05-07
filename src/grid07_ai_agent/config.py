"""Runtime configuration for provider-backed milestones."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_LLM_PROVIDERS = {"local", "openai", "groq", "gemini", "ollama"}


@dataclass(frozen=True)
class AppConfig:
    """Application configuration loaded from environment variables."""

    llm_provider: str = "local"
    openai_api_key: str | None = None
    groq_api_key: str | None = None
    gemini_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    @property
    def is_provider_ready(self) -> bool:
        if self.llm_provider == "openai":
            return bool(self.openai_api_key)
        if self.llm_provider == "groq":
            return bool(self.groq_api_key)
        if self.llm_provider == "gemini":
            return bool(self.gemini_api_key)
        return True

    def validation_messages(self) -> list[str]:
        messages: list[str] = []
        if self.llm_provider not in SUPPORTED_LLM_PROVIDERS:
            messages.append(
                f"Unsupported LLM_PROVIDER '{self.llm_provider}'. "
                f"Use one of: {', '.join(sorted(SUPPORTED_LLM_PROVIDERS))}."
            )
        if self.llm_provider == "openai" and not self.openai_api_key:
            messages.append("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")
        if self.llm_provider == "groq" and not self.groq_api_key:
            messages.append("GROQ_API_KEY is required when LLM_PROVIDER=groq.")
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            messages.append("GEMINI_API_KEY is required when LLM_PROVIDER=gemini.")
        if self.llm_provider == "ollama" and not self.ollama_base_url:
            messages.append("OLLAMA_BASE_URL is required when LLM_PROVIDER=ollama.")
        return messages


def load_config(env_path: str | Path = ".env") -> AppConfig:
    """Load configuration from `.env` when available, then environment."""

    _load_dotenv_if_available(env_path)
    return AppConfig(
        llm_provider=os.getenv("LLM_PROVIDER", "local").strip().lower(),
        openai_api_key=_optional_env("OPENAI_API_KEY"),
        groq_api_key=_optional_env("GROQ_API_KEY"),
        gemini_api_key=_optional_env("GEMINI_API_KEY"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip(),
    )


def config_status(config: AppConfig) -> dict[str, object]:
    """Return secret-safe configuration status for CLI/debug output."""

    messages = config.validation_messages()
    return {
        "llm_provider": config.llm_provider,
        "provider_ready": not messages and config.is_provider_ready,
        "openai_api_key_set": bool(config.openai_api_key),
        "groq_api_key_set": bool(config.groq_api_key),
        "gemini_api_key_set": bool(config.gemini_api_key),
        "ollama_base_url": config.ollama_base_url,
        "messages": messages,
    }


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        return None
    return value.strip()


def _load_dotenv_if_available(env_path: str | Path) -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(dotenv_path=env_path, override=False)
