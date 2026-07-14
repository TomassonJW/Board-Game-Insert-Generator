import json
from copy import deepcopy
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
    PERSONAL_PRESETS_FILENAME,
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
        self.assertEqual(len(response["project_digest"]), 64)
        self.assertEqual(response["lifecycle"]["source"], "current")
        self.assertEqual(response["lifecycle"]["derived"], "pending")

    def test_save_is_atomic_and_load_restores_the_normalized_project(self) -> None:
        project = blank_project_v1()
        project_name = "Éléments d’été — boîte à dés"
        project["project_name"] = project_name
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            saved = handle_palette_request(request("save_project", project=project), ADDIN, ROOT)
            loaded = handle_palette_request(request("load_project"), ADDIN, ROOT)
            path = Path(temp_dir) / CURRENT_PROJECT_FILENAME
            raw = path.read_text(encoding="utf-8")

            self.assertTrue(path.is_file())
            self.assertFalse(path.with_suffix(path.suffix + ".tmp").exists())
            self.assertIn(project_name, raw)
            self.assertEqual(json.loads(raw)["project_name"], project_name)

        self.assertTrue(saved["saved"])
        self.assertEqual(loaded["project"]["project_name"], project_name)

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
        self.assertEqual(response["flat_stack"]["summary"]["status"], "not_required")
        self.assertEqual(response["flat_stack"]["flat_stack"]["semantics"], "localized_top_insets")

    def test_validate_exposes_minimum_and_request_without_a_calculated_size(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [{"id": "c", "name": "Pieces", "shape_kind": "square", "dimensions_mm": {"x": 12, "y": 12, "z": 3}, "quantity": 2, "container_group_id": "g", "content_clearance_mm": None, "measurement_confidence": "exact"}]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("validate_project", project=project), ADDIN, ROOT)

        sizing = response["container_sizing"]["containers"][0]
        self.assertEqual(response["container_sizing"]["proposal_status"], "not_computed")
        self.assertIsNotNone(sizing["minimum_outer_dimensions_mm"])
        self.assertIsNone(sizing["calculated_outer_dimensions_mm"])
        self.assertFalse(response["saved"])
    def test_solve_project_returns_the_p57_partition_without_saving_implicitly(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [{"id": "c", "name": "Pieces", "shape_kind": "square", "dimensions_mm": {"x": 12, "y": 12, "z": 3}, "quantity": 2, "container_group_id": "g", "content_clearance_mm": None, "measurement_confidence": "exact"}]
        project_before = deepcopy(project)
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("solve_project", project=project), ADDIN, ROOT)
        self.assertEqual(project, project_before)
        self.assertEqual(response["partition"]["summary"]["status"], "constructed")
        self.assertEqual(response["partition"]["summary"]["automatic_body_count"], 0)
        self.assertEqual(response["result_view"]["source_plan_digest"], response["partition"]["plan_digest"])
        self.assertTrue(response["result_view"]["invariants"]["derived_from_real_placements"])
        self.assertEqual(response["result_view"]["presentation"]["schema_version"], "bgig.preview_explanations.v1")
        self.assertTrue(response["result_view"]["presentation"]["invariants"]["does_not_change_score"])
        sizing = response["container_sizing"]["containers"][0]
        self.assertEqual(response["container_sizing"]["proposal_status"], "complete")
        self.assertEqual(sizing["container_group_id"], "g")
        self.assertIsNotNone(sizing["minimum_outer_dimensions_mm"])
        self.assertIsNotNone(sizing["calculated_outer_dimensions_mm"])
        self.assertEqual(sizing["axis_contracts"]["x"]["mode"], "auto")
        self.assertTrue(response["container_sizing"]["invariants"]["does_not_mutate_project"])
        self.assertTrue(response["container_sizing"]["invariants"]["does_not_materialize_fusion"])
        self.assertEqual(response["lifecycle"]["derived"], "current")
        self.assertEqual(response["lifecycle"]["solved"], "current")
        self.assertEqual(response["lifecycle"]["materialized"], "not_materialized")
        self.assertFalse(response["saved"])
    def test_materialize_and_regenerate_return_the_same_real_cad_build(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [{"id": "c", "name": "Pieces", "shape_kind": "square", "dimensions_mm": {"x": 12, "y": 12, "z": 3}, "quantity": 2, "container_group_id": "g", "content_clearance_mm": None, "measurement_confidence": "exact"}]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            generated = handle_palette_request(request("materialize_project", project=project), ADDIN, ROOT)
            regenerated = handle_palette_request(request("regenerate_project", project=project), ADDIN, ROOT)

        self.assertEqual(generated["cad_build"]["status"], "ready_for_fusion")
        self.assertEqual(generated["cad_build"]["materialization"]["component_count"], 1)
        self.assertEqual(generated["cad_build"]["materialization"]["automatic_body_count"], 0)
        self.assertEqual(generated["cad_build"]["cad_ir_digest"], regenerated["cad_build"]["cad_ir_digest"])
        self.assertEqual(generated["partition"]["plan_digest"], generated["cad_build"]["source_plan_digest"])

    def test_bridge_round_trip_and_materializes_an_explicit_legacy_complement(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{
            "id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None,
        }]
        project["contents"] = [{
            "id": "c", "name": "Pieces", "shape_kind": "square",
            "dimensions_mm": {"x": 12, "y": 12, "z": 3}, "quantity": 2,
            "container_group_id": "g", "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }]
        project["fill_elements"] = [{
            "id": "legacy-solid", "name": "Cale historique", "kind": "solid", "mode": "exact",
            "dimensions_mm": {"x": 20, "y": 148.8, "z": 56}, "container_group_id": None,
        }]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            imported = handle_palette_request(
                request("import_project", project_json=json.dumps(project)), ADDIN, ROOT
            )
            loaded = handle_palette_request(request("load_project"), ADDIN, ROOT)
            materialized = handle_palette_request(
                request("materialize_project", project=loaded["project"]), ADDIN, ROOT
            )

        legacy = loaded["project"]["fill_elements"]
        self.assertEqual(imported["status"], "ready")
        self.assertEqual(legacy[0]["id"], "legacy-solid")
        self.assertEqual(legacy[0]["kind"], "solid")
        self.assertEqual(legacy[0]["mode"], "exact")
        self.assertEqual(materialized["cad_build"]["status"], "ready_for_fusion")
        self.assertEqual(materialized["cad_build"]["materialization"]["explicit_complement_component_count"], 1)

    def test_p64_partial_proposal_is_visible_but_blocked_before_fusion_materialization(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [{"id": "c", "name": "Pieces", "shape_kind": "square", "dimensions_mm": {"x": 12, "y": 12, "z": 3}, "quantity": 2, "container_group_id": "g", "content_clearance_mm": None, "measurement_confidence": "exact"}]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            baseline = handle_palette_request(request("solve_project", project=project), ADDIN, ROOT)
            minimum = baseline["partition"]["placements"][0]["minimum_outer_envelope_mm"]
            project["container_groups"][0]["expansion_axes"] = {"x": False, "y": False, "z": False}
            project["container_groups"][0]["locked_outer_dimensions_mm"] = minimum
            response = handle_palette_request(request("materialize_project", project=project), ADDIN, ROOT)

        self.assertEqual(response["partition"]["summary"]["status"], "proposal_with_residuals")
        self.assertFalse(response["result_view"]["materializable"])
        self.assertEqual(response["cad_build"]["status"], "not_materializable")
        self.assertIsNone(response["cad_build"]["cad_ir"])
        self.assertEqual(response["lifecycle"]["materialized"], "blocked")

    def test_bridge_quarantines_complement_presets_without_changing_the_response_schema(self) -> None:
        project = blank_project_v1()
        project["flat_items"] = [{
            "id": "board", "name": "Plateau", "kind": "board",
            "dimensions_mm": {"x": 100, "y": 100, "z": 4},
            "quantity": 1, "stack_order": 0,
        }]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("validate_project", project=project), ADDIN, ROOT)

        presets = response["creation_presets"]
        self.assertEqual(presets["schema_version"], "bgig.creation_presets.v1")
        self.assertEqual(presets["complements"], [])
    def test_personal_presets_save_export_import_and_delete_round_trip(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}
        ]
        project["contents"] = [{
            "id": "deck", "name": "Mon deck", "shape_kind": "cards",
            "dimensions_mm": {"x": 66, "y": 91, "z": 20}, "quantity": 60,
            "container_group_id": "g", "content_clearance_mm": None,
            "measurement_confidence": "exact", "storage_orientation": "auto",
        }]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            saved = handle_palette_request(
                request("save_personal_preset", project=project, content_id="deck", preset_name="Deck test"),
                ADDIN, ROOT,
            )
            exported = handle_palette_request(request("export_personal_presets", project=project), ADDIN, ROOT)
            raw_export = Path(exported["export_path"]).read_text(encoding="utf-8")
            deleted = handle_palette_request(
                request("delete_personal_preset", project=project, preset_id="deck-test"), ADDIN, ROOT
            )
            imported = handle_palette_request(
                request("import_personal_presets", project=project, preset_json=raw_export), ADDIN, ROOT
            )
            preset_file_created = (Path(temp_dir) / PERSONAL_PRESETS_FILENAME).is_file()

        self.assertEqual(saved["personal_presets"]["presets"][0]["name"], "Deck test")
        self.assertEqual(deleted["personal_presets"]["presets"], [])
        self.assertEqual(imported["personal_presets"]["presets"][0]["id"], "deck-test")
        self.assertTrue(preset_file_created)

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

    def test_bridge_keeps_fifty_stable_container_identifiers(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {"id": f"group-{index:02d}", "name": f"Bac {index:02d}", "wall_thickness_mm": None, "floor_thickness_mm": None}
            for index in range(50)
        ]
        project["contents"] = [
            {
                "id": f"content-{index:02d}", "name": f"Element {index:02d}", "shape_kind": "square",
                "dimensions_mm": {"x": 8, "y": 8, "z": 2}, "quantity": 1,
                "container_group_id": f"group-{index:02d}", "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
            for index in range(50)
        ]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("validate_project", project=project), ADDIN, ROOT)

        identifiers = [item["container_group_id"] for item in response["container_sizing"]["containers"]]
        self.assertEqual(identifiers, [f"group-{index:02d}" for index in range(50)])
        self.assertEqual(len(set(identifiers)), 50)

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
