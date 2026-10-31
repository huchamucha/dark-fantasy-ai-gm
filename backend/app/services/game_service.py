from __future__ import annotations

import uuid

from app.schemas.turn import TurnRequest, TurnResponse
from app.services.llm_service import call_ai_gm
from app.services.world_service import get_world_snapshot, update_after_turn


class GameService:
    def create_campaign(self, payload):
        from app.services.world_service import create_campaign as create_campaign_fn
        return create_campaign_fn(payload.title, payload.setting, payload.tone)

    def create_character(self, campaign_id: str, payload):
        from app.services.world_service import create_character as create_character_fn
        return create_character_fn(
            campaign_id, payload.player_id, payload.name, payload.class_name,
            payload.strength, payload.agility, payload.intellect, payload.will,
        )

    def get_world(self, campaign_id: str):
        from app.services.world_service import get_campaign_snapshot
        campaign = get_campaign_snapshot(campaign_id)
        return {
            "campaign": campaign,
            "world_flags": campaign["world_flags"],
            "locations": campaign["locations"],
            "npcs": campaign["npcs"],
            "quests": campaign["quests"],
        }

    async def process_turn(self, campaign_id: str, turn: TurnRequest) -> TurnResponse:
        snapshot = get_world_snapshot(campaign_id, turn.character_id)
        context = {
            "campaign": campaign_id,
            "character": snapshot.character,
            "location": snapshot.location,
            "npcs": snapshot.npcs,
            "quests": snapshot.quests,
            "inventory": snapshot.inventory,
            "recent_events": snapshot.recent_events,
            "world_flags": snapshot.world_flags,
            "player_action": turn.action_text,
        }
        ai_result = await call_ai_gm(context)

        # AI writes narrative only. The future Game Engine will validate and
        # execute all mechanical changes before they can be persisted.
        update_after_turn(campaign_id, turn.character_id, turn.action_text, ai_result)

        return TurnResponse(
            turn_id=uuid.uuid4().hex,
            narrative=ai_result.get("narrative", ""),
            outcome=ai_result.get("outcome", "neutral"),
            summary=ai_result.get("summary", "Решение принято."),
            hp_change=0,
            stat_changes={},
            inventory_changes=[],
            quest_updates=[],
            npc_updates=[],
            world_flags={},
            next_scene_hint=ai_result.get("next_scene_hint", "Продолжайте исследование."),
        )