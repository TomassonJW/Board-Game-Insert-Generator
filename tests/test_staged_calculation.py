from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.partition_cad import build_partition_cad
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.staged_calculation import (
    ARTIFACT_KIND_FINALIZED,
    ARTIFACT_KIND_MINIMAL,
    STATUS_CAD_READY,
    STATUS_CURRENT,
    STATUS_DESYNCHRONIZED,
    STATUS_STALE,
    StagedCalculationError,
    StagedCalculationSession,
)


SETTINGS = {"method": "auto", "effort": "quick"}


def _project() -> dict[str, object]:
    project = blank_project_v1()
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


def _synchronize(
    session: StagedCalculationSession,
    project: object,
    engine: IncrementalLocalAnalysisEngine,
    *,
    settings: dict[str, str] = SETTINGS,
) -> dict[str, object]:
    return session.synchronize(
        project,
        engine.snapshot(),
        solver_settings=settings,
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )


def _minimal_cad(
    session: StagedCalculationSession,
    project: dict[str, object],
) -> dict[str, object]:
    selection = session.select_materializable_artifact(ARTIFACT_KIND_MINIMAL)
    return build_partition_cad(
        project,
        partition=selection["partition"],
        artifact_identity=selection,
        effort_profile="quick",
    )


class StagedCalculationTests(unittest.TestCase):
    def test_synchronization_never_invokes_the_global_solver(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)

        initial = _synchronize(session, project, engine)
        changed = deepcopy(project)
        changed["contents"][0]["quantity"] = 3
        refreshed_analysis = engine.update_project(changed)
        refreshed = session.synchronize(
            changed,
            refreshed_analysis,
            solver_settings=SETTINGS,
            container_frontiers=engine.certified_frontiers(),
            frontier_digests=engine.frontier_digests(),
        )

        self.assertEqual(initial["minimal_layout"]["status"], "not_computed")
        self.assertEqual(refreshed["minimal_layout"]["status"], "not_computed")
        self.assertEqual(refreshed["next_action"], "calculate_layout")
        self.assertTrue(refreshed["invariants"]["global_solve_is_explicit"])

    def test_fixture_11_minimal_materialization_is_selected_before_finalization(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)

        calculated = session.calculate_layout(request_id="solve-1", request_revision=0)
        selection = session.select_materializable_artifact(ARTIFACT_KIND_MINIMAL)
        cad = _minimal_cad(session, project)

        self.assertEqual(calculated["solver_result"]["status"], "solution_found")
        self.assertTrue(calculated["staged_calculation"]["minimal_layout"]["placement_certified"])
        self.assertFalse(calculated["staged_calculation"]["minimal_layout"]["finalization_required"])
        self.assertEqual(calculated["staged_calculation"]["finalized_plan"]["status"], "not_finalized")
        self.assertEqual(selection["artifact_kind"], ARTIFACT_KIND_MINIMAL)
        self.assertEqual(selection["partition_plan_digest"], calculated["partition"]["plan_digest"])
        self.assertEqual(cad["status"], "ready_for_fusion")
        self.assertEqual(cad["artifact_identity"]["artifact_kind"], ARTIFACT_KIND_MINIMAL)
        self.assertFalse(cad["partition"]["invariants"]["residual_distributed"])

    def test_certified_witness_is_forwarded_as_recertified_fresh_search(self) -> None:
        project = _project()
        source_engine = _engine(project)
        source = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(source, project, source_engine)
        witness_plan = source.calculate_layout(
            request_id="source-witness", request_revision=0
        )["partition"]

        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        calculated = session.calculate_layout(
            request_id="warm-start",
            request_revision=1,
            initial_incumbent=witness_plan,
        )

        minimal = calculated["staged_calculation"]["minimal_layout"]
        self.assertEqual(
            minimal["calculation_timing"]["result_source"],
            "fresh_search_with_certified_witness",
        )
        self.assertEqual(minimal["warm_start"]["status"], "accepted")
        self.assertTrue(minimal["warm_start"]["search_continued"])
        self.assertTrue(minimal["placement_certified"])
        self.assertEqual(
            calculated["solver_result"]["status"], "solution_found"
        )

    def test_identical_explicit_calculation_reuses_only_a_certified_plan(self) -> None:
        project = _project()
        engine = _engine(project)
        clock = iter((100, 350, 1_000, 1_004))
        session = StagedCalculationSession(
            project,
            solver_settings=SETTINGS,
            monotonic_ms=lambda: next(clock),
        )
        _synchronize(session, project, engine)
        calls = 0

        def counted_solver(raw_project: object, **kwargs: object) -> dict[str, object]:
            nonlocal calls
            calls += 1
            kwargs.pop("solver_method", None)
            return solve_minimal_layout(raw_project, **kwargs)

        first = session.calculate_layout(
            request_id="solve-1", request_revision=0, solver=counted_solver
        )
        second = session.calculate_layout(
            request_id="solve-2", request_revision=2, solver=counted_solver
        )

        self.assertEqual(calls, 1)
        self.assertEqual(first["partition"]["plan_digest"], second["partition"]["plan_digest"])
        first_minimal = first["staged_calculation"]["minimal_layout"]
        second_minimal = second["staged_calculation"]["minimal_layout"]
        self.assertEqual(first_minimal["cache_write_status"], "stored_certified")
        self.assertEqual(first_minimal["calculation_timing"]["result_source"], "fresh_search")
        self.assertEqual(first_minimal["calculation_timing"]["search_elapsed_ms"], 250)
        self.assertEqual(
            first_minimal["calculation_timing"]["retrieval_elapsed_ms"],
            "not_applicable",
        )
        self.assertEqual(second_minimal["cache_status"], "hit")
        self.assertEqual(second_minimal["cache_write_status"], "reused_certified")
        self.assertEqual(
            second_minimal["calculation_timing"],
            {
                "schema_version": "bgig.calculation_timing.v1",
                "result_source": "certified_cache",
                "search_elapsed_ms": 250,
                "request_elapsed_ms": 4,
                "retrieval_elapsed_ms": 4,
            },
        )
        self.assertEqual(
            second["solver_result"]["telemetry"]["request"],
            {"id": "solve-2", "revision": 2},
        )
        self.assertEqual(
            second["solver_result"]["telemetry"]["request_scope"],
            "staged_action",
        )

    def test_negative_result_is_observed_but_never_satisfies_a_new_explicit_run(self) -> None:
        project = _project()
        engine = _engine(project)
        clock = iter((0, 8_000, 9_000, 17_000))
        session = StagedCalculationSession(
            project,
            solver_settings=SETTINGS,
            monotonic_ms=lambda: next(clock),
        )
        _synchronize(session, project, engine)
        calls = 0

        def failing_solver(_raw_project: object, **_kwargs: object) -> dict[str, object]:
            nonlocal calls
            calls += 1
            return {
                "plan_digest": canonical_digest({"negative_attempt": calls}),
                "summary": {
                    "status": "not_constructed",
                    "placement_certified": False,
                },
                "minimal_layout": {
                    "artifact_kind": "minimal_layout",
                    "finalization_applied": False,
                    "global_certificate": {"certified": False},
                },
                "solver": {
                    "result": {"status": "no_solution_within_budget"},
                    "telemetry": {"stop_reason": "test_budget_exhausted"},
                },
            }

        first = session.calculate_layout(
            request_id="negative-1",
            request_revision=0,
            solver=failing_solver,
        )
        second = session.calculate_layout(
            request_id="negative-2",
            request_revision=0,
            solver=failing_solver,
        )

        self.assertEqual(calls, 2)
        for result in (first, second):
            minimal = result["staged_calculation"]["minimal_layout"]
            self.assertEqual(minimal["cache_status"], "miss")
            self.assertEqual(minimal["cache_write_status"], "skipped_non_certified")
            self.assertEqual(minimal["calculation_timing"]["result_source"], "fresh_search")
            self.assertEqual(minimal["calculation_timing"]["search_elapsed_ms"], 8_000)
            self.assertEqual(
                minimal["calculation_timing"]["retrieval_elapsed_ms"],
                "not_applicable",
            )
        self.assertEqual(second["staged_calculation"]["cache"]["current_entries"], 0)

    def test_mutation_during_global_run_is_rejected_as_stale(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)

        def mutating_solver(raw_project: object, **kwargs: object) -> dict[str, object]:
            kwargs.pop("solver_method", None)
            result = solve_minimal_layout(raw_project, **kwargs)
            changed = deepcopy(project)
            changed["contents"][0]["quantity"] = 3
            changed_engine = _engine(changed)
            _synchronize(session, changed, changed_engine)
            return result

        result = session.calculate_layout(
            request_id="solve-stale", request_revision=4, solver=mutating_solver
        )

        self.assertIsNone(result["partition"])
        self.assertEqual(result["solver_result"]["status"], "stale_or_cancelled")
        self.assertEqual(
            result["solver_result"]["telemetry"]["stop_reason"],
            "dependencies_changed_during_global_run",
        )
        self.assertEqual(result["staged_calculation"]["minimal_layout"]["status"], "not_computed")

    def test_fixture_12_failed_finalization_preserves_minimal_materialization(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        calculated = session.calculate_layout(request_id="solve-1", request_revision=0)

        with self.assertRaisesRegex(StagedCalculationError, "Aucune methode de finition"):
            session.finalize_volume()

        selection = session.select_materializable_artifact(ARTIFACT_KIND_MINIMAL)
        snapshot = session.snapshot()
        self.assertEqual(snapshot["minimal_layout"]["status"], STATUS_CURRENT)
        self.assertEqual(
            snapshot["minimal_layout"]["artifact_digest"],
            calculated["staged_calculation"]["minimal_layout"]["artifact_digest"],
        )
        self.assertEqual(snapshot["finalized_plan"]["status"], "not_finalized")
        self.assertEqual(selection["partition_plan_digest"], calculated["partition"]["plan_digest"])

    def test_dual_selection_accepts_a_separately_certified_finalized_plan(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        calculated = session.calculate_layout(request_id="solve-1", request_revision=0)
        minimal_digest = calculated["staged_calculation"]["minimal_layout"]["artifact_digest"]

        def explicit_finalizer(plan: dict[str, object]) -> dict[str, object]:
            finalized = deepcopy(plan)
            finalized["summary"]["materializable"] = True
            finalized["finalization"] = {
                "artifact_kind": ARTIFACT_KIND_FINALIZED,
                "source_minimal_artifact_digest": minimal_digest,
                "certificate": {"certified": True},
            }
            finalized.pop("plan_digest", None)
            finalized["plan_digest"] = canonical_digest(finalized)
            return finalized

        finalized = session.finalize_volume(
            finalizer=explicit_finalizer,
            finishing_policy="test_explicit_policy",
            finishing_budget_digest=canonical_digest({"budget": "test"}),
            finalizer_id="test-finalizer",
            finalizer_version="1",
        )
        selection = session.select_materializable_artifact(ARTIFACT_KIND_FINALIZED)

        self.assertEqual(finalized["staged_calculation"]["finalized_plan"]["status"], STATUS_CURRENT)
        self.assertEqual(selection["artifact_kind"], ARTIFACT_KIND_FINALIZED)
        self.assertNotEqual(
            selection["artifact_digest"],
            calculated["staged_calculation"]["minimal_layout"]["artifact_digest"],
        )
        self.assertEqual(
            session.select_materializable_artifact(ARTIFACT_KIND_MINIMAL)["partition_plan_digest"],
            calculated["partition"]["plan_digest"],
        )

    def test_cad_ready_requires_the_exact_selected_identity(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        session.calculate_layout(request_id="solve-1", request_revision=0)
        cad = _minimal_cad(session, project)

        wrong = deepcopy(cad)
        wrong["artifact_identity"]["artifact_digest"] = "old-artifact"
        with self.assertRaisesRegex(StagedCalculationError, "correspond pas exactement"):
            session.record_cad_ready(wrong)

        session.record_cad_ready(cad)
        snapshot = session.snapshot()
        self.assertEqual(snapshot["materialization"]["status"], STATUS_CAD_READY)
        self.assertFalse(snapshot["materialization"]["fusion_observed"])
        self.assertEqual(snapshot["next_action"], "choose_optional_finishing_or_export")

    def test_fixture_13_new_revision_desynchronizes_the_old_scene_identity(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        session.calculate_layout(request_id="solve-1", request_revision=0)
        cad = _minimal_cad(session, project)
        session.record_cad_ready(cad)

        changed = deepcopy(project)
        changed["contents"][0]["quantity"] = 3
        changed_engine = _engine(changed)
        snapshot = _synchronize(session, changed, changed_engine)

        self.assertEqual(snapshot["minimal_layout"]["status"], STATUS_STALE)
        self.assertEqual(snapshot["materialization"]["status"], STATUS_DESYNCHRONIZED)
        self.assertEqual(snapshot["next_action"], "calculate_layout")
        with self.assertRaises(StagedCalculationError):
            session.select_materializable_artifact(ARTIFACT_KIND_MINIMAL)

    def test_frontier_digest_change_stales_minimal_without_project_mutation(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        session.calculate_layout(request_id="solve-1", request_revision=0)

        changed = session.synchronize(
            project,
            engine.snapshot(),
            solver_settings=SETTINGS,
            container_frontiers=engine.certified_frontiers(),
            frontier_digests=(("g", canonical_digest({"frontier": "changed"})),),
        )

        self.assertEqual(changed["minimal_layout"]["status"], STATUS_STALE)
        self.assertEqual(changed["next_action"], "calculate_layout")
    def test_solver_setting_change_stales_minimal_and_finalized_artifacts(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        session.calculate_layout(request_id="solve-1", request_revision=0)
        changed = session.synchronize(
            project,
            engine.snapshot(),
            solver_settings={"method": "auto", "effort": "normal"},
            container_frontiers=engine.certified_frontiers(),
            frontier_digests=engine.frontier_digests(),
        )
        self.assertEqual(changed["minimal_layout"]["status"], STATUS_STALE)
        self.assertEqual(changed["next_action"], "calculate_layout")


    def test_solver_case_snapshot_preserves_observed_facts_without_operations(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        calculated = session.calculate_layout(
            request_id="solve-case", request_revision=4
        )

        snapshot = session.solver_case_snapshot()

        self.assertEqual(
            snapshot["observed_partition"]["plan_digest"],
            calculated["partition"]["plan_digest"],
        )
        self.assertEqual(
            snapshot["current_minimal_partition"]["plan_digest"],
            calculated["partition"]["plan_digest"],
        )
        self.assertEqual(
            snapshot["staged_calculation"], calculated["staged_calculation"]
        )
        self.assertEqual(
            snapshot["invariants"],
            {
                "snapshot_only": True,
                "global_solver_invocation_count": 0,
                "finalization_invocation_count": 0,
                "cad_build_invocation_count": 0,
                "fusion_materialization_invocation_count": 0,
            },
        )

if __name__ == "__main__":
    unittest.main()