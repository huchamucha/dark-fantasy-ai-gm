import unittest

from app.engine.attributes import get_modifier, validate_attributes
from app.engine.dice import roll_die, roll_dice
from app.engine.skills import get_skill_ability
from app.engine.checks import make_check, make_skill_check


class TestAttributes(unittest.TestCase):

    def test_modifiers(self):
        self.assertEqual(get_modifier(6), -2)
        self.assertEqual(get_modifier(8), -1)
        self.assertEqual(get_modifier(10), 0)
        self.assertEqual(get_modifier(14), 2)
        self.assertEqual(get_modifier(18), 4)
        self.assertEqual(get_modifier(20), 5)

    def test_invalid_score(self):
        with self.assertRaises(ValueError):
            get_modifier(31)

    def test_six_attributes(self):
        attributes = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
        }
        validate_attributes(attributes)


class TestDice(unittest.TestCase):

    def test_die_range(self):
        for _ in range(100):
            result = roll_die(20)
            self.assertGreaterEqual(result, 1)
            self.assertLessEqual(result, 20)

    def test_invalid_die(self):
        with self.assertRaises(ValueError):
            roll_die(7)

    def test_multiple_dice(self):
        result = roll_dice(2, 6, modifier=3)
        self.assertGreaterEqual(result, 5)
        self.assertLessEqual(result, 15)


class TestSkills(unittest.TestCase):

    def test_skill_ability(self):
        self.assertEqual(
            get_skill_ability("stealth").value,
            "dexterity",
        )

        self.assertEqual(
            get_skill_ability("persuasion").value,
            "charisma",
        )

    def test_unknown_skill(self):
        with self.assertRaises(ValueError):
            get_skill_ability("unknown")


class TestChecks(unittest.TestCase):

    def test_successful_check(self):
        result = make_check(score=15, dc=15, roll=12)

        self.assertEqual(result.modifier, 2)
        self.assertEqual(result.total, 14)
        self.assertFalse(result.success)

    def test_proficiency(self):
        result = make_check(
            score=15,
            dc=15,
            proficient=True,
            proficiency_bonus=2,
            roll=11,
        )

        self.assertEqual(result.total, 15)
        self.assertTrue(result.success)

    def test_skill_check(self):
        attributes = {
            "strength": 10,
            "dexterity": 15,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
        }

        result = make_skill_check(
            skill="stealth",
            attributes=attributes,
            proficient_skills=["stealth"],
            dc=15,
            roll=11,
        )

        self.assertEqual(result.total, 15)
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
