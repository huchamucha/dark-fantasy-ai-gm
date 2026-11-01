import math

from app.game_state import Position
from app.world_state import (
    WorldItem,
    WorldObject,
    WorldObstacle,
    WorldState,
)


class WorldStateManager:
    """Управляет объектами и предметами окружающего мира."""

    def __init__(self, state: WorldState):
        self.state = state

    @staticmethod
    def calculate_distance(
        first: Position,
        second: Position,
    ) -> float:
        """Рассчитывает трёхмерное расстояние между позициями."""

        return math.sqrt(
            (first.x - second.x) ** 2
            + (first.y - second.y) ** 2
            + (first.z - second.z) ** 2
        )

    def add_item(self, item: WorldItem) -> None:
        """Добавляет предмет в мир."""

        if any(existing.item_id == item.item_id for existing in self.state.items):
            raise ValueError("Предмет с таким ID уже существует")

        self.state.items.append(item.model_copy(deep=True))

    def get_item(self, item_id: str) -> WorldItem:
        """Находит предмет в мире."""

        item = next(
            (
                entry
                for entry in self.state.items
                if entry.item_id == item_id
            ),
            None,
        )

        if item is None:
            raise ValueError("Предмет не найден в мире")

        return item

    def remove_item(self, item_id: str) -> WorldItem:
        """Удаляет предмет из мира и возвращает его."""

        item = self.get_item(item_id)
        self.state.items.remove(item)
        return item

    def find_nearby_items(
        self,
        position: Position,
        max_distance: float = 2.0,
    ) -> list[WorldItem]:
        """Находит доступные предметы в заданном радиусе."""

        if max_distance < 0:
            raise ValueError("Расстояние не может быть отрицательным")

        return [
            item
            for item in self.state.items
            if item.is_accessible
            and self.calculate_distance(position, item.position) <= max_distance
        ]

    def add_object(self, obj: WorldObject) -> None:
        """Добавляет объект окружения."""

        if any(
            existing.object_id == obj.object_id
            for existing in self.state.objects
        ):
            raise ValueError("Объект с таким ID уже существует")

        self.state.objects.append(obj.model_copy(deep=True))

    def get_object(self, object_id: str) -> WorldObject:
        """Находит объект окружения."""

        obj = next(
            (
                entry
                for entry in self.state.objects
                if entry.object_id == object_id
            ),
            None,
        )

        if obj is None:
            raise ValueError("Объект не найден")

        return obj

    def add_obstacle(self, obstacle: WorldObstacle) -> None:
        """Добавляет препятствие."""

        if any(
            existing.obstacle_id == obstacle.obstacle_id
            for existing in self.state.obstacles
        ):
            raise ValueError("Препятствие с таким ID уже существует")

        self.state.obstacles.append(obstacle.model_copy(deep=True))

    def is_position_blocked(self, position: Position) -> bool:
        """Проверяет, находится ли позиция внутри препятствия."""

        for obstacle in self.state.obstacles:
            if not obstacle.blocks_movement:
                continue

            distance = self.calculate_distance(
                position,
                obstacle.position,
            )

            if distance < obstacle.radius:
                return True

        return False

    def can_move_to(self, position: Position) -> bool:
        """Проверяет возможность занять указанную позицию."""

        return not self.is_position_blocked(position)
