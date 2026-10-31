import unittest

from app.engine.attribute_catalog import get_attribute_catalog


class TestAttributeCatalog(unittest.TestCase):

    def test_all_six_attributes_are_present(self):
        catalog = get_attribute_catalog()

        self.assertEqual(len(catalog), 6)

        ids = {attribute["id"] for attribute in catalog}

        self.assertEqual(
            ids,
            {
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            },
        )

    def test_world_can_change_display_name(self):
        catalog = get_attribute_catalog({
            "charisma": {
                "name": "Обаяние",
            }
        })

        charisma = next(
            item for item in catalog
            if item["id"] == "charisma"
        )

        self.assertEqual(charisma["name"], "Обаяние")
        self.assertEqual(charisma["id"], "charisma")

    def test_world_can_change_description(self):
        catalog = get_attribute_catalog({
            "strength": {
                "description": "Физическая мощь героя.",
            }
        })

        strength = next(
            item for item in catalog
            if item["id"] == "strength"
        )

        self.assertEqual(
            strength["description"],
            "Физическая мощь героя.",
        )

    def test_unknown_attribute_is_rejected(self):
        with self.assertRaises(ValueError):
            get_attribute_catalog({
                "luck": {"name": "Удача"}
            })


if __name__ == "__main__":
    unittest.main()
