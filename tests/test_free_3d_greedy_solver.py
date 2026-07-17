from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.expandable_envelope import derive_expandable_envelope_contract
from board_game_insert_generator.free_3d_greedy_solver import (
    FREE_3D_GREEDY_FAMILY_ID,
    EmptySpace,
    Free3DGreedyError,
    TopInsetZone,
    _initial_extreme_points,
    _top_inset_option_allowed,
    solve_free_3d_greedy,
)
from board_game_insert_generator.partition_solver import (
    _container_participant,
    _solver_clearance_fallbacks,
)
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.solver_contract import SolverBudget
from board_game_insert_generator.top_inset_reservation import derive_top_inset_reservations
from p64_h04_fixture_cases import (
    h01_dense_project,
    h02_reservations_project,
    simple_success_project,
)


def _budget(**overrides: int) -> SolverBudget:
    limits = {
        "max_empty_spaces": 4096,
        "max_extreme_points": 4096,
        "max_placement_trials": 2_000_000,
        "max_search_states": 256,
    }
    limits.update(overrides)
    return SolverBudget(
        FREE_3D_GREEDY_FAMILY_ID,
        "h06-laboratory",
        tuple(sorted(limits.items())),
    )


def _participant(
    identifier: str,
    size: tuple[float, float, float],
) -> dict[str, object]:
    dimensions = dict(zip(("x", "y", "z"), size))
    return {
        "id": identifier,
        "role": "container",
        "name": identifier,
        "minimum_local_mm": dimensions,
        "dimension_modes": {"x": "auto", "y": "auto", "z": "auto"},
        "target_local_mm": {"x": None, "y": None, "z": None},
        "surplus_preference": "balanced",
    }


def _h04_problem(project: dict[str, object]) -> tuple[object, ...]:
    normalized = normalize_project_draft(project).project
    top_insets = derive_top_inset_reservations(normalized)
    storage_height = float(top_insets["design_top_z_mm"])
    box = deepcopy(normalized["box"]["inner_dimensions_mm"])
    envelope = derive_expandable_envelope_contract(
        normalized,
        max_container_height_mm=max(storage_height, 0.001),
    )
    groups = {str(value["id"]): value for value in normalized["container_groups"]}
    default_floor = float(normalized["layout"]["default_floor_thickness_mm"])
    participants = [
        _container_participant(
            contract,
            groups[str(contract["container_group_id"])],
            top_inset_plan=top_insets,
            default_floor_mm=default_floor,
            storage_height_mm=storage_height,
        )
        for contract in envelope["containers"]
        if contract["status"] == "ready"
    ]
    layout = normalized["layout"]
    clearances = _solver_clearance_fallbacks(
        participants,
        float(layout["layout_clearance_mm"]),
        float(layout["container_box_xy_clearance_mm"]),
        float(layout["container_z_clearance_mm"]),
    )
    return participants, box, storage_height, clearances


