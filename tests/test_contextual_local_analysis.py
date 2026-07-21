from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.contextual_local_analysis import (
    COMPATIBLE,
    CONDITIONAL,
    INCOMPATIBLE,
    UNKNOWN,
    IncrementalLocalAnalysisEngine,
    build_contextual_local_analysis,
)
from p64_v2h03b_fixture_cases import (
    localized_reservation_project,
    multi_cavity_tradeoff_project,
)


def _two_container_project() -> dict[str, object]:
    project = multi_cavity_tradeoff_project()
    project["container_groups"].append(
        {
            "id": "neighbor",
            "name": "Bac voisin",
            "wall_thickness_mm": 2.0,
            "floor_thickness_mm": 2.0,
        }
    )
    project["contents"].append(
        {
            "id": "neighbor-content",
            "name": "Element voisin",
            "shape_kind": "rectangle",
            "dimensions_mm": {"x": 12.0, "y": 10.0, "z": 4.0},
            "quantity": 2,
            "container_group_id": "neighbor",
            "content_clearance_mm": 0.0,
            "measurement_confidence": "exact",
        }
    )
    return project


class ContextualLocalAnalysisTests(unittest.TestCase):
    def test_scores_are_explicit_deterministic_and_have_no_opaque_total(self) -> None:
        project = multi_cavity_tradeoff_project()

        first = build_contextual_local_analysis(project)
        second = build_contextual_local_analysis(deepcopy(project))

        self.assertEqual(first, second)
        container = first["containers"][0]
        self.assertEqual(container["engine_frontier_count"], 8)
        self.assertGreater(container["engine_frontier_count"], len(container["visible_representatives"]))
        self.assertTrue(container["invariants"]["shortlist_is_non_normative"])
        labels = {
            label
            for representative in container["visible_representatives"]
            for label in representative["labels"]
        }
        self.assertEqual(labels, {"Compact", "\u00c9quilibr\u00e9", "Bas"})
        for variant in container["variants"]:
            scores = variant["scores"]
            self.assertEqual(
                set(scores),
                {
                    "schema_version",
                    "envelope_efficiency",
                    "volume_mm3",
                    "footprint_area_mm2",
                    "aspect_penalty",
                    "height_mm",
                    "layout_complexity",
                    "compatibility_is_separate",
                    "opaque_total",
                },
            )
            self.assertIsNone(scores["opaque_total"])
            self.assertIsNotNone(scores["envelope_efficiency"]["value"])
            self.assertIn(
                variant["geometry_digest"],
                container["engine_frontier_variant_digests"],
            )

    def test_box_and_localized_reservation_annotations_are_fail_closed(self) -> None:
        compatible = build_contextual_local_analysis(
            localized_reservation_project()
        )["containers"][0]
        for variant in compatible["variants"]:
            self.assertEqual(
                variant["context_compatibility"]["box"]["status"],
                COMPATIBLE,
            )
            self.assertIn(
                variant["context_compatibility"]["top_context"]["status"],
                {COMPATIBLE, CONDITIONAL},
            )
            self.assertFalse(
                variant["context_compatibility"]["unknown_is_compatible"]
            )

        conditional_project = localized_reservation_project()
        conditional_project["flat_items"][0]["dimensions_mm"]["z"] = 40.0
        conditional = build_contextual_local_analysis(
            conditional_project
        )["containers"][0]
        self.assertTrue(
            any(
                reservation["status"] == CONDITIONAL
                for variant in conditional["variants"]
                for reservation in variant["context_compatibility"]["reservations"]
            )
        )

        incompatible_project = multi_cavity_tradeoff_project()
        incompatible_project["box"]["inner_dimensions_mm"] = {
            "x": 20.0,
            "y": 20.0,
            "z": 9.0,
        }
        incompatible_project["box"]["usable_height_mm"] = 8.0
        incompatible = build_contextual_local_analysis(
            incompatible_project
        )["containers"][0]
        self.assertTrue(
            all(
                variant["context_compatibility"]["box"]["status"] == INCOMPATIBLE
                for variant in incompatible["variants"]
            )
        )

    def test_container_without_local_candidate_stays_unknown(self) -> None:
        project = multi_cavity_tradeoff_project()
        project["container_groups"].append(
            {
                "id": "empty",
                "name": "Vide",
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
            }
        )

        analysis = build_contextual_local_analysis(project)
        empty = next(
            value
            for value in analysis["containers"]
            if value["container_group_id"] == "empty"
        )

        self.assertEqual(empty["summary"]["status"], UNKNOWN)
        self.assertEqual(empty["engine_frontier_count"], 0)
        self.assertIn(
            "empty",
            analysis["reactive_global_bounds"][
                "container_without_certified_frontier_ids"
            ],
        )
        self.assertFalse(
            analysis["invariants"]["unknown_promoted_to_compatible"]
        )

    def test_asset_edit_recomputes_exactly_one_local_chain_and_never_solves(self) -> None:
        project = _two_container_project()
        engine = IncrementalLocalAnalysisEngine(project)
        before = {
            value["container_group_id"]: value["frontier_digest"]
            for value in engine.snapshot()["containers"]
        }
        changed = deepcopy(project)
        changed["contents"][0]["quantity"] = 2

        result = engine.update_project(changed)
        incremental = result["incremental"]
        after = {
            value["container_group_id"]: value["frontier_digest"]
            for value in result["containers"]
        }

        self.assertEqual(
            incremental["recomputed_frontier_group_ids"],
            ["tradeoff"],
        )
        self.assertEqual(
            incremental["recomputed_context_group_ids"],
            ["tradeoff"],
        )
        self.assertIn("neighbor", incremental["reused_frontier_group_ids"])
        self.assertIn("neighbor", incremental["reused_context_group_ids"])
        self.assertEqual(before["neighbor"], after["neighbor"])
        self.assertNotEqual(before["tradeoff"], after["tradeoff"])
        self.assertEqual(
            result["invariants"]["global_solver_invocation_count"],
            0,
        )
        self.assertFalse(
            result["reactive_global_bounds"]["placement_performed"]
        )

    def test_box_edit_reuses_intrinsic_frontier_and_refreshes_context_only(self) -> None:
        project = multi_cavity_tradeoff_project()
        engine = IncrementalLocalAnalysisEngine(project)
        frontier_digest = engine.snapshot()["containers"][0]["frontier_digest"]
        changed = deepcopy(project)
        changed["box"]["inner_dimensions_mm"]["x"] = 100.0

        result = engine.update_project(changed)
        incremental = result["incremental"]

        self.assertEqual(incremental["recomputed_frontier_group_ids"], [])
        self.assertEqual(
            incremental["recomputed_context_group_ids"],
            ["tradeoff"],
        )
        self.assertEqual(
            incremental["reused_frontier_group_ids"],
            ["tradeoff"],
        )
        self.assertEqual(
            result["containers"][0]["frontier_digest"],
            frontier_digest,
        )

    def test_identical_update_is_cache_neutral_and_reports_reuse(self) -> None:
        project = _two_container_project()
        engine = IncrementalLocalAnalysisEngine(project)

        result = engine.update_project(deepcopy(project))

        self.assertEqual(
            result["incremental"]["recomputed_frontier_group_ids"],
            [],
        )
        self.assertEqual(
            result["incremental"]["recomputed_context_group_ids"],
            [],
        )
        self.assertEqual(
            result["incremental"]["reused_frontier_group_ids"],
            ["neighbor", "tradeoff"],
        )
        self.assertEqual(
            result["incremental"]["reused_context_group_ids"],
            ["neighbor", "tradeoff"],
        )

    def test_reactive_bounds_never_claim_a_global_solution(self) -> None:
        bounds = build_contextual_local_analysis(
            multi_cavity_tradeoff_project()
        )["reactive_global_bounds"]

        self.assertEqual(bounds["status"], "necessary_bounds_satisfied")
        self.assertGreater(bounds["signed_volume_balance_mm3"], 0.0)
        self.assertFalse(bounds["placement_performed"])
        self.assertFalse(bounds["proves_global_solution"])
        self.assertEqual(bounds["formal_contradictions"], [])


if __name__ == "__main__":
    unittest.main()
