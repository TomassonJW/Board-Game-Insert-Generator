from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.expandable_envelope import derive_expandable_envelope_contract
from board_game_insert_generator.partition_solver import PARTITION_PLAN_SCHEMA_V1, solve_partition_plan
from board_game_insert_generator.project_v1 import blank_project_v1


def project_with_groups(count: int = 2) -> dict[str, object]:
    project = blank_project_v1()
    project["box"] = {
        "inner_dimensions_mm": {"x": 240.0, "y": 180.0, "z": 70.0},
        "usable_height_mm": 66.0,
        "lid_clearance_mm": 2.0,
    }
    project["container_groups"] = [
        {"id": f"g{index}", "name": f"Bac {index}", "wall_thickness_mm": None, "floor_thickness_mm": None}
        for index in range(count)
    ]
    project["contents"] = [
        {
            "id": f"c{index}", "name": f"Pieces {index}", "shape_kind": "square",
            "dimensions_mm": {"x": 18.0, "y": 18.0, "z": 5.0}, "quantity": 4,
            "container_group_id": f"g{index}", "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
        for index in range(count)
    ]
    return project


def mixed_height_cards_project(card_count: int) -> dict[str, object]:
    value = blank_project_v1()
    value["box"] = {
        "inner_dimensions_mm": {"x": 240.0, "y": 180.0, "z": 70.0},
        "usable_height_mm": 70.0,
        "lid_clearance_mm": 0.2,
    }
    value["layout"]["layout_clearance_mm"] = 0.6
    value["container_groups"] = [
        {
            "id": "tokens",
            "name": "Bac jetons",
            "wall_thickness_mm": None,
            "floor_thickness_mm": None,
        },
        *[
            {
                "id": f"cards-{index}",
                "name": "Bac cartes",
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
            }
            for index in range(card_count)
        ],
    ]
    value["contents"] = [
        {
            "id": "coins",
            "name": "Pieces",
            "shape_kind": "round",
            "dimensions_mm": {"x": 18.0, "y": 18.0, "z": 2.5},
            "quantity": 12,
            "container_group_id": "tokens",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        },
        {
            "id": "cubes",
            "name": "Cubes",
            "shape_kind": "cube",
            "dimensions_mm": {"x": 12.0, "y": 12.0, "z": 12.0},
            "quantity": 8,
            "container_group_id": "tokens",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        },
        *[
            {
                "id": f"deck-{index}",
                "name": "Cartes sleevees",
                "shape_kind": "cards",
                "dimensions_mm": {"x": 68.0, "y": 94.0, "z": 28.0},
                "quantity": 1,
                "container_group_id": f"cards-{index}",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
            for index in range(card_count)
        ],
    ]
    return value


class PartitionSolverTests(unittest.TestCase):
    def test_single_requested_container_absorbs_the_printable_volume_without_changing_its_cavity(self) -> None:
        project = project_with_groups(1)
        before = derive_expandable_envelope_contract(project)["containers"][0]["cavity_layout"]
        result = solve_partition_plan(project)
        placement = result["placements"][0]

        self.assertEqual(result["schema_version"], PARTITION_PLAN_SCHEMA_V1)
        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertEqual(result["summary"]["final_body_count"], 1)
        self.assertEqual(result["summary"]["automatic_body_count"], 0)
        self.assertEqual(placement["world_size_mm"], {"x": 238.8, "y": 178.8, "z": 66.0})
        self.assertEqual(placement["cavity_layout"], before)
        self.assertGreater(placement["surplus_distribution_mm"]["below"], 0)
        self.assertTrue(result["summary"]["complete_printable_partition"])
        self.assertEqual(result["validation"]["unassigned_printable_volume_mm3"], 0.0)

    def test_multiple_containers_form_a_collision_free_partition_and_keep_clearances_empty(self) -> None:
        project = project_with_groups(3)
        project["layout"]["layout_clearance_mm"] = 1.0
        result = solve_partition_plan(project)

        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertEqual(result["summary"]["placed_container_count"], 3)
        self.assertTrue(result["validation"]["inside_box"])
        self.assertTrue(result["validation"]["no_collisions"])
        self.assertTrue(result["validation"]["clearances_respected"])
        self.assertTrue(result["summary"]["technical_voids_are_clearances_only"])
        self.assertFalse(result["clearance_policy"]["materialize_clearances"])
        self.assertTrue(all(not item["automatic"] for item in result["placements"]))

    def test_top_inset_keeps_full_height_and_is_supported_by_aligned_requested_bodies(self) -> None:
        project = project_with_groups(2)
        project["flat_items"] = [{
            "id": "board", "name": "Plateau", "kind": "board",
            "dimensions_mm": {"x": 220.0, "y": 160.0, "z": 3.0},
            "quantity": 2, "stack_order": 0,
        }]
        result = solve_partition_plan(project)

        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertEqual(result["box"]["storage_height_mm"], 66.0)
        self.assertEqual(result["support"]["status"], "supported_by_requested_bodies")
        self.assertGreater(result["support"]["top_support_count"], 0)
        self.assertTrue(all(item["world_size_mm"]["z"] == 66.0 for item in result["placements"]))
        self.assertEqual(result["top_inset_reservations"]["status"], "applied")
        self.assertTrue(all(item.get("top_inset_cuts") for item in result["placements"]))

    def test_returns_a_visible_residual_proposal_when_fixed_dimensions_prevent_closure(self) -> None:
        project = project_with_groups(1)
        minimum = solve_partition_plan(project)["placements"][0]["minimum_outer_envelope_mm"]
        project["container_groups"][0]["expansion_axes"] = {"x": False, "y": False, "z": False}
        project["container_groups"][0]["locked_outer_dimensions_mm"] = deepcopy(minimum)

        result = solve_partition_plan(project)

        self.assertEqual(result["summary"]["status"], "proposal_with_residuals")
        self.assertEqual(result["summary"]["solution_status"], "proposal_with_residuals")
        self.assertFalse(result["summary"]["materializable"])
        self.assertEqual(result["summary"]["automatic_body_count"], 0)
        self.assertGreater(result["residuals"]["residual_volume_mm3"], 0.0)
        self.assertTrue(result["suggestions"])
        self.assertFalse(result["suggestions"][0]["automatic"])

    def test_explicit_exact_complement_is_counted_but_never_invented(self) -> None:
        project = project_with_groups(1)
        clearance = project["layout"]["layout_clearance_mm"]
        project["fill_elements"] = [{
            "id": "weight", "name": "Poids lateral", "kind": "solid", "mode": "exact",
            "dimensions_mm": {"x": 20.0, "y": 180.0 - 2 * clearance, "z": 66.0},
            "container_group_id": None,
        }]

        result = solve_partition_plan(project)

        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertEqual(result["summary"]["explicit_complement_count"], 1)
        self.assertEqual(result["summary"]["final_body_count"], 2)
        self.assertEqual(result["summary"]["automatic_body_count"], 0)
        complements = [item for item in result["placements"] if item["role"] == "explicit_complement"]
        self.assertEqual(complements[0]["requested_complement_id"], "weight")

    def test_exact_complement_with_partial_height_can_form_an_explicit_upper_stage(self) -> None:
        project = project_with_groups(1)
        project["fill_elements"] = [{
            "id": "short", "name": "Bloc court", "kind": "solid", "mode": "exact",
            "dimensions_mm": {"x": 20.0, "y": 20.0, "z": 10.0}, "container_group_id": None,
        }]
        result = solve_partition_plan(project)
        self.assertEqual(result["summary"]["status"], "proposal_with_residuals")
        self.assertEqual(result["summary"]["stage_count"], 2)
        complement = next(item for item in result["placements"] if item["role"] == "explicit_complement")
        self.assertGreater(complement["origin_mm"]["z"], 0.0)
        self.assertEqual(complement["world_size_mm"]["z"], 10.0)
        self.assertEqual(result["summary"]["automatic_body_count"], 0)
    def test_auto_sized_complement_is_refused_instead_of_becoming_an_automatic_filler(self) -> None:
        project = project_with_groups(1)
        project["fill_elements"] = [{
            "id": "legacy", "name": "Ancien auto", "kind": "hollow", "mode": "auto",
            "dimensions_mm": None, "container_group_id": None,
        }]

        result = solve_partition_plan(project)

        self.assertEqual(result["summary"]["status"], "impossible")
        self.assertEqual(result["summary"]["automatic_body_count"], 0)
        self.assertIn("EXPLICIT_COMPLEMENT_NEEDS_EXACT_SIZE", {item["code"] for item in result["diagnostics"]})

    def test_xy_pressure_builds_two_complete_stages_with_support_and_removal(self) -> None:
        project = project_with_groups(4)
        project["box"] = {
            "inner_dimensions_mm": {"x": 50.0, "y": 25.0, "z": 50.0},
            "usable_height_mm": 50.0,
            "lid_clearance_mm": 0.0,
        }

        result = solve_partition_plan(project)

        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertEqual(result["summary"]["solution_status"], "complete")
        self.assertEqual(result["summary"]["stage_count"], 2)
        self.assertEqual({item["origin_mm"]["z"] for item in result["placements"]}, {0.0, 25.0})
        self.assertEqual(result["stage_support"]["status"], "supported")
        self.assertTrue(result["validation"]["conserved"])
        self.assertEqual(result["validation"]["unassigned_printable_volume_mm3"], 0.0)
        self.assertEqual(result["summary"]["automatic_body_count"], 0)
        self.assertEqual(result["removal_sequence"][0]["stage_id"], "stage-2")

    def test_handles_fifty_requested_containers_without_a_business_cardinality_limit(self) -> None:
        project = project_with_groups(50)
        project["box"] = {
            "inner_dimensions_mm": {"x": 900.0, "y": 900.0, "z": 100.0},
            "usable_height_mm": 96.0,
            "lid_clearance_mm": 2.0,
        }

        result = solve_partition_plan(project)

        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertEqual(result["summary"]["placed_container_count"], 50)
        self.assertEqual(result["summary"]["final_body_count"], 50)
        self.assertGreater(result["summary"]["candidate_count_evaluated"], 50)

    def test_mixed_height_cards_remain_solvable_when_a_new_z_layer_is_required(self) -> None:
        results = [solve_partition_plan(mixed_height_cards_project(count)) for count in (4, 5, 6)]

        self.assertEqual([item["summary"]["status"] for item in results], ["constructed"] * 3)
        self.assertTrue(all(item["validation"]["no_collisions"] for item in results))
        self.assertTrue(all(item["validation"]["conserved"] for item in results))
        stacked = results[-1]
        self.assertGreater(max(item["origin_mm"]["z"] for item in stacked["placements"]), 0.0)
        self.assertIn("stack_partition_index", stacked["solver"]["search_origin"])
        self.assertTrue(any(stage["spanning_body_ids"] for stage in stacked["stages"]))

    def test_is_deterministic_for_the_same_normalized_project(self) -> None:
        first = solve_partition_plan(project_with_groups(4))
        second = solve_partition_plan(project_with_groups(4))

        self.assertEqual(first["plan_digest"], second["plan_digest"])
        self.assertEqual(first["placements"], second["placements"])
        self.assertFalse(first["solver"]["globally_optimal"])


if __name__ == "__main__":
    unittest.main()
