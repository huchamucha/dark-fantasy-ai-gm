
import unittest

from app.game_state import (
    CharacterState,
    GameState,
    InventoryItem,
    Position,
)
from app.game_state_manager import GameStateManager
from app.actions.execution import ExecutionResult
from app.actions.combat_parry import (
    ParryResult,
    ParryStatus,
)


def create_manager():
    state = GameState(
        session_id="test_session",
        player=CharacterState(
            character_id="hero",
            name="Герой",
        ),
    )
    return GameStateManager(state)


class TestGameStateManager(unittest.TestCase):

    def test_add_item(self):
        manager = create_manager()

        manager.add_item(
            "hero",
            InventoryItem(
                item_id="potion",
                name="Зелье",
                quantity=1,
            ),
        )

        self.assertEqual(len(manager.state.player.inventory), 1)
        self.assertEqual(
            manager.state.player.inventory[0].item_id,
            "potion",
        )

    def test_add_existing_item_increases_quantity(self):
        manager = create_manager()

        item = InventoryItem(
            item_id="potion",
            name="Зелье",
            quantity=1,
        )

        manager.add_item("hero", item)
        manager.add_item("hero", item)

        self.assertEqual(
            manager.state.player.inventory[0].quantity,
            2,
        )

    def test_remove_item(self):
        manager = create_manager()

        manager.add_item(
            "hero",
            InventoryItem(
                item_id="potion",
                name="Зелье",
                quantity=2,
            ),
        )

        removed = manager.remove_item("hero", "potion")

        self.assertEqual(removed.quantity, 1)
        self.assertEqual(
            manager.state.player.inventory[0].quantity,
            1,
        )

    def test_remove_last_item(self):
        manager = create_manager()

        manager.add_item(
            "hero",
            InventoryItem(
                item_id="potion",
                name="Зелье",
            ),
        )

        manager.remove_item("hero", "potion")

        self.assertEqual(manager.state.player.inventory, [])

    def test_remove_missing_item_fails(self):
        manager = create_manager()

        with self.assertRaises(ValueError):
            manager.remove_item("hero", "missing_item")

    def test_move_character(self):
        manager = create_manager()

        manager.move_character(
            "hero",
            Position(x=5, y=3, z=0),
        )

        self.assertEqual(manager.state.player.position.x, 5)
        self.assertEqual(manager.state.player.position.y, 3)

    def test_restrained_character_cannot_move(self):
        manager = create_manager()
        manager.state.player.is_restrained = True

        with self.assertRaises(ValueError):
            manager.move_character(
                "hero",
                Position(x=5, y=3, z=0),
            )

        self.assertEqual(manager.state.player.position.x, 0)

    def test_spend_stamina(self):
        manager = create_manager()

        manager.spend_stamina("hero", 30)

        self.assertEqual(manager.state.player.stamina, 70)

    def test_insufficient_stamina_does_not_change_value(self):
        manager = create_manager()

        with self.assertRaises(ValueError):
            manager.spend_stamina("hero", 150)

        self.assertEqual(manager.state.player.stamina, 100)

    def test_apply_execution_result(self):
        manager = create_manager()

        result = ExecutionResult(
            initial_br=100,
            spent_br=50,
            remaining_br=50,
            initial_stamina=100,
            spent_stamina=10,
            remaining_stamina=90,
            steps=[],
        )

        manager.apply_execution_result("hero", result)

        self.assertEqual(manager.state.player.current_br, 50)
        self.assertEqual(manager.state.player.stamina, 90)

    def test_insufficient_stamina_does_not_apply_execution(self):
        manager = create_manager()
        manager.state.player.stamina = 5

        result = ExecutionResult(
            initial_br=100,
            spent_br=50,
            remaining_br=50,
            initial_stamina=100,
            spent_stamina=10,
            remaining_stamina=90,
            steps=[],
        )

        with self.assertRaises(ValueError):
            manager.apply_execution_result("hero", result)

        self.assertEqual(manager.state.player.current_br, 100)
        self.assertEqual(manager.state.player.stamina, 5)

    def test_start_new_turn(self):
        manager = create_manager()
        manager.state.player.current_br = 20

        manager.start_new_turn()

        self.assertEqual(manager.state.player.current_br, 100)
        self.assertEqual(manager.state.turn_number, 2)

    def test_transfer_initiative_preserves_br(self):
        manager = create_manager()
        manager.state.player.current_br = 60

        manager.transfer_initiative("hero")

        self.assertEqual(manager.state.player.current_br, 60)
        self.assertEqual(
            manager.state.active_character_id,
            "hero",
        )

    def test_transfer_initiative_increases_turn_number(self):
        manager = create_manager()

        manager.transfer_initiative("hero")

        self.assertEqual(manager.state.turn_number, 2)

    def test_dead_character_cannot_receive_initiative(self):
        manager = create_manager()

        manager.state.npcs["enemy"] = CharacterState(
            character_id="enemy",
            name="Противник",
            hp=0,
            is_alive=False,
            is_conscious=False,
        )

        with self.assertRaises(ValueError):
            manager.transfer_initiative("enemy")

        self.assertIsNone(manager.state.active_character_id)
        self.assertEqual(manager.state.turn_number, 1)

    def test_apply_simple_parry_result(self):
        manager = create_manager()

        result = ParryResult(
            status=ParryStatus.PARRIED,
            success=True,
            br_spent=25,
            stamina_spent=5,
            reason="Успешное парирование",
        )

        manager.apply_parry_result("hero", result)

        self.assertEqual(manager.state.player.current_br, 75)
        self.assertEqual(manager.state.player.stamina, 95)
        self.assertIsNone(manager.state.active_character_id)
        self.assertEqual(manager.state.turn_number, 1)

    def test_apply_counter_parry_transfers_initiative(self):
        manager = create_manager()
        manager.state.player.current_br = 60

        result = ParryResult(
            status=ParryStatus.COUNTERED,
            success=True,
            br_spent=30,
            stamina_spent=10,
            counter_attack="Ответный удар",
            initiative_transferred=True,
            reason="Успешная контратака",
        )

        manager.apply_parry_result("hero", result)

        self.assertEqual(manager.state.player.current_br, 30)
        self.assertEqual(manager.state.player.stamina, 90)
        self.assertEqual(manager.state.active_character_id, "hero")
        self.assertEqual(manager.state.turn_number, 2)

    def test_apply_failed_parry_spends_resources_without_transfer(self):
        manager = create_manager()

        result = ParryResult(
            status=ParryStatus.FAILED,
            success=False,
            br_spent=25,
            stamina_spent=5,
            reason="Парирование не удалось",
        )

        manager.apply_parry_result("hero", result)

        self.assertEqual(manager.state.player.current_br, 75)
        self.assertEqual(manager.state.player.stamina, 95)
        self.assertIsNone(manager.state.active_character_id)
        self.assertEqual(manager.state.turn_number, 1)

    def test_insufficient_br_does_not_apply_parry(self):
        manager = create_manager()
        manager.state.player.current_br = 10

        result = ParryResult(
            status=ParryStatus.PARRIED,
            success=True,
            br_spent=25,
            stamina_spent=5,
            reason="Успешное парирование",
        )

        with self.assertRaises(ValueError):
            manager.apply_parry_result("hero", result)

        self.assertEqual(manager.state.player.current_br, 10)
        self.assertEqual(manager.state.player.stamina, 100)
        self.assertIsNone(manager.state.active_character_id)
        self.assertEqual(manager.state.turn_number, 1)


if __name__ == "__main__":
    unittest.main()
