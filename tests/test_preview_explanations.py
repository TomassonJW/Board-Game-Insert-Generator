from copy import deepcopy
import json
import unittest

from board_game_insert_generator.partition_result_view import build_partition_result_view
from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.preview_explanations import PREVIEW_EXPLANATIONS_SCHEMA_V1
from board_game_insert_generator.project_v1 import blank_project_v1


def multistage_project() -> dict[str, object]:
    project = blank_project_v1()
    project["box"] = {
        "inner_dimensions_mm": {"x": 50.0, "y": 25.0, "z": 50.0},
        "usable_height_mm": 50.0,
        "lid_clearance_mm": 0.0,
    }
    project["container_groups"] = [
        {"id": f"g{index}", "name": f"Bac {index}", "wall_thickness_mm": None, "floor_thickness_mm": None}
        for index in range(4)
    ]
    project["contents"] = [
        {
            "id": f"c{index}", "name": f"Pieces {index}", "shape_kind": "square",
            "dimensions_mm": {"x": 18.0, "y": 18.0, "z": 5.0}, "quantity": 4,
            "container_group_id": f"g{index}", "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
        for index in range(4)
    ]
    return project


def residual_project() -> dict[str, object]:
    project = blank_project_v1()
    project["box"] = {
        "inner_dimensions_mm": {"x": 200.0, "y": 150.0, "z": 60.0},
        "usable_height_mm": 56.0,
        "lid_clearance_mm": 2.0,
    }
    project["container_groups"] = [
        {"id": "cards", "name": "Cartes", "wall_thickness_mm": None, "floor_thickness_mm": None}
    ]
    project["contents"] = [{
        "id": "deck", "name": "Deck", "shape_kind": "cards",
        "dimensions_mm": {"x": 63.0, "y": 88.0, "z": 18.0}, "quantity": 50,
        "container_group_id": "cards", "content_clearance_mm": None,
        "measurement_confidence": "exact",
    }]
    minimum = solve_partition_plan(project)["placements"][0]["minimum_outer_envelope_mm"]
    project["container_groups"][0]["expansion_axes"] = {"x": False, "y": False, "z": False}
    project["container_groups"][0]["locked_outer_dimensions_mm"] = minimum
    return project


class PreviewExplanationsTests(unittest.TestCase):
    def test_translates_score_support_and_removal_without_mutating_the_plan(self) -> None:
        plan = solve_partition_plan(multistage_project())
        snapshot = deepcopy(plan)
        presentation = build_partition_result_view(plan)["presentation"]

        self.assertEqual(presentation["schema_version"], PREVIEW_EXPLANATIONS_SCHEMA_V1)
        self.assertEqual(
            [item["label"] for item in presentation["score"]["criteria"]],
            [
                "Simplicite du plan",
                "Respect des tailles ciblees",
                "Repartition de la matiere",
                "Appui des etages",
            ],
        )
        self.assertEqual(presentation["stage_support"]["state"], "confirmed")
        self.assertTrue(presentation["removal"]["entries"])
        self.assertTrue(all("placement_id" not in item for item in presentation["removal"]["entries"]))
        self.assertEqual(plan, snapshot)
        self.assertTrue(presentation["invariants"]["does_not_mutate_plan"])

    def test_translates_flat_support_without_exposing_the_solver_enum(self) -> None:
        project = blank_project_v1()
        project["box"] = {
            "inner_dimensions_mm": {"x": 200.0, "y": 150.0, "z": 60.0},
            "usable_height_mm": 56.0,
            "lid_clearance_mm": 2.0,
        }
        project["container_groups"] = [{
            "id": "cards", "name": "Cartes", "wall_thickness_mm": None, "floor_thickness_mm": None,
        }]
        project["contents"] = [{
            "id": "deck", "name": "Deck", "shape_kind": "cards",
            "dimensions_mm": {"x": 63.0, "y": 88.0, "z": 18.0}, "quantity": 50,
            "container_group_id": "cards", "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }]
        project["flat_items"] = [{
            "id": "board", "name": "Grand plateau", "kind": "board",
            "dimensions_mm": {"x": 190.0, "y": 140.0, "z": 2.0}, "quantity": 1,
            "stack_order": 0,
        }]
        presentation = build_partition_result_view(solve_partition_plan(project))["presentation"]

        self.assertEqual(presentation["flat_support"]["state"], "confirmed")
        self.assertIn("reposent", presentation["flat_support"]["summary"])
        self.assertNotIn("supported_by_requested_bodies", json.dumps(presentation))

    def test_keeps_partial_residuals_explicit_and_non_automatic(self) -> None:
        presentation = build_partition_result_view(solve_partition_plan(residual_project()))["presentation"]

        self.assertTrue(presentation["residual"]["present"])
        self.assertGreater(presentation["residual"]["volume_mm3"], 0.0)
        self.assertTrue(presentation["residual"]["suggestions"])
        self.assertTrue(presentation["residual"]["suggestions"][0]["requires_confirmation"])
        self.assertIn("aucun corps automatiquement", presentation["residual"]["suggestions"][0]["summary"])
        self.assertTrue(presentation["invariants"]["does_not_create_bodies"])


if __name__ == "__main__":
    unittest.main()
