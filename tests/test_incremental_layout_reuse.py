from __future__ import annotations

from copy import deepcopy
import unittest
from unittest.mock import patch

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.incremental_layout_reuse import (
    STATUS_GLOBAL_SOLVE_REQUIRED,
    STATUS_NOT_ATTEMPTED,
    STATUS_PLACEMENT_REUSED,
    attempt_incremental_minimal_layout_reuse,
)
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.partition_cad import build_partition_cad
from board_game_insert_generator.partition_solver import _digest as _partition_digest
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.staged_calculation import (
    ARTIFACT_KIND_MINIMAL,
    STATUS_CURRENT,
    STATUS_DESYNCHRONIZED,
    STATUS_STALE,
    StagedCalculationSession,
)


SETTINGS = {"method": "auto", "effort": "quick"}


def _content(
    identifier: str,
    dimensions: tuple[float, float, float],
) -> dict[str, object]:
    return {
        "id": identifier,
        "name": identifier.upper(),
        "shape_kind": "rectangle",
        "dimensions_mm": dict(zip(("x", "y", "z"), dimensions)),
        "quantity": 1,
        "container_group_id": "g",
        "content_clearance_mm": 0.0,
        "measurement_confidence": "exact",
    }


def _pocket_project() -> dict[str, object]:
    project = blank_project_v1()
    project["box"]["inner_dimensions_mm"] = {
        "x": 120.0,
        "y": 120.0,
        "z": 30.0,
    }
    project["box"]["usable_height_mm"] = 30.0
    project["container_groups"] = [
        {
            "id": "g",
            "name": "Bac",
            "wall_thickness_mm": 2.0,
            "floor_thickness_mm": 2.0,
        }
    ]
    project["contents"] = [
        _content("a", (40.0, 40.0, 10.0)),
        _content("b", (10.0, 20.0, 10.0)),
    ]
    return project


def _with_insert(
    project: dict[str, object],
    dimensions: tuple[float, float, float] = (8.0, 16.0, 8.0),
) -> dict[str, object]:
    changed = deepcopy(project)
    changed["contents"].append(_content("c", dimensions))
    return changed


def _engine(project: object) -> IncrementalLocalAnalysisEngine:
    return IncrementalLocalAnalysisEngine(project, effort_profile="quick")


def _solve(
    project: dict[str, object],
    engine: IncrementalLocalAnalysisEngine,
) -> dict[str, object]:
    return solve_minimal_layout(
        project,
        effort_profile="quick",
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )


def _world_signature(plan: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            key: deepcopy(placement[key])
            for key in (
                "id",
                "role",
                "origin_mm",
                "world_size_mm",
                "final_outer_dimensions_mm",
                "rotation_deg_z",
            )
        }
        for placement in sorted(plan["placements"], key=lambda value: value["id"])
    ]


def _cavity_origins(plan: dict[str, object]) -> dict[str, object]:
    placement = plan["placements"][0]
    return {
        value["cavity_id"]: deepcopy(value["local_origin_mm"])
        for value in placement["cavity_layout"]
    }


def _synchronize(
    session: StagedCalculationSession,
    project: dict[str, object],
    engine: IncrementalLocalAnalysisEngine,
) -> dict[str, object]:
    return session.synchronize(
        project,
        engine.snapshot(),
        solver_settings=SETTINGS,
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )


