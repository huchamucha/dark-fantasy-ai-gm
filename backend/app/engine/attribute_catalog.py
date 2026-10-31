from typing import Any

from app.engine.attributes import Ability


ATTRIBUTE_DEFINITIONS: dict[str, dict[str, Any]] = {
    Ability.STRENGTH.value: {
        "id": "strength",
        "name": "Сила",
        "description": "Физическая мощь персонажа.",
    },
    Ability.DEXTERITY.value: {
        "id": "dexterity",
        "name": "Ловкость",
        "description": "Координация, скорость и точность движений.",
    },
    Ability.CONSTITUTION.value: {
        "id": "constitution",
        "name": "Телосложение",
        "description": "Выносливость и сопротивляемость нагрузкам.",
    },
    Ability.INTELLIGENCE.value: {
        "id": "intelligence",
        "name": "Интеллект",
        "description": "Знания, логика и способность анализировать.",
    },
    Ability.WISDOM.value: {
        "id": "wisdom",
        "name": "Мудрость",
        "description": "Восприятие, интуиция и понимание окружающего мира.",
    },
    Ability.CHARISMA.value: {
        "id": "charisma",
        "name": "Харизма",
        "description": "Умение взаимодействовать и влиять на других.",
    },
}


def get_attribute_catalog(
    overrides: dict[str, dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Возвращает характеристики с необязательными названиями мира."""

    overrides = overrides or {}
    result = []

    for attribute_id, definition in ATTRIBUTE_DEFINITIONS.items():
        custom = overrides.get(attribute_id, {})

        result.append({
            **definition,
            "name": custom.get("name", definition["name"]),
            "description": custom.get(
                "description",
                definition["description"],
            ),
        })

    unknown_ids = set(overrides) - set(ATTRIBUTE_DEFINITIONS)

    if unknown_ids:
        raise ValueError(
            f"Неизвестные характеристики: {', '.join(sorted(unknown_ids))}"
        )

    return result
