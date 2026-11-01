
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import ValidationError

from app.actions.interpreter import (
    _extract_json,
    interpret_action,
)
from app.actions.schemas import ActionType


class TestActionInterpreter(unittest.IsolatedAsyncioTestCase):

    def test_extract_json(self):
        result = _extract_json(
            'Вот ответ:\n{"action_type": "attack", '
            '"intent": "Ранить врага", '
            '"method": "Ударить мечом"}'
        )
        self.assertEqual(result["action_type"], "attack")

    def test_extract_json_from_markdown(self):
        result = _extract_json(
            '```json\n{"action_type": "move", '
            '"intent": "Подойти", '
            '"method": "Переместиться"}\n```'
        )
        self.assertEqual(result["action_type"], "move")

    def test_reject_invalid_json(self):
        with self.assertRaises(ValueError):
            _extract_json("Это не JSON")

    async def _run_interpreter(self, contents, player_action):
        if isinstance(contents, str):
            contents = [contents]

        responses = []

        for content in contents:
            response = MagicMock()
            response.json.return_value = {
                "choices": [
                    {"message": {"content": content}}
                ]
            }
            response.raise_for_status = MagicMock()
            responses.append(response)

        client = MagicMock()
        client.post = AsyncMock(side_effect=responses)

        with patch(
            "app.actions.interpreter.httpx.AsyncClient"
        ) as client_class:
            client_class.return_value.__aenter__ = AsyncMock(
                return_value=client
            )
            client_class.return_value.__aexit__ = AsyncMock(
                return_value=False
            )

            result = await interpret_action(player_action)

        return result, client

    async def test_interpret_valid_action(self):
        response = """
        {
          "action_type": "attack",
          "intent": "Ранить противника",
          "method": "Ударить мечом"
        }
        """

        result, client = await self._run_interpreter(
            [response, response],
            "Бью врага мечом",
        )

        self.assertEqual(result.action_type, ActionType.ATTACK)
        self.assertEqual(result.intent, "Ранить противника")
        self.assertEqual(client.post.await_count, 2)

    async def test_interpret_complete_action_sequence(self):
        response = """
        {
          "action_type": "attack",
          "intent": "Атаковать противника",
          "method": "Последовательность действий",
          "action_sequence": [
            {
              "step": 1,
              "action_type": "attack",
              "description": "Бросаю камень в противника"
            },
            {
              "step": 2,
              "action_type": "interact",
              "description": "Подбираю палку с земли"
            },
            {
              "step": 3,
              "action_type": "move",
              "description": "Делаю шаг в сторону"
            },
            {
              "step": 4,
              "action_type": "attack",
              "description": "Пытаюсь сбить противника с ног палкой"
            }
          ]
        }
        """

        result, _ = await self._run_interpreter(
            [response, response],
            (
                "Бросаю камень в противника, затем подбираю с земли "
                "палку, делаю шаг в сторону и пытаюсь сбить его с ног."
            ),
        )

        self.assertEqual(len(result.action_sequence), 4)
        self.assertEqual(
            [step.step for step in result.action_sequence],
            [1, 2, 3, 4],
        )
        self.assertEqual(
            [step.action_type for step in result.action_sequence],
            [
                ActionType.ATTACK,
                ActionType.INTERACT,
                ActionType.MOVE,
                ActionType.ATTACK,
            ],
        )

    async def test_audit_recovers_missing_actions(self):
        incomplete_response = """
        {
          "action_type": "attack",
          "intent": "Бросить камень",
          "method": "Бросок камня",
          "action_sequence": [
            {
              "step": 1,
              "action_type": "attack",
              "description": "Бросаю камень в противника"
            }
          ]
        }
        """

        corrected_response = """
        {
          "action_type": "attack",
          "intent": "Атаковать противника",
          "method": "Последовательность действий",
          "action_sequence": [
            {
              "step": 1,
              "action_type": "attack",
              "description": "Бросаю камень в противника"
            },
            {
              "step": 2,
              "action_type": "interact",
              "description": "Подбираю палку с земли"
            },
            {
              "step": 3,
              "action_type": "move",
              "description": "Делаю шаг в сторону"
            },
            {
              "step": 4,
              "action_type": "attack",
              "description": "Пытаюсь сбить противника с ног палкой"
            }
          ]
        }
        """

        result, client = await self._run_interpreter(
            [incomplete_response, corrected_response],
            (
                "Бросаю камень в противника, затем подбираю с земли "
                "палку, делаю шаг в сторону и пытаюсь сбить его с ног."
            ),
        )

        self.assertEqual(client.post.await_count, 2)
        self.assertEqual(len(result.action_sequence), 4)

        self.assertEqual(
            [step.action_type for step in result.action_sequence],
            [
                ActionType.ATTACK,
                ActionType.INTERACT,
                ActionType.MOVE,
                ActionType.ATTACK,
            ],
        )

    async def test_reject_invalid_ai_response(self):
        invalid_response = """
        {
          "action_type": "destroy_world",
          "intent": "Уничтожить мир",
          "method": "Магия"
        }
        """

        with self.assertRaises(ValidationError):
            await self._run_interpreter(
                [invalid_response],
                "Атаковать врага",
            )


if __name__ == "__main__":
    unittest.main()
