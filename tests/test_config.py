import os
import sys
import types
import unittest
from unittest.mock import patch

from grid07_ai_agent.config import AppConfig, config_status, load_config
from grid07_ai_agent.llm import describe_llm_provider, run_gemini_smoke_test


class ConfigTest(unittest.TestCase):
    def test_defaults_to_local_provider(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = load_config(env_path=".env.missing")

        self.assertEqual(config.llm_provider, "local")
        self.assertTrue(config.is_provider_ready)

    def test_openai_requires_key(self) -> None:
        config = AppConfig(llm_provider="openai")

        self.assertIn("OPENAI_API_KEY is required", config.validation_messages()[0])
        self.assertFalse(config_status(config)["provider_ready"])

    def test_provider_plan_is_secret_safe(self) -> None:
        config = AppConfig(llm_provider="groq", groq_api_key="secret")
        plan = describe_llm_provider(config)

        self.assertEqual(plan.provider, "groq")
        self.assertEqual(plan.package, "langchain-groq")
        self.assertTrue(plan.ready)

    def test_gemini_requires_key(self) -> None:
        config = AppConfig(llm_provider="gemini")

        self.assertIn("GEMINI_API_KEY is required", config.validation_messages()[0])
        self.assertFalse(config_status(config)["provider_ready"])

    def test_gemini_smoke_test_disables_thinking(self) -> None:
        captured = {}

        class FakeThinkingConfig:
            def __init__(self, thinking_budget: int) -> None:
                captured["thinking_budget"] = thinking_budget

        class FakeGenerateContentConfig:
            def __init__(self, **kwargs) -> None:
                captured["generate_config"] = kwargs

        class FakeModels:
            def generate_content(self, **kwargs):
                captured["request"] = kwargs
                return types.SimpleNamespace(text="OK")

        class FakeClient:
            def __init__(self, api_key: str | None = None) -> None:
                captured["api_key_set"] = bool(api_key)
                self.models = FakeModels()

        fake_google = types.ModuleType("google")
        fake_genai = types.ModuleType("google.genai")
        fake_types = types.SimpleNamespace(
            GenerateContentConfig=FakeGenerateContentConfig,
            ThinkingConfig=FakeThinkingConfig,
        )
        fake_genai.Client = FakeClient
        fake_genai.types = fake_types
        fake_google.genai = fake_genai

        with patch.dict(
            sys.modules,
            {
                "google": fake_google,
                "google.genai": fake_genai,
            },
        ):
            result = run_gemini_smoke_test(
                AppConfig(llm_provider="gemini", gemini_api_key="secret")
            )

        self.assertEqual(result["text"], "OK")
        self.assertTrue(captured["api_key_set"])
        self.assertEqual(captured["thinking_budget"], 0)
        self.assertEqual(captured["generate_config"]["max_output_tokens"], 3)


if __name__ == "__main__":
    unittest.main()
