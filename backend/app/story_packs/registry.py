from copy import deepcopy
from typing import Any


STORY_PACKS: dict[str, dict[str, Any]] = {
    "dark_fantasy": {
        "id": "dark_fantasy",
        "name": "Тёмное фэнтези",
        "description": "Мрачный мир тайн, опасностей и древней магии.",
        "status": "available",
        "presentation": {
            "attribute_overrides": {},
        },
        "initial_world": {
            "current_location_id": "cathedral_approach",
            "main_quest_id": "quest_ashen_crown",
            "world_flags": {
                "shadow_in_city": False,
            },
            "locations": [
                {
                    "id": "cathedral_approach",
                    "name": "Подступы к собору",
                    "description": "Туман и тление на краю города.",
                    "danger_level": 1,
                }
            ],
            "npcs": [
                {
                    "id": "brother_eldric",
                    "name": "Брат Эдрик",
                    "role": "священник",
                    "mood": "настороженный",
                    "dialogue": "Ты уже слишком долго стоишь в тени.",
                }
            ],
            "quests": [
                {
                    "id": "quest_ashen_crown",
                    "title": "Пепельная Корона",
                    "status": "active",
                    "description": (
                        "Рассечь тьму, которая шевелится под старым городом."
                    ),
                }
            ],
        },
    }
}


def get_story_pack(story_pack_id: str) -> dict[str, Any]:
    """Возвращает описание мира или сообщает, что он неизвестен."""
    try:
        return deepcopy(STORY_PACKS[story_pack_id])
    except KeyError:
        raise ValueError(f"Неизвестная компания: {story_pack_id}")


def list_story_packs() -> list[dict[str, Any]]:
    """Возвращает список доступных для выбора миров."""
    return [
        {
            "id": pack["id"],
            "name": pack["name"],
            "description": pack["description"],
            "status": pack["status"],
        }
        for pack in STORY_PACKS.values()
        if pack["status"] == "available"
    ]


def get_initial_world(story_pack_id: str) -> dict[str, Any]:
    """Возвращает независимую начальную копию состояния мира."""
    pack = get_story_pack(story_pack_id)
    return deepcopy(pack["initial_world"])
