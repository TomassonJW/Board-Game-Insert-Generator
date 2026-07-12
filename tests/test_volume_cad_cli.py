from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from board_game_insert_generator.cli import main
from board_game_insert_generator.project_v1 import blank_project_v1
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
    load_cad_ir_json,
)


def _project() -> dict[str, object]:
    project = blank_project_v1()
    project["project_name"] = "Export P42"
    project["container_groups"] = [
        {"id": "cards", "name": "Cartes", "wall_thickness_mm": None, "floor_thickness_mm": None},
    ]
    project["contents"] = [
        {"id": "deck", "name": "Cartes", "shape_kind": "cards", "dimensions_mm": {"x": 63.0, "y": 88.0, "z": 18.0}, "quantity": 100, "container_group_id": "cards", "content_clearance_mm": None, "measurement_confidence": "exact"},
    ]
    return project


class VolumeCadCliTests(unittest.TestCase):
    def test_exports_a_v0_1_project_as_functional_cad_ir(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            project_path = root / "project.json"
            output_path = root / "functional.cad-ir.json"
            project_path.write_text(json.dumps(_project()), encoding="utf-8-sig")
            stdout = StringIO()

            with redirect_stdout(stdout):
                code = main(["export-project-v1-cad", str(project_path), "--output", str(output_path)])

            self.assertEqual(code, 0)
            self.assertTrue(output_path.is_file())
            self.assertIn("Functional CAD export OK - Export P42", stdout.getvalue())
            plan = generation_plan_from_cad_ir(load_cad_ir_json(output_path), FUSION_GENERATION_MODE_COMPACT_ONLY)
            self.assertGreaterEqual(len(plan.blanks), 1)
            self.assertGreaterEqual(len(plan.cavity_cuts), 1)


if __name__ == "__main__":
    unittest.main()
