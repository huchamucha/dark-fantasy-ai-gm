from pydantic import BaseModel, Field
from typing import List, Optional


class HumanCharacter(BaseModel):
    id: str
    name: str
    class_name: str

    level: int = 1
    hp: int
    max_hp: int

    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    gold: int = 0
    location_id: str

    inventory: List[str] = Field(default_factory=list)
    status_flags: dict = Field(default_factory=dict)
    notes: dict = Field(default_factory=dict)


class CampaignCreate(BaseModel):
    title: str
    setting: str = "dark_fantasy"
    tone: str = "dark_fantasy"
    story_pack_id: Optional[str] = None


class Campaign(BaseModel):
    id: str
    title: str
    setting: str
    tone: str
    story_pack_id: str = "dark_fantasy"
    status: str = "active"
    current_location_id: Optional[str] = None
    main_quest_id: Optional[str] = None
    world_flags: dict = Field(default_factory=dict)
