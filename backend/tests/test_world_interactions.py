
import unittest
from unittest.mock import patch

from app.actions.world_interactions import pick_up_item
from app.game_state import CharacterState, GameState, Position
from app.game_state_manager import GameStateManager
from app.world_state import WorldItem, WorldState
from app.world_state_manager import WorldStateManager


class TestWorldInteractions(unittest.TestCase):
    def setUp(self):
        self.character = CharacterState(
            character_id="player",
            name="Герой",
            position=Position(x=0, y=0, z=0),
        )

        self.game_manager = GameStateManager(
            GameState(
                session_id="test",
                player=self.character,
            )
        )

        self.world_manager = WorldStateManager(
            WorldState(world_id="test-world")
        )

        self.item = WorldItem(
            item_id="sword",
            name="Меч",
            position=Position(x=1, y=0, z=0),
            quantity=1,
            weight=2.0,
            description="Старый меч",
        )

        self.world_manager.add_item(self.item)

    def test_pick_up_item_successfully(self):
        result = pick_up_item(
            "player",
            "sword",
            self.game_manager,
            self.world_manager,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.item_id, "sword")
        self.assertEqual(len(self.character.inventory), 1)

        with self.assertRaises(ValueError):
            self.world_manager.get_item("sword")

    def test_cannot_pick_up_item_too_far_away(self):
        self.world_manager.remove_item("sword")
        self.world_manager.add_item(
            WorldItem(
                item_id="sword",
                name="Меч",
                position=Position(x=10, y=0, z=0),
                quantity=1,
                weight=2.0,
                description="Старый меч",
            )
        )

        result = pick_up_item(
            "player",
            "sword",
            self.game_manager,
            self.world_manager,
        )

        self.assertFalse(result.success)
        self.assertEqual(len(self.character.inventory), 0)
        self.world_manager.get_item("sword")

    def test_cannot_pick_up_inaccessible_item(self):
        self.world_manager.remove_item("sword")
        self.world_manager.add_item(
            WorldItem(
                item_id="sword",
                name="Меч",
                position=Position(x=1, y=0, z=0),
                quantity=1,
                weight=2.0,
                description="Старый меч",
                is_accessible=False,
            )
        )

        result = pick_up_item(
            "player",
            "sword",
            self.game_manager,
            self.world_manager,
        )

        self.assertFalse(result.success)
        self.assertEqual(len(self.character.inventory), 0)
        self.world_manager.get_item("sword")

    def test_dead_character_cannot_pick_up_item(self):
        self.character.is_alive = False
        self.character.is_conscious = False

        result = pick_up_item(
            "player",
            "sword",
            self.game_manager,
            self.world_manager,
        )

        self.assertFalse(result.success)
        self.assertEqual(len(self.character.inventory), 0)
        self.world_manager.get_item("sword")

    def test_unconscious_character_cannot_pick_up_item(self):
        self.character.is_conscious = False

        result = pick_up_item(
            "player",
            "sword",
            self.game_manager,
            self.world_manager,
        )

        self.assertFalse(result.success)
        self.assertEqual(len(self.character.inventory), 0)
        self.world_manager.get_item("sword")

    def test_restrained_character_cannot_pick_up_item(self):
        self.character.is_restrained = True

        result = pick_up_item(
            "player",
            "sword",
            self.game_manager,
            self.world_manager,
        )

        self.assertFalse(result.success)
        self.assertEqual(len(self.character.inventory), 0)
        self.world_manager.get_item("sword")

    def test_item_remains_in_world_if_inventory_add_fails(self):
        with patch.object(
            self.game_manager,
            "add_item",
            side_effect=ValueError("Инвентарь переполнен"),
        ):
            result = pick_up_item(
                "player",
                "sword",
                self.game_manager,
                self.world_manager,
            )

        self.assertFalse(result.success)
        self.assertEqual(len(self.character.inventory), 0)
        self.world_manager.get_item("sword")


if __name__ == "__main__":
    unittest.main()
