import json
from pathlib import Path
import tempfile
import unittest

from board_game_insert_generator.personal_presets import (
    delete_personal_preset,
    load_personal_presets,
    normalize_personal_presets,
    save_personal_preset,
    write_personal_presets,
)


def card_template() -> dict[str, object]:
    return {
        "name": "Mes cartes", "shape_kind": "cards",
        "dimensions_mm": {"x": 66, "y": 91, "z": 1}, "quantity": 80,
        "content_clearance_mm": 0.5, "measurement_confidence": "exact",
        "dimension_source": "catalog", "card_format_id": "poker", "sleeved": True,
        "storage_orientation": "auto", "card_stack_mode": "count", "card_thickness_mm": 0.32,
    }


class PersonalPresetTests(unittest.TestCase):
    def test_save_load_replace_and_delete_are_atomic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "personal.json"
            saved = save_personal_preset(path, name="Mon deck", content=card_template())
            replaced = save_personal_preset(path, name="Mon deck", content={**card_template(), "quantity": 100})

            self.assertEqual(saved["presets"][0]["id"], "mon-deck")
            self.assertEqual(len(replaced["presets"]), 1)
            self.assertEqual(load_personal_presets(path)["presets"][0]["content"]["quantity"], 100)
            self.assertFalse(Path(str(path) + ".tmp").exists())
            self.assertEqual(delete_personal_preset(path, "mon-deck")["presets"], [])

    def test_import_export_round_trip_keeps_version_and_resolved_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first.json"
            second = Path(temp_dir) / "second.json"
            collection = save_personal_preset(first, name="Sleeves", content=card_template())
            write_personal_presets(second, json.loads(json.dumps(collection)))

            loaded = load_personal_presets(second)

        self.assertEqual(loaded, normalize_personal_presets(collection))
        self.assertEqual(loaded["presets"][0]["content"]["base_dimensions_mm"]["x"], 66.0)


if __name__ == "__main__":
    unittest.main()
