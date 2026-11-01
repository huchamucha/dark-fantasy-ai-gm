
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class ParryType(str, Enum):
    SIMPLE = "simple"
    COUNTER = "counter"


class ParryStatus(str, Enum):
    FAILED = "failed"
    PARRIED = "parried"
    COUNTERED = "countered"


class ParryRequest(BaseModel):
    """Намерение персонажа выполнить парирование."""

    parry_type: ParryType
    targeted_attack: str = Field(min_length=1, max_length=200)
    counter_attack: str | None = Field(default=None, max_length=200)
    br_cost: int = Field(ge=0)
    stamina_cost: int = Field(ge=0)
    success: bool

    @model_validator(mode="after")
    def validate_counter_attack(self):
        if self.parry_type == ParryType.COUNTER and not self.counter_attack:
            raise ValueError(
                "Для контратакующего парирования нужно указать ответный удар"
            )
        return self


class ParryResult(BaseModel):
    """Результат выполнения парирования."""

    status: ParryStatus
    success: bool
    br_spent: int
    stamina_spent: int
    counter_attack: str | None = None
    initiative_transferred: bool = False
    next_enemy_attack_modifier: int = 0
    reason: str


def resolve_parry(request: ParryRequest) -> ParryResult:
    """Определяет результат парирования без изменения игрового состояния."""

    if not request.success:
        return ParryResult(
            status=ParryStatus.FAILED,
            success=False,
            br_spent=request.br_cost,
            stamina_spent=request.stamina_cost,
            reason="Парирование не удалось.",
        )

    if request.parry_type == ParryType.SIMPLE:
        return ParryResult(
            status=ParryStatus.PARRIED,
            success=True,
            br_spent=request.br_cost,
            stamina_spent=request.stamina_cost,
            next_enemy_attack_modifier=1,
            reason=(
                "Атака успешно парирована. "
                "Следующая атака противника получает штраф сложности."
            ),
        )

    return ParryResult(
        status=ParryStatus.COUNTERED,
        success=True,
        br_spent=request.br_cost,
        stamina_spent=request.stamina_cost,
        counter_attack=request.counter_attack,
        initiative_transferred=True,
        reason=(
            "Контратакующее парирование успешно. "
            "Инициатива переходит защитнику."
        ),
    )
