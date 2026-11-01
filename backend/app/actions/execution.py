
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.actions.schemas import ActionProposal, ActionStep, ActionType


class ExecutionStatus(str, Enum):
    EXECUTED = "executed"
    BLOCKED = "blocked"
    INSUFFICIENT_BR = "insufficient_br"
    INSUFFICIENT_STAMINA = "insufficient_stamina"
    NOT_REACHED = "not_reached"


class ActionCost(BaseModel):
    """Стоимость действия в боевом ресурсе и выносливости."""

    model_config = ConfigDict(extra="forbid")

    br: int = Field(ge=0, le=100)
    stamina: int = Field(default=0, ge=0)


class StepExecutionResult(BaseModel):
    """Результат обработки одного этапа."""

    step: int
    description: str
    action_type: ActionType
    status: ExecutionStatus

    br_cost: int = 0
    stamina_cost: int = 0
    br_remaining: int

    reason: Optional[str] = None


class ExecutionResult(BaseModel):
    """Итог исполнения последовательности действий."""

    initial_br: int
    spent_br: int
    remaining_br: int

    initial_stamina: int
    spent_stamina: int
    remaining_stamina: int

    steps: list[StepExecutionResult] = Field(default_factory=list)


@dataclass
class ExecutionContext:
    """Ресурсы и ограничения текущего исполнения."""

    current_br: int = 100
    current_stamina: int = 100
    blocked_steps: dict[int, str] = field(default_factory=dict)


def calculate_action_cost(step: ActionStep) -> ActionCost:
    """Предварительная стоимость действия."""

    description = step.description.lower()

    if step.action_type == ActionType.ATTACK:
        if any(word in description for word in ("комбинац", "мощн", "сложн")):
            return ActionCost(br=80, stamina=20)

        return ActionCost(br=50, stamina=10)

    if step.action_type == ActionType.DEFEND:
        return ActionCost(br=25, stamina=5)

    if step.action_type == ActionType.MOVE:
        if any(word in description for word in ("бег", "прыж", "рывок", "перекат")):
            return ActionCost(br=30, stamina=10)

        return ActionCost(br=15, stamina=3)

    if step.action_type == ActionType.INTERACT:
        if any(word in description for word in ("подбира", "беру с земли", "поднять с земли")):
            return ActionCost(br=20, stamina=2)

        return ActionCost(br=30, stamina=3)

    if step.action_type == ActionType.USE_ITEM:
        return ActionCost(br=20, stamina=0)

    if step.action_type == ActionType.STEALTH:
        return ActionCost(br=30, stamina=5)

    if step.action_type in {
        ActionType.PERCEPTION,
        ActionType.INVESTIGATION,
        ActionType.DIALOGUE,
    }:
        return ActionCost(br=10, stamina=0)

    if step.action_type in {
        ActionType.MEDICINE,
        ActionType.CRAFTING,
    }:
        return ActionCost(br=40, stamina=5)

    return ActionCost(br=20, stamina=2)


def execute_action_sequence(
    proposal: ActionProposal,
    context: Optional[ExecutionContext] = None,
) -> ExecutionResult:
    """
    Рассчитывает расходы ресурсов для последовательности действий.

    Заблокированные действия не расходуют ресурсы.
    При нехватке БР или выносливости последовательность останавливается.
    """

    context = context or ExecutionContext()

    if not 0 <= context.current_br <= 100:
        raise ValueError("current_br должен быть от 0 до 100")

    if context.current_stamina < 0:
        raise ValueError("current_stamina не может быть отрицательным")

    initial_br = context.current_br
    initial_stamina = context.current_stamina

    remaining_br = initial_br
    remaining_stamina = initial_stamina

    results: list[StepExecutionResult] = []
    stopped = False

    for step in proposal.action_sequence:
        if stopped:
            results.append(
                StepExecutionResult(
                    step=step.step,
                    description=step.description,
                    action_type=step.action_type,
                    status=ExecutionStatus.NOT_REACHED,
                    br_remaining=remaining_br,
                    reason="Предыдущий этап остановил последовательность",
                )
            )
            continue

        blocked_reason = context.blocked_steps.get(step.step)

        if blocked_reason:
            results.append(
                StepExecutionResult(
                    step=step.step,
                    description=step.description,
                    action_type=step.action_type,
                    status=ExecutionStatus.BLOCKED,
                    br_remaining=remaining_br,
                    reason=blocked_reason,
                )
            )
            continue

        cost = calculate_action_cost(step)

        if cost.br > remaining_br:
            results.append(
                StepExecutionResult(
                    step=step.step,
                    description=step.description,
                    action_type=step.action_type,
                    status=ExecutionStatus.INSUFFICIENT_BR,
                    br_remaining=remaining_br,
                    reason=(
                        f"Требуется {cost.br} БР, "
                        f"доступно {remaining_br} БР"
                    ),
                )
            )
            stopped = True
            continue

        if cost.stamina > remaining_stamina:
            results.append(
                StepExecutionResult(
                    step=step.step,
                    description=step.description,
                    action_type=step.action_type,
                    status=ExecutionStatus.INSUFFICIENT_STAMINA,
                    br_remaining=remaining_br,
                    reason=(
                        f"Требуется {cost.stamina} выносливости, "
                        f"доступно {remaining_stamina}"
                    ),
                )
            )
            stopped = True
            continue

        remaining_br -= cost.br
        remaining_stamina -= cost.stamina

        results.append(
            StepExecutionResult(
                step=step.step,
                description=step.description,
                action_type=step.action_type,
                status=ExecutionStatus.EXECUTED,
                br_cost=cost.br,
                stamina_cost=cost.stamina,
                br_remaining=remaining_br,
            )
        )

    return ExecutionResult(
        initial_br=initial_br,
        spent_br=initial_br - remaining_br,
        remaining_br=remaining_br,
        initial_stamina=initial_stamina,
        spent_stamina=initial_stamina - remaining_stamina,
        remaining_stamina=remaining_stamina,
        steps=results,
    )
