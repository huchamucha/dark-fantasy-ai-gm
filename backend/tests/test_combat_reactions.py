import unittest

from app.actions.combat_observation import (
    AttackIntent,
    DefenderObservation,
    ObservationContext,
    ObservationQuality,
)
from app.actions.combat_reactions import (
    CombatReactionRequest,
    process_combat_reaction,
)
from app.actions.combat_timing import (
    AttackPhase,
    AttackTiming,
    ObservableTelegraph,
    ReactionContext,
    ReactionType,
    ReactionWindow,
)


class TestCombatReactions(unittest.TestCase):
    def setUp(self):
        self.intent = AttackIntent(
            intended_attack="Удар сверху с переходом в выпад.",
            intended_target="Корпус",
            follow_up="Резкий выпад вперёд.",
            tactical_goal="Заставить противника ошибиться при выборе защиты.",
        )

        self.observation = DefenderObservation(
            visible_movement="Противник поднимает меч над головой.",
            apparent_attack="Удар сверху",
            apparent_target="Верхняя часть тела",
            quality=ObservationQuality.CLEAR,
            confidence=0.9,
            observed_signals=["Меч поднят", "Корпус развёрнут"],
        )

        self.telegraph = ObservableTelegraph(
            description="Противник готовит удар.",
            visible_movement="Меч поднят над головой.",
            apparent_attack_type="Удар сверху",
            apparent_target="Верхняя часть тела",
            confidence=0.9,
        )

        self.timing = AttackTiming(
            phase=AttackPhase.START_MOVEMENT,
            reaction_window=ReactionWindow.OPEN,
            telegraph=self.telegraph,
            commitment=0.2,
        )

        self.defender = ReactionContext(
            current_br=100,
            current_stamina=100,
            perception=5,
            reaction_skill=5,
        )

        self.observation_context = ObservationContext(
            perception=5,
            awareness=5,
            combat_experience=5,
            visibility=1.0,
            distance=2.0,
        )

    def make_request(self, **overrides):
        data = {
            "attack_intent": self.intent,
            "attack_timing": self.timing,
            "defender_observation": self.observation,
            "defender_context": self.defender,
            "observation_context": self.observation_context,
            "reaction_type": ReactionType.BLOCK,
        }
        data.update(overrides)
        return CombatReactionRequest(**data)

    def test_reaction_is_available(self):
        result = process_combat_reaction(self.make_request())

        self.assertTrue(result.available)
        self.assertIsNotNone(result.assessment)

    def test_reaction_is_denied_when_br_is_insufficient(self):
        defender = self.defender.model_copy(update={"current_br": 10})

        request = self.make_request(defender_context=defender)
        result = process_combat_reaction(request)

        self.assertFalse(result.available)
        self.assertIn("боевого ресурса", result.reason)

    def test_reaction_is_denied_when_visibility_is_zero(self):
        context = self.observation_context.model_copy(
            update={"visibility": 0.0}
        )

        request = self.make_request(observation_context=context)
        result = process_combat_reaction(request)

        self.assertFalse(result.available)

    def test_distraction_reduces_observation_confidence(self):
        context = self.observation_context.model_copy(
            update={"is_distracted": True}
        )

        request = self.make_request(observation_context=context)
        result = process_combat_reaction(request)

        self.assertTrue(result.available)
        self.assertLessEqual(result.assessment.confidence, 0.25)

    def test_reaction_does_not_spend_resources(self):
        initial_br = self.defender.current_br
        initial_stamina = self.defender.current_stamina

        process_combat_reaction(self.make_request())

        self.assertEqual(self.defender.current_br, initial_br)
        self.assertEqual(self.defender.current_stamina, initial_stamina)

    def test_hidden_attack_intent_is_not_returned(self):
        result = process_combat_reaction(self.make_request())
        result_data = result.model_dump()

        self.assertNotIn("attack_intent", result_data)
        self.assertNotIn("follow_up", result_data)
        self.assertNotIn("tactical_goal", result_data)


if __name__ == "__main__":
    unittest.main()
