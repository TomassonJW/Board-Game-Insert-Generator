from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from board_game_insert_generator.partition_cad import (
    PARTITION_CAD_BUILD_SCHEMA_V1,
    PARTITION_CAD_STATUS_READY,
    PartitionCadBuildError,
    build_partition_cad,
)
from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.project_v1 import blank_project_v1
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)


def project(count: int = 2) -> dict[str, object]:
    value = blank_project_v1()
    value["box"] = {"inner_dimensions_mm": {"x": 240.0, "y": 180.0, "z": 70.0}, "usable_height_mm": 66.0, "lid_clearance_mm": 2.0}
    value["container_groups"] = [{"id": f"g{i}", "name": f"Bac {i}", "wall_thickness_mm": None, "floor_thickness_mm": None} for i in range(count)]
    value["contents"] = [{
        "id": f"c{i}", "name": f"Pieces {i}", "shape_kind": "rectangle",
        "dimensions_mm": {"x": 22.0 + i, "y": 14.0, "z": 5.0}, "quantity": 4,
        "container_group_id": f"g{i}", "content_clearance_mm": None, "measurement_confidence": "exact",
    } for i in range(count)]
    return value


def tight_multistage_project() -> dict[str, object]:
    value = project(4)
    value["box"] = {"inner_dimensions_mm": {"x": 50.0, "y": 25.0, "z": 50.0}, "usable_height_mm": 50.0, "lid_clearance_mm": 0.0}
    for content in value["contents"]:
        content["dimensions_mm"] = {"x": 18.0, "y": 18.0, "z": 5.0}
    return value


def fixed_residual_project() -> dict[str, object]:
    value = project(1)
    minimum = solve_partition_plan(value)["placements"][0]["minimum_outer_envelope_mm"]
    value["container_groups"][0]["expansion_axes"] = {"x": False, "y": False, "z": False}
    value["container_groups"][0]["locked_outer_dimensions_mm"] = minimum
    return value


