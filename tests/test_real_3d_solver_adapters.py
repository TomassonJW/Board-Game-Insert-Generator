from __future__ import annotations

import unittest

from board_game_insert_generator.external_solver_adapters import (
    ExternalSolverLimits,
    ExternalSolverRuntime,
)
from board_game_insert_generator.real_3d_solver_adapters import (
    CANDIDATE_FIDELITY,
    STATUS_UNSUPPORTED,
    build_real_3d_exact_controls,
    prepare_real_3d_problem,
    recertify_real_3d_solution,
    run_real_3d_adapter,
)


class Real3DSolverAdaptersTests(unittest.TestCase):
    def test_four_external_engine_families_are_distinct(self) -> None:
        self.assertEqual(
            len({value["family"] for value in CANDIDATE_FIDELITY.values()}),
            4,
        )

    def test_exact_controls_never_expose_a_positive_witness(self) -> None:
        controls = build_real_3d_exact_controls()
        self.assertEqual(len(controls), 6)
        self.assertEqual(
            {control["expected"] for control in controls},
            {"feasible", "infeasible"},
        )
        for control in controls:
            self.assertNotIn("witness", control)
            self.assertNotIn("placements", control)
            self.assertEqual(len(control["world_mm"]), 3)

    def test_laff_refuses_rules_it_does_not_translate(self) -> None:
        control = next(
            value
            for value in build_real_3d_exact_controls()
            if value["control_id"] == "multi-support-feasible"
        )
        prepared, reasons = prepare_real_3d_problem(control, "laff")
        self.assertIsNone(prepared)
        self.assertIn("multi_support", reasons)
        self.assertIn("support", reasons)
        self.assertIn("multi_support_count", reasons)

    def test_complete_models_keep_multi_support_semantics(self) -> None:
        control = next(
            value
            for value in build_real_3d_exact_controls()
            if value["control_id"] == "multi-support-feasible"
        )
        for candidate in ("ortools_cp_sat", "scip"):
            prepared, reasons = prepare_real_3d_problem(control, candidate)
            self.assertIsNotNone(prepared)
            self.assertEqual(reasons, ())

    def test_recertifier_accepts_a_real_stack(self) -> None:
        control = next(
            value
            for value in build_real_3d_exact_controls()
            if value["control_id"] == "stacking-feasible"
        )
        placements = [
            {
                "participant_id": "a",
                "x": 0,
                "y": 0,
                "z": 0,
                "size": [6, 6, 3],
                "orientation": "xyz",
                "selected_variant_id": "v0",
                "assigned_content_count": 1,
                "support_ids": [],
                "removal_rank": 8,
            },
            {
                "participant_id": "b",
                "x": 0,
                "y": 0,
                "z": 3,
                "size": [6, 6, 5],
                "orientation": "xyz",
                "selected_variant_id": "v0",
                "assigned_content_count": 1,
                "support_ids": ["a"],
                "removal_rank": 5,
            },
        ]
        self.assertEqual(recertify_real_3d_solution(control, placements), ())

    def test_recertifier_rejects_missing_support(self) -> None:
        control = next(
            value
            for value in build_real_3d_exact_controls()
            if value["control_id"] == "stacking-feasible"
        )
        placements = [
            {
                "participant_id": "a",
                "x": 0,
                "y": 0,
                "z": 0,
                "size": [6, 6, 3],
                "orientation": "xyz",
                "selected_variant_id": "v0",
                "assigned_content_count": 1,
                "support_ids": [],
                "removal_rank": 8,
            },
            {
                "participant_id": "b",
                "x": 0,
                "y": 0,
                "z": 3,
                "size": [6, 6, 5],
                "orientation": "xyz",
                "selected_variant_id": "v0",
                "assigned_content_count": 1,
                "support_ids": [],
                "removal_rank": 5,
            },
        ]
        errors = recertify_real_3d_solution(control, placements)
        self.assertIn("support_count:b", errors)
        self.assertIn("support_coverage:b", errors)

    def test_unsupported_report_does_not_invoke_worker(self) -> None:
        control = next(
            value
            for value in build_real_3d_exact_controls()
            if value["control_id"] == "reservation-feasible"
        )
        report = run_real_3d_adapter(
            control,
            candidate_id="laff",
            runtime=ExternalSolverRuntime(
                candidate_id="laff",
                command=("never-called",),
                environment=(),
                scratch_root="never-called",
                worker_digest="0" * 64,
            ),
            limits=ExternalSolverLimits(
                wall_seconds=1,
                memory_mebibytes=64,
                threads=1,
                seed=1,
            ),
            artifact_receipt={"bundle_digest": "1" * 64},
            exact_control=True,
        )
        self.assertEqual(report["status"], STATUS_UNSUPPORTED)
        self.assertEqual(report["worker_invocation_count"], 0)
        self.assertIn("reservation_volumes", report["unsupported_constraints"])


if __name__ == "__main__":
    unittest.main()
