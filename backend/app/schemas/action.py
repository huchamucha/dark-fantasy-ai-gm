
from pydantic import BaseModel, ConfigDict, Field


class ActionInterpretationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_action: str = Field(min_length=1, max_length=3000)
    world_context: dict = Field(default_factory=dict)
