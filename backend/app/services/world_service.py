from __future__ import annotations

from typing import Any, Dict

from app.services.world_state import GameWorldStore
from app.schemas.world import WorldSnapshot


store = GameWorldStore()


def create_campaign(title: str, setting: str = "dark_fantasy", tone: str = "dark_fantasy") -> Dict[str, Any]:
    return store.create_campaign(title, setting, tone)


def create_character(campaign_id: str, player_id: str, name: str, class_name: str, strength: int, agility: int, intellect: int, will: int) -> Dict[str, Any]:
    return store.create_character(campaign_id, player_id, name, class_name, strength, agility, intellect, will)


def get_world_snapshot(campaign_id: str, character_id: str) -> WorldSnapshot:
    return store.get_world_snapshot(campaign_id, character_id)


def get_campaign_snapshot(campaign_id: str) -> Dict[str, Any]:
    return store.get_campaign(campaign_id)


def update_after_turn(campaign_id: str, character_id: str, ai_result: Dict[str, Any]) -> None:
    store.update_campaign_after_turn(campaign_id, character_id, ai_result)
