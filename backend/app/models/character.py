from pydantic import BaseModel


class CharacterCreate(BaseModel):
    player_id: str
    name: str
    class_name: str
    strength: int = 10
    agility: int = 10
    intellect: int = 10
    will: int = 10
