from __future__ import annotations

import json
import unittest
from pathlib import Path

from board_game_insert_generator.coupled_finalization import finalize_coupled_volume
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.partition_cad import build_partition_cad
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "scripts" / "fusion" / "p66_mvp_complete_project.json"


class ExactMinimalFinalizationTests(unittest.TestCase):
    def test_composite_fallback_restarts_from_certified_minimal_placements(
        self,
    ) -> None:
        source = (
            ROOT
            / "src"
            / "board_game_insert_generator"
            / "coupled_finalization.py"
        ).read_text(encoding="utf-8")
        start = source.index("composite = close_xy_composite_partition(")
        block = source[start : source.index("composite_certified =", start)]

        self.assertIn("participants,\n            placements,", block)
        self.assertNotIn("continuous.placements", block)

    def test_tray_case_finalizes_only_the_selected_minimal_plan(self) -> None:
        project = json.loads(FIXTURE.read_text(encoding="utf-8"))

        minimal = solve_minimal_layout(project, effort_profile="normal")
        search_origin = minimal["solver"]["search_origin"]

        self.assertEqual(minimal["solver"]["result"]["status"], "solution_found")
        self.assertTrue(search_origin["finishing_candidate_pool_bounded"])
        self.assertEqual(search_origin["finishing_candidate_pool_count"], 0)
        self.assertEqual(search_origin["finishing_candidate_pool_limit"], 0)
        self.assertTrue(
            search_origin["finalization_uses_exact_selected_minimal_plan"]
        )

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
        self.assertEqual(selection["candidate_pool_count"], 1)
        self.assertEqual(selection["selected_candidate_index"], 0)
        self.assertEqual(selection["attempt_count"], 1)
        self.assertTrue(selection["shared_deadline_enforced"])
        self.assertTrue(selection["exact_selected_minimal_plan"])
        self.assertFalse(selection["alternate_candidate_attempted"])
        self.assertEqual(
            selection["selected_placement_digest"],
            minimal["plan_digest"],
        )
        self.assertTrue(materialization["certified"])
        minimal_by_id = {
            placement["id"]: placement for placement in minimal["placements"]
        }
        for placement in finalized["placements"]:
            source = minimal_by_id[placement["id"]]
            self.assertEqual(
                placement["composite_bounds_v2"][
                    "source_minimum_origin_mm"
                ],
                source["origin_mm"],
            )
            self.assertEqual(
                placement["composite_bounds_v2"][
                    "source_minimum_size_mm"
                ],
                source["world_size_mm"],
            )
            for cavity in placement["frozen_cavities_v1"]:
                self.assertEqual(
                    cavity["source_owner_origin_mm"],
                    source["origin_mm"],
                )
                self.assertEqual(
                    cavity["source_owner_world_size_mm"],
                    source["world_size_mm"],
                )
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
        cad = build_partition_cad(
            project,
            partition=finalized,
            artifact_identity={
                "artifact_kind": "finalized_plan",
                "artifact_digest": "test-tray-candidate-pool",
                "partition_plan_digest": finalized["plan_digest"],
                "source_revision": 0,
            },
            effort_profile="normal",
        )
        self.assertEqual(cad["status"], "ready_for_fusion")
        fusion = generation_plan_from_cad_ir(
            cad["cad_ir"],
            FUSION_GENERATION_MODE_COMPACT_ONLY,
        )
        self.assertEqual(
            fusion.module_component_count,
            len(finalized["placements"]),
        )
        self.assertFalse(
            any(
                value.cavity_source
                == "frozen_cavity_vertical_access"
                for value in fusion.cavity_cuts
            )
        )
        self.assertTrue(
            any(
                value.cavity_source == "frozen_content_cavity"
                and value.anchor_kind
                in {"open_top", "below_top_inset"}
                and value.calibrated_depth_source_mm
                == value.calibrated_depth_final_mm
                for value in fusion.cavity_cuts
            )
        )


if __name__ == "__main__":
    unittest.main()
