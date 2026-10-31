from typing import Any

from app.engine.skills import SKILL_ABILITIES


SKILL_DEFINITIONS: dict[str, dict[str, Any]] = {
    "athletics": {
        "name": "Атлетика",
        "description": "Бег, прыжки, лазание и физические усилия.",
    },
    "acrobatics": {
        "name": "Акробатика",
        "description": "Баланс, координация и сложные движения.",
    },
    "stealth": {
        "name": "Скрытность",
        "description": "Передвижение незаметно и укрытие от чужих глаз.",
    },
    "sleight_of_hand": {
        "name": "Ловкость рук",
        "description": "Манипуляции с предметами и незаметные действия руками.",
    },
    "endurance": {
        "name": "Выносливость",
        "description": "Переносимость физических нагрузок и истощения.",
    },
    "history": {
        "name": "История",
        "description": "Знание исторических событий и цивилизаций.",
    },
    "investigation": {
        "name": "Расследование",
        "description": "Поиск улик, анализ деталей и логические выводы.",
    },
    "arcana": {
        "name": "Магия",
        "description": "Знание магии, заклинаний и сверхъестественных явлений.",
    },
    "nature": {
        "name": "Природа",
        "description": "Знание животных, растений и природных процессов.",
    },
    "religion": {
        "name": "Религия",
        "description": "Знание верований, культов и религиозных обрядов.",
    },
    "perception": {
        "name": "Восприятие",
        "description": "Обнаружение звуков, движений и скрытых объектов.",
    },
    "insight": {
        "name": "Проницательность",
        "description": "Понимание намерений и эмоционального состояния других.",
    },
    "medicine": {
        "name": "Медицина",
        "description": "Диагностика, лечение и оказание первой помощи.",
    },
    "survival": {
        "name": "Выживание",
        "description": "Ориентирование, поиск ресурсов и жизнь в дикой местности.",
    },
    "animal_handling": {
        "name": "Обращение с животными",
        "description": "Уход за животными и управление их поведением.",
    },
    "persuasion": {
        "name": "Убеждение",
        "description": "Умение договариваться и склонять других к своей позиции.",
    },
    "deception": {
        "name": "Обман",
        "description": "Ложь, маскировка намерений и введение в заблуждение.",
    },
    "intimidation": {
        "name": "Запугивание",
        "description": "Воздействие на других угрозами и демонстрацией силы.",
    },
    "performance": {
        "name": "Выступление",
        "description": "Выступления, артистизм и развлечение аудитории.",
    },
}


def get_skill_catalog(
    overrides: dict[str, dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Возвращает навыки с названиями и связями из общего движка."""

    overrides = overrides or {}

    unknown_ids = set(overrides) - set(SKILL_ABILITIES)

    if unknown_ids:
        raise ValueError(
            f"Неизвестные навыки: {', '.join(sorted(unknown_ids))}"
        )

    result = []

    for skill_id, ability in SKILL_ABILITIES.items():
        definition = SKILL_DEFINITIONS[skill_id]
        custom = overrides.get(skill_id, {})

        result.append({
            "id": skill_id,
            "name": custom.get("name", definition["name"]),
            "description": custom.get(
                "description",
                definition["description"],
            ),
            "ability": ability.value,
        })

    return result
