from __future__ import annotations

import uuid
from typing import Any, Dict, List

from app.schemas.world import WorldSnapshot


class GameWorldStore:
    def __init__(self) -> None:
        self.campaigns: Dict[str, Dict[str, Any]] = {}
        self.characters: Dict[str, Dict[str, Any]] = {}

    def create_campaign(self, title: str, setting: str = "dark_fantasy", tone: str = "dark_fantasy") -> Dict[str, Any]:
        campaign_id = uuid.uuid4().hex
        campaign = {
            "id": campaign_id,
            "title": title,
            "setting": setting,
            "tone": tone,
            "status": "active",
            "current_location_id": "cathedral_approach",
            "main_quest_id": "quest_ashen_crown",
            "world_flags": {"shadow_in_city": False},
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
                    "description": "Рассечь тьму, которая шевелится под старым городом.",
                }
            ],
            "recent_events": [],
        }
        self.campaigns[campaign_id] = campaign
        return campaign

    def create_character(
        self,
        campaign_id: str,
        player_id: str,
        name: str,
        class_name: str,
        strength: int,
        agility: int,
        intellect: int,
        will: int,
    ) -> Dict[str, Any]:
        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        character_id = uuid.uuid4().hex
        character = {
            "id": character_id,
            "player_id": player_id,
            "name": name,
            "class_name": class_name,
            "level": 1,
            "hp": 18,
            "max_hp": 18,
            "strength": strength,
            "agility": agility,
            "intellect": intellect,
            "will": will,
            "gold": 0,
            "location_id": self.campaigns[campaign_id]["current_location_id"],
            "inventory": [],
            "status_flags": {},
            "notes": {},
        }
        self.characters[character_id] = character
        self.campaigns[campaign_id]["characters"] = self.campaigns[campaign_id].get("characters", [])
        self.campaigns[campaign_id]["characters"].append(character_id)
        return character

    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")
        return self.campaigns[campaign_id]

    def get_world_snapshot(self, campaign_id: str, character_id: str) -> WorldSnapshot:
        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")
        if character_id not in self.characters:
            raise ValueError(f"Character {character_id} not found")

        campaign = self.campaigns[campaign_id]
        character = self.characters[character_id]
        location = next(
            (entry for entry in campaign.get("locations", []) if entry.get("id") == character["location_id"]),
            {
                "id": character["location_id"],
                "name": "Пепельный перекрёсток",
                "description": "Город дышит тишиной и страхом.",
                "danger_level": 1,
            },
        )

        return WorldSnapshot(
            campaign_id=campaign_id,
            character=character,
            location=location,
            npcs=campaign.get("npcs", []),
            quests=campaign.get("quests", []),
            inventory=character.get("inventory", []),
            recent_events=campaign.get("recent_events", []),
            world_flags=campaign.get("world_flags", {}),
        )

    def update_campaign_after_turn(self, campaign_id: str, character_id: str, ai_result: Dict[str, Any]) -> None:
        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")
        if character_id not in self.characters:
            raise ValueError(f"Character {character_id} not found")

        campaign = self.campaigns[campaign_id]
        character = self.characters[character_id]

        event = {
            "character_id": character_id,
            "narrative": ai_result.get("narrative", ""),
            "summary": ai_result.get("summary", ""),
            "outcome": ai_result.get("outcome", "neutral"),
        }
        campaign.setdefault("recent_events", []).append(event)

        if "world_flags" in ai_result:
            campaign["world_flags"].update(ai_result["world_flags"])

        hp_change = int(ai_result.get("hp_change", 0))
        character["hp"] = max(0, min(character["max_hp"], character["hp"] + hp_change))

        stat_changes = ai_result.get("stat_changes", {}) or {}
        for key, value in stat_changes.items():
            if key in {"strength", "agility", "intellect", "will"}:
                character[key] = int(character.get(key, 0)) + int(value)

        inventory_changes = ai_result.get("inventory_changes", []) or []
        for item in inventory_changes:
            if item.get("action") == "add":
                character.setdefault("inventory", []).append(item.get("item"))
            elif item.get("action") == "remove":
                character.setdefault("inventory", []).remove(item.get("item"))

        quest_updates = ai_result.get("quest_updates", []) or []
        for quest in quest_updates:
            for existing in campaign.get("quests", []):
                if existing.get("id") == quest.get("id"):
                    existing.update({k: v for k, v in quest.items() if k != "id"})
                    break

        npc_updates = ai_result.get("npc_updates", []) or []
        for npc in npc_updates:
            for existing in campaign.get("npcs", []):
                if existing.get("id") == npc.get("id"):
                    existing.update({k: v for k, v in npc.items() if k != "id"})
                    break