class IncrementalLayoutReuseTests(unittest.TestCase):
    def test_inserts_one_cavity_without_moving_world_or_existing_cavities(self) -> None:
        project = _pocket_project()
        initial_engine = _engine(project)
        initial = _solve(project, initial_engine)
        changed = _with_insert(project)
        changed_engine = _engine(changed)

        attempt = attempt_incremental_minimal_layout_reuse(
            project,
            changed,
            initial,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )

        self.assertEqual(attempt.report["status"], STATUS_PLACEMENT_REUSED)
        self.assertEqual(attempt.report["global_solver_invocation_count"], 0)
        self.assertEqual(attempt.report["local_recertification_attempt_count"], 1)
        self.assertFalse(attempt.report["world_placements_changed"])
        self.assertIsNotNone(attempt.partition)
        assert attempt.partition is not None
        self.assertEqual(_world_signature(initial), _world_signature(attempt.partition))
        before = _cavity_origins(initial)
        after = _cavity_origins(attempt.partition)
        self.assertEqual(after["compartment:a"], before["compartment:a"])
        self.assertEqual(after["compartment:b"], before["compartment:b"])
        self.assertEqual(
            after["compartment:c"],
            {"x": 44.0, "y": 24.0, "z": 2.0},
        )
        self.assertNotEqual(initial["plan_digest"], attempt.partition["plan_digest"])
        self.assertTrue(
            attempt.partition["minimal_layout"]["global_certificate"]["certified"]
        )
        self.assertTrue(
            attempt.partition["minimal_layout"]["container_variant_certificate"][
                "certified"
            ]
        )

    def test_reuse_is_deterministic_under_observable_caps(self) -> None:
        project = _pocket_project()
        engine = _engine(project)
        initial = _solve(project, engine)
        changed = _with_insert(project)
        changed_engine = _engine(changed)

        first = attempt_incremental_minimal_layout_reuse(
            project,
            changed,
            initial,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )
        second = attempt_incremental_minimal_layout_reuse(
            project,
            changed,
            initial,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )

        self.assertEqual(first.report, second.report)
        self.assertEqual(
            first.partition["plan_digest"] if first.partition else None,
            second.partition["plan_digest"] if second.partition else None,
        )
        self.assertLessEqual(
            first.report["counters"]["search_states"],
            first.report["budget"]["max_search_states_per_container"],
        )

    def test_too_large_insert_fails_closed_without_global_solve(self) -> None:
        project = _pocket_project()
        engine = _engine(project)
        initial = _solve(project, engine)
        changed = _with_insert(project, (20.0, 20.0, 10.0))
        changed_engine = _engine(changed)

        attempt = attempt_incremental_minimal_layout_reuse(
            project,
            changed,
            initial,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )

        self.assertIsNone(attempt.partition)
        self.assertEqual(attempt.report["status"], STATUS_GLOBAL_SOLVE_REQUIRED)
        self.assertEqual(attempt.report["global_solver_invocation_count"], 0)
        self.assertEqual(attempt.report["stop_reason"], "fixed_envelope_rejected")

    def test_global_dependency_change_is_not_attempted(self) -> None:
        project = _pocket_project()
        engine = _engine(project)
        initial = _solve(project, engine)
        changed = deepcopy(project)
        changed["box"]["inner_dimensions_mm"]["x"] = 121.0
        changed_engine = _engine(changed)

        attempt = attempt_incremental_minimal_layout_reuse(
            project,
            changed,
            initial,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )

        self.assertIsNone(attempt.partition)
        self.assertEqual(attempt.report["status"], STATUS_NOT_ATTEMPTED)
        self.assertEqual(attempt.report["stop_reason"], "global_dependency_changed")

    def test_tampered_source_certificate_or_digest_is_rejected(self) -> None:
        project = _pocket_project()
        engine = _engine(project)
        initial = _solve(project, engine)
        changed = _with_insert(project)
        changed_engine = _engine(changed)

        tampered_certificate = deepcopy(initial)
        tampered_certificate["minimal_layout"]["global_certificate"][
            "certified"
        ] = False
        certificate_payload = deepcopy(tampered_certificate)
        certificate_payload.pop("plan_digest")
        tampered_certificate["plan_digest"] = _partition_digest(
            certificate_payload
        )

        tampered_placement = deepcopy(initial)
        tampered_placement["placements"][0]["origin_mm"]["x"] += 1.0

        for label, source_plan in (
            ("certificate", tampered_certificate),
            ("plan_digest", tampered_placement),
        ):
            with self.subTest(label=label):
                attempt = attempt_incremental_minimal_layout_reuse(
                    project,
                    changed,
                    source_plan,
                    container_frontiers=changed_engine.certified_frontiers(),
                    effort_profile="quick",
                )

                self.assertIsNone(attempt.partition)
                self.assertEqual(
                    attempt.report["stop_reason"],
                    "source_plan_not_certified",
                )

    def test_new_container_requires_global_solve_instead_of_raising(self) -> None:
        project = _pocket_project()
        engine = _engine(project)
        initial = _solve(project, engine)
        changed = deepcopy(project)
        changed["container_groups"].append(
            {
                "id": "g2",
                "name": "Autre bac",
                "wall_thickness_mm": 2.0,
                "floor_thickness_mm": 2.0,
            }
        )
        content = _content("c", (8.0, 8.0, 8.0))
        content["container_group_id"] = "g2"
        changed["contents"].append(content)
        changed_engine = _engine(changed)

        attempt = attempt_incremental_minimal_layout_reuse(
            project,
            changed,
            initial,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )

        self.assertIsNone(attempt.partition)
        self.assertEqual(attempt.report["status"], STATUS_GLOBAL_SOLVE_REQUIRED)
        self.assertEqual(
            attempt.report["stop_reason"],
            "container_set_or_contract_changed",
        )

    def test_same_envelope_frontier_can_relayout_only_the_changed_container(self) -> None:
        project = _pocket_project()
        engine = _engine(project)
        initial = _solve(project, engine)
        changed = deepcopy(project)
        changed["contents"][0]["dimensions_mm"] = {
            "x": 10.0,
            "y": 20.0,
            "z": 10.0,
        }
        changed["contents"][1]["dimensions_mm"] = {
            "x": 40.0,
            "y": 40.0,
            "z": 10.0,
        }
        changed_engine = _engine(changed)

        attempt = attempt_incremental_minimal_layout_reuse(
            project,
            changed,
            initial,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )

        self.assertEqual(attempt.report["status"], STATUS_PLACEMENT_REUSED)
        self.assertEqual(
            attempt.report["selection_mode"],
            "same_envelope_frontier_fallback",
        )
        self.assertEqual(
            attempt.report["counters"]["same_envelope_frontier_fallbacks"],
            1,
        )
        self.assertEqual(
            attempt.report["counters"]["fixed_envelope_variants_certified"],
            0,
        )
        assert attempt.partition is not None
        self.assertEqual(_world_signature(initial), _world_signature(attempt.partition))
        self.assertNotEqual(_cavity_origins(initial), _cavity_origins(attempt.partition))
    def test_staged_session_promotes_reuse_without_calling_global_solver(self) -> None:
        project = _pocket_project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        calculated = session.calculate_layout(
            request_id="initial",
            request_revision=0,
        )
        initial_artifact = calculated["staged_calculation"]["minimal_layout"][
            "artifact_digest"
        ]

        def finalizer(plan: dict[str, object]) -> dict[str, object]:
            finalized = deepcopy(plan)
            finalized["summary"]["materializable"] = True
            finalized["finalization"] = {
                "artifact_kind": "finalized_plan",
                "source_minimal_artifact_digest": initial_artifact,
                "certificate": {"certified": True},
            }
            finalized.pop("plan_digest", None)
            finalized["plan_digest"] = canonical_digest(finalized)
            return finalized

        session.finalize_volume(
            finalizer=finalizer,
            finishing_policy="test-policy",
            finishing_budget_digest=canonical_digest({"budget": "test"}),
            finalizer_id="test-finalizer",
            finalizer_version="1",
        )
        selection = session.select_materializable_artifact(ARTIFACT_KIND_MINIMAL)
        cad = build_partition_cad(
            project,
            partition=selection["partition"],
            artifact_identity=selection,
            effort_profile="quick",
        )
        session.record_cad_ready(cad)

        changed = _with_insert(project)
        changed_engine = _engine(changed)
        with patch(
            "board_game_insert_generator.minimal_layout_solver.solve_minimal_layout",
            side_effect=AssertionError("global solver must stay explicit"),
        ):
            snapshot = _synchronize(session, changed, changed_engine)

        self.assertEqual(snapshot["minimal_layout"]["status"], STATUS_CURRENT)
        self.assertTrue(snapshot["minimal_layout"]["placement_certified"])
        self.assertNotEqual(
            snapshot["minimal_layout"]["artifact_digest"],
            initial_artifact,
        )
        self.assertEqual(
            snapshot["minimal_layout"]["cache_status"],
            "local_reuse_not_cached",
        )
        self.assertEqual(
            snapshot["local_reuse"]["status"],
            STATUS_PLACEMENT_REUSED,
        )
        self.assertEqual(
            snapshot["local_reuse"]["global_solver_invocation_count"],
            0,
        )
        self.assertEqual(
            snapshot["materialization"]["status"],
            STATUS_DESYNCHRONIZED,
        )
        self.assertEqual(snapshot["finalized_plan"]["status"], STATUS_STALE)
        self.assertIsNotNone(session.current_minimal_partition())

    def test_staged_failure_keeps_old_plan_stale(self) -> None:
        project = _pocket_project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        _synchronize(session, project, engine)
        session.calculate_layout(request_id="initial", request_revision=0)

        changed = _with_insert(project, (20.0, 20.0, 10.0))
        changed_engine = _engine(changed)
        snapshot = _synchronize(session, changed, changed_engine)

        self.assertEqual(snapshot["minimal_layout"]["status"], STATUS_STALE)
        self.assertEqual(
            snapshot["local_reuse"]["status"],
            STATUS_GLOBAL_SOLVE_REQUIRED,
        )
        self.assertEqual(snapshot["next_action"], "calculate_layout")
        self.assertIsNone(session.current_minimal_partition())


if __name__ == "__main__":
    unittest.main()
