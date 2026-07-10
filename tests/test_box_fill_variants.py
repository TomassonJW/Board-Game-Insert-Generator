from __future__ import annotations
import unittest
from context import ROOT
from board_game_insert_generator.box_fill_solver_io import load_box_fill_solve_request
from board_game_insert_generator.box_fill_variants import BoxFillVariantRequest, VariantPreferenceProfile, generate_box_fill_variants

class BoxFillVariantsTests(unittest.TestCase):
    def test_portfolio_is_deterministic_and_never_recommends_blocked(self):
        request = BoxFillVariantRequest(load_box_fill_solve_request(ROOT / 'examples' / 'p20' / 'greedy_valid_simple.json'))
        first = generate_box_fill_variants(request)
        second = generate_box_fill_variants(request)
        self.assertEqual(first.digest, second.digest)
        self.assertEqual(first.schema_version, 'box_fill_variants.v0')
        self.assertIsNotNone(first.recommended_variant_id)
        self.assertTrue(all(item.result.status == 'solved' for item in first.variants))

if __name__ == '__main__': unittest.main()
