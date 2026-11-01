
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ActionType(str, Enum):
    ATTACK = "attack"
    DEFEND = "defend"
    MOVE = "move"
    INTERACT = "interact"
    DIALOGUE = "dialogue"
    STEALTH = "stealth"
    PERCEPTION = "perception"
    INVESTIGATION = "investigation"
    MEDICINE = "medicine"
    CRAFTING = "crafting"
    USE_ITEM = "use_item"
    OTHER = "other"


class ActionStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: int = Field(ge=1, le=10)
    action_type: ActionType
    description: str = Field(min_length=1, max_length=500)

    intent: Optional[str] = Field(default=None, max_length=500)
    target_id: Optional[str] = Field(default=None, max_length=100)
    target_description: Optional[str] = Field(default=None, max_length=300)

    method: Optional[str] = Field(default=None, max_length=500)

    technique_ids: list[str] = Field(default_factory=list, max_length=10)
    skill_candidates: list[str] = Field(default_factory=list, max_length=5)


class ActionProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: ActionType
    intent: str = Field(min_length=1, max_length=500)

    target_id: Optional[str] = Field(default=None, max_length=100)
    target_description: Optional[str] = Field(default=None, max_length=300)

    method: str = Field(min_length=1, max_length=500)

    technique_ids: list[str] = Field(default_factory=list, max_length=10)
    skill_candidates: list[str] = Field(default_factory=list, max_length=5)

    tactical_description: Optional[str] = Field(default=None, max_length=500)
    uncertainties: list[str] = Field(default_factory=list, max_length=5)

    action_sequence: list[ActionStep] = Field(
        default_factory=list,
        max_length=10,
    )

    defensive_bypass: Optional[str] = Field(default=None, max_length=300)
