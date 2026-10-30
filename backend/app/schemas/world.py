from pydantic import BaseModel
from typing import Any, Dict, List


class WorldSnapshot(BaseModel):
    campaign_id: str
    character: Dict[str, Any]
    location: Dict[str, Any]
    npcs: List[Dict[str, Any]]
    quests: List[Dict[str, Any]]
    inventory: List[Dict[str, Any]]
    recent_events: List[Dict[str, Any]]
    world_flags: Dict[str, Any]
