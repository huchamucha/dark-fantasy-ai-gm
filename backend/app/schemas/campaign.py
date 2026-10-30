from pydantic import BaseModel
from typing import List, Optional


class HumanCharacter(BaseModel):
    id: str
    name: str
    class_name: str
    level: int = 1
    hp: int
    max_hp: int
    strength: int
    agility: int
    intellect: int
    will: int
    gold: int = 0
    location_id: str
    inventory: List[str] = []
    status_flags: dict = {}
    notes: dict = {}


class CampaignCreate(BaseModel):
    title: str
    setting: str = "dark_fantasy"
    tone: str = "dark_fantasy"


class Campaign(BaseModel):
    id: str
    title: str
    setting: str
    tone: str
    status: str = "active"
    current_location_id: Optional[str] = None
    main_quest_id: Optional[str] = None
    world_flags: dict = {}
