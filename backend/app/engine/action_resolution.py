from typing import Any

from app.engine.skills import get_skill_ability
from app.engine.checks import make_skill_check


# Первая версия распознавания действий.
# Ключевые слова можно расширять по мере тестирования.
ACTION_RULES = [
    {
        "skill": "stealth",
        "keywords": (
            "незаметно", "скрытно", "прокрасться",
            "крадусь", "пробраться незаметно", "тихо пройти",
        ),
        "dc": 15,
    },
    {
        "skill": "perception",
        "keywords": (
            "осмотреться", "прислушаться", "осмотреть",
            "заметить", "ищу следы", "высматриваю",
        ),
        "dc": 12,
    },
    {
        "skill": "investigation",
        "keywords": (
            "исследовать механизм", "изучить руны",
            "разобраться в механизме", "обыскать",
            "изучить улики",
        ),
        "dc": 15,
    },
    {
        "skill": "persuasion",
        "keywords": (
            "убедить", "уговорить", "договориться",
            "убедить его", "убедить её",
        ),
        "dc": 15,
    },
    {
        "skill": "athletics",
        "keywords": (
            "взобраться", "перепрыгнуть", "взломать дверь",
            "выбить дверь", "перетащить",
        ),
        "dc": 15,
    },
]


def resolve_action_check(
    action_text: str,
    character: dict[str, Any],
) -> dict[str, Any] | None:
    """Распознаёт ограниченный набор действий и выполняет проверку."""

    action = action_text.casefold()

    matched_rule = next(
        (
            rule
            for rule in ACTION_RULES
            if any(word in action for word in rule["keywords"])
        ),
        None,
    )

    # Обычный разговор или действие, которому пока не нужна проверка.
    if matched_rule is None:
        return None

    skill = matched_rule["skill"]
    attributes = {
        "strength": character.get("strength", 10),
        "dexterity": character.get("dexterity", 10),
        "constitution": character.get("constitution", 10),
        "intelligence": character.get("intelligence", 10),
        "wisdom": character.get("wisdom", 10),
        "charisma": character.get("charisma", 10),
    }

    try:
        result = make_skill_check(
            skill=skill,
            attributes=attributes,
            proficient_skills=character.get("proficient_skills", []),
            proficiency_bonus=character.get("proficiency_bonus", 2),
            dc=matched_rule["dc"],
        )
        ability = get_skill_ability(skill)

    except (ValueError, TypeError) as exc:
        raise ValueError(f"Не удалось выполнить проверку навыка: {exc}") from exc

    return {
        "skill": skill,
        "ability": ability.value,
        "roll": result.roll,
        "modifier": result.modifier,
        "proficiency_bonus": result.proficiency_bonus,
        "extra_bonus": result.extra_bonus,
        "total": result.total,
        "dc": result.dc,
        "success": result.success,
    }
