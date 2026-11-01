
import unittest

from pydantic import ValidationError

from app.actions.combat_parry import (
    ParryRequest,
    ParryType,
    ParryStatus,
    resolve_parry,
)


class TestCombatParry(unittest.TestCase):

    def test_simple_parry_success(self):
        result = resolve_parry(
            ParryRequest(
                parry_type=ParryType.SIMPLE,
                targeted_attack="Колющий удар",
                br_cost=25,
                stamina_cost=5,
                success=True,
            )
        )

        self.assertEqual(result.status, ParryStatus.PARRIED)
        self.assertEqual(result.br_spent, 25)
        self.assertEqual(result.stamina_spent, 5)
        self.assertEqual(result.next_enemy_attack_modifier, 1)
        self.assertFalse(result.initiative_transferred)

    def test_counter_parry_success(self):
        result = resolve_parry(
            ParryRequest(
                parry_type=ParryType.COUNTER,
                targeted_attack="Колющий удар",
                counter_attack="Мой колющий удар",
                br_cost=40,
                stamina_cost=10,
                success=True,
            )
        )

        self.assertEqual(result.status, ParryStatus.COUNTERED)
        self.assertTrue(result.initiative_transferred)
        self.assertEqual(result.counter_attack, "Мой колющий удар")
        self.assertEqual(result.br_spent, 40)

    def test_failed_counter_does_not_transfer_initiative(self):
        result = resolve_parry(
            ParryRequest(
                parry_type=ParryType.COUNTER,
                targeted_attack="Колющий удар",
                counter_attack="Мой колющий удар",
                br_cost=40,
                stamina_cost=10,
                success=False,
            )
        )

        self.assertEqual(result.status, ParryStatus.FAILED)
        self.assertFalse(result.initiative_transferred)

    def test_counter_requires_counter_attack(self):
        with self.assertRaises(ValidationError):
            resolve_parry(
                ParryRequest(
                    parry_type=ParryType.COUNTER,
                    targeted_attack="Колющий удар",
                    br_cost=40,
                    stamina_cost=10,
                    success=True,
                )
            )

    def test_simple_parry_does_not_have_counter_attack(self):
        result = resolve_parry(
            ParryRequest(
                parry_type=ParryType.SIMPLE,
                targeted_attack="Рубящий удар",
                br_cost=25,
                stamina_cost=5,
                success=True,
            )
        )

        self.assertIsNone(result.counter_attack)

    def test_failed_parry_still_spends_declared_resources(self):
        result = resolve_parry(
            ParryRequest(
                parry_type=ParryType.SIMPLE,
                targeted_attack="Рубящий удар",
                br_cost=25,
                stamina_cost=5,
                success=False,
            )
        )

        self.assertEqual(result.br_spent, 25)
        self.assertEqual(result.stamina_spent, 5)


if __name__ == "__main__":
    unittest.main()
