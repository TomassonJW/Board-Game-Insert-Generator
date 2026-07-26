from __future__ import annotations

import json
import unittest
from pathlib import Path

from board_game_insert_generator.coupled_finalization import finalize_coupled_volume
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "scripts" / "fusion" / "p66_mvp_complete_project.json"


class PlateauCandidatePoolTests(unittest.TestCase):
    def test_tray_case_uses_bounded_minimal_candidate_pool(self) -> None:
        project = json.loads(FIXTURE.read_text(encoding="utf-8"))

        minimal = solve_minimal_layout(project, effort_profile="normal")
        search_origin = minimal["solver"]["search_origin"]

        self.assertEqual(minimal["solver"]["result"]["status"], "solution_found")
        self.assertTrue(search_origin["finishing_candidate_pool_bounded"])
        self.assertGreater(search_origin["finishing_candidate_pool_count"], 0)
        self.assertLessEqual(search_origin["finishing_candidate_pool_count"], 12)

        finalized = finalize_coupled_volume(
            project,
            minimal,
            source_minimal_artifact_digest="test-tray-candidate-pool",
            effort_profile="normal",
        )

        selection = finalized["finalization"]["minimal_candidate_selection"]
        composite = finalized["finalization"]["xy_composite_closure"]["certificate"]
        materialization = finalized["finalization"][
            "composite_materialization_certificate"
        ]
        self.assertEqual(finalized["solver"]["result"]["status"], "solution_found")
        self.assertEqual(
            composite["printable_residual_volume_mm3"],
            0.0,
        )
        self.assertGreaterEqual(selection["selected_candidate_index"], 0)
        self.assertGreaterEqual(selection["attempt_count"], 1)
        self.assertTrue(selection["shared_deadline_enforced"])
        self.assertTrue(materialization["certified"])
        owners = finalized["finalization"]["xy_composite_closure"]["owners"]
        self.assertTrue(
            all(
                owner["certificate"]["minimum_envelope_contained_by_union"]
                for owner in owners
            )
        )
        for placement in finalized["placements"]:
            for axis in ("x", "y", "z"):
                self.assertGreaterEqual(
                    placement["final_outer_dimensions_mm"][axis] + 0.0001,
                    placement["minimum_outer_envelope_mm"][axis],
                )
        fixed = next(
            placement
            for placement in finalized["placements"]
            if placement["id"] == "container:c2"
        )
        self.assertEqual(
            fixed["final_outer_dimensions_mm"]["x"],
            fixed["minimum_outer_envelope_mm"]["x"],
        )


if __name__ == "__main__":
    unittest.main()
