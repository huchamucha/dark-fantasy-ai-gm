from pydantic import BaseModel
from typing import Any, Dict, List


class TurnRequest(BaseModel):
    character_id: str
    action_text: str


class TurnResponse(BaseModel):
    turn_id: str
    narrative: str
    outcome: str
    summary: str
    hp_change: int = 0
    stat_changes: Dict[str, Any] = {}
    inventory_changes: List[Dict[str, Any]] = []
    quest_updates: List[Dict[str, Any]] = []
    npc_updates: List[Dict[str, Any]] = []
    world_flags: Dict[str, Any] = {}
    next_scene_hint: str = ""
