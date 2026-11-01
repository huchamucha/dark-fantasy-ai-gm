import unittest

from app.game_state import Position
from app.world_state import (
    WorldItem,
    WorldObject,
    WorldObstacle,
    WorldState,
)
from app.world_state_manager import WorldStateManager


def create_manager():
    state = WorldState(world_id="test_world")
    return WorldStateManager(state)


class TestWorldStateManager(unittest.TestCase):

    def test_add_and_get_item(self):
        manager = create_manager()

        item = WorldItem(
            item_id="sword_01",
            name="Железный меч",
            position=Position(x=1, y=0, z=0),
        )

        manager.add_item(item)

        found = manager.get_item("sword_01")

        self.assertEqual(found.name, "Железный меч")

    def test_duplicate_item_is_rejected(self):
        manager = create_manager()

        item = WorldItem(
            item_id="sword_01",
            name="Железный меч",
        )

        manager.add_item(item)

        with self.assertRaises(ValueError):
            manager.add_item(item)

    def test_remove_item(self):
        manager = create_manager()

        manager.add_item(
            WorldItem(
                item_id="sword_01",
                name="Меч",
            )
        )

        removed = manager.remove_item("sword_01")

        self.assertEqual(removed.item_id, "sword_01")
        self.assertEqual(manager.state.items, [])

    def test_find_nearby_items(self):
        manager = create_manager()

        manager.add_item(
            WorldItem(
                item_id="near",
                name="Ближний предмет",
                position=Position(x=1, y=0, z=0),
            )
        )

        manager.add_item(
            WorldItem(
                item_id="far",
                name="Дальний предмет",
                position=Position(x=10, y=0, z=0),
            )
        )

        nearby = manager.find_nearby_items(
            Position(x=0, y=0, z=0),
            max_distance=2,
        )

        self.assertEqual(len(nearby), 1)
        self.assertEqual(nearby[0].item_id, "near")

    def test_inaccessible_item_is_not_found(self):
        manager = create_manager()

        manager.add_item(
            WorldItem(
                item_id="hidden",
                name="Недоступный предмет",
                is_accessible=False,
            )
        )

        nearby = manager.find_nearby_items(Position())

        self.assertEqual(nearby, [])

    def test_calculate_distance(self):
        distance = WorldStateManager.calculate_distance(
            Position(x=0, y=0, z=0),
            Position(x=3, y=4, z=0),
        )

        self.assertEqual(distance, 5)

    def test_add_and_get_object(self):
        manager = create_manager()

        manager.add_object(
            WorldObject(
                object_id="door_01",
                name="Деревянная дверь",
            )
        )

        obj = manager.get_object("door_01")

        self.assertEqual(obj.name, "Деревянная дверь")

    def test_add_obstacle(self):
        manager = create_manager()

        manager.add_obstacle(
            WorldObstacle(
                obstacle_id="wall_01",
                name="Каменная стена",
                position=Position(x=5, y=0, z=0),
                radius=2,
            )
        )

        self.assertTrue(
            manager.is_position_blocked(
                Position(x=5, y=0, z=0)
            )
        )

    def test_position_outside_obstacle(self):
        manager = create_manager()

        manager.add_obstacle(
            WorldObstacle(
                obstacle_id="wall_01",
                name="Стена",
                position=Position(x=5, y=0, z=0),
                radius=2,
            )
        )

        self.assertFalse(
            manager.is_position_blocked(
                Position(x=0, y=0, z=0)
            )
        )

    def test_non_blocking_obstacle_allows_movement(self):
        manager = create_manager()

        manager.add_obstacle(
            WorldObstacle(
                obstacle_id="decoration",
                name="Декоративный объект",
                position=Position(x=0, y=0, z=0),
                radius=2,
                blocks_movement=False,
            )
        )

        self.assertTrue(manager.can_move_to(Position()))

    def test_negative_distance_is_rejected(self):
        manager = create_manager()

        with self.assertRaises(ValueError):
            manager.find_nearby_items(Position(), max_distance=-1)


if __name__ == "__main__":
    unittest.main()
