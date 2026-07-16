from __future__ import annotations

import json
import unittest
from pathlib import Path
from copy import deepcopy

from board_game_insert_generator.container_derivation import derive_container_plan
from board_game_insert_generator.project_v1 import blank_project_v1, normalize_project_draft
from board_game_insert_generator.partition_cad import PARTITION_CAD_STATUS_READY, build_partition_cad
from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.top_inset_reservation import derive_top_inset_reservations
from board_game_insert_generator.volumetric_stage_solver import solve_stage_portfolio


def project_with_clearances() -> dict[str, object]:
    project = blank_project_v1()
    project["layout"]["clearance_defaults_v1"] = {
        "asset_cavity_mm": {"x": 0.2, "y": 0.3, "z": 0.4},
        "flat_inset_mm": {"x": 0.5, "y": 0.6, "z": 0.7},
        "container_between_mm": {"x": 0.8, "y": 0.9, "z": 1.0},
        "container_box_per_side_xy_mm": {"x": 0.1, "y": 0.2},
    }
    project["container_groups"] = [{
        "id": "tokens",
        "name": "Jetons",
        "wall_thickness_mm": None,
        "floor_thickness_mm": None,
        "clearance_overrides_v1": {
            "between_mm": {"x": 0.0, "y": None, "z": 1.2},
            "box_per_side_xy_mm": {"x": 0.0, "y": None},
        },
    }]
    project["contents"] = [{
        "id": "coins",
        "name": "Pieces",
        "shape_kind": "round",
        "dimensions_mm": {"x": 18.0, "y": 18.0, "z": 2.5},
        "quantity": 1,
        "container_group_id": "tokens",
        "content_clearance_mm": 0.9,
        "clearance_override_mm": {"x": 0.0, "y": None, "z": 0.6},
        "measurement_confidence": "exact",
    }]
    project["flat_items"] = [{
        "id": "board",
        "name": "Plateau",
        "kind": "board",
        "dimensions_mm": {"x": 40.0, "y": 30.0, "z": 2.0},
        "quantity": 2,
        "stack_order": 0,
        "origin_mm": None,
        "rotation_deg_z": 0,
        "clearance_override_mm": {"x": None, "y": 0.0, "z": None},
    }]
    return project


