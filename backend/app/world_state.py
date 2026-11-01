from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.game_state import Position


class WorldItem(BaseModel):
    """Предмет, находящийся непосредственно в игровом мире."""

    model_config = ConfigDict(extra="forbid")

    item_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    position: Position = Field(default_factory=Position)

    quantity: int = Field(default=1, ge=1)
    weight: float = Field(default=0, ge=0)

    description: Optional[str] = Field(default=None, max_length=500)
    is_accessible: bool = True


class WorldObject(BaseModel):
    """Объект окружения: дверь, сундук, рычаг и т. п."""

    model_config = ConfigDict(extra="forbid")

    object_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)

    position: Position = Field(default_factory=Position)

    is_interactable: bool = True
    is_blocking: bool = False
    is_open: bool = False

    description: Optional[str] = Field(default=None, max_length=500)


class WorldObstacle(BaseModel):
    """Препятствие, занимающее область пространства."""

    model_config = ConfigDict(extra="forbid")

    obstacle_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)

    position: Position = Field(default_factory=Position)
    radius: float = Field(default=0.5, gt=0)

    blocks_movement: bool = True


class WorldState(BaseModel):
    """Состояние окружающего игрового мира."""

    model_config = ConfigDict(extra="forbid")

    world_id: str = Field(min_length=1, max_length=100)

    items: list[WorldItem] = Field(default_factory=list)
    objects: list[WorldObject] = Field(default_factory=list)
    obstacles: list[WorldObstacle] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_ids(self):
        item_ids = [item.item_id for item in self.items]
        object_ids = [obj.object_id for obj in self.objects]
        obstacle_ids = [obs.obstacle_id for obs in self.obstacles]

        if len(item_ids) != len(set(item_ids)):
            raise ValueError("ID предметов в мире должны быть уникальными")

        if len(object_ids) != len(set(object_ids)):
            raise ValueError("ID объектов мира должны быть уникальными")

        if len(obstacle_ids) != len(set(obstacle_ids)):
            raise ValueError("ID препятствий должны быть уникальными")

        return self
