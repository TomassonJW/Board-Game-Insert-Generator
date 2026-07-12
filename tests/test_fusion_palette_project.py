import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from board_game_insert_generator.project_v1 import blank_project_v1


ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / "fusion_addin" / "BoardGameInsertGenerator"

import sys
sys.path.insert(0, str(ADDIN))

from palette_project import (  # noqa: E402
    CURRENT_PROJECT_FILENAME,
    PALETTE_REQUEST_SCHEMA,
    PALETTE_RESPONSE_SCHEMA,
    handle_palette_request,
)


def request(action: str, **values: object) -> dict[str, object]:
    return {
        "schema": PALETTE_REQUEST_SCHEMA,
        "request_id": f"test-{action}",
        "action": action,
        **values,
    }


class FusionPaletteProjectTests(unittest.TestCase):
    def test_load_returns_a_valid_blank_project_without_creating_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("load_project"), ADDIN, ROOT)
            self.assertFalse((Path(temp_dir) / CURRENT_PROJECT_FILENAME).exists())

        self.assertEqual(response["schema"], PALETTE_RESPONSE_SCHEMA)
        self.assertEqual(response["status"], "ready")
        self.assertEqual(response["project"]["schema_version"], "bgig.project.v1")

    def test_save_is_atomic_and_load_restores_the_normalized_project(self) -> None:
        project = blank_project_v1()
        project["project_name"] = "Mon jeu"
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            saved = handle_palette_request(request("save_project", project=project), ADDIN, ROOT)
            loaded = handle_palette_request(request("load_project"), ADDIN, ROOT)
            path = Path(temp_dir) / CURRENT_PROJECT_FILENAME

            self.assertTrue(path.is_file())
            self.assertFalse(path.with_suffix(path.suffix + ".tmp").exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["project_name"], "Mon jeu")

        self.assertTrue(saved["saved"])
        self.assertEqual(loaded["project"]["project_name"], "Mon jeu")

    def test_validate_delegates_project_rules_and_p55_envelopes_to_python(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "tokens", "name": "Jetons", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [{
            "id": "coin", "name": "Piece", "shape_kind": "round",
            "dimensions_mm": {"x": 20, "y": 20, "z": 3}, "quantity": 4,
            "container_group_id": "tokens", "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }]

        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("validate_project", project=project), ADDIN, ROOT)

        self.assertEqual(response["status"], "ready")
        self.assertEqual(response["envelopes"]["containers"][0]["container_group_id"], "tokens")
        self.assertEqual(response["flat_stack"]["summary"]["status"], "ready_for_p41")

    def test_solve_project_returns_the_p57_partition_without_saving_implicitly(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [{"id": "c", "name": "Pieces", "shape_kind": "square", "dimensions_mm": {"x": 12, "y": 12, "z": 3}, "quantity": 2, "container_group_id": "g", "content_clearance_mm": None, "measurement_confidence": "exact"}]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("solve_project", project=project), ADDIN, ROOT)
        self.assertEqual(response["partition"]["summary"]["status"], "constructed")
        self.assertEqual(response["partition"]["summary"]["automatic_body_count"], 0)
        self.assertFalse(response["saved"])
    def test_invalid_project_returns_an_actionable_response_without_overwriting_saved_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            valid = blank_project_v1()
            handle_palette_request(request("save_project", project=valid), ADDIN, ROOT)
            invalid = dict(valid)
            invalid["project_name"] = ""
            response = handle_palette_request(request("save_project", project=invalid), ADDIN, ROOT)
            persisted = json.loads((Path(temp_dir) / CURRENT_PROJECT_FILENAME).read_text(encoding="utf-8"))

        self.assertEqual(response["status"], "invalid")
        self.assertTrue(response["errors"])
        self.assertEqual(persisted["project_name"], "Mon insert")

    def test_import_migrates_legacy_json_and_export_writes_an_explicit_copy(self) -> None:
        project = blank_project_v1()
        project["project_name"] = "Jeu test"
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            imported = handle_palette_request(
                request("import_project", project_json=json.dumps(project)), ADDIN, ROOT
            )
            exported = handle_palette_request(
                request("export_project", project=imported["project"]), ADDIN, ROOT
            )

            self.assertTrue(Path(exported["export_path"]).is_file())

        self.assertTrue(imported["saved"])
        self.assertEqual(exported["status"], "ready")

    def test_rejects_unversioned_and_unknown_messages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            malformed = handle_palette_request([], ADDIN, ROOT)
            missing_id = handle_palette_request({"schema": PALETTE_REQUEST_SCHEMA, "action": "load_project"}, ADDIN, ROOT)
            missing_schema = handle_palette_request({"request_id": "x", "action": "load_project"}, ADDIN, ROOT)
            unknown = handle_palette_request(request("delete_everything"), ADDIN, ROOT)

        self.assertEqual(malformed["status"], "invalid")
        self.assertEqual(missing_id["status"], "invalid")
        self.assertEqual(missing_schema["status"], "invalid")
        self.assertEqual(unknown["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
