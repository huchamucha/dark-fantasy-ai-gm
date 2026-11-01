import unittest
from unittest.mock import AsyncMock, patch

from app.actions.execution import ExecutionStatus
from app.actions.pipeline import (
    ActionPipelineContext,
    process_player_action,
)
from app.actions.schemas import ActionProposal, ActionStep, ActionType
from app.actions.validation import ActionValidationContext


def make_proposal():
    return ActionProposal(
        action_type=ActionType.ATTACK,
        intent="Атакую, подбираю предмет и отступаю",
        method="Последовательность действий",
        action_sequence=[
            ActionStep(
                step=1,
                action_type=ActionType.ATTACK,
                description="Атакую противника",
                target_id="enemy_01",
            ),
            ActionStep(
                step=2,
                action_type=ActionType.USE_ITEM,
                description="Использую зелье",
                target_id="potion_01",
            ),
            ActionStep(
                step=3,
                action_type=ActionType.MOVE,
                description="Отхожу назад",
            ),
        ],
    )


class TestActionPipeline(unittest.IsolatedAsyncioTestCase):

    @patch(
        "app.actions.pipeline.interpret_action",
        new_callable=AsyncMock,
    )
    async def test_full_pipeline(self, mock_interpret):
        mock_interpret.return_value = make_proposal()

        context = ActionPipelineContext(
            validation=ActionValidationContext(
                accessible_target_ids={"enemy_01"},
                inventory_item_ids={"potion_01"},
            ),
            execution=__import__(
                "app.actions.execution",
                fromlist=["ExecutionContext"],
            ).ExecutionContext(current_br=100),
        )

        result = await process_player_action(
            player_action="Атакую врага, использую зелье и отступаю",
            pipeline_context=context,
        )

        mock_interpret.assert_awaited_once()

        self.assertEqual(result.validation.valid_steps, 3)
        self.assertEqual(result.validation.blocked_steps, 0)

        self.assertEqual(result.execution.spent_br, 85)
        self.assertEqual(result.execution.remaining_br, 15)

        self.assertTrue(
            all(
                step.status == ExecutionStatus.EXECUTED
                for step in result.execution.steps
            )
        )

    @patch(
        "app.actions.pipeline.interpret_action",
        new_callable=AsyncMock,
    )
    async def test_blocked_action_does_not_consume_br(self, mock_interpret):
        mock_interpret.return_value = make_proposal()

        from app.actions.execution import ExecutionContext

        context = ActionPipelineContext(
            validation=ActionValidationContext(
                accessible_target_ids={"enemy_01"},
                inventory_item_ids=set(),
            ),
            execution=ExecutionContext(current_br=100),
        )

        result = await process_player_action(
            player_action="Атакую врага, использую зелье и отступаю",
            pipeline_context=context,
        )

        self.assertEqual(result.validation.valid_steps, 2)
        self.assertEqual(result.validation.blocked_steps, 1)

        self.assertEqual(
            result.execution.steps[1].status,
            ExecutionStatus.BLOCKED,
        )

        # Атака: 50 БР. Зелье заблокировано: 0 БР.
        # Движение: 15 БР.
        self.assertEqual(result.execution.spent_br, 65)
        self.assertEqual(result.execution.remaining_br, 35)

        self.assertEqual(
            result.execution.steps[2].status,
            ExecutionStatus.EXECUTED,
        )

    async def test_empty_action_is_rejected(self):
        with self.assertRaises(ValueError):
            await process_player_action("   ")


if __name__ == "__main__":
    unittest.main()
