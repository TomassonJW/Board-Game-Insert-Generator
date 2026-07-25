from __future__ import annotations

import unittest

from board_game_insert_generator.free_3d_beam_solver import (
    BEAM_SEARCH_BRIDGE_EMS,
    BEAM_SEARCH_LEGACY_EMS,
)
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.solver_portfolio import (
    EFFORT_NORMAL,
    _beam_search_runs,
    portfolio_effort_profiles,
    solve_partition_portfolio,
)
from p64_h04_fixture_cases import h01_dense_project, h02_reservations_project


def _two_level_project() -> dict[str, object]:
    project = blank_project_v1()
    project["box"] = {
        "inner_dimensions_mm": {"x": 50.0, "y": 50.0, "z": 80.0},
        "usable_height_mm": 80.0,
        "lid_clearance_mm": 0.0,
    }
    project["container_groups"] = [
        {"id": "a", "name": "Bac A", "wall_thickness_mm": None, "floor_thickness_mm": None},
        {"id": "b", "name": "Bac B", "wall_thickness_mm": None, "floor_thickness_mm": None},
    ]
    project["contents"] = [
        {
            "id": "asset-a",
            "name": "Asset A",
            "shape_kind": "custom",
            "dimensions_mm": {"x": 32.0, "y": 32.0, "z": 20.0},
            "quantity": 1,
            "container_group_id": "a",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        },
        {
            "id": "asset-b",
            "name": "Asset B",
            "shape_kind": "custom",
            "dimensions_mm": {"x": 32.0, "y": 32.0, "z": 20.0},
            "quantity": 1,
            "container_group_id": "b",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        },
    ]
    return project


class SolverPortfolioTests(unittest.TestCase):
    def test_effort_profiles_are_monotone_and_never_remove_a_family(self) -> None:
        profiles = portfolio_effort_profiles()

        self.assertEqual(
            [value.profile_id for value in profiles],
            ["quick", "short", "normal", "long", "deep"],
        )
        for previous, current in zip(profiles, profiles[1:]):
            self.assertTrue(current.is_at_least_as_permissive_as(previous))
            self.assertEqual(previous.allowed_family_ids, current.allowed_family_ids)
        expected_branches = [1, 1, 2, 3, 4]
        for profile, maximum in zip(profiles, expected_branches):
            runs = _beam_search_runs(profile)
            self.assertEqual(
                tuple(search_variant for _, search_variant in runs),
                (BEAM_SEARCH_LEGACY_EMS, BEAM_SEARCH_BRIDGE_EMS),
            )
            self.assertEqual(dict(runs[0][0].limits)["max_participant_branches"], 1)
            self.assertEqual(
                dict(runs[1][0].limits)["max_participant_branches"],
                maximum,
            )
    def test_simple_stage_solution_keeps_the_fast_path(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {"id": "only", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}
        ]
        project["contents"] = [
            {
                "id": "asset",
                "name": "Asset",
                "shape_kind": "custom",
                "dimensions_mm": {"x": 20.0, "y": 20.0, "z": 10.0},
                "quantity": 1,
                "container_group_id": "only",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
        ]

        execution = solve_partition_portfolio(project, effort_profile=EFFORT_NORMAL)

        self.assertEqual(execution.status, "solution_found")
        self.assertTrue(execution.fast_path_used)
        self.assertEqual(execution.selected_family_id, "stage_stack")
        self.assertTrue(execution.certified_candidates[0].certificate.certified)
        self.assertTrue(all(report.skipped_by_fast_path for report in execution.family_reports[1:]))

    def test_non_trivial_auto_keeps_only_envelope_certified_families(self) -> None:
        execution = solve_partition_portfolio(_two_level_project(), effort_profile=EFFORT_NORMAL)

        self.assertEqual(execution.status, "solution_found")
        self.assertFalse(execution.fast_path_used)
        self.assertEqual(
            tuple(report.family_id for report in execution.family_reports),
            ("stage_stack", "free_3d_greedy", "free_3d_beam"),
        )
        beam_report = execution.family_reports[2]
        self.assertGreater(beam_report.certified_candidate_count, 0)
        self.assertEqual(beam_report.status, "solution_found")
        self.assertTrue(execution.certified_candidates)
        self.assertTrue(
            all(value.certificate.certified for value in execution.certified_candidates)
        )
        self.assertTrue(execution.selected_plan["summary"]["materializable"])

    def test_cancellation_before_search_is_not_painted_as_a_current_failure(self) -> None:
        execution = solve_partition_portfolio(
            _two_level_project(),
            effort_profile=EFFORT_NORMAL,
            cancel_check=lambda: True,
        )

        self.assertEqual(execution.status, "stale_or_cancelled")
        self.assertIsNone(execution.selected_plan)
        self.assertTrue(
            all(report.status == "stale_or_cancelled" for report in execution.family_reports)
        )

    def test_h04_dense_corpus_keeps_only_envelope_certified_candidates(self) -> None:
        accepted = solve_partition_portfolio(
            h01_dense_project(),
            effort_profile=EFFORT_NORMAL,
        )
        rejected = solve_partition_portfolio(
            h02_reservations_project(),
            effort_profile=EFFORT_NORMAL,
        )

        self.assertEqual(accepted.status, "solution_found")
        self.assertIsNotNone(accepted.selected_plan)
        self.assertTrue(accepted.certified_candidates)
        self.assertTrue(
            all(value.certificate.certified for value in accepted.certified_candidates)
        )
        self.assertEqual(rejected.status, "solution_found")
        self.assertIsNotNone(rejected.selected_plan)
        self.assertTrue(rejected.certified_candidates)
        self.assertTrue(
            all(value.certificate.certified for value in rejected.certified_candidates)
        )


if __name__ == "__main__":
    unittest.main()
