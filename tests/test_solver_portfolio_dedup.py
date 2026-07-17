from __future__ import annotations

from dataclasses import replace
import unittest

from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.solver_portfolio import (
    _deduplicate_candidates,
    solve_partition_portfolio,
)


class SolverPortfolioDedupTests(unittest.TestCase):
    def test_identical_placements_are_deduplicated_across_family_labels(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {"id": "only", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}
        ]
        project["contents"] = [
            {
                "id": "asset",
                "name": "Asset",
                "shape_kind": "custom",
                "dimensions_mm": {"x": 20.0, "y": 20.0, "z": 10.0},
                "quantity": 1,
                "container_group_id": "only",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
        ]
        original = solve_partition_portfolio(project).certified_candidates[0]
        duplicate = replace(
            original,
            family_id="free_3d_beam",
            rank_key=(999, "duplicate"),
        )

        retained, duplicate_count = _deduplicate_candidates([duplicate, original])

        self.assertEqual(len(retained), 1)
        self.assertEqual(duplicate_count, 1)
        self.assertEqual(retained[0].family_id, "stage_stack")


if __name__ == "__main__":
    unittest.main()
