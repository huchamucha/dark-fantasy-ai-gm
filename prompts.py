from __future__ import annotations

from game_state import GameState


def build_story_prompt(game_state: GameState, *, player_input: str = "", choice: str | None = None) -> str:
    history = "\n".join(game_state.history[-4:]) if game_state.history else game_state.current_scene
    choice_block = f"\nThe player has chosen: {choice}\n" if choice else ""
    player_input_block = f"\nCurrent player input: {player_input}\n" if player_input else ""

    return """
You are the Game Master for a dark fantasy RPG.

World title: {title}
Current location: {location}
Player: {player_name}
Player trait: {trait}
Inventory: {inventory}
Morality: {morality}
World flags: {world_flags}

Recent scene history:
{history}

Current scene:
{current_scene}
{choice_block}{player_input_block}

Return ONLY a valid JSON object with this exact schema and nothing else:
{{
  "scene": "brief but vivid narration",
  "choices": ["choice A", "choice B", "choice C"],
  "state_summary": "short world update",
  "flags": {{"nightfall": false, "ruin_vision": false, "threat_level": 1}},
  "inventory": ["item 1", "item 2"],
  "morality": 0
}}

Rules:
- Output valid JSON only.
- No markdown code fences.
- No explanation.
- No extra commentary.
- Use double quotes only.
- Use lowercase booleans: true/false.
- Use integers for threat_level and morality.
- Keep it dark, atmospheric, and grounded.
- Reflect the player's trait and current world state.
""".format(
        title=game_state.title,
        location=game_state.location,
        player_name=game_state.player_name,
        trait=game_state.trait,
        inventory=", ".join(game_state.inventory) if game_state.inventory else "empty",
        morality=game_state.morality,
        world_flags=game_state.world_flags,
        history=history,
        current_scene=game_state.current_scene,
        choice_block=choice_block,
        player_input_block=player_input_block,
    )
