from __future__ import annotations

import uuid
from copy import deepcopy
from typing import Any

from app.schemas.world import WorldSnapshot
from app.story_packs.registry import get_initial_world


class GameWorldStore:
    def __init__(self) -> None:
        self.campaigns: dict[str, dict[str, Any]] = {}
        self.characters: dict[str, dict[str, Any]] = {}

    def create_campaign(
        self,
        title: str,
        setting: str = "dark_fantasy",
        tone: str = "dark_fantasy",
        story_pack_id: str | None = None,
    ) -> dict[str, Any]:
        selected_pack = story_pack_id or setting
        initial_world = get_initial_world(selected_pack)

        campaign_id = uuid.uuid4().hex

        campaign = {
            "id": campaign_id,
            "title": title,
            "story_pack_id": selected_pack,
            "setting": selected_pack,
            "tone": tone,
            "status": "active",
            "current_location_id": initial_world["current_location_id"],
            "main_quest_id": initial_world["main_quest_id"],
            "world_flags": initial_world["world_flags"],
            "locations": initial_world["locations"],
            "npcs": initial_world["npcs"],
            "quests": initial_world["quests"],
            "characters": [],
            "recent_events": [],
        }

        self.campaigns[campaign_id] = campaign
        return deepcopy(campaign)

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
        campaign = self.get_campaign(campaign_id)

        character_id = uuid.uuid4().hex

        character = {
            "id": character_id,
            "player_id": player_id,
            "campaign_id": campaign_id,
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
            "location_id": campaign["current_location_id"],
            "inventory": [],
            "status_flags": {},
            "notes": {},
        }

        self.characters[character_id] = character
        campaign["characters"].append(character_id)

        return deepcopy(character)

    def get_campaign(self, campaign_id: str) -> dict[str, Any]:
        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        return deepcopy(self.campaigns[campaign_id])

    def _get_owned_character(
        self,
        campaign_id: str,
        character_id: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        campaign = self.campaigns.get(campaign_id)
        if campaign is None:
            raise ValueError(f"Campaign {campaign_id} not found")

        character = self.characters.get(character_id)
        if character is None:
            raise ValueError(f"Character {character_id} not found")

        if character_id not in campaign["characters"]:
            raise ValueError(
                f"Character {character_id} does not belong to campaign {campaign_id}"
            )

        return campaign, character

    def get_world_snapshot(
        self,
        campaign_id: str,
        character_id: str,
    ) -> WorldSnapshot:
        campaign, character = self._get_owned_character(
            campaign_id,
            character_id,
        )

        location = next(
            (
                entry
                for entry in campaign.get("locations", [])
                if entry.get("id") == character["location_id"]
            ),
            {
                "id": character["location_id"],
                "name": "Неизвестное место",
                "description": "Окружающий мир пока не описан.",
                "danger_level": 1,
            },
        )

        return WorldSnapshot(
            campaign_id=campaign_id,
            character=deepcopy(character),
            location=deepcopy(location),
            npcs=deepcopy(campaign.get("npcs", [])),
            quests=deepcopy(campaign.get("quests", [])),
            inventory=deepcopy(character.get("inventory", [])),
            recent_events=deepcopy(campaign.get("recent_events", [])),
            world_flags=deepcopy(campaign.get("world_flags", {})),
        )

    def update_campaign_after_turn(
        self,
        campaign_id: str,
        character_id: str,
        player_action: str,
        ai_result: dict[str, Any],
    ) -> None:
        campaign, _ = self._get_owned_character(
            campaign_id,
            character_id,
        )

        event = {
            "event_id": uuid.uuid4().hex,
            "character_id": character_id,
            "player_action": player_action,
            "narrative": ai_result.get("narrative", ""),
            "summary": ai_result.get("summary", ""),
            "outcome": ai_result.get("outcome", "neutral"),
        }

        campaign.setdefault("recent_events", []).append(event)
