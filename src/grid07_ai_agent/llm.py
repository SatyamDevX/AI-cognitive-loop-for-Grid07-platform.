"""Provider selection helpers for future LLM-backed graph nodes."""

from __future__ import annotations

import json
from dataclasses import dataclass

from grid07_ai_agent.config import AppConfig
from grid07_ai_agent.personas import BotPersona


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


def generate_gemini_post(
    config: AppConfig,
    bot: BotPersona,
    topic: str,
    search_results: str,
    model: str = "gemini-2.5-flash",
) -> dict[str, str]:
    """Generate one strict JSON post with Gemini using a tight token budget."""

    if config.llm_provider != "gemini":
        raise ValueError("Set LLM_PROVIDER=gemini before running Gemini generation.")
    messages = config.validation_messages()
    if messages:
        raise ValueError(" ".join(messages))

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError("Install google-genai with `python3 -m pip install -r requirements.txt`.") from exc

    client = genai.Client(api_key=config.gemini_api_key)
    prompt = _build_gemini_post_prompt(bot, topic, search_results)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            max_output_tokens=120,
            temperature=0.4,
            candidate_count=1,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return _parse_generated_post_json(response.text or "", expected_bot_id=bot.bot_id)


def _build_gemini_post_prompt(bot: BotPersona, topic: str, search_results: str) -> str:
    return (
        "Create one highly opinionated social post for this bot persona.\n"
        "Return only strict JSON with exactly these keys: bot_id, topic, post_content.\n"
        "Rules: post_content must be 280 characters or fewer. No markdown. No extra keys.\n\n"
        f"bot_id: {bot.bot_id}\n"
        f"persona name: {bot.name}\n"
        f"persona: {bot.description}\n"
        f"topic: {topic}\n"
        f"search context: {search_results}\n"
    )


def _parse_generated_post_json(raw_text: str, expected_bot_id: str) -> dict[str, str]:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Gemini did not return valid JSON: {raw_text!r}") from exc

    required_keys = {"bot_id", "topic", "post_content"}
    if set(payload) != required_keys:
        raise ValueError(f"Gemini JSON must contain exactly {sorted(required_keys)}")
    if payload["bot_id"] != expected_bot_id:
        raise ValueError(f"Gemini returned unexpected bot_id: {payload['bot_id']!r}")
    if len(payload["post_content"]) > 280:
        raise ValueError("Gemini post_content exceeds 280 characters")
    for key in required_keys:
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise ValueError(f"Gemini field is empty: {key}")
    return payload
