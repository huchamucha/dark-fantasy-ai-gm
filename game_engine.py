from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from game_state import GameState
from llm_client import LMStudioClient, parse_json_response
from prompts import build_story_prompt


@dataclass
class GameEngine:
    base_url: str = "http://localhost:1234/v1"
    api_key: str = "lm-studio"
    model: str = "Qwen2.5-7B-Instruct-GGUF"
    client: LMStudioClient | None = None

    def __post_init__(self):
        if self.client is None:
            self.client = LMStudioClient(self.base_url, self.api_key, self.model)

    def advance(self, game_state: GameState, *, player_input: str = "", choice: str | None = None) -> dict[str, Any]:
        prompt = build_story_prompt(game_state, player_input=player_input, choice=choice)
        raw_reply = self.client.ask(prompt, temperature=0.8, max_tokens=900)
        payload = parse_json_response(raw_reply)

        if not payload or "scene" not in payload:
            payload = {
                "scene": "The silence deepens around you. The old stone remembers a forgotten oath.",
                "choices": [
                    "Listen to the whisper in the walls",
                    "Open the iron gate",
                    "Leave the ruined keep before sunrise",
                ],
                "state_summary": "The world feels restless and the ancient place is watching.",
                "flags": {"nightfall": False, "ruin_vision": False, "threat_level": 2},
                "inventory": game_state.inventory,
                "morality": game_state.morality,
            }

        game_state.current_scene = str(payload.get("scene") or game_state.current_scene)
        game_state.history.append(game_state.current_scene)

        flags = payload.get("flags") or {}
        if isinstance(flags, dict):
            for key, value in flags.items():
                game_state.world_flags[key] = value

        if "inventory" in payload and isinstance(payload["inventory"], list):
            game_state.inventory = payload["inventory"]

        if "morality" in payload:
            try:
                game_state.morality = int(payload["morality"])
            except (TypeError, ValueError):
                pass

        return {
            "scene": game_state.current_scene,
            "title": game_state.title,
            "location": game_state.location,
            "choices": payload.get("choices") or ["Press deeper into the darkness", "Retreat and wait"],
            "state_summary": payload.get("state_summary") or "The dark keeps moving.",
            "flags": game_state.world_flags,
            "inventory": game_state.inventory,
            "morality": game_state.morality,
            "choice": choice,
        }
