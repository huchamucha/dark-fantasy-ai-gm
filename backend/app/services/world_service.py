from typing import Any, Dict
from app.schemas.world import WorldSnapshot


def build_world_snapshot(campaign_id: str, character_id: str) -> WorldSnapshot:
    return WorldSnapshot(
        campaign_id=campaign_id,
        character={
            "id": character_id,
            "name": "Эдрик",
            "class_name": "Рыцарь Пепельного Ордена",
            "hp": 24,
            "max_hp": 24,
            "strength": 12,
            "agility": 8,
            "intellect": 7,
            "will": 10,
        },
        location={
            "id": "loc_serb_1",
            "name": "Серебряный Логов",
            "description": "Город дышит пеплом.",
        },
        npcs=[
            {"id": "npc_adel", "name": "Адела Серый Молох", "role": "алхимик"},
            {"id": "npc_edmon", "name": "Брат Эдмон", "role": "монах"},
            {"id": "npc_mark", "name": "Марк Скис", "role": "наёмник"},
        ],
        quests=[
            {"id": "quest_1", "title": "Пепельный Отголосок", "status": "active"}
        ],
        inventory=[
            {"id": "item_1", "name": "Пепельный факел", "type": "light"},
            {"id": "item_2", "name": "Крючок для катакомб", "type": "tool"},
        ],
        recent_events=[
            {"message": "Колокола церкви звенели без причины."},
            {"message": "Из-под площади просочилась тень."},
        ],
        world_flags={
            "catacombs_open": False,
            "monastery_locked": True,
            "shadow_in_city": True,
        },
    )
