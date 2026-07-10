from __future__ import annotations
import unittest
from context import ROOT
from board_game_insert_generator.box_fill_solver import BoxFillCandidate, BoxFillSolveRequest, solve_box_fill_greedy
from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.models import Dimension3D

class GreedyBoxFillTests(unittest.TestCase):
    def test_places_candidates_deterministically_without_moving_lock(self):
        config = load_config(ROOT / 'examples' / 'box_fill_valid_v0.json')
        assert config.box_fill_plan is not None
        request = BoxFillSolveRequest(config.box_fill_plan, (BoxFillCandidate('auto-small', 'Auto small', Dimension3D(10, 10, 10), allowed_layer_ids=('base-layer',), allow_xy_rotation=True),))
        first, second = solve_box_fill_greedy(request), solve_box_fill_greedy(request)
        self.assertEqual(first.status, 'solved')
        self.assertEqual(first.solver_result_digest, second.solver_result_digest)
        self.assertEqual(first.solved_plan.modules[0].origin, config.box_fill_plan.modules[0].origin)
        self.assertEqual(first.placements[0].module_id, 'auto-small')

    def test_refuses_candidate_taller_than_layer(self):
        config = load_config(ROOT / 'examples' / 'box_fill_valid_v0.json')
        assert config.box_fill_plan is not None
        result = solve_box_fill_greedy(BoxFillSolveRequest(config.box_fill_plan, (BoxFillCandidate('too-tall', 'Too tall', Dimension3D(10, 10, 50), allowed_layer_ids=('base-layer',)),)))
        self.assertEqual(result.status, 'blocked')
        self.assertEqual(result.diagnostics[0].code, 'no_layer_with_sufficient_height')

if __name__ == '__main__': unittest.main()