class Free3DGreedySolverTests(unittest.TestCase):
    def test_h04_corpus_is_packed_with_one_canonical_envelope_per_container(self) -> None:
        for fixture in (simple_success_project, h01_dense_project, h02_reservations_project):
            with self.subTest(fixture=fixture.__name__):
                participants, box, storage_height, clearances = _h04_problem(fixture())
                execution = solve_free_3d_greedy(
                    participants,
                    box,
                    storage_height,
                    clearances[0],
                    box_perimeter_xy_mm=clearances[1],
                    between_bodies_z_mm=clearances[2],
                    budget=_budget(),
                )

                self.assertEqual(execution.status, "solution_found")
                self.assertEqual(len(execution.placements), len(participants))
                self.assertIsNotNone(execution.candidate)
                self.assertIsNotNone(execution.geometry_admission)
                self.assertTrue(execution.geometry_admission.admitted)
                self.assertEqual(execution.geometry_admission.rejection_codes, ())

    def test_top_inset_boundaries_are_seeded_and_only_overlapping_cavities_add_depth(self) -> None:
        spaces = (EmptySpace((0.6, 0.6, 0.0), (248.8, 178.8, 69.8)),)
        seed_zone = TopInsetZone((9.4, 9.4), (116.2, 111.2), 60.8, 9.0)
        points = _initial_extreme_points(spaces, (seed_zone,))
        self.assertIn((125.6, 0.6, 0.0), points)
        self.assertIn((0.6, 120.6, 0.0), points)

        participant = _participant("localized", (80.0, 80.0, 65.0))
        participant["top_inset_search_hint_v1"] = {
            "floor_thickness_mm": 1.2,
            "cavities": [
                {
                    "local_origin_mm": {"x": 1.2, "y": 1.2, "z": 1.2},
                    "inner_dimensions_mm": {"x": 20.0, "y": 20.0, "z": 63.8},
                }
            ],
        }
        clear_solid_zone = TopInsetZone((60.0, 60.0), (10.0, 10.0), 60.0, 9.0)
        overlapping_cavity_zone = TopInsetZone((10.0, 10.0), (10.0, 10.0), 60.0, 9.0)
        self.assertTrue(
            _top_inset_option_allowed(
                participant, (0.0, 0.0, 0.0), (80.0, 80.0, 65.0), 0, 69.8, (clear_solid_zone,)
            )
        )
        self.assertFalse(
            _top_inset_option_allowed(
                participant, (0.0, 0.0, 0.0), (80.0, 80.0, 65.0), 0, 69.8, (overlapping_cavity_zone,)
            )
        )

    def test_localized_top_inset_uses_centered_cavity_after_rotation_and_growth(self) -> None:
        participant = _participant("rotated", (80.0, 60.0, 65.0))
        participant["top_inset_search_hint_v1"] = {
            "floor_thickness_mm": 1.2,
            "cavities": [
                {
                    "local_origin_mm": {"x": 1.0, "y": 1.0, "z": 1.2},
                    "inner_dimensions_mm": {"x": 20.0, "y": 20.0, "z": 63.8},
                }
            ],
        }
        zone = TopInsetZone((60.0, 12.0), (8.0, 8.0), 60.0, 9.0)

        self.assertFalse(
            _top_inset_option_allowed(
                participant,
                (0.0, 0.0, 0.0),
                (100.0, 100.0, 65.0),
                90,
                69.8,
                (zone,),
            )
        )

    def test_one_body_can_cross_a_neighbours_local_z_plane(self) -> None:
        participants = [
            _participant("a-tall", (50.0, 60.0, 45.0)),
            _participant("b-lower", (50.0, 60.0, 35.0)),
            _participant("c-crossing", (50.0, 60.0, 20.0)),
        ]
        execution = solve_free_3d_greedy(
            participants,
            {"x": 100.0, "y": 60.0, "z": 60.0},
            60.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
        )

        self.assertEqual(execution.status, "solution_found")
        tall = next(value for value in execution.placements if value.participant_id == "a-tall")
        crossing = next(value for value in execution.placements if value.participant_id == "c-crossing")
        tall_top = tall.origin_mm[2] + tall.world_size_mm[2]
        self.assertLess(crossing.origin_mm[2], tall_top)
        self.assertGreater(crossing.origin_mm[2] + crossing.world_size_mm[2], tall_top)

    def test_upper_body_can_be_supported_by_multiple_lower_bodies(self) -> None:
        participants = [
            _participant("a-lower", (20.0, 20.0, 60.0)),
            _participant("b-lower", (20.0, 20.0, 60.0)),
            _participant("z-upper", (100.0, 20.0, 10.0)),
        ]
        execution = solve_free_3d_greedy(
            participants,
            {"x": 100.0, "y": 20.0, "z": 100.0},
            100.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
        )

        self.assertEqual(execution.status, "solution_found")
        upper = next(value for value in execution.placements if value.participant_id == "z-upper")
        self.assertGreater(upper.origin_mm[2], 0.0)
        self.assertEqual(upper.supporting_ids, ("a-lower", "b-lower"))
        self.assertAlmostEqual(upper.support_coverage_ratio, 0.4)

    def test_execution_is_deterministic_and_deduplicates_ems_and_points(self) -> None:
        participants = [
            _participant("a", (30.0, 20.0, 10.0)),
            _participant("b", (20.0, 30.0, 10.0)),
            _participant("c", (15.0, 15.0, 15.0)),
        ]
        arguments = (
            participants,
            {"x": 80.0, "y": 60.0, "z": 40.0},
            40.0,
            0.5,
        )
        first = solve_free_3d_greedy(
            *arguments,
            box_perimeter_xy_mm=1.0,
            between_bodies_z_mm=0.5,
            budget=_budget(),
        )
        second = solve_free_3d_greedy(
            *arguments,
            box_perimeter_xy_mm=1.0,
            between_bodies_z_mm=0.5,
            budget=_budget(),
        )

        self.assertEqual(first, second)
        self.assertEqual(first.deterministic_digest, second.deterministic_digest)
        self.assertEqual(len(first.empty_spaces), len(set(first.empty_spaces)))
        self.assertEqual(len(first.extreme_points_mm), len(set(first.extreme_points_mm)))
        self.assertGreater(first.telemetry.empty_spaces_deduplicated, 0)
        changed = deepcopy(participants)
        changed[0]["name"] = "same-geometry-different-input"
        third = solve_free_3d_greedy(
            changed,
            arguments[1],
            arguments[2],
            arguments[3],
            box_perimeter_xy_mm=1.0,
            between_bodies_z_mm=0.5,
            budget=_budget(),
        )
        self.assertNotEqual(first.candidate.plan_digest, third.candidate.plan_digest)

    def test_hard_budget_never_becomes_a_proven_impossibility(self) -> None:
        execution = solve_free_3d_greedy(
            [_participant("a", (10.0, 10.0, 10.0)), _participant("b", (10.0, 10.0, 10.0))],
            {"x": 100.0, "y": 100.0, "z": 100.0},
            100.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(max_placement_trials=1),
        )

        self.assertEqual(execution.status, "no_solution_within_budget")
        self.assertEqual(execution.stop_reason, "hard_budget_reached")
        self.assertTrue(execution.telemetry.budget_exhausted)
        self.assertIsNone(execution.candidate)

    def test_only_necessary_bounds_can_report_proven_impossible(self) -> None:
        execution = solve_free_3d_greedy(
            [_participant("too-wide", (110.0, 10.0, 10.0))],
            {"x": 100.0, "y": 100.0, "z": 100.0},
            100.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
        )

        self.assertEqual(execution.status, "proven_impossible")
        self.assertIn("minimum_envelope_exceeds_axis", execution.stop_reason)

    def test_fixed_axis_uses_its_explicit_target_dimension(self) -> None:
        participant = _participant("fixed-x", (10.0, 10.0, 10.0))
        participant["dimension_modes"]["x"] = "fixed"
        participant["target_local_mm"]["x"] = 30.0
        execution = solve_free_3d_greedy(
            [participant],
            {"x": 40.0, "y": 40.0, "z": 40.0},
            40.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
        )

        self.assertEqual(execution.status, "solution_found")
        self.assertEqual(execution.placements[0].local_size_mm, (30.0, 10.0, 10.0))

    def test_budget_requires_every_hard_limit_and_the_correct_family(self) -> None:
        participant = [_participant("a", (10.0, 10.0, 10.0))]
        with self.assertRaisesRegex(Free3DGreedyError, "Missing hard budget"):
            solve_free_3d_greedy(
                participant,
                {"x": 20.0, "y": 20.0, "z": 20.0},
                20.0,
                0.0,
                box_perimeter_xy_mm=0.0,
                between_bodies_z_mm=0.0,
                budget=SolverBudget(FREE_3D_GREEDY_FAMILY_ID, "test", (("max_search_states", 1),)),
            )


if __name__ == "__main__":
    unittest.main()
