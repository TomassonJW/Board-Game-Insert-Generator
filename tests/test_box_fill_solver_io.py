from __future__ import annotations
import unittest
from context import ROOT
from board_game_insert_generator.box_fill_solver import solve_box_fill_greedy
from board_game_insert_generator.box_fill_solver_io import load_box_fill_solve_request, solve_request_from_executable_asset_plan
from board_game_insert_generator.config_loader import load_config

class BoxFillSolverIoTests(unittest.TestCase):
    def test_loads_request_and_preserves_determinism(self):
        request = load_box_fill_solve_request(ROOT / 'examples' / 'p20' / 'greedy_valid_simple.json')
        self.assertEqual(solve_box_fill_greedy(request).status, 'solved')

    def test_rotation_fixture_places_rotated_candidate(self):
        result = solve_box_fill_greedy(load_box_fill_solve_request(ROOT / 'examples' / 'p20' / 'rotation_required.json'))
        self.assertEqual(result.placements[0].orientation, 'rotated_90_z')

    def test_bridge_keeps_asset_first_provenance(self):
        request = solve_request_from_executable_asset_plan(load_config(ROOT / 'examples' / 'simple_asset_executable_plan.json'))
        self.assertEqual(request.source_plan.metadata['source'], 'derived_from_executable_asset_plan')
        self.assertTrue(all(item.source == 'derived_from_executable_asset_plan' for item in request.candidates))

if __name__ == '__main__': unittest.main()
