from pydantic import BaseModel, Field

from app.actions.combat_observation import (
    AttackIntent,
    DefenderObservation,
    ObservationContext,
    ObservationQuality,
    ReactionAssessment,
    assess_reaction,
)
from app.actions.combat_timing import (
    AttackTiming,
    ReactionContext,
    ReactionResult,
    ReactionType,
    can_react,
)


class CombatReactionRequest(BaseModel):
    """
    Запрос на обработку защитной реакции.

    AttackIntent — внутренний замысел атакующего.
    DefenderObservation — информация, доступная защитнику.
    Эти данные не смешиваются.
    """

    attack_intent: AttackIntent
    attack_timing: AttackTiming
    defender_observation: DefenderObservation
    defender_context: ReactionContext
    observation_context: ObservationContext
    reaction_type: ReactionType

    br_cost: int = Field(default=25, ge=0)
    stamina_cost: int = Field(default=5, ge=0)


class CombatReactionResult(BaseModel):
    available: bool
    reaction_type: ReactionType
    timing_result: ReactionResult
    assessment: ReactionAssessment | None = None
    reason: str


def process_combat_reaction(
    request: CombatReactionRequest,
) -> CombatReactionResult:
    """
    Проверяет возможность защитной реакции.

    Не рассчитывает попадание, урон или изменение состояния.
    Не раскрывает защитнику полный замысел атакующего.
    """

    # Сначала проверяем время реакции и ресурсы.
    timing_result = can_react(
        attack=request.attack_timing,
        defender=request.defender_context,
        reaction_type=request.reaction_type,
        br_cost=request.br_cost,
        stamina_cost=request.stamina_cost,
    )

    if not timing_result.available:
        return CombatReactionResult(
            available=False,
            reaction_type=request.reaction_type,
            timing_result=timing_result,
            reason=timing_result.reason,
        )

    # Работаем только с информацией, доступной защитнику.
    observation = request.defender_observation.model_copy(deep=True)

    context = request.observation_context

    if context.visibility <= 0:
        observation.quality = ObservationQuality.NONE
        observation.confidence = 0.0

    elif context.is_distracted:
        observation.quality = ObservationQuality.POOR
        observation.confidence = min(observation.confidence, 0.25)

    assessment = assess_reaction(
        observation=observation,
        reaction=request.reaction_type.value,
    )

    if not assessment.matches_observation:
        return CombatReactionResult(
            available=False,
            reaction_type=request.reaction_type,
            timing_result=timing_result,
            assessment=assessment,
            reason=assessment.reason,
        )

    return CombatReactionResult(
        available=True,
        reaction_type=request.reaction_type,
        timing_result=timing_result,
        assessment=assessment,
        reason="Защитник успел заметить атаку и может выполнить выбранную реакцию.",
    )
