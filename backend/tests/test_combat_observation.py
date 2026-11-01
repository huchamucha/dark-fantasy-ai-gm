import unittest

from app.actions.combat_observation import (
    AttackIntent,
    DefenderObservation,
    ObservationQuality,
    ReactionAssessment,
    assess_reaction,
)


class TestCombatObservation(unittest.TestCase):
    def setUp(self):
        self.hidden_intent = AttackIntent(
            intended_attack="удар сверху",
            intended_target="голова",
            follow_up="резко изменить направление и выполнить выпад в корпус",
            feints=["ложное движение плечом"],
            tactical_goal="заставить противника поднять защиту",
        )

        self.observation = DefenderObservation(
            visible_movement="Противник поднимает меч над головой.",
            apparent_attack="удар сверху",
            apparent_target="верхняя часть тела",
            quality=ObservationQuality.CLEAR,
            confidence=0.9,
            observed_signals=["меч поднят", "корпус развёрнут"],
        )

    def test_hidden_intent_contains_follow_up(self):
        self.assertIsNotNone(self.hidden_intent.follow_up)
        self.assertIn("выпад", self.hidden_intent.follow_up)

    def test_defender_observation_does_not_contain_hidden_follow_up(self):
        observation_data = self.observation.model_dump()

        self.assertNotIn("follow_up", observation_data)
        self.assertNotIn("tactical_goal", observation_data)
        self.assertNotIn("feints", observation_data)

    def test_defender_can_choose_reaction_to_visible_attack(self):
        result = assess_reaction(
            self.observation,
            "block",
        )

        self.assertTrue(result.matches_observation)
        self.assertGreater(result.confidence, 0)

    def test_defender_can_attempt_dodge(self):
        result = assess_reaction(
            self.observation,
            "dodge",
        )

        self.assertTrue(result.matches_observation)

    def test_no_observation_prevents_informed_reaction(self):
        observation = DefenderObservation(
            visible_movement="Защитник ничего не заметил.",
            quality=ObservationQuality.NONE,
            confidence=0.0,
        )
        result = assess_reaction(observation, "block")

        self.assertFalse(result.matches_observation)
        self.assertEqual(result.confidence, 0.0)

    def test_empty_reaction_is_rejected(self):
        result = assess_reaction(self.observation, "   ")

        self.assertFalse(result.matches_observation)
        self.assertEqual(result.confidence, 0.0)

    def test_unknown_reaction_is_not_automatically_accepted(self):
        result = assess_reaction(
            self.observation,
            "teleport",
        )

        self.assertFalse(result.matches_observation)

    def test_reaction_assessment_does_not_reveal_hidden_intent(self):
        result = assess_reaction(
            self.observation,
            "block",
        )

        result_data = result.model_dump()

        self.assertNotIn("intended_attack", result_data)
        self.assertNotIn("follow_up", result_data)
        self.assertNotIn("tactical_goal", result_data)


if __name__ == "__main__":
    unittest.main()
