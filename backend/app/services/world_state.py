from __future__ import annotations

import uuid
from typing import Any

from app.schemas.world import WorldSnapshot


class GameWorldStore:
    def __init__(self) -> None:
        self.campaigns: dict[str, dict[str, Any]] = {}
        self.characters: dict[str, dict[str, Any]] = {}

    def create_campaign(
        self,
        title: str,
        setting: str = "dark_fantasy",
        tone: str = "dark_fantasy",
    ) -> dict[str, Any]:
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
        dexterity: int,
        constitution: int,
        intelligence: int,
        wisdom: int,
        charisma: int,
    ) -> dict[str, Any]:

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
            "dexterity": dexterity,
            "constitution": constitution,
            "intelligence": intelligence,
            "wisdom": wisdom,
            "charisma": charisma,

            "proficiency_bonus": 2,
            "proficient_skills": [],

            "gold": 0,
            "location_id": self.campaigns[campaign_id]["current_location_id"],
            "inventory": [],
            "status_flags": {},
            "notes": {},
        }

        self.characters[character_id] = character
        self.campaigns[campaign_id].setdefault("characters", []).append(character_id)

        return character

    def get_campaign(self, campaign_id: str) -> dict[str, Any]:
        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        return self.campaigns[campaign_id]

    def get_world_snapshot(
        self,
        campaign_id: str,
        character_id: str,
    ) -> WorldSnapshot:

        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        if character_id not in self.characters:
            raise ValueError(f"Character {character_id} not found")

        campaign = self.campaigns[campaign_id]
        character = self.characters[character_id]

        location = next(
            (
                entry
                for entry in campaign.get("locations", [])
                if entry.get("id") == character["location_id"]
            ),
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

    def update_campaign_after_turn(
        self,
        campaign_id: str,
        character_id: str,
        player_action: str,
        ai_result: dict[str, Any],
    ) -> None:

        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        if character_id not in self.characters:
            raise ValueError(f"Character {character_id} not found")

        campaign = self.campaigns[campaign_id]

        event = {
            "event_id": uuid.uuid4().hex,
            "character_id": character_id,
            "player_action": player_action,
            "narrative": ai_result.get("narrative", ""),
            "summary": ai_result.get("summary", ""),
            "outcome": ai_result.get("outcome", "neutral"),
        }

        campaign.setdefault("recent_events", []).append(event)
