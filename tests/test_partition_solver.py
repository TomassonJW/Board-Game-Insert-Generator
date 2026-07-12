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

    def test_flat_stack_reduces_height_and_is_supported_by_aligned_requested_bodies(self) -> None:
        project = project_with_groups(2)
        project["flat_items"] = [{
            "id": "board", "name": "Plateau", "kind": "board",
            "dimensions_mm": {"x": 220.0, "y": 160.0, "z": 3.0},
            "quantity": 2, "stack_order": 0,
        }]
        result = solve_partition_plan(project)

        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertLess(result["box"]["storage_height_mm"], 66.0)
        self.assertEqual(result["support"]["status"], "supported_by_requested_bodies")
        self.assertGreater(result["support"]["top_support_count"], 0)
        self.assertTrue(all(item["world_size_mm"]["z"] == result["box"]["storage_height_mm"] for item in result["placements"]))

    def test_reports_actionable_impossible_when_axes_and_dimensions_prevent_a_complete_partition(self) -> None:
        project = project_with_groups(1)
        minimum = solve_partition_plan(project)["placements"][0]["minimum_outer_envelope_mm"]
        project["container_groups"][0]["expansion_axes"] = {"x": False, "y": False, "z": False}
        project["container_groups"][0]["locked_outer_dimensions_mm"] = deepcopy(minimum)

        result = solve_partition_plan(project)

        self.assertEqual(result["summary"]["status"], "impossible")
        self.assertEqual(result["summary"]["automatic_body_count"], 0)
        self.assertIn("NO_COMPLETE_PARTITION", {item["code"] for item in result["diagnostics"]})
        self.assertTrue(all(item["action"] for item in result["diagnostics"]))

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

    def test_exact_complement_with_partial_height_gets_a_specific_correction(self) -> None:
        project = project_with_groups(1)
        project["fill_elements"] = [{
            "id": "short", "name": "Bloc court", "kind": "solid", "mode": "exact",
            "dimensions_mm": {"x": 20.0, "y": 20.0, "z": 10.0}, "container_group_id": None,
        }]
        result = solve_partition_plan(project)
        self.assertEqual(result["summary"]["status"], "impossible")
        self.assertIn("EXPLICIT_COMPLEMENT_HEIGHT_BREAKS_PARTITION", {item["code"] for item in result["diagnostics"]})
        self.assertIn("hauteur Z", " ".join(item["action"] for item in result["diagnostics"]))
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

    def test_is_deterministic_for_the_same_normalized_project(self) -> None:
        first = solve_partition_plan(project_with_groups(4))
        second = solve_partition_plan(project_with_groups(4))

        self.assertEqual(first["plan_digest"], second["plan_digest"])
        self.assertEqual(first["placements"], second["placements"])
        self.assertFalse(first["solver"]["globally_optimal"])


if __name__ == "__main__":
    unittest.main()
