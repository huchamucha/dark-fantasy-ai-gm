from pydantic import BaseModel
from typing import Optional


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
