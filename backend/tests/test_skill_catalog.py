import unittest

from app.engine.skill_catalog import get_skill_catalog
from app.engine.skills import SKILL_ABILITIES


class TestSkillCatalog(unittest.TestCase):

    def test_all_nineteen_skills_are_present(self):
        catalog = get_skill_catalog()

        self.assertEqual(len(catalog), 19)
        self.assertEqual(
            {skill["id"] for skill in catalog},
            set(SKILL_ABILITIES),
        )

    def test_every_skill_has_valid_ability(self):
        catalog = get_skill_catalog()

        for skill in catalog:
            self.assertEqual(
                skill["ability"],
                SKILL_ABILITIES[skill["id"]].value,
            )

    def test_world_can_change_skill_name(self):
        catalog = get_skill_catalog({
            "stealth": {"name": "Незаметность"}
        })

        stealth = next(
            skill for skill in catalog
            if skill["id"] == "stealth"
        )

        self.assertEqual(stealth["name"], "Незаметность")
        self.assertEqual(stealth["id"], "stealth")
        self.assertEqual(stealth["ability"], "dexterity")

    def test_world_can_change_description(self):
        catalog = get_skill_catalog({
            "persuasion": {
                "description": "Искусство дипломатии."
            }
        })

        persuasion = next(
            skill for skill in catalog
            if skill["id"] == "persuasion"
        )

        self.assertEqual(
            persuasion["description"],
            "Искусство дипломатии.",
        )

    def test_unknown_skill_is_rejected(self):
        with self.assertRaises(ValueError):
            get_skill_catalog({
                "luck": {"name": "Удача"}
            })


if __name__ == "__main__":
    unittest.main()
