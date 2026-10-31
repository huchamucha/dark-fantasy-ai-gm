import unittest

from app.services.world_state import GameWorldStore
from app.story_packs.registry import get_story_pack, list_story_packs


class TestStoryPacks(unittest.TestCase):

    def setUp(self):
        self.store = GameWorldStore()

    def test_dark_fantasy_is_registered(self):
        pack = get_story_pack("dark_fantasy")

        self.assertEqual(pack["id"], "dark_fantasy")
        self.assertEqual(pack["status"], "available")

    def test_unknown_story_pack_is_rejected(self):
        with self.assertRaises(ValueError):
            get_story_pack("unknown_world")

    def test_catalog_lists_available_worlds(self):
        packs = list_story_packs()

        self.assertTrue(any(
            pack["id"] == "dark_fantasy"
            for pack in packs
        ))

    def test_campaign_is_bound_to_story_pack(self):
        campaign = self.store.create_campaign(
            title="Пепельная Корона",
            story_pack_id="dark_fantasy",
        )

        self.assertEqual(campaign["story_pack_id"], "dark_fantasy")
        self.assertEqual(campaign["current_location_id"], "cathedral_approach")
        self.assertEqual(campaign["npcs"][0]["id"], "brother_eldric")

    def test_legacy_campaign_creation_still_works(self):
        campaign = self.store.create_campaign(
            title="Старая кампания",
            setting="dark_fantasy",
        )

        self.assertEqual(campaign["story_pack_id"], "dark_fantasy")

    def test_campaigns_have_independent_world_state(self):
        first = self.store.create_campaign("Первая")
        second = self.store.create_campaign("Вторая")

        first["world_flags"]["shadow_in_city"] = True

        stored_second = self.store.get_campaign(second["id"])

        self.assertFalse(stored_second["world_flags"]["shadow_in_city"])

    def test_character_cannot_be_used_in_another_campaign(self):
        first = self.store.create_campaign("Первая")
        second = self.store.create_campaign("Вторая")

        character = self.store.create_character(
            campaign_id=first["id"],
            player_id="player1",
            name="Герой",
            class_name="Воин",
            strength=15,
            dexterity=12,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10,
        )

        with self.assertRaises(ValueError):
            self.store.get_world_snapshot(
                second["id"],
                character["id"],
            )

    def test_character_cannot_write_to_another_campaign(self):
        first = self.store.create_campaign("Первая")
        second = self.store.create_campaign("Вторая")

        character = self.store.create_character(
            campaign_id=first["id"],
            player_id="player1",
            name="Герой",
            class_name="Воин",
            strength=15,
            dexterity=12,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10,
        )

        with self.assertRaises(ValueError):
            self.store.update_campaign_after_turn(
                second["id"],
                character["id"],
                "Открываю дверь",
                {"narrative": "Дверь открылась"},
            )


if __name__ == "__main__":
    unittest.main()
