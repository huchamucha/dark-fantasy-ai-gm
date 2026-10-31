from dataclasses import dataclass

from app.engine.attributes import get_modifier
from app.engine.dice import roll_die
from app.engine.skills import get_skill_ability


@dataclass(frozen=True)
class CheckResult:
    roll: int
    modifier: int
    proficiency_bonus: int
    extra_bonus: int
    total: int
    dc: int
    success: bool


def make_check(
    score: int,
    dc: int,
    proficient: bool = False,
    proficiency_bonus: int = 2,
    extra_bonus: int = 0,
    roll: int | None = None,
) -> CheckResult:
    """Выполняет проверку D20 против сложности DC."""

    if not isinstance(dc, int) or isinstance(dc, bool) or dc < 1:
        raise ValueError("DC должен быть положительным целым числом")

    if not isinstance(proficiency_bonus, int) or isinstance(proficiency_bonus, bool) or proficiency_bonus < 0:
        raise ValueError("Бонус мастерства не может быть отрицательным")

    if roll is None:
        roll = roll_die(20)

    if not isinstance(roll, int) or isinstance(roll, bool) or not 1 <= roll <= 20:
        raise ValueError("Результат D20 должен быть от 1 до 20")

    modifier = get_modifier(score)
    proficiency = proficiency_bonus if proficient else 0
    total = roll + modifier + proficiency + extra_bonus

    return CheckResult(
        roll=roll,
        modifier=modifier,
        proficiency_bonus=proficiency,
        extra_bonus=extra_bonus,
        total=total,
        dc=dc,
        success=total >= dc,
    )


def make_skill_check(
    skill: str,
    attributes: dict[str, int],
    proficient_skills: list[str],
    dc: int,
    proficiency_bonus: int = 2,
    extra_bonus: int = 0,
    roll: int | None = None,
) -> CheckResult:
    """Выполняет проверку конкретного навыка."""

    ability = get_skill_ability(skill)

    if ability.value not in attributes:
        raise ValueError(f"Отсутствует характеристика {ability.value}")

    return make_check(
        score=attributes[ability.value],
        dc=dc,
        proficient=skill in proficient_skills,
        proficiency_bonus=proficiency_bonus,
        extra_bonus=extra_bonus,
        roll=roll,
    )
