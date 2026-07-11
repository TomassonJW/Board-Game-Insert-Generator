from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from context import ROOT

from board_game_insert_generator.cli import main
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    generation_plan_from_cad_ir,
    load_cad_ir_json,
)


class CliTests(unittest.TestCase):
    def test_cli_root_help_lists_export_cad_ir_subcommand(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            code = main(["--help"])

        output = stdout.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("export-cad-ir CONFIG --output PATH", output)
        self.assertIn("export-local-composer-selection", output)
        self.assertIn("serve-local-composer", output)
        self.assertIn("not an --export-cad-ir option", output)
    def test_cli_diagnose_reports_ok(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            code = main(["diagnose", str(ROOT / "examples" / "simple_box.json")])

        output = stdout.getvalue()

        self.assertEqual(code, 0)
        self.assertIn("Diagnostic OK - Simple square box V0", output)
        self.assertIn("- Generated instances: 4", output)
        self.assertIn("- Markdown report: OK", output)
        self.assertIn("- JSON report: OK", output)

    def test_cli_exports_cad_ir_json_compatible_with_fusion_addin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "cad_ir_input.json"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                code = main(
                    [
                        "export-cad-ir",
                        str(ROOT / "examples" / "simple_box.json"),
                        "--output",
                        str(output_path),
                    ]
                )

            self.assertTrue(output_path.is_file())
            payload = load_cad_ir_json(output_path)
            plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(code, 0)
        self.assertIn("CAD IR export OK - Simple square box V0", stdout.getvalue())
        self.assertEqual(output_path.name, "cad_ir_input.json")
        self.assertEqual(payload["schema_version"], "cad_ir.v0")
        self.assertEqual(payload["metadata"]["project_name"], "Simple square box V0")
        self.assertEqual(plan.created_object_count, 9)
        self.assertEqual(len(plan.exploded_occurrences), 4)
        self.assertTrue(plan.linked_exploded_occurrences)
        self.assertEqual(
            plan.reference_box.component_name,
            "Box reference - not printable",
        )
        self.assertEqual(plan.blanks[0].body_name, "cards-main-01 rectangular blank")
        self.assertEqual(
            plan.blanks[0].size_mm.to_dict(),
            {"x": 68.9, "y": 99.2, "z": 44.0},
        )
        self.assertEqual(
            plan.exploded_occurrences[0].occurrence_name,
            "cards-main-01 rectangular blank exploded occurrence",
        )
        self.assertEqual(plan.exploded_occurrences[0].component_id, plan.blanks[0].cad_id)

    def test_cli_exports_local_composer_selection_compatible_with_fusion_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "local_composer_selection.cad-ir.json"
            selection_path = Path(temporary_directory) / "local_composer_selection.json"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                code = main(
                    [
                        "export-local-composer-selection",
                        "--starter",
                        "mixed-box",
                        "--output",
                        str(output_path),
                        "--selection-output",
                        str(selection_path),
                    ]
                )

            payload = load_cad_ir_json(output_path)
            plan = generation_plan_from_cad_ir(payload)
            selection = json.loads(selection_path.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertIn("Local composer selection export OK", stdout.getvalue())
        self.assertEqual(
            payload["metadata"]["local_composer"]["geometry_status"],
            "open_top_tray_candidates",
        )
        self.assertEqual(len(payload["components"]), 3)
        self.assertEqual(len(plan.blanks), 3)
        self.assertEqual(len(plan.cavity_cuts), 3)
        self.assertIn("open-top tray candidates", stdout.getvalue())
        self.assertEqual(
            selection["selected_variant_id"],
            payload["metadata"]["box_fill_variant_selection"]["selected_variant_id"],
        )

    def test_cli_exports_a_sliding_lid_coupon_for_fusion_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "sliding_lid_coupon.cad-ir.json"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                code = main(
                    [
                        "export-local-composer-selection",
                        "--starter",
                        "mixed-box",
                        "--mechanism",
                        "sliding_lid",
                        "--output",
                        str(output_path),
                    ]
                )

            payload = load_cad_ir_json(output_path)
            plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(code, 0)
        self.assertIn("Mechanism: sliding_lid", stdout.getvalue())
        self.assertIn("Coupon: prepared_for_fusion_smoke", stdout.getvalue())
        self.assertEqual(payload["metadata"]["mechanism_coupon"]["piece_count"], 2)
        self.assertEqual(len(plan.additive_prism_joins), 2)

    def test_cli_exports_cad_ir_with_rectangular_cavity_compatible_with_fusion_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "simple_tray_cad_ir.json"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                code = main(
                    [
                        "export-cad-ir",
                        str(ROOT / "examples" / "simple_tray.json"),
                        "--output",
                        str(output_path),
                    ]
                )

            payload = load_cad_ir_json(output_path)
            plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(code, 0)
        self.assertIn("CAD IR export OK - Simple tray with planned cavity V0", stdout.getvalue())
        self.assertEqual(payload["components"][0]["body"]["cavities"][0]["id"], "token-pocket")
        self.assertEqual(
            payload["components"][0]["body"]["operations"][1]["kind"],
            "subtract_rectangular_cavity",
        )
        self.assertEqual(plan.created_object_count, 4)
        self.assertEqual(len(plan.exploded_occurrences), 1)
        self.assertTrue(plan.linked_exploded_occurrences)
        self.assertEqual(len(plan.cavity_cuts), 1)
        self.assertEqual(plan.cavity_cuts[0].cavity_id, "token-pocket")
        self.assertEqual(plan.blanks[0].body_name, "token-tray-01 rectangular blank")

    def test_cli_exports_multilayer_cad_ir_compatible_with_fusion_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "multilayer_cad_ir.json"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                code = main(
                    [
                        "export-cad-ir",
                        str(ROOT / "examples" / "simple_multilayer_grid_scene.json"),
                        "--output",
                        str(output_path),
                    ]
                )

            payload = load_cad_ir_json(output_path)
            plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(code, 0)
        self.assertIn("CAD IR export OK - Simple multilayer grid scene V0", stdout.getvalue())
        self.assertEqual(len(plan.grid_positioned_blanks), 0)
        self.assertEqual(plan.multi_layer_grid_module_count, 0)
        self.assertEqual(plan.grid_modules_with_z_placement_count, 0)
        self.assertEqual(plan.grid_module_height_variant_count, 0)
        self.assertEqual(len(plan.compact_occurrences), 1)
        self.assertEqual(len(plan.exploded_occurrences), 1)
        self.assertEqual(len(plan.rejected_grid_modules), 1)
        self.assertEqual(plan.rejected_grid_modules[0].code, "DIMENSIONS_INCOMPATIBLE")
        self.assertTrue(plan.linked_exploded_occurrences)

    def test_cli_reports_configuration_error_category(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "config.json"
            path.write_text(json.dumps({"unexpected": True}), encoding="utf-8")
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                code = main([str(path)])

        self.assertEqual(code, 2)
        self.assertIn("Configuration error:", stderr.getvalue())
        self.assertIn("Unknown field(s) in 'root': unexpected", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
