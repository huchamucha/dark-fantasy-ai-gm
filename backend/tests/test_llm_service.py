import unittest

from app.services.llm_service import DEFAULT_FALLBACK, parse_json


class LLMServiceParsingTests(unittest.TestCase):
    def test_valid_narrative_is_preserved(self):
        result = parse_json('{"narrative":"NPC отвечает прямо.","outcome":"dialogue","summary":"Ответ NPC"}')
        self.assertEqual(result["narrative"], "NPC отвечает прямо.")
        self.assertEqual(result["outcome"], "dialogue")

    def test_model_cannot_change_character_stats_or_inventory(self):
        result = parse_json(
            '{"narrative":"Вы видите алтарь.","hp_change":-99,'
            '"stat_changes":{"will":100},"inventory_changes":['
            '{"action":"add","item":"несуществующий ключ"}],'
            '"world_flags":{"door_open":true}}'
        )
        self.assertEqual(result["hp_change"], 0)
        self.assertEqual(result["stat_changes"], {})
        self.assertEqual(result["inventory_changes"], [])
        self.assertEqual(result["world_flags"], {})

    def test_markdown_json_fence_is_supported(self):
        result = parse_json('```json\n{"narrative":"Туман рассеивается."}\n```')
        self.assertEqual(result["narrative"], "Туман рассеивается.")

    def test_invalid_json_returns_neutral_fallback(self):
        result = parse_json("это не JSON")
        self.assertEqual(result, DEFAULT_FALLBACK)
        self.assertEqual(result["hp_change"], 0)
        self.assertEqual(result["world_flags"], {})


if __name__ == "__main__":
    unittest.main()