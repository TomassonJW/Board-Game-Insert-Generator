from copy import deepcopy
import unittest

from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.project_presets import (
    CREATION_PRESETS_SCHEMA_V1,
    build_creation_presets,
)
from board_game_insert_generator.project_v1 import blank_project_v1


class ProjectPresetTests(unittest.TestCase):
    def test_exposes_editable_content_starters_without_fusion_dependency(self) -> None:
        presets = build_creation_presets(blank_project_v1())

        self.assertEqual(presets["schema_version"], CREATION_PRESETS_SCHEMA_V1)
        self.assertEqual(
            [item["key"] for item in presets["contents"]],
            ["tokens", "cards", "dice", "pawns"],
        )
        self.assertEqual(presets["contents"][0]["content"]["shape_kind"], "round")
        self.assertNotIn("id", presets["contents"][0]["content"])
        card_preset = next(item for item in presets["contents"] if item["key"] == "cards")
        cards = card_preset["content"]
        self.assertEqual(card_preset["label"], "Cartes")
        self.assertEqual(cards["name"], "Cartes")
        self.assertFalse(cards["sleeved"])
        self.assertNotIn("sleeve_extra_xy_mm", cards)
        self.assertNotIn("sleeve_extra_z_mm_per_card", cards)
        self.assertEqual(cards["base_dimensions_mm"], {"x": 63.5, "y": 88.9, "z": 24.0})

    def test_quarantines_complement_starters_from_normal_creation_presets(self) -> None:
        presets = build_creation_presets(blank_project_v1(), storage_height_mm=42.5)

        self.assertEqual(presets["complements"], [])
    def test_default_group_keeps_all_dimensions_automatic_and_expandable(self) -> None:
        defaults = build_creation_presets(blank_project_v1())["defaults"]["container_group"]

        self.assertEqual(defaults["locked_outer_dimensions_mm"], {"x": None, "y": None, "z": None})
        self.assertEqual(defaults["target_outer_dimensions_mm"], {"x": None, "y": None, "z": None})
        self.assertEqual(defaults["dimension_modes"], {"x": "auto", "y": "auto", "z": "auto"})
        self.assertEqual(defaults["expansion_axes"], {"x": True, "y": True, "z": True})

    def test_each_content_starter_builds_a_real_one_body_partition(self) -> None:
        for preset in build_creation_presets(blank_project_v1())["contents"]:
            with self.subTest(preset=preset["key"]):
                project = blank_project_v1()
                group = deepcopy(build_creation_presets(project)["defaults"]["container_group"])
                group.update({"id": f"group-{preset['key']}", "name": preset["group_name"]})
                content = deepcopy(preset["content"])
                content.update({"id": f"content-{preset['key']}", "container_group_id": group["id"]})
                project["container_groups"] = [group]
                project["contents"] = [content]

                result = solve_partition_plan(project)

                self.assertEqual(result["summary"]["status"], "constructed")
                self.assertEqual(result["summary"]["final_body_count"], 1)


if __name__ == "__main__":
    unittest.main()
