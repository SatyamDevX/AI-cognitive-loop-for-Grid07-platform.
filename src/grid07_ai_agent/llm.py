"""Provider selection helpers for future LLM-backed graph nodes."""

from __future__ import annotations

from dataclasses import dataclass

from grid07_ai_agent.config import AppConfig


@dataclass(frozen=True)
class LLMProviderPlan:
    """Secret-safe description of the provider that would be used."""

    provider: str
    package: str | None
    model_family: str
    ready: bool


def describe_llm_provider(config: AppConfig) -> LLMProviderPlan:
    """Describe the configured provider without constructing network clients."""

    if config.llm_provider == "openai":
        return LLMProviderPlan(
            provider="openai",
            package="langchain-openai",
            model_family="OpenAI chat/completions model",
            ready=config.is_provider_ready,
        )
    if config.llm_provider == "groq":
        return LLMProviderPlan(
            provider="groq",
            package="langchain-groq",
            model_family="Groq-hosted chat model",
            ready=config.is_provider_ready,
        )
    if config.llm_provider == "ollama":
        return LLMProviderPlan(
            provider="ollama",
            package="langchain",
            model_family="Local Ollama chat model",
            ready=config.is_provider_ready,
        )
    return LLMProviderPlan(
        provider=config.llm_provider,
        package=None,
        model_family="Deterministic local prototype",
        ready=config.is_provider_ready,
    )

