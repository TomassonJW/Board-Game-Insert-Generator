from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from context import ROOT

from board_game_insert_generator.cad_ir import build_blank_cad_scene
from board_game_insert_generator.config_loader import ConfigError, load_config
from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.report import layout_to_json, layout_to_markdown
from board_game_insert_generator.validation import validate_config
from board_game_insert_generator.volumetric import build_volumetric_summary


class VolumetricGridTests(unittest.TestCase):
    def test_loads_and_summarizes_explicit_3d_grid(self) -> None:
        config = load_config(ROOT / "examples" / "simple_3d_grid.json")

        self.assertIsNotNone(config.volumetric_grid)
        grid = config.volumetric_grid
        assert grid is not None
        self.assertEqual(grid.unit_size_mm.x, 30.0)
        self.assertEqual(grid.size_units.x, 4)
        self.assertEqual(grid.size_units.y, 3)
        self.assertEqual(grid.size_units.z, 3)
        self.assertEqual(len(grid.layers), 2)
        self.assertEqual(len(grid.module_placements), 2)
        self.assertEqual(len(grid.zones), 2)

        summary = build_volumetric_summary(config)
        assert summary is not None
        self.assertEqual(summary.total_cell_count, 36)
        self.assertEqual(summary.occupied_cell_count, 5)
        self.assertEqual(summary.reserved_cell_count, 12)
        self.assertEqual(summary.forbidden_cell_count, 1)
        self.assertEqual(summary.free_cell_count, 18)
        self.assertEqual(summary.approximate_free_volume_mm3, 162000.0)

    def test_valid_3d_grid_has_no_validation_issues(self) -> None:
        config = load_config(ROOT / "examples" / "simple_3d_grid.json")

        self.assertEqual(validate_config(config), [])

    def test_reports_expose_volumetric_grid_occupation_and_free_space(self) -> None:
        config = load_config(ROOT / "examples" / "simple_3d_grid.json")
        layout = generate_basic_layout(config)

        markdown = layout_to_markdown(config, layout)
        payload = json.loads(layout_to_json(config, layout))

        self.assertIn("## Volumetric grid", markdown)
        self.assertIn("- Grid units: 4 x 3 x 3", markdown)
        self.assertIn("- Free cells: 18", markdown)
        self.assertIn("cards-stack-volume | cards-stack", markdown)
        self.assertIn("board-reservation-band | reserved", markdown)
        self.assertEqual(payload["volumetric_grid"]["total_cell_count"], 36)
        self.assertEqual(payload["volumetric_grid"]["occupied_cell_count"], 5)
        self.assertEqual(payload["volumetric_grid"]["free_cell_count"], 18)
        self.assertEqual(payload["volumetric_grid"]["module_placements"][0]["size_units"], {"x": 2, "y": 1, "z": 2})

    def test_cad_ir_transports_volumetric_grid_metadata_without_fusion_operations(self) -> None:
        config = load_config(ROOT / "examples" / "simple_3d_grid.json")
        layout = generate_basic_layout(config)

        payload = build_blank_cad_scene(config, layout).to_dict()

        grid = payload["metadata"]["volumetric_grid"]
        self.assertEqual(grid["size_units"], {"x": 4, "y": 3, "z": 3})
        self.assertEqual(grid["free_cell_count"], 18)
        operation_kinds = [
            operation["kind"]
            for component in payload["components"]
            for operation in component["body"]["operations"]
        ]
        self.assertEqual(operation_kinds, ["create_rectangular_prism", "create_rectangular_prism"])

    def test_rejects_unknown_volumetric_grid_field(self) -> None:
        payload = _simple_grid_payload()
        payload["volumetric_grid"]["solver"] = "not-yet"

        with self.assertRaisesRegex(ConfigError, "Unknown field"):
            _load_payload(payload)

    def test_validation_reports_grid_coverage_mismatch(self) -> None:
        payload = _simple_grid_payload()
        payload["volumetric_grid"]["size_units"]["x"] = 3
        config = _load_payload(payload)

        keys = _issue_keys(validate_config(config))

        self.assertIn(("volumetric_grid.size_units.x", "VOLUMETRIC_GRID_COVERAGE_MISMATCH"), keys)

    def test_validation_reports_collision_between_module_and_reserved_zone(self) -> None:
        payload = _simple_grid_payload()
        payload["volumetric_grid"]["zones"][0]["origin_units"] = {"x": 0, "y": 0, "z": 0}
        payload["volumetric_grid"]["zones"][0]["size_units"] = {"x": 1, "y": 1, "z": 1}
        config = _load_payload(payload)

        keys = _issue_keys(validate_config(config))

        self.assertIn(("volumetric_grid.zones[0]", "VOLUMETRIC_CELL_COLLISION"), keys)

    def test_validation_reports_module_placement_too_small_for_module_mm_size(self) -> None:
        payload = _simple_grid_payload()
        payload["volumetric_grid"]["module_placements"][0]["size_units"] = {"x": 1, "y": 1, "z": 1}
        config = _load_payload(payload)

        keys = _issue_keys(validate_config(config))

        self.assertIn(("volumetric_grid.module_placements[0]", "VOLUMETRIC_PLACEMENT_TOO_SMALL"), keys)

    def test_validation_reports_instance_id_that_does_not_match_module(self) -> None:
        payload = _simple_grid_payload()
        payload["volumetric_grid"]["module_placements"][0]["instance_id"] = "other-module-01"
        config = _load_payload(payload)

        keys = _issue_keys(validate_config(config))

        self.assertIn(("volumetric_grid.module_placements[0].instance_id", "VOLUMETRIC_INSTANCE_ID_UNSUPPORTED"), keys)


    def test_loads_reservations_removal_order_and_support_surfaces(self) -> None:
        config = load_config(ROOT / "examples" / "simple_3d_reservations.json")

        grid = config.volumetric_grid
        assert grid is not None
        self.assertEqual(len(grid.support_surfaces), 2)
        self.assertEqual(grid.zones[0].reservation_kind, "flat_asset_layer")
        self.assertEqual(grid.zones[0].asset_kind, "board_or_rules")
        self.assertEqual(grid.zones[0].removal_order, 1)
        self.assertEqual(grid.module_placements[0].removal_order, 2)
        self.assertEqual(validate_config(config), [])

        summary = build_volumetric_summary(config)
        assert summary is not None
        payload = summary.to_dict()
        self.assertEqual(payload["support_surfaces"][0]["status"], "abstract_only")
        self.assertEqual(payload["support_surfaces"][0]["physical_validation"], "not_validated")
        self.assertEqual(
            [entry["target_id"] for entry in payload["removal_sequence"]],
            ["board-and-rules-reservation", "cards-stack-volume", "token-bin-volume"],
        )

    def test_reports_expose_reservations_removal_order_and_supports(self) -> None:
        config = load_config(ROOT / "examples" / "simple_3d_reservations.json")
        layout = generate_basic_layout(config)

        markdown = layout_to_markdown(config, layout)
        payload = json.loads(layout_to_json(config, layout))

        self.assertIn("### Support surfaces", markdown)
        self.assertIn("### Removal sequence", markdown)
        self.assertIn("board-and-rules-reservation | reserved | flat_asset_layer | board_or_rules", markdown)
        self.assertIn("cards-stack-top-support | module_placement:cards-stack-volume | top", markdown)
        self.assertEqual(payload["volumetric_grid"]["support_surfaces"][1]["owner_id"], "cards-stack-volume")
        self.assertEqual(payload["volumetric_grid"]["removal_sequence"][0]["order"], 1)

    def test_cad_ir_transports_reservation_support_metadata_without_new_operations(self) -> None:
        config = load_config(ROOT / "examples" / "simple_3d_reservations.json")
        layout = generate_basic_layout(config)

        payload = build_blank_cad_scene(config, layout).to_dict()

        grid = payload["metadata"]["volumetric_grid"]
        self.assertEqual(len(grid["support_surfaces"]), 2)
        self.assertEqual(grid["removal_sequence"][0]["target_id"], "board-and-rules-reservation")
        operation_kinds = [
            operation["kind"]
            for component in payload["components"]
            for operation in component["body"]["operations"]
        ]
        self.assertEqual(operation_kinds, ["create_rectangular_prism", "create_rectangular_prism"])

    def test_validation_reports_unknown_support_surface_reference(self) -> None:
        payload = _reservation_payload()
        payload["volumetric_grid"]["module_placements"][0]["support_surface_id"] = "missing-support"
        config = _load_payload(payload)

        keys = _issue_keys(validate_config(config))

        self.assertIn(("volumetric_grid.module_placements[0].support_surface_id", "VOLUMETRIC_UNKNOWN_SUPPORT_SURFACE"), keys)

    def test_validation_reports_forbidden_zone_with_removal_order(self) -> None:
        payload = _reservation_payload()
        payload["volumetric_grid"]["zones"][1]["removal_order"] = 4
        config = _load_payload(payload)

        keys = _issue_keys(validate_config(config))

        self.assertIn(("volumetric_grid.zones[1].removal_order", "VOLUMETRIC_FORBIDDEN_ZONE_NOT_REMOVABLE"), keys)

    def test_validation_reports_duplicate_removal_order(self) -> None:
        payload = _reservation_payload()
        payload["volumetric_grid"]["module_placements"][0]["removal_order"] = 1
        config = _load_payload(payload)

        keys = _issue_keys(validate_config(config))

        self.assertIn(("volumetric_grid.zones[0].removal_order", "VOLUMETRIC_REMOVAL_ORDER_DUPLICATE"), keys)
def _simple_grid_payload() -> dict:
    return json.loads((ROOT / "examples" / "simple_3d_grid.json").read_text(encoding="utf-8"))


def _reservation_payload() -> dict:
    return json.loads((ROOT / "examples" / "simple_3d_reservations.json").read_text(encoding="utf-8"))


def _load_payload(payload: dict):
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return load_config(path)


def _issue_keys(issues) -> set[tuple[str, str]]:
    return {(issue.field, issue.code) for issue in issues}


if __name__ == "__main__":
    unittest.main()
