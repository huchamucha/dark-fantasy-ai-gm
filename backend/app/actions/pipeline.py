
from dataclasses import dataclass
from typing import Optional

from app.actions.execution import (
    ExecutionContext,
    ExecutionResult,
    execute_action_sequence,
)
from app.actions.interpreter import interpret_action
from app.actions.schemas import ActionProposal
from app.actions.validation import (
    ActionValidationContext,
    ValidationResult,
    ValidationStatus,
    validate_action_sequence,
)


@dataclass
class ActionPipelineContext:
    """Общий контекст обработки действий."""

    validation: ActionValidationContext
    execution: ExecutionContext


@dataclass
class ActionPipelineResult:
    """Полный результат обработки действия игрока."""

    proposal: ActionProposal
    validation: ValidationResult
    execution: ExecutionResult


async def process_player_action(
    player_action: str,
    world_context: Optional[dict] = None,
    pipeline_context: Optional[ActionPipelineContext] = None,
) -> ActionPipelineResult:
    """
    Полный цикл обработки действия игрока:

    1. Интерпретация свободного текста.
    2. Проверка физической возможности действий.
    3. Расчёт затрат БР и выносливости.
    """

    if not player_action or not player_action.strip():
        raise ValueError("Действие игрока не может быть пустым")

    context = pipeline_context or ActionPipelineContext(
        validation=ActionValidationContext(),
        execution=ExecutionContext(),
    )

    proposal = await interpret_action(
        player_action=player_action,
        world_context=world_context or {},
    )

    validation = validate_action_sequence(
        proposal=proposal,
        context=context.validation,
    )

    blocked_steps = {
        step.step: step.reason or "Действие невозможно"
        for step in validation.steps
        if step.status == ValidationStatus.BLOCKED
    }

    execution_context = ExecutionContext(
        current_br=context.execution.current_br,
        current_stamina=context.execution.current_stamina,
        blocked_steps=blocked_steps,
    )

    execution = execute_action_sequence(
        proposal=proposal,
        context=execution_context,
    )

    return ActionPipelineResult(
        proposal=proposal,
        validation=validation,
        execution=execution,
    )
