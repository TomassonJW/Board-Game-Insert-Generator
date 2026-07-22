from __future__ import annotations

from copy import deepcopy
import unittest
from unittest.mock import patch

from board_game_insert_generator.certified_plan_witness import (
    CERTIFIED_PLAN_WITNESS_SCHEMA_V1,
    WITNESS_ACCEPTED,
    WITNESS_REJECTED,
    build_certified_plan_witness,
    certified_plan_witness_identity,
    validate_certified_plan_witness,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.free_3d_beam_solver import (
    Free3DBeamExecution,
    Free3DBeamTelemetry,
)
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.solver_contract import SolverStrategy
from board_game_insert_generator.solver_outcome import (
    NO_SOLUTION_WITHIN_BUDGET,
    SOLUTION_FOUND,
)


def _project() -> dict[str, object]:
    project = blank_project_v1()
    project["project_name"] = "Witness limite"
    project["container_groups"] = [
        {
            "id": "g",
            "name": "Bac",
            "wall_thickness_mm": None,
            "floor_thickness_mm": None,
        }
    ]
    project["contents"] = [
        {
            "id": "c",
            "name": "Pieces",
            "shape_kind": "square",
            "dimensions_mm": {"x": 12, "y": 12, "z": 3},
            "quantity": 2,
            "container_group_id": "g",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
    ]
    return project


def _engine(project: object) -> IncrementalLocalAnalysisEngine:
    return IncrementalLocalAnalysisEngine(project, effort_profile="quick")


def _certified_plan(
    project: object,
    engine: IncrementalLocalAnalysisEngine,
) -> dict[str, object]:
    return solve_minimal_layout(
        project,
        effort_profile="quick",
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )


def _empty_execution(*args: object, **kwargs: object) -> Free3DBeamExecution:
    telemetry = Free3DBeamTelemetry(
        search_states=1,
        placement_trials=1,
        feasible_options=0,
        states_generated=0,
        states_deduplicated=0,
        states_pruned_by_width=0,
        states_pruned_by_space_limit=0,
        geometric_completions=0,
        completions_with_printable_residual=0,
        admitted_complete_solutions=0,
        maximum_beam_width_retained=1,
        maximum_depth_reached=0,
        maximum_empty_spaces_retained=1,
        maximum_extreme_points_retained=1,
        budget_exhausted=True,
        cancelled=False,
        timed_out=False,
    )
    return Free3DBeamExecution(
        strategy=SolverStrategy("forced_empty_lane", "1"),
        budget=kwargs["budget"],
        status=NO_SOLUTION_WITHIN_BUDGET,
        stop_reason="hard_budget_reached",
        solutions=(),
        remaining_best_participant_ids=(),
        telemetry=telemetry,
        deterministic_digest="d" * 64,
    )


class CertifiedPlanWitnessTests(unittest.TestCase):
    def test_witness_is_deterministic_and_effort_agnostic_but_frontier_exact(self) -> None:
        project = _project()
        engine = _engine(project)
        plan = _certified_plan(project, engine)

        first = build_certified_plan_witness(
            project,
            plan,
            frontier_digests=engine.frontier_digests(),
        )
        second = build_certified_plan_witness(
            deepcopy(project),
            deepcopy(plan),
            frontier_digests=engine.frontier_digests(),
        )
        accepted = validate_certified_plan_witness(
            first,
            project,
            frontier_digests=engine.frontier_digests(),
        )

        self.assertEqual(first, second)
        self.assertEqual(first["schema_version"], CERTIFIED_PLAN_WITNESS_SCHEMA_V1)
        self.assertEqual(len(first["source"]["rank_axes"]), 7)
        self.assertEqual(accepted["status"], WITNESS_ACCEPTED)
        self.assertEqual(accepted["partition"]["plan_digest"], plan["plan_digest"])
        self.assertTrue(first["invariants"]["effort_profile_is_not_a_compatibility_key"])
        identity = certified_plan_witness_identity(project, engine.frontier_digests())
        self.assertEqual(first["identity"], identity)

    def test_changed_project_frontier_or_payload_is_rejected_fail_closed(self) -> None:
        project = _project()
        engine = _engine(project)
        plan = _certified_plan(project, engine)
        witness = build_certified_plan_witness(
            project,
            plan,
            frontier_digests=engine.frontier_digests(),
        )
        changed = deepcopy(project)
        changed["contents"][0]["quantity"] = 3
        changed_engine = _engine(changed)
        dependency_rejection = validate_certified_plan_witness(
            witness,
            changed,
            frontier_digests=changed_engine.frontier_digests(),
        )
        tampered = deepcopy(witness)
        tampered["partition"]["placements"][0]["origin_mm"]["x"] += 1
        digest_rejection = validate_certified_plan_witness(
            tampered,
            project,
            frontier_digests=engine.frontier_digests(),
        )

        self.assertEqual(dependency_rejection["status"], WITNESS_REJECTED)
        self.assertEqual(
            dependency_rejection["stop_reason"],
            "witness_dependencies_changed",
        )
        self.assertEqual(digest_rejection["status"], WITNESS_REJECTED)
        self.assertEqual(digest_rejection["stop_reason"], "witness_digest_mismatch")
        rank_tampered = deepcopy(witness)
        rank_tampered["source"]["rank_axes"][0] -= 1.0
        rank_tampered.pop("witness_digest")
        rank_tampered["witness_digest"] = canonical_digest(rank_tampered)
        rank_rejection = validate_certified_plan_witness(
            rank_tampered,
            project,
            frontier_digests=engine.frontier_digests(),
        )
        self.assertEqual(rank_rejection["status"], WITNESS_REJECTED)
        self.assertEqual(
            rank_rejection["stop_reason"],
            "witness_rank_axes_mismatch",
        )

    def test_recertified_witness_survives_empty_lanes_and_search_still_runs(self) -> None:
        project = _project()
        engine = _engine(project)
        plan = _certified_plan(project, engine)
        calls = 0

        def counted_empty(*args: object, **kwargs: object) -> Free3DBeamExecution:
            nonlocal calls
            calls += 1
            return _empty_execution(*args, **kwargs)

        with patch(
            "board_game_insert_generator.minimal_layout_solver.solve_free_3d_beam",
            side_effect=counted_empty,
        ):
            without_witness = solve_minimal_layout(
                project,
                effort_profile="quick",
                container_frontiers=engine.certified_frontiers(),
                frontier_digests=engine.frontier_digests(),
            )
            calls_without_witness = calls
            with_witness = solve_minimal_layout(
                project,
                effort_profile="quick",
                container_frontiers=engine.certified_frontiers(),
                frontier_digests=engine.frontier_digests(),
                initial_incumbent=plan,
            )

        self.assertEqual(
            without_witness["solver"]["result"]["status"],
            NO_SOLUTION_WITHIN_BUDGET,
        )
        self.assertEqual(with_witness["solver"]["result"]["status"], SOLUTION_FOUND)
        provenance = with_witness["minimal_layout"]["search_provenance"]
        self.assertEqual(provenance["warm_start"]["status"], "accepted")
        self.assertTrue(provenance["warm_start"]["selected"])
        self.assertTrue(provenance["warm_start"]["search_continued"])
        self.assertEqual(provenance["warm_start"]["lane_count_added"], 0)
        self.assertEqual(provenance["selected"]["candidate_source"], "certified_witness")
        self.assertEqual(
            provenance["lane_prefix_ids"],
            without_witness["minimal_layout"]["search_provenance"]["lane_prefix_ids"],
        )
        self.assertGreater(calls_without_witness, 0)
        self.assertGreater(calls, calls_without_witness)

    def test_deep_recertifies_witness_only_in_extension_after_normal_prefix(self) -> None:
        project = _project()
        deep_engine = IncrementalLocalAnalysisEngine(
            project,
            effort_profile="deep",
        )
        plan = solve_minimal_layout(
            project,
            effort_profile="deep",
            container_frontiers=deep_engine.certified_frontiers(),
            frontier_digests=deep_engine.frontier_digests(),
        )
        calls = 0

        def counted_empty(*args: object, **kwargs: object) -> Free3DBeamExecution:
            nonlocal calls
            calls += 1
            return _empty_execution(*args, **kwargs)

        with patch(
            "board_game_insert_generator.minimal_layout_solver.solve_free_3d_beam",
            side_effect=counted_empty,
        ):
            rebuilt = solve_minimal_layout(
                project,
                effort_profile="deep",
                container_frontiers=deep_engine.certified_frontiers(),
                frontier_digests=deep_engine.frontier_digests(),
                initial_incumbent=plan,
            )

        self.assertEqual(
            rebuilt["solver"]["result"]["status"],
            SOLUTION_FOUND,
        )
        provenance = rebuilt["minimal_layout"]["search_provenance"]
        normal_phase = provenance["phases"]["normal_prefix"]
        deep_phase = provenance["phases"]["deep_extension"]
        self.assertEqual(normal_phase["warm_start"]["status"], "not_supplied")
        self.assertEqual(deep_phase["warm_start"]["status"], "accepted")
        self.assertEqual(deep_phase["warm_start"]["lane_count_added"], 0)
        self.assertEqual(len(normal_phase["attempted_lane_ids"]), 6)
        self.assertEqual(len(deep_phase["attempted_lane_ids"]), 3)
        self.assertEqual(calls, 9)
        self.assertTrue(deep_phase["warm_start"]["search_continued"])


if __name__ == "__main__":
    unittest.main()
