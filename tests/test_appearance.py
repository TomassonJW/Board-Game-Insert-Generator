from __future__ import annotations

import unittest

from board_game_insert_generator.appearance import (
    APPEARANCE_SCHEMA_V0,
    AppearanceError,
    default_appearance,
    normalize_appearance,
)


class AppearanceTests(unittest.TestCase):
    def test_default_appearance_is_versioned_and_independent(self) -> None:
        first = default_appearance()
        second = default_appearance()

        self.assertEqual(first["schema_version"], APPEARANCE_SCHEMA_V0)
        first["shape"]["corner_radius_mm"] = 9.0
        self.assertEqual(second["shape"]["corner_radius_mm"], 3.0)

    def test_normalizes_supported_preview_only_preferences(self) -> None:
        appearance = normalize_appearance(
            {
                "schema_version": APPEARANCE_SCHEMA_V0,
                "shape": {
                    "corner_style": "chamfered",
                    "corner_radius_mm": 8,
                    "chamfer_mm": 4,
                    "notch_style": "thumb_notch",
                },
                "visual": {
                    "theme": "graphite",
                    "label_mode": "module_name_and_role",
                    "typography": "bold",
                },
            }
        )

        self.assertEqual(appearance["shape"]["corner_style"], "chamfered")
        self.assertEqual(appearance["visual"]["theme"], "graphite")

    def test_rejects_an_out_of_range_or_unknown_appearance_value(self) -> None:
        appearance = default_appearance()
        appearance["shape"]["corner_radius_mm"] = 13.0
        with self.assertRaisesRegex(AppearanceError, "between 0 and 12"):
            normalize_appearance(appearance)

        appearance = default_appearance()
        appearance["visual"]["theme"] = "neon"
        with self.assertRaisesRegex(AppearanceError, "theme"):
            normalize_appearance(appearance)


if __name__ == "__main__":
    unittest.main()