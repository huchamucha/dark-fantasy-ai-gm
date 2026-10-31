from __future__ import annotations

import uuid

from app.engine.action_resolution import resolve_action_check
from app.schemas.turn import TurnRequest, TurnResponse
from app.services.llm_service import call_ai_gm
from app.services.world_service import get_world_snapshot, update_after_turn


class GameService:
    def create_campaign(self, payload):
        from app.services.world_service import create_campaign as create_campaign_fn

        return create_campaign_fn(
            title=payload.title,
            setting=payload.setting,
            tone=payload.tone,
            story_pack_id=getattr(payload, "story_pack_id", None),
        )

    def create_character(self, campaign_id: str, payload):
        from app.services.world_service import create_character as create_character_fn

        return create_character_fn(
            campaign_id=campaign_id,
            player_id=payload.player_id,
            name=payload.name,
            class_name=payload.class_name,
            strength=payload.strength,
            dexterity=payload.dexterity,
            constitution=payload.constitution,
            intelligence=payload.intelligence,
            wisdom=payload.wisdom,
            charisma=payload.charisma,
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

    async def process_turn(
        self,
        campaign_id: str,
        turn: TurnRequest,
    ) -> TurnResponse:
        snapshot = get_world_snapshot(campaign_id, turn.character_id)

        character = snapshot.character

        mechanical_check = resolve_action_check(
            turn.action_text,
            character,
        )

        context = {
            "campaign": campaign_id,
            "character": character,
            "location": snapshot.location,
            "npcs": snapshot.npcs,
            "quests": snapshot.quests,
            "inventory": snapshot.inventory,
            "recent_events": snapshot.recent_events,
            "world_flags": snapshot.world_flags,
            "player_action": turn.action_text,
            "mechanical_check": mechanical_check,
        }

        ai_result = await call_ai_gm(context)

        update_after_turn(
            campaign_id,
            turn.character_id,
            turn.action_text,
            ai_result,
        )

        summary = ai_result.get("summary", "Решение принято.")

        if mechanical_check is not None:
            skill = mechanical_check["skill"]
            total = mechanical_check["total"]
            dc = mechanical_check["dc"]
            success = mechanical_check["success"]

            result_text = (
                f"Проверка {skill}: D20 {mechanical_check['roll']}, "
                f"модификатор {mechanical_check['modifier']:+d}, "
                f"бонус мастерства "
                f"{mechanical_check['proficiency_bonus']:+d}. "
                f"Итого {total} против DC {dc}: "
                f"{'успех' if success else 'провал'}."
            )

            summary = f"{result_text} {summary}".strip()

        return TurnResponse(
            turn_id=uuid.uuid4().hex,
            narrative=ai_result.get("narrative", ""),
            outcome=ai_result.get("outcome", "neutral"),
            summary=summary,
            hp_change=0,
            stat_changes={},
            inventory_changes=[],
            quest_updates=[],
            npc_updates=[],
            world_flags={},
            next_scene_hint=ai_result.get(
                "next_scene_hint",
                "Продолжайте исследование.",
            ),
        )
