
from __future__ import annotations

import uuid
from copy import deepcopy
from typing import Any

from sqlalchemy import select

from app.database.session import SessionLocal
from app.database.models import CampaignRecord, CharacterRecord, StoryPack
from app.schemas.world import WorldSnapshot
from app.story_packs.registry import get_initial_world, get_story_pack


class GameWorldStore:
    """Постоянное хранилище игрового состояния в SQLite."""

    def create_campaign(
        self,
        title: str,
        setting: str = "dark_fantasy",
        tone: str = "dark_fantasy",
        story_pack_id: str | None = None,
    ) -> dict[str, Any]:
        selected_pack = story_pack_id or setting
        pack_data = get_story_pack(selected_pack)
        initial_world = get_initial_world(selected_pack)

        campaign_id = uuid.uuid4().hex

        campaign = {
            "id": campaign_id,
            "title": title,
            "story_pack_id": selected_pack,
            "story_pack_version": pack_data["version"]
            if "version" in pack_data
            else "1.0.0",
            "setting": selected_pack,
            "tone": tone,
            "status": "active",
            "current_location_id": initial_world["current_location_id"],
            "main_quest_id": initial_world["main_quest_id"],
            "world_flags": deepcopy(initial_world["world_flags"]),
            "locations": deepcopy(initial_world["locations"]),
            "npcs": deepcopy(initial_world["npcs"]),
            "quests": deepcopy(initial_world["quests"]),
            "characters": [],
            "recent_events": [],
        }

        with SessionLocal() as session:
            story_pack = session.get(StoryPack, selected_pack)

            if story_pack is None:
                story_pack = StoryPack(
                    id=selected_pack,
                    name=pack_data["name"],
                    description=pack_data.get("description"),
                    current_version=campaign["story_pack_version"],
                    is_active=pack_data.get("status") == "available",
                )
                session.add(story_pack)
                session.flush()

            campaign_record = CampaignRecord(
                id=campaign_id,
                title=title,
                story_pack_id=selected_pack,
                story_pack_version=campaign["story_pack_version"],
                setting=selected_pack,
                tone=tone,
                status="active",
                current_location_id=campaign["current_location_id"],
                main_quest_id=campaign["main_quest_id"],
                world_flags=deepcopy(campaign["world_flags"]),
                world_data={
                    "locations": deepcopy(campaign["locations"]),
                    "npcs": deepcopy(campaign["npcs"]),
                    "quests": deepcopy(campaign["quests"]),
                    "recent_events": [],
                },
            )

            session.add(campaign_record)
            session.commit()

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
        character_id = uuid.uuid4().hex

        with SessionLocal() as session:
            campaign = session.get(CampaignRecord, campaign_id)

            if campaign is None:
                raise ValueError(f"Campaign {campaign_id} not found")

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
                "location_id": campaign.current_location_id,
                "inventory": [],
                "status_flags": {},
                "notes": {},
            }

            session.add(
                CharacterRecord(
                    id=character_id,
                    campaign_id=campaign_id,
                    player_id=player_id,
                    name=name,
                    class_name=class_name,
                    level=1,
                    hp=18,
                    max_hp=18,
                    strength=strength,
                    dexterity=dexterity,
                    constitution=constitution,
                    intelligence=intelligence,
                    wisdom=wisdom,
                    charisma=charisma,
                    proficiency_bonus=2,
                    proficient_skills=[],
                    gold=0,
                    location_id=campaign.current_location_id,
                    inventory=[],
                    status_flags={},
                    notes={},
                )
            )

            session.commit()

        return deepcopy(character)

    def get_campaign(self, campaign_id: str) -> dict[str, Any]:
        with SessionLocal() as session:
            campaign = session.get(CampaignRecord, campaign_id)

            if campaign is None:
                raise ValueError(f"Campaign {campaign_id} not found")

            character_ids = session.scalars(
                select(CharacterRecord.id).where(
                    CharacterRecord.campaign_id == campaign_id
                )
            ).all()

            world_data = deepcopy(campaign.world_data or {})

            return {
                "id": campaign.id,
                "title": campaign.title,
                "story_pack_id": campaign.story_pack_id,
                "story_pack_version": campaign.story_pack_version,
                "setting": campaign.setting,
                "tone": campaign.tone,
                "status": campaign.status,
                "current_location_id": campaign.current_location_id,
                "main_quest_id": campaign.main_quest_id,
                "world_flags": deepcopy(campaign.world_flags or {}),
                "locations": deepcopy(world_data.get("locations", [])),
                "npcs": deepcopy(world_data.get("npcs", [])),
                "quests": deepcopy(world_data.get("quests", [])),
                "characters": list(character_ids),
                "recent_events": deepcopy(world_data.get("recent_events", [])),
            }

    def _get_owned_character(
        self,
        session,
        campaign_id: str,
        character_id: str,
    ) -> tuple[CampaignRecord, CharacterRecord]:
        campaign = session.get(CampaignRecord, campaign_id)

        if campaign is None:
            raise ValueError(f"Campaign {campaign_id} not found")

        character = session.get(CharacterRecord, character_id)

        if character is None:
            raise ValueError(f"Character {character_id} not found")

        if character.campaign_id != campaign_id:
            raise ValueError(
                f"Character {character_id} does not belong to campaign {campaign_id}"
            )

        return campaign, character

    @staticmethod
    def _character_to_dict(character: CharacterRecord) -> dict[str, Any]:
        return {
            "id": character.id,
            "player_id": character.player_id,
            "campaign_id": character.campaign_id,
            "name": character.name,
            "class_name": character.class_name,
            "level": character.level,
            "hp": character.hp,
            "max_hp": character.max_hp,
            "strength": character.strength,
            "dexterity": character.dexterity,
            "constitution": character.constitution,
            "intelligence": character.intelligence,
            "wisdom": character.wisdom,
            "charisma": character.charisma,
            "proficiency_bonus": character.proficiency_bonus,
            "proficient_skills": deepcopy(character.proficient_skills or []),
            "gold": character.gold,
            "location_id": character.location_id,
            "inventory": deepcopy(character.inventory or []),
            "status_flags": deepcopy(character.status_flags or {}),
            "notes": deepcopy(character.notes or {}),
        }

    def get_world_snapshot(
        self,
        campaign_id: str,
        character_id: str,
    ) -> WorldSnapshot:
        with SessionLocal() as session:
            campaign, character = self._get_owned_character(
                session,
                campaign_id,
                character_id,
            )

            world_data = deepcopy(campaign.world_data or {})
            character_data = self._character_to_dict(character)

            location = next(
                (
                    entry
                    for entry in world_data.get("locations", [])
                    if entry.get("id") == character_data["location_id"]
                ),
                {
                    "id": character_data["location_id"],
                    "name": "Неизвестное место",
                    "description": "Окружающий мир пока не описан.",
                    "danger_level": 1,
                },
            )

            return WorldSnapshot(
                campaign_id=campaign_id,
                character=character_data,
                location=deepcopy(location),
                npcs=deepcopy(world_data.get("npcs", [])),
                quests=deepcopy(world_data.get("quests", [])),
                inventory=deepcopy(character_data["inventory"]),
                recent_events=deepcopy(world_data.get("recent_events", [])),
                world_flags=deepcopy(campaign.world_flags or {}),
            )

    def update_campaign_after_turn(
        self,
        campaign_id: str,
        character_id: str,
        player_action: str,
        ai_result: dict[str, Any],
    ) -> None:
        with SessionLocal() as session:
            campaign, _ = self._get_owned_character(
                session,
                campaign_id,
                character_id,
            )

            world_data = deepcopy(campaign.world_data or {})
            recent_events = world_data.setdefault("recent_events", [])

            recent_events.append(
                {
                    "event_id": uuid.uuid4().hex,
                    "character_id": character_id,
                    "player_action": player_action,
                    "narrative": ai_result.get("narrative", ""),
                    "summary": ai_result.get("summary", ""),
                    "outcome": ai_result.get("outcome", "neutral"),
                }
            )

            campaign.world_data = world_data
            session.commit()
