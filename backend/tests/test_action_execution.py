import unittest

from app.actions.execution import (
    ExecutionContext,
    ExecutionStatus,
    execute_action_sequence,
)
from app.actions.schemas import ActionProposal, ActionStep, ActionType


def make_proposal(*steps):
    return ActionProposal(
        action_type=steps[0].action_type if steps else ActionType.OTHER,
        intent="Проверка движка",
        method="Тестовое действие",
        action_sequence=list(steps),
    )


def make_step(number, action_type, description):
    return ActionStep(
        step=number,
        action_type=action_type,
        description=description,
    )


class TestActionExecution(unittest.TestCase):
    def test_attack_spends_br(self):
        proposal = make_proposal(
            make_step(1, ActionType.ATTACK, "Атакую противника")
        )

        result = execute_action_sequence(proposal)

        self.assertEqual(result.spent_br, 50)
        self.assertEqual(result.remaining_br, 50)
        self.assertEqual(result.steps[0].status, ExecutionStatus.EXECUTED)

    def test_blocked_action_does_not_spend_br_and_continues(self):
        proposal = make_proposal(
            make_step(1, ActionType.INTERACT, "Подбираю палку"),
            make_step(2, ActionType.MOVE, "Делаю шаг в сторону"),
        )

        context = ExecutionContext(
            current_br=100,
            blocked_steps={1: "Палки нет в доступном окружении"},
        )

        result = execute_action_sequence(proposal, context)

        self.assertEqual(result.steps[0].status, ExecutionStatus.BLOCKED)
        self.assertEqual(result.steps[1].status, ExecutionStatus.EXECUTED)
        self.assertEqual(result.spent_br, 15)
        self.assertEqual(result.remaining_br, 85)

    def test_insufficient_br_stops_remaining_sequence(self):
        proposal = make_proposal(
            make_step(1, ActionType.ATTACK, "Атакую противника"),
            make_step(2, ActionType.ATTACK, "Провожу вторую атаку"),
            make_step(3, ActionType.MOVE, "Отхожу назад"),
        )

        context = ExecutionContext(current_br=70)
        result = execute_action_sequence(proposal, context)

        self.assertEqual(result.steps[0].status, ExecutionStatus.EXECUTED)
        self.assertEqual(
            result.steps[1].status,
            ExecutionStatus.INSUFFICIENT_BR,
        )
        self.assertEqual(result.steps[2].status, ExecutionStatus.NOT_REACHED)
        self.assertEqual(result.spent_br, 50)
        self.assertEqual(result.remaining_br, 20)

    def test_br_never_becomes_negative(self):
        proposal = make_proposal(
            make_step(1, ActionType.ATTACK, "Атакую"),
            make_step(2, ActionType.ATTACK, "Атакую ещё раз"),
        )

        result = execute_action_sequence(
            proposal,
            ExecutionContext(current_br=30),
        )

        self.assertGreaterEqual(result.remaining_br, 0)
        self.assertEqual(result.spent_br, 0)

    def test_invalid_initial_br_is_rejected(self):
        proposal = make_proposal(
            make_step(1, ActionType.MOVE, "Двигаюсь"),
        )

        with self.assertRaises(ValueError):
            execute_action_sequence(
                proposal,
                ExecutionContext(current_br=101),
            )

    def test_empty_sequence(self):
        proposal = make_proposal()

        result = execute_action_sequence(proposal)

        self.assertEqual(result.spent_br, 0)
        self.assertEqual(result.remaining_br, 100)
        self.assertEqual(result.steps, [])


if __name__ == "__main__":
    unittest.main()
