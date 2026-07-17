from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
sys.path.insert(0, str(ADDIN))

from palette_project import PALETTE_REQUEST_SCHEMA, handle_palette_request  # noqa: E402
from board_game_insert_generator.project_v1 import blank_project_v1  # noqa: E402


def request(action: str, **values: object) -> dict[str, object]:
    return {"schema": PALETTE_REQUEST_SCHEMA, "request_id": "h04-transport", "action": action, **values}


class SolverOutcomeTransportTests(unittest.TestCase):
    def test_solve_transports_request_revision_and_additive_solver_result(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [{"id": "c", "name": "Pièces", "shape_kind": "square", "dimensions_mm": {"x": 12, "y": 12, "z": 3}, "quantity": 2, "container_group_id": "g", "content_clearance_mm": None, "measurement_confidence": "exact"}]

        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("solve_project", project=project, source_revision=23), ADDIN, ROOT)

        self.assertEqual(response["status"], "ready")
        self.assertEqual(response["solver_result"]["status"], "solution_found")
        self.assertEqual(response["solver_result"]["telemetry"]["request"], {"id": "h04-transport", "revision": 23})
        self.assertEqual(response["solver_result"], {**response["partition"]["solver"]["result"], "telemetry": response["partition"]["solver"]["telemetry"]})

    def test_invalid_input_returns_the_same_truthful_contract_before_search(self) -> None:
        project = blank_project_v1()
        project["project_name"] = ""

        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("solve_project", project=project, source_revision=24), ADDIN, ROOT)

        self.assertEqual(response["status"], "invalid")
        self.assertEqual(response["solver_result"]["status"], "invalid_input")
        self.assertEqual(response["solver_result"]["telemetry"]["stop_reason"], "input_validation_failed")

    def test_palette_keeps_stale_solver_responses_out_of_the_editable_dom(self) -> None:
        markup = (ADDIN / "palette.html").read_text(encoding="utf-8")

        self.assertIn("source_revision:sourceRevision", markup)
        self.assertIn("staleSolverResponse(payload);return;", markup)
        self.assertIn("SOLVER_RESULT_PRESENTATIONS", markup)
        self.assertIn("Aucune solution trouvée dans le budget", markup)
        self.assertIn("Niveaux de départ Z", markup)
        self.assertLess(markup.index("staleSolverResponse(payload);return;"), markup.index("if(payload.status==='cancelled')"))


if __name__ == "__main__":
    unittest.main()
