
import unittest
from dataclasses import FrozenInstanceError

from app.actions.techniques import (
    TECHNIQUES,
    get_all_techniques,
    get_technique,
)


class TestTechniques(unittest.TestCase):

    def test_catalog_is_not_empty(self):
        self.assertGreater(len(TECHNIQUES), 0)

    def test_get_existing_technique(self):
        technique = get_technique("feint")

        self.assertIsNotNone(technique)
        self.assertEqual(technique.id, "feint")
        self.assertEqual(technique.name, "Финт")

    def test_unknown_technique_returns_none(self):
        self.assertIsNone(get_technique("unknown_technique"))

    def test_get_all_techniques(self):
        techniques = get_all_techniques()

        self.assertIsInstance(techniques, tuple)
        self.assertEqual(len(techniques), len(TECHNIQUES))

    def test_technique_definition_is_immutable(self):
        technique = get_technique("feint")

        with self.assertRaises(FrozenInstanceError):
            technique.name = "Изменённый финт"

    def test_every_technique_has_required_data(self):
        for technique_id, technique in TECHNIQUES.items():
            with self.subTest(technique=technique_id):
                self.assertEqual(technique.id, technique_id)
                self.assertTrue(technique.name)
                self.assertTrue(technique.description)
                self.assertIsInstance(technique.examples, tuple)


if __name__ == "__main__":
    unittest.main()
