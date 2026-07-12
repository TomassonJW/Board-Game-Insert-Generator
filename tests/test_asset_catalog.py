import unittest

from board_game_insert_generator.asset_catalog import (
    card_catalog,
    card_format_dimensions,
    card_stack_thickness_mm,
    orient_dimensions,
)


class AssetCatalogTests(unittest.TestCase):
    def test_catalog_exposes_named_unsleeved_and_sleeved_dimensions(self) -> None:
        catalog = card_catalog()

        self.assertEqual(catalog["schema_version"], "bgig.card_catalog.v1")
        self.assertGreaterEqual(len(catalog["formats"]), 5)
        self.assertEqual(card_format_dimensions("poker", sleeved=False), {"x": 63.5, "y": 88.9})
        self.assertEqual(card_format_dimensions("poker", sleeved=True), {"x": 66.0, "y": 91.0})

    def test_counted_sleeved_stack_changes_full_deck_thickness(self) -> None:
        self.assertEqual(
            card_stack_thickness_mm(
                mode="count", declared_thickness_mm=1, quantity=100,
                card_thickness_mm=0.32, sleeved=True,
            ),
            40.0,
        )

    def test_orientations_change_xyz_and_auto_respects_available_height(self) -> None:
        base = {"x": 63.0, "y": 88.0, "z": 24.0}

        self.assertEqual(
            orient_dimensions(base, "upright_long_edge", max_height_mm=70),
            ("upright_long_edge", {"x": 88.0, "y": 24.0, "z": 63.0}),
        )
        self.assertEqual(
            orient_dimensions(base, "upright_short_edge", max_height_mm=100),
            ("upright_short_edge", {"x": 63.0, "y": 24.0, "z": 88.0}),
        )
        self.assertEqual(orient_dimensions(base, "auto", max_height_mm=70)[0], "upright_long_edge")
        self.assertEqual(orient_dimensions(base, "auto", max_height_mm=50)[0], "flat")


if __name__ == "__main__":
    unittest.main()
