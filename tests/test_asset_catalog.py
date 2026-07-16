import unittest

from board_game_insert_generator.asset_catalog import (
    card_catalog,
    card_format_dimensions,
    card_stack_thickness_mm,
    estimate_card_count_from_thickness,
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

    def test_explicit_sleeve_deltas_override_catalog_and_stack_defaults(self) -> None:
        self.assertEqual(
            card_format_dimensions(
                "poker", sleeved=True, sleeve_extra_xy_mm=2.0
            ),
            {"x": 65.5, "y": 90.9},
        )
        self.assertEqual(
            card_stack_thickness_mm(
                mode="count", declared_thickness_mm=1, quantity=100,
                card_thickness_mm=0.32, sleeved=True,
                sleeve_extra_z_mm_per_card=0.1,
            ),
            42.0,
        )

    def test_estimates_count_and_adds_explicit_sleeve_z_to_declared_stack(self) -> None:
        self.assertEqual(estimate_card_count_from_thickness(24.0), 77)
        self.assertEqual(
            card_stack_thickness_mm(
                mode="thickness", declared_thickness_mm=24.0, quantity=60,
                card_thickness_mm=0.32, sleeved=True,
                sleeve_extra_z_mm_per_card=0.19,
            ),
            38.63,
        )
        self.assertEqual(
            card_stack_thickness_mm(
                mode="thickness", declared_thickness_mm=24.0, quantity=60,
                card_thickness_mm=0.32, sleeved=False,
                sleeve_extra_z_mm_per_card=0.19,
            ),
            24.0,
        )
        self.assertEqual(
            card_stack_thickness_mm(
                mode="thickness", declared_thickness_mm=24.0, quantity=60,
                card_thickness_mm=0.32, sleeved=True,
            ),
            24.0,
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
