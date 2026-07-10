from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from context import ROOT

from board_game_insert_generator.box_fill_solver_io import load_box_fill_solve_request
from board_game_insert_generator.box_fill_variants import (
    BoxFillVariantRequest,
    format_variant_portfolio_markdown,
    generate_box_fill_variants,
    render_variant_portfolio_html,
    select_box_fill_variant,
    selected_variant_to_dict,
    variant_portfolio_to_dict,
)
from board_game_insert_generator.cli import main


class BoxFillVariantsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request_path = ROOT / "examples" / "p21" / "portfolio.json"
        self.request = BoxFillVariantRequest(load_box_fill_solve_request(self.request_path))

    def test_portfolio_is_deterministic_and_exposes_distinct_layouts(self) -> None:
        first = generate_box_fill_variants(self.request)
        second = generate_box_fill_variants(self.request)

        self.assertEqual(first.digest, second.digest)
        self.assertEqual(first.schema_version, "box_fill_variants.v0")
        self.assertGreaterEqual(len(first.variants), 2)
        self.assertIsNotNone(first.recommended_variant_id)
        self.assertTrue(all(item.result.status == "solved" for item in first.variants))
        self.assertTrue(first.duplicate_policy_ids)
        self.assertEqual(self.request.solve_request.source_plan.modules, ())

    def test_selection_and_serializers_are_explicit_and_actionable(self) -> None:
        portfolio = generate_box_fill_variants(self.request)
        selected = select_box_fill_variant(portfolio)
        selection = selected_variant_to_dict(portfolio)
        serialized = variant_portfolio_to_dict(portfolio)

        self.assertEqual(selected.id, portfolio.recommended_variant_id)
        self.assertEqual(selection["selected_variant_id"], selected.id)
        self.assertEqual(selection["selected_by"], "recommendation")
        self.assertIn("solution", selection["variant"])
        self.assertEqual(serialized["recommended_variant_id"], selected.id)
        self.assertIn(selected.id, {item["id"] for item in serialized["variants"]})
        with self.assertRaises(ValueError):
            select_box_fill_variant(portfolio, "variant:missing")

    def test_human_readable_markdown_and_static_dashboard_are_generated(self) -> None:
        portfolio = generate_box_fill_variants(self.request)
        markdown = format_variant_portfolio_markdown(portfolio)
        html = render_variant_portfolio_html(portfolio)

        self.assertIn("# BoxFill variant portfolio", markdown)
        self.assertIn("## Limits", markdown)
        self.assertIn("Choose a BoxFill layout with evidence", html)
        self.assertIn("<svg", html)
        self.assertIn(portfolio.recommended_variant_id, html)

    def test_cli_reports_dashboard_and_explicit_cad_ir_selection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            report = output_dir / "portfolio.json"
            dashboard = output_dir / "dashboard.html"
            selection = output_dir / "selection.json"
            cad_ir = output_dir / "selection-cad-ir.json"

            self.assertEqual(
                main(["report-box-fill-variants", str(self.request_path), "--format", "json", "--output", str(report)]),
                0,
            )
            self.assertEqual(
                main(["render-box-fill-variant-dashboard", str(self.request_path), "--output", str(dashboard)]),
                0,
            )
            self.assertEqual(
                main([
                    "export-box-fill-variant",
                    str(self.request_path),
                    "--output",
                    str(selection),
                    "--cad-ir-output",
                    str(cad_ir),
                ]),
                0,
            )

            report_payload = json.loads(report.read_text(encoding="utf-8"))
            selection_payload = json.loads(selection.read_text(encoding="utf-8"))
            cad_payload = json.loads(cad_ir.read_text(encoding="utf-8"))
            self.assertEqual(report_payload["schema_version"], "box_fill_variants.v0")
            self.assertEqual(selection_payload["selection"]["selected_by"], "recommendation")
            self.assertIn("box_fill_variant_selection", cad_payload["metadata"])
            self.assertIn("box_fill_solution", cad_payload["metadata"])
            self.assertIn("Choose a BoxFill layout", dashboard.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
