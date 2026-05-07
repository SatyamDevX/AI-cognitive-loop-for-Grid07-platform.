import os
import unittest
from unittest.mock import patch

from grid07_ai_agent.config import AppConfig, config_status, load_config
from grid07_ai_agent.llm import describe_llm_provider


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


if __name__ == "__main__":
    unittest.main()
