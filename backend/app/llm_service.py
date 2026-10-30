from __future__ import annotations

import json
import os
import re
from typing import Any, Dict

import httpx

from app.config import LLM_MODEL, LLM_URL


DEFAULT_FALLBACK = {
    "narrative": "Колокола вдалеке звенят, и вы чувствуете, как тень под городом пытается шевельнуться. Серебряный Логов дыханием затайл ожидание.",
    "outcome": "exploration",
    "summary": "Вы ощущаете приближение древней угрозы.",
    "hp_change": 0,
    "stat_changes": {"will": 1},
    "inventory_changes": [],
    "quest_updates": [],
    "npc_updates": [],
    "world_flags": {"shadow_in_city": True},
    "next_scene_hint": "Брат Эдмон ждёт в монастыре у тайного архива.",
}


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

Требуемый JSON формат:
{{
  "narrative": "...",
  "outcome": "success|failure|neutral|exploration|dialogue|combat",
  "summary": "...",
  "hp_change": 0,
  "stat_changes": {{"strength": 0, "agility": 0, "intellect": 0, "will": 0}},
  "inventory_changes": [],
  "quest_updates": [],
  "npc_updates": [],
  "world_flags": {{}}
}}

Верни ТОЛЬКО валидный JSON без пояснений, без markdown, без комментариев.
    """.strip()


async def call_ai_gm(context: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "model": LLM_MODEL,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты — ведущий тёмного фэнтези. "
                    "Пиши атмосферно, но чётко. "
                    "Возвращай только валидный JSON и ничего лишнего."
                ),
            },
            {"role": "user", "content": format_context_for_prompt(context)},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(LLM_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return parse_json(content)
    except Exception:
        return DEFAULT_FALLBACK


def parse_json(raw: str) -> Dict[str, Any]:
    if raw is None:
        return DEFAULT_FALLBACK

    text = str(raw).strip()

    text = re.sub(r"```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "").strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]

    try:
        return json.loads(text)
    except Exception:
        return DEFAULT_FALLBACK
