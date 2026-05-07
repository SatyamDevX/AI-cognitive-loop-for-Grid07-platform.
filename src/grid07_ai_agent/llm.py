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
    if config.llm_provider == "gemini":
        return LLMProviderPlan(
            provider="gemini",
            package="google-genai",
            model_family="Gemini API model",
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


def run_gemini_smoke_test(config: AppConfig, model: str = "gemini-2.5-flash") -> dict[str, object]:
    """Make one tiny Gemini call to verify credentials and SDK wiring."""

    if config.llm_provider != "gemini":
        raise ValueError("Set LLM_PROVIDER=gemini before running the Gemini smoke test.")
    messages = config.validation_messages()
    if messages:
        raise ValueError(" ".join(messages))

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError("Install google-genai with `python3 -m pip install -r requirements.txt`.") from exc

    client = genai.Client(api_key=config.gemini_api_key)
    response = client.models.generate_content(
        model=model,
        contents="Reply with exactly one word: OK",
        config=types.GenerateContentConfig(
            max_output_tokens=3,
            temperature=0.0,
            candidate_count=1,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return {
        "provider": "gemini",
        "model": model,
        "prompt": "Reply with exactly one word: OK",
        "max_output_tokens": 3,
        "text": (response.text or "").strip(),
    }
