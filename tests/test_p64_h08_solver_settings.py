from __future__ import annotations

import unittest

from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.solver_settings import normalize_solver_settings


def _simple_project() -> dict[str, object]:
    project = blank_project_v1()
    project["container_groups"] = [
        {"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}
    ]
    project["contents"] = [
        {
            "id": "asset",
            "name": "Pions",
            "shape_kind": "custom",
            "dimensions_mm": {"x": 20.0, "y": 20.0, "z": 10.0},
            "quantity": 1,
            "container_group_id": "g",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
    ]
    return project


class P64H08SolverSettingsTests(unittest.TestCase):
    def test_normalization_defaults_and_rejects_unknown_local_preferences(self) -> None:
        self.assertEqual(normalize_solver_settings(None), {"method": "auto", "effort": "normal"})
        self.assertEqual(
            normalize_solver_settings({"method": "free_3d", "effort": "deep"}),
            {"method": "free_3d", "effort": "deep"},
        )
        self.assertEqual(
            normalize_solver_settings({"method": "unknown", "effort": "unsafe"}),
            {"method": "auto", "effort": "normal"},
        )

    def test_public_auto_and_stage_methods_report_the_selected_product_method(self) -> None:
        project = _simple_project()
        auto = solve_partition_plan(
            project,
            request_id="h08-auto",
            request_revision=4,
            solver_method="auto",
            effort_profile="normal",
        )
        stage = solve_partition_plan(
            project,
            request_id="h08-stage",
            request_revision=4,
            solver_method="stage_stack",
            effort_profile="deep",
        )

        self.assertEqual(auto["solver"]["portfolio"]["method"], "auto")
        self.assertEqual(auto["solver"]["portfolio"]["effort_profile"], "normal")
        self.assertEqual(auto["solver"]["result"]["status"], "solution_found")
        self.assertTrue(auto["solver"]["result"]["materializable"])
        self.assertEqual(stage["solver"]["portfolio"]["method"], "stage_stack")
        self.assertEqual(stage["solver"]["portfolio"]["effort_profile"], "deep")
        self.assertEqual(stage["solver"]["portfolio"]["selected_family_id"], "stage_stack")
        self.assertEqual(stage["solver"]["result"]["status"], "solution_found")

    def test_free_3d_restricts_the_ranked_candidate_to_free_3d_families(self) -> None:
        plan = solve_partition_plan(
            _simple_project(),
            request_id="h08-free",
            request_revision=7,
            solver_method="free_3d",
            effort_profile="quick",
        )

        portfolio = plan["solver"]["portfolio"]
        self.assertEqual(portfolio["method"], "free_3d")
        selected = portfolio["selected_family_id"]
        self.assertIn(selected, {None, "free_3d_greedy", "free_3d_beam"})
        self.assertEqual(
            plan["solver"]["result"]["materializable"],
            plan["summary"]["status"] == "constructed",
        )


if __name__ == "__main__":
    unittest.main()