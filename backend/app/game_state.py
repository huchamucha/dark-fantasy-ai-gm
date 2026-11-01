
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Position(BaseModel):
    """Положение персонажа в игровом мире."""

    model_config = ConfigDict(extra="forbid")

    x: float = 0
    y: float = 0
    z: float = 0


class BodyPartState(BaseModel):
    """Состояние отдельной части тела."""

    model_config = ConfigDict(extra="forbid")

    hp: int = Field(ge=0)
    max_hp: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_hp(self):
        if self.hp > self.max_hp:
            raise ValueError("HP части тела не может превышать max_hp")
        return self


class InventoryItem(BaseModel):
    """Предмет в инвентаре персонажа."""

    model_config = ConfigDict(extra="forbid")

    item_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    quantity: int = Field(default=1, ge=1)
    weight: float = Field(default=0, ge=0)

    equipped: bool = False
    description: Optional[str] = Field(default=None, max_length=500)


class CharacterState(BaseModel):
    """Полное состояние игрового персонажа."""

    model_config = ConfigDict(extra="forbid")

    character_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)

    hp: int = Field(default=100, ge=0)
    max_hp: int = Field(default=100, gt=0)

    stamina: int = Field(default=100, ge=0)
    max_stamina: int = Field(default=100, gt=0)

    current_br: int = Field(default=100, ge=0)
    max_br: int = Field(default=100, gt=0)

    position: Position = Field(default_factory=Position)

    inventory: list[InventoryItem] = Field(default_factory=list)

    body_parts: dict[str, BodyPartState] = Field(default_factory=dict)

    is_alive: bool = True
    is_conscious: bool = True
    is_restrained: bool = False

    @model_validator(mode="after")
    def validate_character_state(self):
        if self.hp > self.max_hp:
            raise ValueError("HP не может превышать max_hp")

        if self.stamina > self.max_stamina:
            raise ValueError("Выносливость не может превышать max_stamina")

        if self.current_br > self.max_br:
            raise ValueError("БР не может превышать max_br")

        if self.hp == 0 and self.is_alive:
            raise ValueError("Персонаж с нулевым HP не может быть жив")

        if self.is_conscious and not self.is_alive:
            raise ValueError("Мёртвый персонаж не может быть в сознании")

        item_ids = [item.item_id for item in self.inventory]

        if len(item_ids) != len(set(item_ids)):
            raise ValueError("ID предметов в инвентаре должны быть уникальными")

        return self


class GameState(BaseModel):
    """Основное состояние игровой сессии."""

    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1, max_length=100)

    player: CharacterState

    npcs: dict[str, CharacterState] = Field(default_factory=dict)

    turn_number: int = Field(default=1, ge=1)

    active_character_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_active_character(self):
        if self.active_character_id is not None:
            character_ids = {
                self.player.character_id,
                *self.npcs.keys(),
            }

            if self.active_character_id not in character_ids:
                raise ValueError("Активный персонаж отсутствует в игровой сессии")

        return self
