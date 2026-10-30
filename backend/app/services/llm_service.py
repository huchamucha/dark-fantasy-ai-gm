import os
from typing import Any, Dict

import httpx

from app.config import LLM_MODEL, LLM_URL


def format_context_for_prompt(context: Dict[str, Any]) -> str:
    return f"""
Campaign: {context.get('campaign')}
Character: {context.get('character')}
Location: {context.get('location')}
NPCs: {context.get('npcs')}
Active quests: {context.get('quests')}
Inventory: {context.get('inventory')}
Recent events: {context.get('recent_events')}
World flags: {context.get('world_flags')}
Player action: {context.get('player_action')}
    """.strip()


async def call_ai_gm(context: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты — ведущий тёмного фэнтези. "
                    "Пиши атмосферно, чётко и в стиле dark fantasy. "
                    "Сохраняй непрерывность сюжета и возвращай валидный JSON."
                ),
            },
            {"role": "user", "content": format_context_for_prompt(context)},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(LLM_URL, json=payload)
            response.raise_for_status()
            raw = response.json()
            content = raw["choices"][0]["message"]["content"]
            return parse_json(content)
    except Exception:
        return {
            "narrative": "Колокола вдалеке звенят, и в воздухе чувствуется холодная тьма. Пепел шевелится у ваших ног, как будто мир сам пытается напомнить о древней угрозе.",
            "outcome": "exploration",
            "summary": "Вы идёте вперёд и сталкиваетесь с тёмной предчувствием.",
            "hp_change": 0,
            "stat_changes": {"will": 1},
            "inventory_changes": [],
            "quest_updates": [],
            "npc_updates": [],
            "world_flags": {"shadow_in_city": True},
            "next_scene_hint": "Слышен шёпот из глубины монастыря.",
        }


def parse_json(raw: str) -> Dict[str, Any]:
    import json

    try:
        return json.loads(raw)
    except Exception:
        return {
            "narrative": raw,
            "outcome": "neutral",
            "summary": "Сюжет разворачивается.",
            "hp_change": 0,
            "stat_changes": {},
            "inventory_changes": [],
            "quest_updates": [],
            "npc_updates": [],
            "world_flags": {},
            "next_scene_hint": "Нужно продолжать расследование.",
        }
