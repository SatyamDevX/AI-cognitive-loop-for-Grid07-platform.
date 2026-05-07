import json
import unittest

from grid07_ai_agent.content_engine import (
    generate_opinionated_post,
    generate_opinionated_post_json,
    mock_searxng_search,
)


class ContentEngineTest(unittest.TestCase):
    def test_mock_search_returns_keyword_specific_news(self) -> None:
        result = mock_searxng_search("crypto bitcoin ETF")

        self.assertIn("Bitcoin", result)
        self.assertIn("ETF", result)

    def test_generates_strict_json_shape(self) -> None:
        generated = generate_opinionated_post("bot_b")

        self.assertEqual(set(generated), {"bot_id", "topic", "post_content"})
        self.assertEqual(generated["bot_id"], "bot_b")
        self.assertLessEqual(len(generated["post_content"]), 280)

    def test_json_text_is_parseable(self) -> None:
        payload = json.loads(generate_opinionated_post_json("bot_c"))

        self.assertEqual(payload["bot_id"], "bot_c")
        self.assertIsInstance(payload["topic"], str)
        self.assertIsInstance(payload["post_content"], str)


if __name__ == "__main__":
    unittest.main()
