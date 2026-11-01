import unittest

from app.actions.schemas import ActionProposal, ActionStep, ActionType
from app.actions.validation import (
    ActionValidationContext,
    ValidationStatus,
    validate_action_sequence,
)


def make_step(number, action_type, description, target_id=None):
    return ActionStep(
        step=number,
        action_type=action_type,
        description=description,
        target_id=target_id,
    )


def make_proposal(*steps):
    return ActionProposal(
        action_type=steps[0].action_type if steps else ActionType.OTHER,
        intent="Проверка валидации",
        method="Тестовое действие",
        action_sequence=list(steps),
    )


class TestActionValidation(unittest.TestCase):
    def test_valid_actions(self):
        proposal = make_proposal(
            make_step(1, ActionType.ATTACK, "Атакую противника"),
            make_step(2, ActionType.MOVE, "Отхожу назад"),
        )

        result = validate_action_sequence(proposal)

        self.assertEqual(result.valid_steps, 2)
        self.assertEqual(result.blocked_steps, 0)

    def test_restrained_character_cannot_move(self):
        proposal = make_proposal(
            make_step(1, ActionType.MOVE, "Пытаюсь отойти"),
        )

        context = ActionValidationContext(is_restrained=True)
        result = validate_action_sequence(proposal, context)

        self.assertEqual(result.steps[0].status, ValidationStatus.BLOCKED)
        self.assertIn("скован", result.steps[0].reason)

    def test_missing_item_blocks_use(self):
        proposal = make_proposal(
            make_step(
                1,
                ActionType.USE_ITEM,
                "Использую зелье",
                target_id="potion_01",
            ),
        )

        result = validate_action_sequence(
            proposal,
            ActionValidationContext(inventory_item_ids=set()),
        )

        self.assertEqual(result.steps[0].status, ValidationStatus.BLOCKED)
        self.assertIn("инвентаре", result.steps[0].reason)

    def test_available_item_can_be_used(self):
        proposal = make_proposal(
            make_step(
                1,
                ActionType.USE_ITEM,
                "Использую зелье",
                target_id="potion_01",
            ),
        )

        context = ActionValidationContext(
            inventory_item_ids={"potion_01"},
        )
        result = validate_action_sequence(proposal, context)

        self.assertEqual(result.steps[0].status, ValidationStatus.VALID)

    def test_inaccessible_target_blocks_attack(self):
        proposal = make_proposal(
            make_step(
                1,
                ActionType.ATTACK,
                "Атакую врага",
                target_id="enemy_01",
            ),
        )

        result = validate_action_sequence(
            proposal,
            ActionValidationContext(accessible_target_ids=set()),
        )

        self.assertEqual(result.steps[0].status, ValidationStatus.BLOCKED)

    def test_blocked_step_does_not_cancel_next_step(self):
        proposal = make_proposal(
            make_step(1, ActionType.MOVE, "Пытаюсь двигаться"),
            make_step(2, ActionType.DIALOGUE, "Кричу противнику"),
        )

        context = ActionValidationContext(is_restrained=True)
        result = validate_action_sequence(proposal, context)

        self.assertEqual(result.steps[0].status, ValidationStatus.BLOCKED)
        self.assertEqual(result.steps[1].status, ValidationStatus.VALID)

    def test_unconscious_character_cannot_act(self):
        proposal = make_proposal(
            make_step(1, ActionType.ATTACK, "Пытаюсь атаковать"),
        )

        context = ActionValidationContext(is_conscious=False)
        result = validate_action_sequence(proposal, context)

        self.assertEqual(result.steps[0].status, ValidationStatus.BLOCKED)

    def test_lack_of_skill_does_not_block_action(self):
        proposal = make_proposal(
            make_step(1, ActionType.ATTACK, "Бросаю меч во врага"),
        )

        result = validate_action_sequence(proposal)

        self.assertEqual(result.steps[0].status, ValidationStatus.VALID)


if __name__ == "__main__":
    unittest.main()
