from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.actions.schemas import ActionProposal, ActionType


class ValidationStatus(str, Enum):
    VALID = "valid"
    BLOCKED = "blocked"


class StepValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: int
    description: str
    action_type: ActionType
    status: ValidationStatus
    reason: Optional[str] = None


class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valid_steps: int
    blocked_steps: int
    steps: list[StepValidationResult] = Field(default_factory=list)


@dataclass
class ActionValidationContext:
    """
    Состояние игрового мира, передаваемое системой.

    Все ID должны соответствовать ID объектов и персонажей
    в игровом состоянии.
    """

    is_alive: bool = True
    is_conscious: bool = True
    is_restrained: bool = False

    inventory_item_ids: set[str] = field(default_factory=set)
    accessible_target_ids: set[str] = field(default_factory=set)


def _validate_step(step, context: ActionValidationContext) -> Optional[str]:
    """
    Возвращает причину блокировки или None, если действие допустимо.
    """

    if not context.is_alive:
        return "Персонаж мёртв и не может выполнять действия"

    if not context.is_conscious:
        return "Персонаж без сознания"

    if (
        context.is_restrained
        and step.action_type in {
            ActionType.MOVE,
            ActionType.STEALTH,
        }
    ):
        return "Персонаж скован и не может свободно двигаться"

    if (
        step.action_type == ActionType.USE_ITEM
        and step.target_id
        and step.target_id not in context.inventory_item_ids
    ):
        return "Предмет отсутствует в инвентаре персонажа"

    if (
        step.action_type in {
            ActionType.ATTACK,
            ActionType.INTERACT,
        }
        and step.target_id
        and step.target_id not in context.accessible_target_ids
    ):
        return "Указанная цель недоступна персонажу"

    return None


def validate_action_sequence(
    proposal: ActionProposal,
    context: Optional[ActionValidationContext] = None,
) -> ValidationResult:
    """
    Проверяет физическую и ситуационную допустимость этапов.

    Заблокированный этап не отменяет последующие:
    каждое действие проверяется независимо.
    """

    context = context or ActionValidationContext()

    results: list[StepValidationResult] = []
    valid_count = 0
    blocked_count = 0

    for step in proposal.action_sequence:
        reason = _validate_step(step, context)

        if reason:
            status = ValidationStatus.BLOCKED
            blocked_count += 1
        else:
            status = ValidationStatus.VALID
            valid_count += 1

        results.append(
            StepValidationResult(
                step=step.step,
                description=step.description,
                action_type=step.action_type,
                status=status,
                reason=reason,
            )
        )

    return ValidationResult(
        valid_steps=valid_count,
        blocked_steps=blocked_count,
        steps=results,
    )
