from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.solver_case_bundle import build_solver_case_bundle
from board_game_insert_generator.solver_case_corpus import (
    CORPUS_TIER_CI,
    CORPUS_TIER_EXTENDED,
    SOLVER_CASE_CORPUS_SCHEMA_V1,
    SolverCaseCorpusError,
    anonymize_solver_case_project,
    build_solver_case,
    build_solver_case_corpus,
    compare_solver_case_replays,
    replay_solver_case_corpus,
    solver_case_from_bundle,
    validate_solver_case_bundle,
    validate_solver_case_corpus,
)
from board_game_insert_generator.solver_outcome import (
    NO_SOLUTION_WITHIN_BUDGET,
    SOLUTION_FOUND,
)
from p64_h04_fixture_cases import simple_success_project


class _Clock:
    def __init__(self, values: list[float]) -> None:
        self._values = iter(values)

    def __call__(self) -> float:
        return next(self._values)


class SolverCaseCorpusTests(unittest.TestCase):
    def test_manifest_is_deterministic_canonical_and_fail_closed(self) -> None:
        case = build_solver_case(
            "simple-quick",
            simple_success_project(),
            solver_settings={"method": "auto", "effort": "quick"},
            accepted_statuses=(SOLUTION_FOUND,),
            source={"kind": "fixture", "id": "simple_success_project"},
        )
        first = build_solver_case_corpus([case])
        second = build_solver_case_corpus([deepcopy(case)])

        self.assertEqual(first, second)
        self.assertEqual(first["schema_version"], SOLVER_CASE_CORPUS_SCHEMA_V1)
        self.assertEqual(validate_solver_case_corpus(first), first)
        self.assertEqual(first["summary"]["ci_case_count"], 1)
        self.assertTrue(first["invariants"]["functional_evidence_deterministic"])
        self.assertTrue(first["invariants"]["wall_clock_samples_non_normative"])

        tampered = deepcopy(first)
        tampered["cases"][0]["project"]["project_name"] = "tampered"
        with self.assertRaisesRegex(SolverCaseCorpusError, "digest mismatch"):
            validate_solver_case_corpus(tampered)
        with self.assertRaisesRegex(SolverCaseCorpusError, "unique"):
            build_solver_case_corpus([case, case])

    def test_bundle_import_validates_every_digest_and_drops_trace_values(self) -> None:
        project = simple_success_project()
        engine = IncrementalLocalAnalysisEngine(project, effort_profile="quick")
        bundle = build_solver_case_bundle(
            project,
            solver_settings={"method": "auto", "effort": "quick"},
            solver_case_state={
                "staged_calculation": {
                    "minimal_layout": {
                        "solver_result_status": NO_SOLUTION_WITHIN_BUDGET,
                        "stop_reason": "captured_limit",
                    }
                }
            },
            local_analysis=engine.snapshot(),
            container_frontiers=engine.certified_frontiers(),
            interaction_events=[{"event_type": "ui_action", "action": "solve_project"}],
            client_context={},
            capture_id="capture-corpus",
            captured_at_ms=1,
            source_revision=2,
        )
        validated = validate_solver_case_bundle(bundle)
        case = solver_case_from_bundle(
            bundle,
            case_id="captured-limit",
            execution_tier=CORPUS_TIER_EXTENDED,
        )

        self.assertEqual(validated["bundle_digest"], bundle["bundle_digest"])
        self.assertEqual(case["source"]["kind"], "solver_case_bundle")
        self.assertEqual(case["source"]["bundle_digest"], bundle["bundle_digest"])
        self.assertNotIn("interaction_trace", case)
        self.assertNotIn("client_context", case)
        self.assertEqual(
            case["expectations"]["accepted_statuses"],
            [SOLUTION_FOUND, NO_SOLUTION_WITHIN_BUDGET],
        )
        tampered = deepcopy(bundle)
        tampered["local_analysis"]["status"] = "tampered"
        with self.assertRaisesRegex(SolverCaseCorpusError, "digest mismatch"):
            validate_solver_case_bundle(tampered)

    def test_anonymizes_project_labels_identifiers_and_deferred_metadata(self) -> None:
        project = simple_success_project()
        project["project_name"] = "Projet personnel PrivateOwner"
        project["container_groups"][0]["id"] = "container-private"
        project["container_groups"][0]["name"] = "Bac personnel"
        project["contents"][0]["id"] = "content-private"
        project["contents"][0]["name"] = "Pièce personnelle"
        project["contents"][0]["container_group_id"] = "container-private"
        project["flat_items"] = [
            {
                "id": "flat-private",
                "name": "Livret personnel",
                "kind": "rulebook",
                "dimensions_mm": {"x": 80.0, "y": 60.0, "z": 2.0},
                "quantity": 1,
                "stack_order": 0,
                "origin_mm": None,
                "rotation_deg_z": None,
            }
        ]
        project["fill_elements"] = [
            {
                "id": "fill-private",
                "name": "Cale personnelle",
                "kind": "separator",
                "mode": "exact",
                "dimensions_mm": {"x": 1.0, "y": 2.0, "z": 3.0},
                "container_group_id": "container-private",
            }
        ]
        project["deferred_features"] = {
            "appearance": {"personal_label": "PrivateOwner"},
            "mechanism": None,
        }
        original = deepcopy(project)

        anonymized = anonymize_solver_case_project(project)
        rendered = json.dumps(anonymized, ensure_ascii=False, sort_keys=True)

        self.assertEqual(project, original)
        self.assertEqual(anonymized["project_name"], "Cas solveur anonymisé")
        self.assertEqual(anonymized["container_groups"][0]["id"], "container-001")
        self.assertEqual(anonymized["contents"][0]["id"], "content-001")
        self.assertEqual(
            anonymized["contents"][0]["container_group_id"],
            "container-001",
        )
        self.assertEqual(anonymized["flat_items"][0]["id"], "flat-001")
        self.assertEqual(anonymized["fill_elements"][0]["id"], "fill-001")
        self.assertEqual(
            anonymized["fill_elements"][0]["container_group_id"],
            "container-001",
        )
        self.assertEqual(
            anonymized["contents"][0]["dimensions_mm"],
            original["contents"][0]["dimensions_mm"],
        )
        self.assertEqual(
            anonymized["deferred_features"],
            {"appearance": None, "mechanism": None},
        )
        for personal_value in (
            "PrivateOwner",
            "container-private",
            "content-private",
            "flat-private",
            "fill-private",
        ):
            self.assertNotIn(personal_value, rendered)

    def test_functional_digest_excludes_observed_wall_clock_samples(self) -> None:
        project = simple_success_project()
        partition = solve_minimal_layout(project, effort_profile="quick")
        corpus = build_solver_case_corpus(
            [
                build_solver_case(
                    "simple-quick",
                    project,
                    solver_settings={"method": "auto", "effort": "quick"},
                    accepted_statuses=(SOLUTION_FOUND,),
                )
            ]
        )

        first = replay_solver_case_corpus(
            corpus,
            repetitions=2,
            solver=lambda *_args, **_kwargs: deepcopy(partition),
            clock=_Clock([0.0, 0.010, 1.0, 1.030]),
        )
        second = replay_solver_case_corpus(
            corpus,
            repetitions=2,
            solver=lambda *_args, **_kwargs: deepcopy(partition),
            clock=_Clock([0.0, 0.100, 1.0, 1.200]),
        )

        self.assertEqual(first["functional_digest"], second["functional_digest"])
        self.assertNotEqual(
            first["cases"][0]["performance"],
            second["cases"][0]["performance"],
        )
        self.assertTrue(first["summary"]["all_expectations_met"])
        self.assertEqual(first["cases"][0]["performance"]["sample_count"], 2)

    def test_ab_comparison_rejects_functional_loss_before_timing_gain(self) -> None:
        project = simple_success_project()
        partition = solve_minimal_layout(project, effort_profile="quick")
        corpus = build_solver_case_corpus(
            [
                build_solver_case(
                    "simple-quick",
                    project,
                    solver_settings={"method": "auto", "effort": "quick"},
                    accepted_statuses=(SOLUTION_FOUND,),
                )
            ]
        )
        slower = replay_solver_case_corpus(
            corpus,
            solver=lambda *_args, **_kwargs: deepcopy(partition),
            clock=_Clock([0.0, 0.100]),
        )
        faster = replay_solver_case_corpus(
            corpus,
            solver=lambda *_args, **_kwargs: deepcopy(partition),
            clock=_Clock([0.0, 0.010]),
        )
        accepted = compare_solver_case_replays(
            slower,
            faster,
            maximum_performance_regression_ratio=0.0,
        )
        regressed = deepcopy(faster)
        regressed["cases"][0]["functional"]["status"] = NO_SOLUTION_WITHIN_BUDGET
        regressed["cases"][0]["functional"]["certificate_certified"] = False
        rejected = compare_solver_case_replays(
            slower,
            regressed,
            maximum_performance_regression_ratio=0.0,
        )

        self.assertTrue(accepted["summary"]["candidate_acceptable"])
        self.assertLess(accepted["summary"]["candidate_to_baseline_ratio"], 1.0)
        self.assertFalse(rejected["summary"]["candidate_acceptable"])
        self.assertEqual(rejected["summary"]["functional_regression_count"], 1)
        self.assertIn(
            "known_solution_lost",
            rejected["cases"][0]["regression_reasons"],
        )

    def test_checked_in_ci_corpus_records_solutions_and_honest_limits(self) -> None:
        path = Path(__file__).resolve().parent / "fixtures" / "p64_l05d_solver_case_corpus.v1.json"
        corpus = json.loads(path.read_text(encoding="utf-8"))
        validated = validate_solver_case_corpus(corpus)
        report = replay_solver_case_corpus(
            validated,
            include_tiers=(CORPUS_TIER_CI,),
        )

        self.assertEqual(
            validated["corpus_digest"],
            "409c75095c47c4ca85a6dda469e986d36d67d460bf308ac9a96e1d3898ac26cf",
        )
        self.assertEqual(
            report["functional_digest"],
            "3aacd2eb29edf4414190bd0622c3b5539b6579430d5800bfbe52cd2419250338",
        )
        self.assertTrue(report["summary"]["all_expectations_met"])
        self.assertEqual(report["summary"]["executed_case_count"], 5)
        self.assertEqual(report["summary"]["solution_found_count"], 2)
        self.assertEqual(report["summary"]["no_solution_within_budget_count"], 3)
        for result in report["cases"]:
            self.assertTrue(result["comparison"]["checks"]["lane_prefix_exact"])
            self.assertEqual(
                result["comparison"]["baseline_transition"],
                "stable",
            )
            self.assertEqual(
                result["performance"]["kind"],
                "observed_wall_clock_non_normative",
            )


if __name__ == "__main__":
    unittest.main()
