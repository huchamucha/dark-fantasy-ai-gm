from __future__ import annotations

from typing import Any

from game_state import GameState


def build_story_prompt(game_state: GameState, *, player_input: str = "", choice: str | None = None) -> str:
    history = "\n".join(game_state.history[-4:]) if game_state.history else game_state.current_scene
    choice_block = f"\nThe player has chosen: {choice}\n" if choice else ""
    player_input_block = f"\nCurrent player input: {player_input}\n" if player_input else ""

    return f"""
You are the Game Master for a dark fantasy RPG.

World title: {game_state.title}
Current location: {game_state.location}
Player: {game_state.player_name}
Player trait: {game_state.trait}
Inventory: {', '.join(game_state.inventory) if game_state.inventory else 'empty'}
Morality: {game_state.morality}
World flags: {game_state.world_flags}

Recent scene history:
{history}

Current scene:
{game_state.current_scene}
{choice_block}{player_input_block}

Return ONLY valid JSON with this schema:
{
  "scene": "brief but vivid narration",
  "choices": ["choice A", "choice B", "choice C"],
  "state_summary": "short world update",
  "flags": {"threat_level": 1, "nightfall": false, "ruin_vision": false},
  "inventory": ["item 1", "item 2"],
  "morality": 0
}

Rules:
- Keep it dark, atmospheric, and grounded.
- Do not include markdown fences.
- Keep scene narration concise but evocative.
- Choices must be short and game-like.
- Reflect the player's trait and current world state.
- Preserve the lore style of a grim fantasy adventure.
"""
