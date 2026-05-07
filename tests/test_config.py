import json
import os
import sys
import types
import unittest
from unittest.mock import patch

from grid07_ai_agent.config import AppConfig, config_status, load_config
from grid07_ai_agent.llm import describe_llm_provider, generate_gemini_post, run_gemini_smoke_test
from grid07_ai_agent.personas import find_persona_by_id


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

    def test_gemini_post_generation_uses_json_and_small_budget(self) -> None:
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
                return types.SimpleNamespace(
                    text=(
                        '{"bot_id":"bot_a","topic":"AI coding acceleration",'
                        '"post_content":"AI tooling is compounding. Build faster."}'
                    )
                )

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

        with patch.dict(sys.modules, {"google": fake_google, "google.genai": fake_genai}):
            result = generate_gemini_post(
                AppConfig(llm_provider="gemini", gemini_api_key="secret"),
                find_persona_by_id("bot_a"),
                "AI coding acceleration",
                "OpenAI releases a faster coding model.",
            )

        self.assertEqual(result["bot_id"], "bot_a")
        self.assertTrue(captured["api_key_set"])
        self.assertEqual(captured["thinking_budget"], 0)
        self.assertEqual(captured["generate_config"]["response_mime_type"], "application/json")
        self.assertEqual(captured["generate_config"]["max_output_tokens"], 90)

    def test_gemini_post_generation_trims_long_post_content(self) -> None:
        captured = {}
        long_post = "x" * 320

        class FakeThinkingConfig:
            def __init__(self, thinking_budget: int) -> None:
                captured["thinking_budget"] = thinking_budget

        class FakeGenerateContentConfig:
            def __init__(self, **kwargs) -> None:
                captured["generate_config"] = kwargs

        class FakeModels:
            def generate_content(self, **kwargs):
                return types.SimpleNamespace(
                    text=json.dumps(
                        {
                            "bot_id": "bot_b",
                            "topic": "AI labor displacement and tech monopoly power",
                            "post_content": long_post,
                        }
                    )
                )

        class FakeClient:
            def __init__(self, api_key: str | None = None) -> None:
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

        with patch.dict(sys.modules, {"google": fake_google, "google.genai": fake_genai}):
            result = generate_gemini_post(
                AppConfig(llm_provider="gemini", gemini_api_key="secret"),
                find_persona_by_id("bot_b"),
                "AI labor displacement and tech monopoly power",
                "OpenAI releases a faster coding model.",
            )

        self.assertLessEqual(len(result["post_content"]), 280)
        self.assertTrue(result["post_content"].endswith("..."))


if __name__ == "__main__":
    unittest.main()
