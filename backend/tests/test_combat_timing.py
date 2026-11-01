import unittest

from app.actions.combat_timing import (
    AttackPhase,
    AttackTiming,
    ObservableTelegraph,
    ReactionContext,
    ReactionType,
    ReactionWindow,
    can_react,
)


class TestCombatTiming(unittest.TestCase):
    def setUp(self):
        self.telegraph = ObservableTelegraph(
            description="Противник поднимает меч над головой.",
            visible_movement="Меч поднят, корпус готовится к замаху.",
            apparent_attack_type="overhead_slash",
            apparent_target="upper_body",
        )

        self.defender = ReactionContext(
            current_br=100,
            current_stamina=100,
            perception=5,
            reaction_skill=5,
        )

        self.attack = AttackTiming(
            phase=AttackPhase.START_MOVEMENT,
            reaction_window=ReactionWindow.OPEN,
            telegraph=self.telegraph,
            commitment=0.2,
        )

    def test_defender_can_react_to_visible_telegraph(self):
        result = can_react(
            self.attack,
            self.defender,
            ReactionType.DODGE,
        )

        self.assertTrue(result.available)
        self.assertEqual(result.br_cost, 25)
        self.assertEqual(result.stamina_cost, 5)
        self.assertIsNotNone(result.observed_telegraph)

    def test_reaction_is_denied_when_window_is_closed(self):
        self.attack.reaction_window = ReactionWindow.CLOSED

        result = can_react(
            self.attack,
            self.defender,
            ReactionType.BLOCK,
        )

        self.assertFalse(result.available)
        self.assertIn("закрыто", result.reason)

    def test_reaction_is_denied_at_impact(self):
        self.attack.phase = AttackPhase.IMPACT

        result = can_react(
            self.attack,
            self.defender,
            ReactionType.PARRY,
        )

        self.assertFalse(result.available)

    def test_reaction_is_denied_without_telegraph(self):
        self.attack.telegraph = None

        result = can_react(
            self.attack,
            self.defender,
            ReactionType.DODGE,
        )

        self.assertFalse(result.available)
        self.assertIn("сигналов", result.reason)

    def test_reaction_is_denied_with_insufficient_br(self):
        self.defender.current_br = 20

        result = can_react(
            self.attack,
            self.defender,
            ReactionType.BLOCK,
        )

        self.assertFalse(result.available)
        self.assertIn("боевого ресурса", result.reason)

    def test_reaction_is_denied_with_insufficient_stamina(self):
        self.defender.current_stamina = 3

        result = can_react(
            self.attack,
            self.defender,
            ReactionType.DODGE,
        )

        self.assertFalse(result.available)
        self.assertIn("выносливости", result.reason)

    def test_movement_reaction_is_denied_when_movement_is_impossible(self):
        self.defender.can_move = False

        result = can_react(
            self.attack,
            self.defender,
            ReactionType.STEP_LEFT,
        )

        self.assertFalse(result.available)
        self.assertIn("перемещаться", result.reason)

    def test_restrained_defender_cannot_react(self):
        self.defender.is_restrained = True

        result = can_react(
            self.attack,
            self.defender,
            ReactionType.BLOCK,
        )

        self.assertFalse(result.available)

    def test_dead_defender_cannot_react(self):
        self.defender.is_alive = False

        result = can_react(
            self.attack,
            self.defender,
            ReactionType.DODGE,
        )

        self.assertFalse(result.available)

    def test_unconscious_defender_cannot_react(self):
        self.defender.is_conscious = False

        result = can_react(
            self.attack,
            self.defender,
            ReactionType.BLOCK,
        )

        self.assertFalse(result.available)

    def test_reaction_does_not_spend_resources(self):
        initial_br = self.defender.current_br
        initial_stamina = self.defender.current_stamina

        result = can_react(
            self.attack,
            self.defender,
            ReactionType.DODGE,
        )

        self.assertTrue(result.available)
        self.assertEqual(self.defender.current_br, initial_br)
        self.assertEqual(self.defender.current_stamina, initial_stamina)


if __name__ == "__main__":
    unittest.main()
