from enum import Enum

from pydantic import BaseModel, Field


class AttackPhase(str, Enum):
    PREPARATION = "preparation"
    START_MOVEMENT = "start_movement"
    DEVELOPMENT = "development"
    IMPACT = "impact"
    COMPLETION = "completion"


class ReactionType(str, Enum):
    DODGE = "dodge"
    BLOCK = "block"
    PARRY = "parry"
    STEP_BACK = "step_back"
    STEP_LEFT = "step_left"
    STEP_RIGHT = "step_right"


class ReactionWindow(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    NARROW = "narrow"


class ObservableTelegraph(BaseModel):
    description: str = Field(min_length=1)
    visible_movement: str = Field(min_length=1)
    apparent_attack_type: str | None = None
    apparent_target: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class AttackTiming(BaseModel):
    phase: AttackPhase
    reaction_window: ReactionWindow
    telegraph: ObservableTelegraph | None = None
    commitment: float = Field(default=0.0, ge=0.0, le=1.0)


class ReactionContext(BaseModel):
    current_br: int = Field(ge=0)
    current_stamina: int = Field(ge=0)
    perception: int = Field(default=0, ge=0)
    reaction_skill: int = Field(default=0, ge=0)
    is_alive: bool = True
    is_conscious: bool = True
    is_restrained: bool = False
    can_move: bool = True


class ReactionResult(BaseModel):
    available: bool
    reaction_type: ReactionType
    reason: str
    br_cost: int = 0
    stamina_cost: int = 0
    observed_telegraph: ObservableTelegraph | None = None


def can_react(
    attack: AttackTiming,
    defender: ReactionContext,
    reaction_type: ReactionType,
    br_cost: int = 25,
    stamina_cost: int = 5,
) -> ReactionResult:
    """
    Определяет, может ли защитник начать реакцию на текущей фазе атаки.

    Функция пока не списывает ресурсы и не рассчитывает исход защиты.
    Она только проверяет доступность реакции.
    """

    def denied(reason: str) -> ReactionResult:
        return ReactionResult(
            available=False,
            reaction_type=reaction_type,
            reason=reason,
            observed_telegraph=attack.telegraph,
        )

    if not defender.is_alive:
        return denied("Персонаж мёртв.")

    if not defender.is_conscious:
        return denied("Персонаж без сознания.")

    if defender.is_restrained:
        return denied("Персонаж обездвижен.")

    if attack.reaction_window == ReactionWindow.CLOSED:
        return denied("Окно для новой реакции уже закрыто.")

    if attack.phase in (AttackPhase.IMPACT, AttackPhase.COMPLETION):
        return denied("Атака уже достигла завершающей фазы.")

    if attack.telegraph is None:
        return denied("Защитник не получил наблюдаемых сигналов атаки.")

    if reaction_type in (
        ReactionType.DODGE,
        ReactionType.STEP_BACK,
        ReactionType.STEP_LEFT,
        ReactionType.STEP_RIGHT,
    ) and not defender.can_move:
        return denied("Защитник не может перемещаться.")

    if br_cost < 0 or stamina_cost < 0:
        return denied("Стоимость реакции не может быть отрицательной.")

    if defender.current_br < br_cost:
        return denied("Недостаточно боевого ресурса.")

    if defender.current_stamina < stamina_cost:
        return denied("Недостаточно выносливости.")

    return ReactionResult(
        available=True,
        reaction_type=reaction_type,
        reason="Защитник успел заметить движение и может начать реакцию.",
        br_cost=br_cost,
        stamina_cost=stamina_cost,
        observed_telegraph=attack.telegraph,
    )
