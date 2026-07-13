from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.local_composer import starter_draft
from board_game_insert_generator.project_v1 import (
    LEGACY_LOCAL_COMPOSER_SCHEMA_V0,
    PROJECT_SCHEMA_V1,
    ProjectContractError,
    blank_project_v1,
    migrate_local_composer_v0,
    normalize_project_draft,
)


class ProjectV1Tests(unittest.TestCase):
    def test_blank_project_is_valid_and_has_user_first_defaults(self) -> None:
        normalized = normalize_project_draft(blank_project_v1())

        self.assertEqual(normalized.source_schema, PROJECT_SCHEMA_V1)
        self.assertFalse(normalized.migrated)
        self.assertEqual(normalized.project["contents"], [])
        self.assertEqual(normalized.project["layout"]["layout_clearance_mm"], 0.6)
        self.assertEqual(normalized.project["layout"]["container_z_clearance_mm"], 0.6)
        self.assertEqual(normalized.project["deferred_features"], {"appearance": None, "mechanism": None})

    def test_native_project_without_z_clearance_inherits_xy_clearance(self) -> None:
        project = blank_project_v1()
        project["layout"]["layout_clearance_mm"] = 0.85
        project["layout"].pop("container_z_clearance_mm")

        normalized = normalize_project_draft(project)

        self.assertFalse(normalized.migrated)
        self.assertEqual(normalized.project["layout"]["container_z_clearance_mm"], 0.85)
    def test_native_project_supports_groups_flat_items_and_fill_elements(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {"id": "cards", "name": "Bac cartes", "wall_thickness_mm": 1.4, "floor_thickness_mm": None},
            {"id": "tokens", "name": "Bac jetons", "wall_thickness_mm": None, "floor_thickness_mm": None},
        ]
        project["contents"] = [
            {
                "id": "deck",
                "name": "Cartes",
                "shape_kind": "cards",
                "dimensions_mm": {"x": 63, "y": 88, "z": 24},
                "quantity": 120,
                "container_group_id": "cards",
                "content_clearance_mm": 0.4,
                "measurement_confidence": "exact",
            },
            {
                "id": "coins",
                "name": "Pieces",
                "shape_kind": "round",
                "dimensions_mm": {"x": 20, "y": 20, "z": 2},
                "quantity": 48,
                "container_group_id": "tokens",
                "content_clearance_mm": None,
                "measurement_confidence": "approximate",
            },
        ]
        project["flat_items"] = [
            {
                "id": "rules",
                "name": "Livret de regles",
                "kind": "rulebook",
                "dimensions_mm": {"x": 180, "y": 120, "z": 3},
                "quantity": 2,
                "stack_order": 0,
            }
        ]
        project["fill_elements"] = [
            {
                "id": "spare-box",
                "name": "Bac vide",
                "kind": "hollow",
                "mode": "auto",
                "dimensions_mm": None,
                "container_group_id": None,
            },
            {
                "id": "divider",
                "name": "Separateur centre",
                "kind": "separator",
                "mode": "exact",
                "dimensions_mm": {"x": 2, "y": 100, "z": 30},
                "container_group_id": "tokens",
            },
        ]

        normalized = normalize_project_draft(project).project

        self.assertEqual([item["container_group_id"] for item in normalized["contents"]], ["cards", "tokens"])
        self.assertEqual(normalized["container_groups"][0]["wall_thickness_mm"], 1.4)
        self.assertEqual(normalized["flat_items"][0]["quantity"], 2)
        self.assertEqual(normalized["fill_elements"][1]["mode"], "exact")

    def test_card_orientation_resolves_dimensions_without_losing_physical_base(self) -> None:
        project = blank_project_v1()
        project["box"]["usable_height_mm"] = 70
        project["container_groups"] = [
            {"id": "cards", "name": "Cartes", "wall_thickness_mm": None, "floor_thickness_mm": None}
        ]
        project["contents"] = [{
            "id": "deck", "name": "Deck", "shape_kind": "cards",
            "dimensions_mm": {"x": 63, "y": 88, "z": 24}, "quantity": 100,
            "container_group_id": "cards", "content_clearance_mm": None,
            "measurement_confidence": "exact", "storage_orientation": "upright_long_edge",
        }]

        content = normalize_project_draft(project).project["contents"][0]

        self.assertEqual(content["base_dimensions_mm"], {"x": 63.0, "y": 88.0, "z": 24.0})
        self.assertEqual(content["dimensions_mm"], {"x": 88.0, "y": 24.0, "z": 63.0})
        self.assertEqual(content["resolved_orientation"], "upright_long_edge")

    def test_catalog_sleeves_and_counted_stack_are_resolved_but_explicit_dimensions_win(self) -> None:
        project = blank_project_v1()
        project["box"]["usable_height_mm"] = 70
        project["container_groups"] = [
            {"id": "cards", "name": "Cartes", "wall_thickness_mm": None, "floor_thickness_mm": None}
        ]
        content = {
            "id": "deck", "name": "Deck", "shape_kind": "cards",
            "dimensions_mm": {"x": 1, "y": 1, "z": 1}, "quantity": 100,
            "container_group_id": "cards", "content_clearance_mm": None,
            "measurement_confidence": "exact", "dimension_source": "catalog",
            "card_format_id": "poker", "sleeved": True, "storage_orientation": "auto",
            "card_stack_mode": "count", "card_thickness_mm": 0.32,
        }
        project["contents"] = [content]

        catalog_content = normalize_project_draft(project).project["contents"][0]

        self.assertEqual(catalog_content["base_dimensions_mm"], {"x": 66.0, "y": 91.0, "z": 40.0})
        self.assertEqual(catalog_content["resolved_orientation"], "upright_long_edge")
        self.assertEqual(catalog_content["dimensions_mm"], {"x": 91.0, "y": 40.0, "z": 66.0})

        content.update({
            "dimension_source": "explicit",
            "base_dimensions_mm": {"x": 70, "y": 100, "z": 20},
            "card_stack_mode": "thickness",
            "storage_orientation": "flat",
        })
        explicit = normalize_project_draft(project).project["contents"][0]
        self.assertEqual(explicit["base_dimensions_mm"], {"x": 70.0, "y": 100.0, "z": 20.0})
        self.assertEqual(explicit["dimensions_mm"], {"x": 70.0, "y": 100.0, "z": 20.0})

    def test_legacy_migration_preserves_groups_flats_and_deferred_features(self) -> None:
        legacy = starter_draft()
        original = deepcopy(legacy)

        migrated = migrate_local_composer_v0(legacy)

        self.assertEqual(migrated["schema_version"], PROJECT_SCHEMA_V1)
        self.assertEqual(migrated["migration"]["source_schema"], LEGACY_LOCAL_COMPOSER_SCHEMA_V0)
        self.assertEqual([group["id"] for group in migrated["container_groups"]], ["card-tray", "token-tray", "dice-tray"])
        self.assertEqual(migrated["contents"][0]["container_group_id"], "card-tray")
        self.assertEqual(migrated["flat_items"][0]["kind"], "rulebook")
        self.assertEqual(migrated["deferred_features"]["appearance"], legacy["appearance"])
        self.assertEqual(migrated["deferred_features"]["mechanism"], legacy["mechanism"])
        self.assertEqual(legacy, original)

    def test_unassigned_legacy_asset_receives_its_own_group(self) -> None:
        legacy = starter_draft()
        legacy["candidates"] = legacy["candidates"][:1]

        migrated = migrate_local_composer_v0(legacy)

        groups = {group["id"] for group in migrated["container_groups"]}
        assignments = {item["id"]: item["container_group_id"] for item in migrated["contents"]}
        self.assertEqual(assignments["cards"], "card-tray")
        self.assertIn("group:tokens", groups)
        self.assertIn("group:dice", groups)

    def test_rejects_invalid_group_reference_and_exact_fill_without_dimensions(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "one", "name": "Bac 1", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [
            {
                "id": "item",
                "name": "Item",
                "shape_kind": "square",
                "dimensions_mm": {"x": 10, "y": 10, "z": 2},
                "quantity": 1,
                "container_group_id": "missing",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
        ]
        with self.assertRaisesRegex(ProjectContractError, "unknown group"):
            normalize_project_draft(project)

        project["contents"][0]["container_group_id"] = "one"
        project["fill_elements"] = [
            {
                "id": "fill",
                "name": "Remplissage",
                "kind": "solid",
                "mode": "exact",
                "dimensions_mm": None,
                "container_group_id": None,
            }
        ]
        with self.assertRaisesRegex(ProjectContractError, "dimensions_mm is required"):
            normalize_project_draft(project)

    def test_dimension_mode_validation_keeps_legacy_locks_and_rejects_ambiguous_targets(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{
            "id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None,
            "locked_outer_dimensions_mm": {"x": 42.0, "y": None, "z": None},
        }]
        normalized = normalize_project_draft(project).project["container_groups"][0]
        self.assertEqual(normalized["dimension_modes"]["x"], "fixed")
        self.assertEqual(normalized["target_outer_dimensions_mm"]["x"], 42.0)

        project["container_groups"][0].update({
            "dimension_modes": {"x": "auto", "y": "auto", "z": "auto"},
            "target_outer_dimensions_mm": {"x": 42.0, "y": None, "z": None},
            "locked_outer_dimensions_mm": {"x": None, "y": None, "z": None},
        })
        with self.assertRaisesRegex(ProjectContractError, "must be null in auto mode"):
            normalize_project_draft(project)


    def test_has_no_business_cardinality_limit(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {"id": f"group-{index}", "name": f"Bac {index}", "wall_thickness_mm": None, "floor_thickness_mm": None}
            for index in range(50)
        ]
        project["contents"] = [
            {
                "id": f"item-{index}",
                "name": f"Piece {index}",
                "shape_kind": "custom",
                "dimensions_mm": {"x": 10, "y": 10, "z": 2},
                "quantity": index + 1,
                "container_group_id": f"group-{index % 50}",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
            for index in range(72)
        ]
        project["flat_items"] = [
            {
                "id": f"flat-{index}",
                "name": f"Plateau {index}",
                "kind": "board",
                "dimensions_mm": {"x": 100, "y": 80, "z": 1},
                "quantity": 1,
                "stack_order": index,
            }
            for index in range(25)
        ]

        normalized = normalize_project_draft(project).project

        self.assertEqual(len(normalized["container_groups"]), 50)
        self.assertEqual(len(normalized["contents"]), 72)
        self.assertEqual(len(normalized["flat_items"]), 25)


if __name__ == "__main__":
    unittest.main()
