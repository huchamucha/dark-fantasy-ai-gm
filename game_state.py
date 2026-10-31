import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameState:
    session_id: str
    title: str
    location: str
    trait: str
    player_name: str
    world_flags: dict[str, Any] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)
    current_scene: str = ""
    inventory: list[str] = field(default_factory=list)
    morality: int = 0

    @classmethod
    def create(cls, *, player_name: str, title: str, location: str, trait: str) -> "GameState":
        return cls(
            session_id=str(uuid.uuid4()),
            title=title,
            location=location,
            trait=trait,
            player_name=player_name,
            world_flags={
                "nightfall": False,
                "threat_level": 1,
                "ruin_vision": False,
            },
            history=[],
            current_scene="The morning fog hangs over the ruined chapel and the bells are silent.",
            inventory=["charcoal knife", "iron token"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "title": self.title,
            "location": self.location,
            "trait": self.trait,
            "player_name": self.player_name,
            "world_flags": self.world_flags,
            "history": self.history,
            "current_scene": self.current_scene,
            "inventory": self.inventory,
            "morality": self.morality,
        }
