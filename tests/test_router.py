import unittest

from grid07_ai_agent.router import route_post_to_bots


class RoutePostToBotsTest(unittest.TestCase):
    def test_routes_ai_post_to_tech_and_skeptic_personas(self) -> None:
        matches = route_post_to_bots(
            "OpenAI just released a new model that might replace junior developers.",
            threshold=0.35,
        )

        bot_ids = {match["bot_id"] for match in matches}

        self.assertIn("bot_a", bot_ids)
        self.assertIn("bot_b", bot_ids)
        self.assertNotIn("bot_c", bot_ids)

    def test_routes_finance_post_to_finance_bro(self) -> None:
        matches = route_post_to_bots(
            "The Fed held interest rates while trading algorithms chased market ROI.",
            threshold=0.45,
        )

        bot_ids = {match["bot_id"] for match in matches}

        self.assertEqual(bot_ids, {"bot_c"})

    def test_threshold_can_filter_all_matches(self) -> None:
        matches = route_post_to_bots("A quiet update about office snacks.", threshold=0.1)

        self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()
