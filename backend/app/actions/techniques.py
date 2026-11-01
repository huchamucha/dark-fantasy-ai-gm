
from dataclasses import dataclass


@dataclass(frozen=True)
class TechniqueDefinition:
    id: str
    name: str
    description: str
    examples: tuple[str, ...]
    related_skills: tuple[str, ...] = ()


TECHNIQUES = {
    "feint": TechniqueDefinition(
        id="feint",
        name="Финт",
        description=(
            "Обманное движение, предназначенное для вызова "
            "определённой реакции противника."
        ),
        examples=(
            "Ложный замах с последующей сменой направления.",
            "Имитация удара для провокации блока.",
            "Ложное движение с последующим отступлением.",
        ),
    ),
    "direction_change": TechniqueDefinition(
        id="direction_change",
        name="Смена направления",
        description="Изменение направления атаки во время её выполнения.",
        examples=(
            "Переход от удара сверху к удару сбоку.",
            "Изменение направления после реакции противника.",
        ),
    ),
    "aimed_attack": TechniqueDefinition(
        id="aimed_attack",
        name="Прицельная атака",
        description="Попытка атаковать конкретную часть тела противника.",
        examples=(
            "Удар в левое колено.",
            "Удар по руке с оружием.",
            "Атака в область головы.",
        ),
    ),
    "counterattack": TechniqueDefinition(
        id="counterattack",
        name="Контратака",
        description="Атака в ответ на действие противника.",
        examples=(
            "Удар после неудачной атаки противника.",
            "Ответный выпад после парирования.",
        ),
    ),
    "parry": TechniqueDefinition(
        id="parry",
        name="Парирование",
        description="Отклонение или перенаправление атаки противника.",
        examples=(
            "Отведение клинка в сторону.",
            "Парирование с последующей контратакой.",
        ),
    ),
    "block": TechniqueDefinition(
        id="block",
        name="Блок",
        description="Остановка или смягчение атаки защитным действием.",
        examples=(
            "Блок мечом.",
            "Защита щитом.",
        ),
    ),
    "dodge": TechniqueDefinition(
        id="dodge",
        name="Уклонение",
        description="Изменение положения тела для ухода от атаки.",
        examples=(
            "Шаг в сторону.",
            "Наклон корпуса.",
            "Отскок назад.",
        ),
    ),
    "disarm": TechniqueDefinition(
        id="disarm",
        name="Обезоруживание",
        description="Попытка лишить противника удерживаемого оружия.",
        examples=(
            "Выбить меч из руки.",
            "Захватить оружие и вывернуть кисть.",
        ),
    ),
    "grapple": TechniqueDefinition(
        id="grapple",
        name="Захват",
        description="Попытка физически удержать или контролировать противника.",
        examples=(
            "Захватить руку.",
            "Схватить противника за одежду.",
            "Перейти в борьбу вблизи.",
        ),
    ),
}


def get_technique(technique_id: str) -> TechniqueDefinition | None:
    return TECHNIQUES.get(technique_id)


def get_all_techniques() -> tuple[TechniqueDefinition, ...]:
    return tuple(TECHNIQUES.values())
