
import unittest

from pydantic import ValidationError

from app.actions.schemas import ActionProposal, ActionType


class TestActionSchema(unittest.TestCase):

    def test_valid_attack_action(self):
        action = ActionProposal(
            action_type=ActionType.ATTACK,
            intent="Ранить противника",
            method="Обманный замах с последующим ударом по ноге",
            target_id="enemy_1",
            technique_ids=["feint"],
            skill_candidates=["deception", "melee_combat"],
            tactical_description="Попытка заставить противника преждевременно поднять оружие",
        )

        self.assertEqual(action.action_type, ActionType.ATTACK)
        self.assertEqual(action.target_id, "enemy_1")
        self.assertIn("feint", action.technique_ids)

    def test_valid_non_combat_action(self):
        action = ActionProposal(
            action_type=ActionType.DIALOGUE,
            intent="Убедить стражника пропустить героя",
            method="Спокойно объяснить причину визита",
        )

        self.assertEqual(action.action_type, ActionType.DIALOGUE)
        self.assertEqual(action.technique_ids, [])

    def test_reject_unknown_action_type(self):
        with self.assertRaises(ValidationError):
            ActionProposal(
                action_type="destroy_world",
                intent="Что-то сделать",
                method="Неизвестный способ",
            )

    def test_reject_unknown_fields(self):
        with self.assertRaises(ValidationError):
            ActionProposal(
                action_type="attack",
                intent="Атаковать",
                method="Ударить мечом",
                damage_bonus=1000,
            )

    def test_reject_empty_intent(self):
        with self.assertRaises(ValidationError):
            ActionProposal(
                action_type="attack",
                intent="",
                method="Ударить мечом",
            )

    def test_reject_too_many_techniques(self):
        with self.assertRaises(ValidationError):
            ActionProposal(
                action_type="attack",
                intent="Атаковать",
                method="Комбинированная атака",
                technique_ids=[f"technique_{i}" for i in range(11)],
            )


if __name__ == "__main__":
    unittest.main()