class PartitionCadTests(unittest.TestCase):
    def test_builds_one_fusion_component_per_requested_p57_body(self) -> None:
        value = project(3)
        plan = solve_partition_plan(value)
        result = build_partition_cad(value, partition=plan)
        fusion = generation_plan_from_cad_ir(result["cad_ir"], FUSION_GENERATION_MODE_COMPACT_ONLY)

        self.assertEqual(result["schema_version"], PARTITION_CAD_BUILD_SCHEMA_V1)
        self.assertEqual(result["status"], PARTITION_CAD_STATUS_READY)
        self.assertEqual(result["source_plan_digest"], plan["plan_digest"])
        self.assertEqual(result["materialization"]["component_count"], plan["summary"]["final_body_count"])
        self.assertEqual(fusion.module_component_count, plan["summary"]["final_body_count"])
        self.assertEqual(len(fusion.compact_occurrences), plan["summary"]["final_body_count"])
        self.assertEqual(len(fusion.exploded_occurrences), 0)
        parameters = {item["id"]: item["value"] for item in result["cad_ir"]["parameters"]}
        self.assertEqual(parameters["container_z_clearance_mm"], 0.6)

    def test_repeated_user_names_still_create_unique_fusion_body_names(self) -> None:
        value = project(4)
        for group in value["container_groups"]:
            group["name"] = "Bac cartes"

        plan = solve_partition_plan(value)
        result = build_partition_cad(value, partition=plan)
        fusion = generation_plan_from_cad_ir(
            result["cad_ir"],
            FUSION_GENERATION_MODE_COMPACT_ONLY,
        )
        body_names = [
            component["body"]["name"]
            for component in result["cad_ir"]["components"]
        ]

        self.assertEqual(result["status"], PARTITION_CAD_STATUS_READY)
        self.assertEqual(len(body_names), len(set(body_names)))
        self.assertEqual(fusion.module_component_count, 4)

    def test_compensated_cavity_depth_is_transported_to_fusion(self) -> None:
        value = project(1)
        value["flat_items"] = [{
            "id": "board",
            "name": "Plateau",
            "kind": "board",
            "dimensions_mm": {"x": 220.0, "y": 160.0, "z": 2.0},
            "quantity": 1,
            "stack_order": 0,
        }]

        plan = solve_partition_plan(value)
        result = build_partition_cad(value, partition=plan)
        component = result["cad_ir"]["components"][0]
        cavity = plan["placements"][0]["cavity_layout"][0]
        operation = next(
            item
            for item in component["body"]["operations"]
            if item["kind"] == "subtract_rectangular_cavity"
        )

        self.assertEqual(cavity["top_inset_compensation_mm"], 2.0)
        self.assertEqual(
            operation["parameters"]["size_mm"]["z"],
            cavity["base_inner_dimensions_mm"]["z"] + 2.0,
        )
        self.assertAlmostEqual(
            operation["parameters"]["local_origin_mm"]["z"]
            + operation["parameters"]["size_mm"]["z"],
            component["body"]["printable_size_mm"]["z"],
        )
        generation_plan_from_cad_ir(result["cad_ir"], FUSION_GENERATION_MODE_COMPACT_ONLY)
    def test_cavity_operations_keep_p55_dimensions_and_open_on_the_final_top(self) -> None:
        value = project(2)
        plan = solve_partition_plan(value)
        result = build_partition_cad(value, partition=plan)
        components = {item["instance_id"]: item for item in result["cad_ir"]["components"]}

        for placement in plan["placements"]:
            component = components[placement["id"]]
            body_size = component["body"]["printable_size_mm"]
            operations = [item for item in component["body"]["operations"] if item["kind"] == "subtract_rectangular_cavity"]
            self.assertEqual(len(operations), len(placement["cavity_layout"]))
            for operation, cavity in zip(operations, placement["cavity_layout"]):
                origin = operation["parameters"]["local_origin_mm"]
                size = operation["parameters"]["size_mm"]
                expected_xy = sorted([cavity["inner_dimensions_mm"]["x"], cavity["inner_dimensions_mm"]["y"]])
                self.assertEqual(sorted([size["x"], size["y"]]), expected_xy)
                self.assertEqual(size["z"], cavity["inner_dimensions_mm"]["z"])
                self.assertAlmostEqual(origin["z"] + size["z"], body_size["z"])

    def test_multiple_cavity_heights_remain_open_on_the_final_top(self) -> None:
        value = project(1)
        value["contents"] = [
            {"id": "low", "name": "Bas", "shape_kind": "square", "dimensions_mm": {"x": 18.0, "y": 18.0, "z": 2.0}, "quantity": 2, "container_group_id": "g0", "content_clearance_mm": None, "measurement_confidence": "exact"},
            {"id": "high", "name": "Haut", "shape_kind": "cube", "dimensions_mm": {"x": 12.0, "y": 12.0, "z": 12.0}, "quantity": 4, "container_group_id": "g0", "content_clearance_mm": None, "measurement_confidence": "exact"},
        ]
        result = build_partition_cad(value)
        body = result["cad_ir"]["components"][0]["body"]

        self.assertGreater(len(body["cavities"]), 1)
        for cavity in body["cavities"]:
            self.assertAlmostEqual(
                cavity["local_origin_mm"]["z"] + cavity["size_mm"]["z"],
                body["printable_size_mm"]["z"],
            )
    def test_metadata_proves_zero_automatic_or_free_region_body(self) -> None:
        result = build_partition_cad(project(2))
        metadata = result["cad_ir"]["metadata"]

        self.assertEqual(result["materialization"]["automatic_body_count"], 0)
        self.assertFalse(result["invariants"]["free_regions_materialized"])
        self.assertEqual(metadata["box_fill_plan"]["automatic_body_count"], 0)
        self.assertFalse(metadata["box_fill_plan"]["free_regions_materialized"])
        self.assertTrue(all(not component["metadata"]["automatic"] for component in result["cad_ir"]["components"]))
        self.assertNotIn("p42_automatic_residual_fill", str(result["cad_ir"]))

    def test_materializes_an_explicit_hollow_complement_with_no_invented_body(self) -> None:
        value = project(1)
        value["contents"][0]["shape_kind"] = "square"
        value["contents"][0]["dimensions_mm"] = {"x": 18.0, "y": 18.0, "z": 5.0}
        clearance = value["layout"]["layout_clearance_mm"]
        value["fill_elements"] = [{
            "id": "empty", "name": "Bac vide voulu", "kind": "hollow", "mode": "exact",
            "dimensions_mm": {"x": 20.0, "y": 180.0 - 2 * clearance, "z": 66.0}, "container_group_id": None,
        }]
        result = build_partition_cad(value)

        self.assertEqual(result["status"], PARTITION_CAD_STATUS_READY)
        self.assertEqual(result["materialization"]["explicit_complement_component_count"], 1)
        self.assertEqual(result["materialization"]["component_count"], 2)
        complement = next(item for item in result["cad_ir"]["components"] if item["metadata"]["role"] == "explicit_complement")
        self.assertEqual(complement["metadata"]["requested_complement_id"], "empty")
        self.assertEqual(len(complement["body"]["cavities"]), 1)

    def test_transports_top_insets_as_reservation_cuts_distinct_from_content_cavities(self) -> None:
        value = project(2)
        value["flat_items"] = [{
            "id": "board", "name": "Plateau", "kind": "board",
            "dimensions_mm": {"x": 220.0, "y": 160.0, "z": 3.0},
            "quantity": 1, "stack_order": 0,
        }]

        result = build_partition_cad(value)
        fusion = generation_plan_from_cad_ir(result["cad_ir"], FUSION_GENERATION_MODE_COMPACT_ONLY)
        operations = [
            operation
            for component in result["cad_ir"]["components"]
            for operation in component["body"]["operations"]
        ]
        top_operations = [
            operation for operation in operations
            if operation["kind"] in {"subtract_top_inset_reservation", "subtract_top_inset_grip"}
        ]

        self.assertEqual(result["status"], PARTITION_CAD_STATUS_READY)
        self.assertEqual(result["materialization"]["top_inset_cut_count"], len(top_operations))
        self.assertGreater(len(top_operations), 0)
        self.assertTrue(all(operation["parameters"]["non_perforating"] for operation in top_operations))
        self.assertEqual(
            len([cut for cut in fusion.cavity_cuts if cut.cavity_source.startswith("top_inset")]),
            len(top_operations),
        )
        self.assertTrue(result["invariants"]["top_insets_are_reservations_not_cavities"])
        self.assertTrue(result["invariants"]["top_inset_cut_count_matches_plan"])

    def test_p64_transports_nonzero_stage_origins_to_the_cad_ir(self) -> None:
        result = build_partition_cad(tight_multistage_project())
        components = result["cad_ir"]["components"]

        self.assertEqual(result["status"], PARTITION_CAD_STATUS_READY)
        self.assertEqual({component["body"]["printable_origin_mm"]["z"] for component in components}, {0.0, 25.3})
        self.assertEqual(len(result["cad_ir"]["metadata"]["box_fill_plan"]["stages"]), 2)
        self.assertEqual(result["cad_ir"]["metadata"]["box_fill_plan"]["stage_support"]["status"], "supported")
        self.assertEqual(result["materialization"]["automatic_body_count"], 0)

    def test_p64_partial_proposal_never_produces_cad_ir(self) -> None:
        result = build_partition_cad(fixed_residual_project())

        self.assertEqual(result["status"], "not_materializable")
        self.assertIsNone(result["cad_ir"])
        self.assertEqual(result["materialization"]["status"], "blocked_partial")
        self.assertEqual(result["materialization"]["component_count"], 0)
        self.assertEqual(result["materialization"]["automatic_body_count"], 0)
        self.assertIn("volumes residuels", result["blockers"][0])

    def test_impossible_project_returns_no_cad_ir(self) -> None:
        result = build_partition_cad(blank_project_v1())

        self.assertEqual(result["status"], "impossible")
        self.assertIsNone(result["cad_ir"])
        self.assertEqual(result["materialization"]["component_count"], 0)
        self.assertEqual(result["materialization"]["automatic_body_count"], 0)

    def test_rejects_a_stale_or_tampered_partition(self) -> None:
        value = project(1)
        plan = solve_partition_plan(value)
        stale = deepcopy(plan)
        stale["placements"][0]["world_size_mm"]["x"] += 1.0
        stale["plan_digest"] = plan["plan_digest"]  # Un digest recopie ne doit pas masquer un payload modifie.

        with self.assertRaisesRegex(PartitionCadBuildError, "obsolete"):
            build_partition_cad(value, partition=stale)

    def test_cad_ir_digest_is_deterministic(self) -> None:
        first = build_partition_cad(project(4))
        second = build_partition_cad(project(4))

        self.assertEqual(first["cad_ir_digest"], second["cad_ir_digest"])
        self.assertEqual(first["cad_ir"], second["cad_ir"])

    def test_handles_fifty_bodies_and_the_installed_core_stays_adsk_free(self) -> None:
        value = project(50)
        value["box"] = {"inner_dimensions_mm": {"x": 900.0, "y": 900.0, "z": 100.0}, "usable_height_mm": 96.0, "lid_clearance_mm": 2.0}
        result = build_partition_cad(value)
        fusion = generation_plan_from_cad_ir(result["cad_ir"], FUSION_GENERATION_MODE_COMPACT_ONLY)

        self.assertEqual(result["materialization"]["component_count"], 50)
        self.assertEqual(fusion.module_component_count, 50)
        source = (Path(__file__).resolve().parents[1] / "src" / "board_game_insert_generator" / "partition_cad.py").read_text(encoding="utf-8")
        self.assertNotIn("import adsk", source)


if __name__ == "__main__":
    unittest.main()
