from enum import Enum

from pydantic import BaseModel, Field


class AttackIntent(BaseModel):
    """
    Полный замысел атаки.

    Доступен атакующему и внутренней логике боевой системы.
    Не должен напрямую передаваться защитнику.
    """

    intended_attack: str = Field(min_length=1)
    intended_target: str | None = None
    follow_up: str | None = None
    feints: list[str] = Field(default_factory=list)
    tactical_goal: str | None = None


class ObservationQuality(str, Enum):
    NONE = "none"
    POOR = "poor"
    PARTIAL = "partial"
    CLEAR = "clear"


class DefenderObservation(BaseModel):
    """
    Только та информация, которую защитник действительно заметил.
    Здесь нет скрытого замысла атакующего.
    """

    visible_movement: str = Field(min_length=1)
    apparent_attack: str | None = None
    apparent_target: str | None = None
    quality: ObservationQuality = ObservationQuality.PARTIAL
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    observed_signals: list[str] = Field(default_factory=list)


class ObservationContext(BaseModel):
    perception: int = Field(default=0, ge=0)
    awareness: int = Field(default=0, ge=0)
    combat_experience: int = Field(default=0, ge=0)
    visibility: float = Field(default=1.0, ge=0.0, le=1.0)
    distance: float = Field(default=1.0, ge=0.0)
    is_distracted: bool = False


class ReactionAssessment(BaseModel):
    """
    Оценка того, насколько выбранная защитником реакция
    соответствует замеченным им сигналам.
    """

    reaction: str = Field(min_length=1)
    matches_observation: bool
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)


def assess_reaction(
    observation: DefenderObservation,
    reaction: str,
) -> ReactionAssessment:
    """
    Проверяет соответствие реакции наблюдаемым признакам.

    Не раскрывает настоящий замысел атакующего и пока
    не рассчитывает успешность защиты.
    """

    normalized_reaction = reaction.strip().lower()

    if not normalized_reaction:
        return ReactionAssessment(
            reaction=reaction,
            matches_observation=False,
            reason="Тип реакции не указан.",
            confidence=0.0,
        )

    if observation.quality == ObservationQuality.NONE:
        return ReactionAssessment(
            reaction=reaction,
            matches_observation=False,
            reason="Защитник не заметил достаточно признаков для осмысленного выбора.",
            confidence=0.0,
        )

    apparent_attack = (observation.apparent_attack or "").lower()
    apparent_target = (observation.apparent_target or "").lower()

    if normalized_reaction in {"block", "parry", "блок", "парирование"}:
        if not apparent_attack and not apparent_target:
            return ReactionAssessment(
                reaction=reaction,
                matches_observation=False,
                reason="Защитник не смог определить направление или характер атаки.",
                confidence=0.2,
            )

        return ReactionAssessment(
            reaction=reaction,
            matches_observation=True,
            reason="Защитник заметил признаки атаки и может выбрать защиту оружием.",
            confidence=observation.confidence,
        )

    if normalized_reaction in {
        "dodge",
        "step_back",
        "step_left",
        "step_right",
        "уклонение",
        "шаг назад",
        "шаг влево",
        "шаг вправо",
    }:
        return ReactionAssessment(
            reaction=reaction,
            matches_observation=True,
            reason="Защитник заметил движение и может попытаться изменить своё положение.",
            confidence=observation.confidence,
        )

    return ReactionAssessment(
        reaction=reaction,
        matches_observation=False,
        reason="Для этой реакции пока не определено соответствие наблюдаемым признакам.",
        confidence=0.0,
    )
