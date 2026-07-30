from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.selected_product_identity import (
    selected_product_digest,
)


def _plan() -> dict[str, object]:
    return {
        "schema_version": "bgig.partition_plan.v1",
        "box": {"inner_mm": {"x": 100.0, "y": 80.0, "z": 40.0}},
        "placements": {
            "container": {
                "id": "container:a",
                "origin_mm": {"x": 1.0, "y": 2.0, "z": 0.0},
                "world_size_mm": {"x": 10.0, "y": 20.0, "z": 5.0},
            }
        },
        "residuals": [{"volume_mm3": 100.0}],
        "summary": {
            "candidate_count_evaluated": 10,
            "candidate_count_feasible": 8,
        },
        "solver": {
            "candidate_id": "request-a:candidate-1",
            "search_origin": {"proposal_count": 10},
            "telemetry": {"elapsed_ms": 1000},
        },
        "plan_digest": "a" * 64,
        "minimal_layout": {
            "schema_version": "bgig.minimal_layout_artifact.v1",
            "artifact_kind": "minimal_layout",
            "geometry_statement": "selected_geometry",
            "best_candidate_statement": "best_within_budget",
            "metrics": {"cluster_volume_mm3": 1000.0},
            "residual": {"volume_mm3": 100.0, "fragment_count": 1},
            "finalization_applied": True,
            "automatic_body_count": 2,
            "flat_geometry_certificate": {"certified": True},
            "search_provenance": {
                "candidate_count_before_dedup": 10,
                "certificate_rejection_count": 4,
            },
            "certifiable_payload_digest": "b" * 64,
        },
    }


class SelectedProductIdentityTests(unittest.TestCase):
    def test_excludes_request_search_progress_and_telemetry(self) -> None:
        first = _plan()
        second = deepcopy(first)
        second["plan_digest"] = "c" * 64
        second["summary"]["candidate_count_evaluated"] = 11
        second["solver"]["candidate_id"] = "request-b:candidate-9"
        second["solver"]["search_origin"]["proposal_count"] = 11
        second["solver"]["telemetry"]["elapsed_ms"] = 1200
        second["minimal_layout"]["search_provenance"][
            "certificate_rejection_count"
        ] = 32
        second["minimal_layout"]["certifiable_payload_digest"] = "d" * 64

        self.assertEqual(
            selected_product_digest(first),
            selected_product_digest(second),
        )

    def test_changes_when_selected_geometry_changes(self) -> None:
        first = _plan()
        second = deepcopy(first)
        second["placements"]["container"]["origin_mm"]["x"] = 2.0

        self.assertNotEqual(
            selected_product_digest(first),
            selected_product_digest(second),
        )

    def test_changes_when_downstream_product_contract_changes(self) -> None:
        first = _plan()
        second = deepcopy(first)
        second["minimal_layout"]["finalization_applied"] = False

        self.assertNotEqual(
            selected_product_digest(first),
            selected_product_digest(second),
        )


if __name__ == "__main__":
    unittest.main()
