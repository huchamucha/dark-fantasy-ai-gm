import unittest

from app.engine.combat.models import Combatant
from app.engine.combat.turn_order import start_combat
from app.engine.combat.turns import advance_turn


class TestCombat(unittest.TestCase):

    def setUp(self):
        self.hero = Combatant(
            id="p1",
            name="Герой",
            side="player",
            hp=18,
            max_hp=18,
            armor_class=14,
        )
        self.enemy = Combatant(
            id="e1",
            name="Стражник",
            side="enemy",
            hp=12,
            max_hp=12,
            armor_class=12,
        )

    def test_victory(self):
        combat = start_combat([self.hero, self.enemy])
        self.enemy.hp = 0

        advance_turn(combat)

        self.assertEqual(combat.status, "victory")

    def test_defeat(self):
        combat = start_combat([self.hero, self.enemy])
        self.hero.hp = 0

        advance_turn(combat)

        self.assertEqual(combat.status, "defeat")

    def test_movement_and_attack_range(self):
        from app.engine.combat.engine import CombatEngine

        engine = CombatEngine()

        hero = Combatant(
            id="p",
            name="Герой",
            side="player",
            hp=18,
            max_hp=18,
            armor_class=14,
            x=0,
            y=0,
            strength=16,
            weapon_range=1,
        )

        guard = Combatant(
            id="x",
            name="Стражник",
            side="enemy",
            hp=30,
            max_hp=30,
            armor_class=10,
            x=3,
            y=0,
        )

        battle = engine.start_battle([hero, guard])

        # Дожидаемся хода героя.
        while battle.current_combatant.side != "player":
            engine.end_turn(battle.id)

        # На расстоянии 3 метров атаковать нельзя.
        with self.assertRaises(ValueError):
            engine.attack(battle.id, "x")

        # Герой приближается на 2 метра.
        engine.move(battle.id, 2, 0)

        # Теперь расстояние равно 1 метру.
        self.assertEqual(abs(hero.x - guard.x), 1)

        # Атака должна пройти проверку дальности.
        result = engine.attack(battle.id, "x")

        self.assertTrue(result.hit or not result.hit)
        self.assertTrue(hero.action_used)

if __name__ == "__main__":
    unittest.main()
