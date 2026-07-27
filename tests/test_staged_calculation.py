from __future__ import annotations

from copy import deepcopy
import unittest
from unittest.mock import patch

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.coupled_finalization import (
    coupled_finalization_budget,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.partition_cad import build_partition_cad
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)
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


def _project_with_flat_reservation() -> dict[str, object]:
    project = _project()
    project["flat_items"] = [
        {
            "id": "board",
            "name": "Plateau",
            "kind": "board",
            "dimensions_mm": {"x": 40.0, "y": 30.0, "z": 2.0},
            "quantity": 1,
            "stack_order": 0,
            "origin_mm": {"x": 5.0, "y": 5.0},
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

    def test_every_geometric_edit_stales_minimal_final_and_scene(self) -> None:
        project = _project()
        edits: list[tuple[str, dict[str, object]]] = []

        changed_content = deepcopy(project)
        changed_content["contents"][0]["quantity"] = 3
        edits.append(("content", changed_content))

        added_container = deepcopy(project)
        added_container["container_groups"].append(
            {
                "id": "g2",
                "name": "Second bac",
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
            }
        )
        edits.append(("container", added_container))

        changed_box = deepcopy(project)
        changed_box["box"]["inner_dimensions_mm"]["x"] = 210.0
        edits.append(("box", changed_box))

        changed_clearance = deepcopy(project)
        changed_clearance["layout"]["layout_clearance_mm"] = 0.8
        edits.append(("clearance", changed_clearance))

        added_reservation = deepcopy(project)
        added_reservation["flat_items"] = [
            {
                "id": "board",
                "name": "Plateau",
                "kind": "board",
                "dimensions_mm": {"x": 40.0, "y": 30.0, "z": 2.0},
                "quantity": 1,
                "stack_order": 0,
                "origin_mm": None,
            }
        ]
        edits.append(("reservation", added_reservation))

        for label, changed in edits:
            with self.subTest(edit=label):
                engine = _engine(project)
                session = StagedCalculationSession(project, solver_settings=SETTINGS)
                _synchronize(session, project, engine)
                session.calculate_layout(
                    request_id=f"solve-before-{label}",
                    request_revision=0,
                )
                session.finalize_volume(finishing_effort_profile="quick")
                session.record_cad_ready(_minimal_cad(session, project))

                changed_engine = _engine(changed)
                snapshot = _synchronize(session, changed, changed_engine)

                self.assertEqual(snapshot["minimal_layout"]["status"], STATUS_STALE)
                self.assertEqual(snapshot["finalized_plan"]["status"], STATUS_STALE)
                self.assertEqual(
                    snapshot["materialization"]["status"],
                    STATUS_DESYNCHRONIZED,
                )
                self.assertEqual(snapshot["next_action"], "calculate_layout")
                self.assertTrue(
                    snapshot["invariants"]["automatic_plan_reuse_disabled"]
                )
                self.assertNotIn("local_reuse", snapshot)
                self.assertNotIn("global_void_reuse", snapshot)

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
        self.assertFalse(
            calculated["staged_calculation"]["minimal_layout"]["finalization_required"]
        )
        self.assertEqual(
            calculated["staged_calculation"]["finalized_plan"]["status"], "not_finalized"
        )
        self.assertEqual(selection["artifact_kind"], ARTIFACT_KIND_MINIMAL)
        self.assertEqual(selection["partition_plan_digest"], calculated["partition"]["plan_digest"])
        self.assertEqual(cad["status"], "ready_for_fusion")
        self.assertEqual(cad["artifact_identity"]["artifact_kind"], ARTIFACT_KIND_MINIMAL)
        self.assertFalse(cad["partition"]["invariants"]["residual_distributed"])

    def test_active_top_reservation_keeps_minimal_materializable_before_optional_finish(self) -> None:
        project = _project_with_flat_reservation()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)

        calculated = session.calculate_layout(
            request_id="solve-with-flat",
            request_revision=0,
        )
        minimal = calculated["staged_calculation"]["minimal_layout"]

        self.assertTrue(minimal["placement_certified"])
        self.assertFalse(minimal["finalization_required"])
        self.assertTrue(minimal["materializable_without_finalization"])
        self.assertEqual(
            calculated["staged_calculation"]["next_action"],
            "materialize_minimal_in_fusion",
        )
        self.assertTrue(
            calculated["staged_calculation"]["available_artifacts"][ARTIFACT_KIND_MINIMAL]
        )
        self.assertIsNotNone(session.current_minimal_partition())
        minimal_selection = session.select_materializable_artifact(
            ARTIFACT_KIND_MINIMAL
        )
        self.assertEqual(
            minimal_selection["artifact_digest"],
            minimal["artifact_digest"],
        )
        reservations = calculated["partition"]["top_inset_reservations"][
            "reservations"
        ]
        self.assertTrue(reservations)
        self.assertTrue(
            all(item["placement_source"] == "automatic_xy" for item in reservations)
        )

    def test_finishing_has_five_independent_monotone_total_budgets(self) -> None:
        profiles = ("quick", "short", "normal", "long", "deep")
        deadlines = (3_000, 10_000, 20_000, 60_000, 180_000)
        budgets = [coupled_finalization_budget(value) for value in profiles]

        self.assertEqual(
            [dict(value.limits)["max_total_elapsed_ms"] for value in budgets],
            list(deadlines),
        )
        self.assertEqual(
            [dict(value.limits)["max_closure_elapsed_ms"] for value in budgets],
            list(deadlines),
        )
        for key in (
            "max_closure_iterations",
            "max_closure_candidates",
            "max_local_repairs",
        ):
            values = [int(dict(value.limits)[key]) for value in budgets]
            self.assertEqual(values, sorted(values))
        with self.assertRaisesRegex(ValueError, "Unsupported effort profile"):
            coupled_finalization_budget("unbounded")

    def test_finish_only_setting_invalidates_only_final_plan(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        calculated = session.calculate_layout(
            request_id="solve-before-finish-setting",
            request_revision=0,
        )
        minimal = calculated["staged_calculation"]["minimal_layout"]
        finalized = session.finalize_volume(
            finishing_effort_profile="normal",
        )
        self.assertEqual(
            finalized["staged_calculation"]["finalized_plan"]["status"],
            STATUS_CURRENT,
        )

        changed = session.select_finishing_effort_profile("long")

        self.assertEqual(changed["minimal_layout"]["status"], STATUS_CURRENT)
        self.assertEqual(
            changed["minimal_layout"]["artifact_digest"],
            minimal["artifact_digest"],
        )
        self.assertEqual(changed["finalized_plan"]["status"], STATUS_STALE)
        self.assertEqual(
            changed["finalized_plan"]["finishing_effort_profile"],
            "long",
        )
        self.assertEqual(
            changed["finalized_plan"]["last_attempt"]["stop_reason"],
            "finishing_settings_changed",
        )
        selection = session.select_materializable_artifact(
            ARTIFACT_KIND_MINIMAL
        )
        self.assertEqual(selection["artifact_digest"], minimal["artifact_digest"])
        with self.assertRaises(StagedCalculationError):
            session.select_materializable_artifact(ARTIFACT_KIND_FINALIZED)

    def test_non_slicing_top_reservation_materializes_one_exact_composite_owner(self) -> None:
        project = _project_with_flat_reservation()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)

        calculated = session.calculate_layout(
            request_id="global-closure-with-flat",
            request_revision=0,
        )
        finalized = session.finalize_volume(finishing_effort_profile="normal")
        partition = finalized["partition"]
        selected = session.select_materializable_artifact(ARTIFACT_KIND_FINALIZED)
        cad = build_partition_cad(
            project,
            partition=selected["partition"],
            artifact_identity=selected,
            effort_profile="quick",
        )
        fusion = generation_plan_from_cad_ir(
            cad["cad_ir"],
            FUSION_GENERATION_MODE_COMPACT_ONLY,
        )

        self.assertTrue(
            calculated["staged_calculation"]["minimal_layout"][
                "placement_certified"
            ]
        )
        self.assertIsNotNone(partition)
        self.assertEqual(
            finalized["staged_calculation"]["finalized_plan"]["status"],
            STATUS_CURRENT,
        )
        self.assertTrue(partition["summary"]["materializable"])
        self.assertTrue(partition["finalization"]["certificate"]["certified"])
        self.assertEqual(
            [
                (
                    item["flat_item_id"],
                    item["rotation_deg_z"],
                    item["cut_origin_mm"],
                    item["cut_size_mm"],
                )
                for item in partition["top_inset_reservations"]["reservations"]
            ],
            [
                (
                    item["flat_item_id"],
                    item["rotation_deg_z"],
                    item["cut_origin_mm"],
                    item["cut_size_mm"],
                )
                for item in calculated["partition"]["top_inset_reservations"][
                    "reservations"
                ]
            ],
        )
        self.assertEqual(
            partition["finalization"]["selected_plan_source"],
            "f_xy_composite_v2_union_cavities_insets",
        )
        composite_certificate = partition["finalization"][
            "composite_materialization_certificate"
        ]
        self.assertTrue(composite_certificate["certified"])
        self.assertEqual(
            composite_certificate["printable_residual_volume_mm3"],
            0.0,
        )
        self.assertGreater(composite_certificate["joined_annex_count"], 0)
        self.assertTrue(partition["invariants"]["composite_annexes_applied"])
        self.assertEqual(cad["status"], "ready_for_fusion")
        self.assertEqual(cad["materialization"]["component_count"], 1)
        self.assertEqual(cad["materialization"]["composite_owner_count"], 1)
        self.assertGreater(
            cad["materialization"]["joined_composite_prism_count"],
            0,
        )
        self.assertGreater(cad["materialization"]["top_inset_cut_count"], 0)
        operations = cad["cad_ir"]["components"][0]["body"]["operations"]
        kinds = [value["kind"] for value in operations]
        first_cut = min(
            index for index, kind in enumerate(kinds) if kind.startswith("subtract_")
        )
        last_join = max(
            index for index, kind in enumerate(kinds) if kind == "join_rectangular_prism"
        )
        self.assertLess(last_join, first_cut)
        self.assertEqual(fusion.module_component_count, 1)
        self.assertEqual(
            len(fusion.additive_prism_joins),
            cad["materialization"]["joined_composite_prism_count"],
        )
        self.assertTrue(
            all(
                value.policy == "hybrid_xy_composite_v2"
                and value.attachment_axis in {"x", "y"}
                for value in fusion.additive_prism_joins
            )
        )
        self.assertEqual(
            len(
                [
                    value
                    for value in fusion.cavity_cuts
                    if value.cavity_source.startswith("top_inset")
                ]
            ),
            cad["materialization"]["top_inset_cut_count"],
        )

    def test_finishing_without_current_minimal_returns_explainable_result(
        self,
    ) -> None:
        project = _project()
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, _engine(project))

        result = session.finalize_volume(
            finishing_effort_profile="quick",
        )

        self.assertIsNone(result["partition"])
        self.assertEqual(
            result["solver_result"]["status"],
            "no_solution_within_budget",
        )
        diagnostics = result["solver_result"]["stop_diagnostics"]
        self.assertEqual(
            diagnostics["schema_version"],
            "bgig.finalization_stop_diagnostics.v1",
        )
        self.assertEqual(
            diagnostics["outcome_kind"],
            "prerequisite_missing",
        )
        self.assertEqual(diagnostics["phase"], "prerequis")
        self.assertEqual(diagnostics["elapsed_ms"], 0)
        self.assertEqual(diagnostics["budget_cap_ms"], 3_000)
        self.assertTrue(diagnostics["stopped_before_cap"])
        self.assertFalse(diagnostics["proof_of_impossibility"])
        self.assertEqual(
            result["staged_calculation"]["finalized_plan"][
                "finishing_effort_profile"
            ],
            "quick",
        )

    def test_total_finishing_timeout_preserves_exact_minimal_artifact(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        calculated = session.calculate_layout(
            request_id="solve-before-timeout",
            request_revision=0,
        )
        minimal = calculated["staged_calculation"]["minimal_layout"]
        minimal_value_digest = canonical_digest(session.current_minimal_partition())

        with patch(
            "board_game_insert_generator.coupled_finalization.perf_counter",
            side_effect=(0.0, 0.0, 0.0, 3.0),
        ):
            failed = session.finalize_volume(
                finishing_effort_profile="quick",
            )

        snapshot = failed["staged_calculation"]
        self.assertIsNone(failed["partition"])
        self.assertEqual(
            failed["solver_result"]["status"],
            "no_solution_within_budget",
        )
        self.assertEqual(
            failed["solver_result"]["telemetry"]["stop_reason"],
            "global_deadline_reached_before_final_certificate",
        )
        diagnostics = failed["solver_result"]["stop_diagnostics"]
        self.assertEqual(diagnostics["outcome_kind"], "deadline_reached")
        self.assertEqual(diagnostics["phase"], "certificat_final")
        self.assertEqual(diagnostics["budget_cap_ms"], 3_000)
        self.assertFalse(diagnostics["stopped_before_cap"])
        self.assertFalse(diagnostics["proof_of_impossibility"])
        self.assertEqual(
            failed["solver_result"]["telemetry"]["stop_diagnostics"],
            diagnostics,
        )
        self.assertEqual(snapshot["minimal_layout"]["status"], STATUS_CURRENT)
        self.assertEqual(
            snapshot["minimal_layout"]["artifact_digest"],
            minimal["artifact_digest"],
        )
        self.assertEqual(
            canonical_digest(session.current_minimal_partition()),
            minimal_value_digest,
        )
        self.assertEqual(snapshot["finalized_plan"]["status"], "not_finalized")
        self.assertEqual(
            snapshot["finalized_plan"]["last_attempt"][
                "finishing_effort_profile"
            ],
            "quick",
        )
        self.assertTrue(
            snapshot["finalized_plan"]["last_attempt"][
                "minimal_artifact_preserved"
            ]
        )
        self.assertEqual(
            snapshot["finalized_plan"]["last_attempt"]["stop_diagnostics"][
                "outcome_kind"
            ],
            "deadline_reached",
        )
        selection = session.select_materializable_artifact(
            ARTIFACT_KIND_MINIMAL
        )
        self.assertEqual(selection["artifact_digest"], minimal["artifact_digest"])

    def test_certified_witness_is_forwarded_as_recertified_fresh_search(self) -> None:
        project = _project()
        source_engine = _engine(project)
        source = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(source, project, source_engine)
        witness_plan = source.calculate_layout(request_id="source-witness", request_revision=0)[
            "partition"
        ]

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
        self.assertEqual(calculated["solver_result"]["status"], "solution_found")

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

    def test_source_change_during_finishing_rejects_stale_result(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        session.calculate_layout(request_id="solve-before-stale", request_revision=0)

        def stale_finalizer(plan: dict[str, object]) -> dict[str, object]:
            changed = deepcopy(project)
            changed["contents"][0]["quantity"] = 3
            changed_engine = _engine(changed)
            _synchronize(session, changed, changed_engine)
            return deepcopy(plan)

        stale = session.finalize_volume(
            finishing_effort_profile="long",
            finalizer=stale_finalizer,
            finishing_policy="test_stale_policy",
            finishing_budget_digest=canonical_digest({"budget": "long"}),
            finalizer_id="test-stale-finalizer",
            finalizer_version="1",
        )

        self.assertIsNone(stale["partition"])
        self.assertEqual(stale["solver_result"]["status"], "stale_or_cancelled")
        self.assertEqual(
            stale["solver_result"]["telemetry"]["stop_reason"],
            "finalization_result_stale",
        )
        snapshot = stale["staged_calculation"]
        self.assertEqual(snapshot["minimal_layout"]["status"], STATUS_STALE)
        self.assertNotEqual(snapshot["finalized_plan"]["status"], STATUS_CURRENT)
        self.assertFalse(snapshot["available_artifacts"][ARTIFACT_KIND_FINALIZED])
        self.assertFalse(
            snapshot["finalized_plan"]["last_attempt"]["partial_plan_published"]
        )
        self.assertTrue(
            snapshot["finalized_plan"]["last_attempt"][
                "minimal_artifact_preserved"
            ]
        )
        self.assertEqual(
            snapshot["finalized_plan"]["last_attempt"]["stop_diagnostics"][
                "outcome_kind"
            ],
            "stale",
        )

    def test_fixture_12_failed_finalization_preserves_minimal_materialization(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        calculated = session.calculate_layout(request_id="solve-1", request_revision=0)
        minimal_value_digest = canonical_digest(session.current_minimal_partition())

        def rejected_finalizer(plan: dict[str, object]) -> dict[str, object]:
            return deepcopy(plan)

        with self.assertRaisesRegex(StagedCalculationError, "a ete rejetee"):
            session.finalize_volume(
                finalizer=rejected_finalizer,
                finishing_policy="test_rejected_policy",
                finishing_budget_digest=canonical_digest({"budget": "test"}),
                finalizer_id="test-rejected-finalizer",
                finalizer_version="1",
            )

        selection = session.select_materializable_artifact(ARTIFACT_KIND_MINIMAL)
        snapshot = session.snapshot()
        self.assertEqual(snapshot["minimal_layout"]["status"], STATUS_CURRENT)
        self.assertEqual(
            snapshot["minimal_layout"]["artifact_digest"],
            calculated["staged_calculation"]["minimal_layout"]["artifact_digest"],
        )
        self.assertEqual(snapshot["finalized_plan"]["status"], "not_finalized")
        self.assertEqual(
            canonical_digest(session.current_minimal_partition()),
            minimal_value_digest,
        )
        self.assertTrue(
            snapshot["finalized_plan"]["last_attempt"][
                "minimal_artifact_preserved"
            ]
        )
        diagnostics = snapshot["finalized_plan"]["last_attempt"][
            "stop_diagnostics"
        ]
        self.assertEqual(diagnostics["outcome_kind"], "certificate_rejected")
        self.assertFalse(diagnostics["proof_of_impossibility"])
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

        self.assertEqual(
            finalized["staged_calculation"]["finalized_plan"]["status"], STATUS_CURRENT
        )
        self.assertEqual(selection["artifact_kind"], ARTIFACT_KIND_FINALIZED)
        self.assertNotEqual(
            selection["artifact_digest"],
            calculated["staged_calculation"]["minimal_layout"]["artifact_digest"],
        )
        self.assertEqual(
            session.select_materializable_artifact(ARTIFACT_KIND_MINIMAL)["partition_plan_digest"],
            calculated["partition"]["plan_digest"],
        )
        self.assertEqual(
            finalized["staged_calculation"]["finalized_plan"]["last_attempt"][
                "stop_diagnostics"
            ]["outcome_kind"],
            "success",
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
        calculated = session.calculate_layout(request_id="solve-case", request_revision=4)

        snapshot = session.solver_case_snapshot()

        self.assertEqual(
            snapshot["observed_partition"]["plan_digest"],
            calculated["partition"]["plan_digest"],
        )
        self.assertEqual(
            snapshot["current_minimal_partition"]["plan_digest"],
            calculated["partition"]["plan_digest"],
        )
        self.assertEqual(snapshot["staged_calculation"], calculated["staged_calculation"])
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