class P44M009ClearanceOverrideTests(unittest.TestCase):
    def test_resolves_roles_axis_by_axis_with_zero_and_sources(self) -> None:
        project = normalize_project_draft(project_with_clearances()).project
        content = project["contents"][0]
        self.assertEqual(content["clearance_effective_v1"]["values_mm"], {"x": 0.0, "y": 0.9, "z": 0.6})
        self.assertEqual(
            content["clearance_effective_v1"]["source_by_axis"],
            {"x": "object_override", "y": "legacy_content_clearance_mm", "z": "object_override"},
        )
        flat = project["flat_items"][0]
        self.assertEqual(flat["clearance_effective_v1"]["values_mm"], {"x": 0.5, "y": 0.0, "z": 0.7})
        self.assertEqual(
            flat["clearance_effective_v1"]["source_by_axis"],
            {"x": "project_default", "y": "object_override", "z": "project_default"},
        )
        group = project["container_groups"][0]["clearance_effective_v1"]
        self.assertEqual(group["between_mm"], {"x": 0.0, "y": 0.9, "z": 1.2})
        self.assertEqual(group["box_per_side_xy_mm"], {"x": 0.0, "y": 0.2})
        self.assertEqual(group["source_by_vector"]["between_mm"]["x"], "object_override")
        self.assertEqual(group["source_by_vector"]["between_mm"]["y"], "project_default")

    def test_cavity_and_top_inset_use_the_resolved_vectors(self) -> None:
        project = project_with_clearances()
        container = derive_container_plan(project)["containers"][0]
        compartment = container["compartments"][0]
        self.assertEqual(compartment["inner_dimensions_mm"], {"x": 18.0, "y": 19.8, "z": 3.1})
        self.assertEqual(compartment["clearance_effective_v1"]["values_mm"], {"x": 0.0, "y": 0.9, "z": 0.6})

        top = derive_top_inset_reservations(project)
        reservation = top["reservations"][0]
        self.assertEqual(reservation["cut_size_mm"], {"x": 41.0, "y": 30.0})
        self.assertEqual(reservation["total_thickness_mm"], 4.7)
        self.assertEqual(reservation["clearance_effective_v1"]["values_mm"], {"x": 0.5, "y": 0.0, "z": 0.7})

    def test_pairwise_neighborhood_uses_maximum_not_sum(self) -> None:
        policy_left = {
            "role": "external_container",
            "between_mm": {"x": 0.2, "y": 0.0, "z": 0.0},
            "box_per_side_xy_mm": {"x": 0.0, "y": 0.0},
        }
        policy_right = {
            "role": "external_container",
            "between_mm": {"x": 0.8, "y": 0.0, "z": 0.0},
            "box_per_side_xy_mm": {"x": 0.0, "y": 0.0},
        }
        participant = lambda identifier, policy: {
            "id": identifier, "role": "container", "name": identifier,
            "minimum_local_mm": {"x": 20.0, "y": 10.0, "z": 10.0},
            "dimension_modes": {"x": "fixed", "y": "fixed", "z": "fixed"},
            "target_local_mm": {"x": 20.0, "y": 10.0, "z": 10.0},
            "external_clearance_effective_v1": policy,
        }
        result = solve_stage_portfolio(
            [participant("left", policy_left), participant("right", policy_right)],
            {"x": 40.8, "y": 10.0, "z": 20.0},
            10.0,
            0.6,
            box_clearance_mm=0.6,
            vertical_clearance_mm=0.6,
        )
        candidate = result["best_candidate"]
        self.assertIsNotNone(candidate)
        placements = sorted(candidate["placements"], key=lambda item: item["origin_mm"]["x"])
        gap = placements[1]["origin_mm"]["x"] - placements[0]["origin_mm"]["x"] - placements[0]["world_size_mm"]["x"]
        self.assertAlmostEqual(gap, 0.8, places=4)

    def test_pairwise_vertical_neighborhood_uses_maximum_not_sum(self) -> None:
        policy_lower = {
            "role": "external_container",
            "between_mm": {"x": 0.0, "y": 0.0, "z": 0.2},
            "box_per_side_xy_mm": {"x": 0.0, "y": 0.0},
        }
        policy_upper = {
            "role": "external_container",
            "between_mm": {"x": 0.0, "y": 0.0, "z": 0.8},
            "box_per_side_xy_mm": {"x": 0.0, "y": 0.0},
        }

        def participant(identifier: str, policy: dict[str, object]) -> dict[str, object]:
            return {
                "id": identifier,
                "role": "container",
                "name": identifier,
                "minimum_local_mm": {"x": 20.0, "y": 10.0, "z": 10.0},
                "dimension_modes": {"x": "fixed", "y": "fixed", "z": "fixed"},
                "target_local_mm": {"x": 20.0, "y": 10.0, "z": 10.0},
                "external_clearance_effective_v1": policy,
            }

        result = solve_stage_portfolio(
            [participant("lower", policy_lower), participant("upper", policy_upper)],
            {"x": 20.0, "y": 10.0, "z": 30.0},
            20.8,
            0.6,
            box_clearance_mm=0.6,
            vertical_clearance_mm=0.6,
        )
        candidate = result["best_candidate"]
        self.assertIsNotNone(candidate)
        placements = sorted(candidate["placements"], key=lambda item: item["origin_mm"]["z"])
        gap = (
            placements[1]["origin_mm"]["z"]
            - placements[0]["origin_mm"]["z"]
            - placements[0]["world_size_mm"]["z"]
        )
        self.assertAlmostEqual(gap, 0.8, places=4)

    def test_lower_asset_override_replaces_global_and_stays_local(self) -> None:
        project = blank_project_v1()
        project["layout"]["clearance_defaults_v1"] = {
            "asset_cavity_mm": {"x": 0.5, "y": 0.5, "z": 0.5},
            "flat_inset_mm": {"x": 0.2, "y": 0.2, "z": 0.0},
            "container_between_mm": {"x": 0.2, "y": 0.2, "z": 0.2},
            "container_box_per_side_xy_mm": {"x": 0.2, "y": 0.2},
        }
        project["container_groups"] = [
            {"id": "local", "name": "Local", "wall_thickness_mm": None, "floor_thickness_mm": None},
            {"id": "global", "name": "Global", "wall_thickness_mm": None, "floor_thickness_mm": None},
        ]
        base_content = {
            "name": "Objet", "shape_kind": "rectangle",
            "dimensions_mm": {"x": 10.0, "y": 8.0, "z": 2.0},
            "quantity": 1, "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
        project["contents"] = [
            {**base_content, "id": "local-item", "container_group_id": "local",
             "clearance_override_mm": {"x": 0.1, "y": 0.1, "z": 0.1}},
            {**base_content, "id": "global-item", "container_group_id": "global"},
        ]

        containers = {
            item["container_group_id"]: item for item in derive_container_plan(project)["containers"]
        }
        local = containers["local"]["compartments"][0]
        inherited = containers["global"]["compartments"][0]
        self.assertEqual(local["clearance_effective_v1"]["values_mm"], {"x": 0.1, "y": 0.1, "z": 0.1})
        self.assertEqual(inherited["clearance_effective_v1"]["values_mm"], {"x": 0.5, "y": 0.5, "z": 0.5})
        self.assertEqual(local["inner_dimensions_mm"], {"x": 10.2, "y": 8.2, "z": 2.1})
        self.assertEqual(inherited["inner_dimensions_mm"], {"x": 11.0, "y": 9.0, "z": 2.5})

    def test_one_container_override_does_not_propagate_to_other_pairs(self) -> None:
        def participant(identifier: str, clearance: float) -> dict[str, object]:
            policy = {
                "role": "external_container",
                "between_mm": {"x": clearance, "y": clearance, "z": 0.0},
                "box_per_side_xy_mm": {"x": 0.0, "y": 0.0},
            }
            return {
                "id": identifier, "role": "container", "name": identifier,
                "minimum_local_mm": {"x": 10.0, "y": 10.0, "z": 10.0},
                "dimension_modes": {"x": "fixed", "y": "fixed", "z": "fixed"},
                "target_local_mm": {"x": 10.0, "y": 10.0, "z": 10.0},
                "external_clearance_effective_v1": policy,
            }

        result = solve_stage_portfolio(
            [participant("wide", 2.0), participant("normal-a", 0.2), participant("normal-b", 0.2)],
            {"x": 32.2, "y": 10.0, "z": 10.0},
            10.0,
            0.2,
            box_clearance_mm=0.0,
            vertical_clearance_mm=0.0,
        )
        candidate = result["best_candidate"]
        self.assertIsNotNone(candidate)
        placements = sorted(candidate["placements"], key=lambda item: item["origin_mm"]["x"])
        gaps = [
            placements[index + 1]["origin_mm"]["x"]
            - placements[index]["origin_mm"]["x"]
            - placements[index]["world_size_mm"]["x"]
            for index in range(2)
        ]
        self.assertEqual(sorted(round(gap, 4) for gap in gaps), [0.2, 2.0])

    def test_historical_fixture_stays_materializable_with_legacy_sources(self) -> None:
        fixture = Path(__file__).resolve().parents[1] / "scripts" / "fusion" / "p66_mvp_complete_project.json"
        raw = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertNotIn("clearance_defaults_v1", raw["layout"])

        plan = solve_partition_plan(raw)
        cad = build_partition_cad(raw, partition=plan)

        self.assertTrue(plan["summary"]["materializable"])
        self.assertEqual(
            plan["clearance_policy"]["role_default_sources_v1"]["asset_cavity_mm"]["x"],
            "compatibility_legacy_scalar",
        )
        self.assertEqual(cad["status"], PARTITION_CAD_STATUS_READY)
        self.assertEqual(cad["materialization"]["component_count"], 8)
        self.assertEqual(cad["materialization"]["automatic_body_count"], 0)

    def test_normalized_roundtrip_preserves_legacy_provenance(self) -> None:
        project = blank_project_v1()
        project["layout"]["layout_clearance_mm"] = 0.4
        project["layout"]["default_content_clearance_mm"] = 0.25
        first = normalize_project_draft(project).project
        second = normalize_project_draft(deepcopy(first)).project
        self.assertEqual(first, second)
        self.assertEqual(
            second["layout"]["clearance_default_sources_v1"]["asset_cavity_mm"]["x"],
            "compatibility_legacy_scalar",
        )


if __name__ == "__main__":
    unittest.main()
