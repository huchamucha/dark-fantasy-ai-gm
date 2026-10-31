from enum import Enum


class Ability(str, Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


def get_modifier(score: int) -> int:
    """Вычисляет модификатор характеристики."""
    if not 1 <= score <= 30:
        raise ValueError("Характеристика должна быть от 1 до 30")

    return (score - 10) // 2


def validate_attributes(attributes: dict[str, int]) -> None:
    """Проверяет наличие и допустимые значения шести характеристик."""
    required = {ability.value for ability in Ability}

    if set(attributes) != required:
        raise ValueError("Необходимо указать ровно шесть характеристик")

    for name, score in attributes.items():
        if not isinstance(score, int) or isinstance(score, bool):
            raise ValueError(f"{name}: значение должно быть целым числом")

        if not 1 <= score <= 30:
            raise ValueError(f"{name}: значение должно быть от 1 до 30")
