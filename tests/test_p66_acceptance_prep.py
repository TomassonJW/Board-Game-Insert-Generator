from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from board_game_insert_generator.partition_cad import PARTITION_CAD_STATUS_READY
from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.project_v1 import blank_project_v1, normalize_project_draft


ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
COMPLETE_FIXTURE = ROOT / "scripts" / "fusion" / "p66_mvp_complete_project.json"
IMPOSSIBLE_FIXTURE = ROOT / "scripts" / "fusion" / "p66_mvp_impossible_project.json"
PREFLIGHT_SCRIPT = ROOT / "scripts" / "fusion" / "p66_preflight.py"
PREPARE_SCRIPT = ROOT / "scripts" / "fusion" / "prepare_p66_mvp_acceptance.ps1"
CHECK_SCRIPT = ROOT / "scripts" / "fusion" / "check_installed_addin.ps1"
ACCEPTANCE_DOC = ROOT / "docs" / "P66_FUSION_MVP_ACCEPTANCE.md"
MANIFEST = ADDIN / "BoardGameInsertGenerator.manifest"

if str(ADDIN) not in sys.path:
    sys.path.insert(0, str(ADDIN))

from palette_project import (  # noqa: E402
    CURRENT_PROJECT_FILENAME,
    PALETTE_REQUEST_SCHEMA,
    handle_palette_request,
)


def request(action: str, **values: object) -> dict[str, object]:
    return {
        "schema": PALETTE_REQUEST_SCHEMA,
        "request_id": f"p66-{action}",
        "action": action,
        **values,
    }


def load_preflight_module() -> object:
    spec = importlib.util.spec_from_file_location("p66_preflight", PREFLIGHT_SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("P66 preflight script cannot be imported.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class P66AcceptancePreparationTests(unittest.TestCase):
    def test_complete_fixture_is_deterministic_and_covers_p61_to_p65(self) -> None:
        raw = json.loads(COMPLETE_FIXTURE.read_text(encoding="utf-8"))
        normalized = normalize_project_draft(raw).project
        preflight = load_preflight_module()
        first = preflight.build_preflight(raw)
        second = preflight.build_preflight(json.loads(json.dumps(raw)))
        plan = first["partition"]
        cad = first["cad_build"]
        fusion = first["fusion_generation_plan"]

        self.assertEqual(raw["fill_elements"], [])
        self.assertEqual(normalized, first["normalized_project"])
        self.assertEqual(first["summary"], second["summary"])
        self.assertEqual(first["partition"], second["partition"])
        self.assertEqual(first["summary"], {
            "status": "constructed",
            "plan_digest": "478a5cb44ca7d9f905df0aeba3f8e702518b5a8a01defa326a7b335247b26880",
            "cad_digest": "f908845dc669448117b766572facdf23ee49d4ec6b1db56b29a48af792887a84",
            "source_digest": "bc176b0562b4eff493413d928129485ff49e136cd91e84ee9ccb9c21a7d3337c",
            "materializable": True,
            "cad_ready": True,
            "fusion_plan_ready": True,
        })
        self.assertEqual(plan["summary"]["requested_container_count"], 8)
        self.assertEqual(plan["summary"]["final_body_count"], 8)
        self.assertEqual(plan["summary"]["automatic_body_count"], 0)
        self.assertEqual(plan["summary"]["explicit_complement_count"], 0)
        self.assertEqual(plan["summary"]["stage_count"], 2)
        self.assertTrue(plan["validation"]["conserved"])
        self.assertTrue(plan["validation"]["no_collisions"])
        self.assertEqual(plan["clearance_policy"]["box_perimeter_xy_mm"], 0.8)
        self.assertEqual(plan["clearance_policy"]["between_bodies_xy_mm"], 0.6)
        self.assertEqual(plan["clearance_policy"]["between_bodies_z_mm"], 1.2)
        self.assertEqual(plan["clearance_policy"]["box_top_z_clearance_mm"], 0.2)
        self.assertEqual([stage["origin_z_mm"] for stage in plan["stages"]], [0.0, 35.6])
        self.assertEqual(plan["stage_support"]["status"], "supported")
        self.assertEqual(plan["top_inset_reservations"]["summary"]["reservation_count"], 2)
        self.assertEqual(plan["top_inset_reservations"]["summary"]["cut_count"], 7)
        self.assertEqual(plan["top_inset_reservations"]["summary"]["cavity_depth_compensation_count"], 4)
        self.assertEqual(cad["status"], PARTITION_CAD_STATUS_READY)
        self.assertEqual(cad["materialization"]["component_count"], 8)
        self.assertEqual(cad["materialization"]["cavity_count"], 9)
        self.assertEqual(cad["materialization"]["top_inset_cut_count"], 7)
        body_names = [item["body"]["name"] for item in cad["cad_ir"]["components"]]
        self.assertEqual(len(body_names), len(set(body_names)))
        self.assertEqual(len(fusion["compact_occurrences"]), 8)
        self.assertEqual(fusion["exploded_occurrences"], [])
        self.assertEqual(len(fusion["cavity_cuts"]), 16)
        self.assertTrue(all(item["linked_component"] for item in fusion["compact_occurrences"]))

    def test_bridge_lifecycle_axes_roundtrip_and_regeneration_are_explicit(self) -> None:
        raw = json.loads(COMPLETE_FIXTURE.read_text(encoding="utf-8"))
        edited = deepcopy(raw)
        edited["contents"][0]["dimensions_mm"]["x"] = 19.0
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            estimated = handle_palette_request(request("validate_project", project=raw), ADDIN, ROOT)
            solved = handle_palette_request(request("solve_project", project=raw), ADDIN, ROOT)
            generated = handle_palette_request(request("materialize_project", project=raw), ADDIN, ROOT)
            regenerated = handle_palette_request(request("regenerate_project", project=raw), ADDIN, ROOT)
            edited_response = handle_palette_request(request("validate_project", project=edited), ADDIN, ROOT)
            imported = handle_palette_request(request("import_project", project_json=json.dumps(raw)), ADDIN, ROOT)
            loaded = handle_palette_request(request("load_project"), ADDIN, ROOT)
            project_path = Path(temp_dir) / CURRENT_PROJECT_FILENAME
            persisted = project_path.is_file()

        cards = {item["id"]: item for item in solved["project"]["contents"]}
        axes = {item["container_group_id"]: item["axis_contracts"] for item in solved["container_sizing"]["containers"]}
        self.assertFalse(estimated["saved"])
        self.assertIsNone(estimated["cad_build"])
        self.assertEqual(estimated["container_sizing"]["proposal_status"], "not_computed")
        self.assertEqual(solved["lifecycle"], {
            "source": "current", "derived": "current", "solved": "current", "materialized": "not_materialized",
        })
        self.assertEqual(cards["cards-0"]["base_dimensions_mm"], {"x": 63.0, "y": 88.0, "z": 24.0})
        self.assertEqual(cards["cards-0"]["resolved_orientation"], "flat")
        self.assertEqual(cards["cards-1"]["dimensions_mm"], {"x": 88.0, "y": 24.0, "z": 63.0})
        self.assertEqual(cards["cards-1"]["resolved_orientation"], "upright_long_edge")
        self.assertEqual(axes["tokens"]["x"]["mode"], "auto")
        self.assertEqual(axes["c0"]["x"]["mode"], "target")
        self.assertEqual(axes["c2"]["x"]["mode"], "fixed")
        self.assertEqual(generated["lifecycle"]["materialized"], "cad_ready")
        self.assertEqual(generated["cad_build"]["materialization"]["automatic_body_count"], 0)
        self.assertEqual(generated["cad_build"]["cad_ir_digest"], regenerated["cad_build"]["cad_ir_digest"])
        self.assertNotEqual(solved["project_digest"], solved["partition"]["plan_digest"])
        self.assertNotEqual(generated["cad_build"]["cad_ir_digest"], generated["partition"]["plan_digest"])
        self.assertNotEqual(solved["project_digest"], edited_response["project_digest"])
        self.assertEqual(edited_response["lifecycle"]["solved"], "not_computed")
        self.assertEqual(edited_response["lifecycle"]["materialized"], "not_materialized")
        self.assertFalse(edited_response["saved"])
        self.assertTrue(persisted)
        self.assertTrue(imported["saved"])
        self.assertEqual(loaded["project"], solved["project"])

    def test_impossible_fixture_has_a_local_blocker_and_never_emits_cad(self) -> None:
        raw = json.loads(IMPOSSIBLE_FIXTURE.read_text(encoding="utf-8"))
        preflight = load_preflight_module().build_preflight(raw)
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("materialize_project", project=raw), ADDIN, ROOT)
            project_path = Path(temp_dir) / CURRENT_PROJECT_FILENAME
            persisted = project_path.is_file()

        self.assertEqual(preflight["summary"]["status"], "impossible")
        self.assertFalse(preflight["summary"]["materializable"])
        self.assertFalse(preflight["summary"]["cad_ready"])
        self.assertIsNone(preflight["fusion_generation_plan"])
        self.assertIn("CONTAINER_MINIMUM_BLOCKED", {item["code"] for item in preflight["partition"]["diagnostics"]})
        self.assertEqual(response["cad_build"]["status"], "impossible")
        self.assertIsNone(response["cad_build"]["cad_ir"])
        self.assertEqual(response["cad_build"]["materialization"]["component_count"], 0)
        self.assertEqual(response["lifecycle"]["materialized"], "blocked")
        self.assertFalse(persisted)

    def test_fifty_requested_containers_remain_an_automated_non_materialized_proof(self) -> None:
        project = blank_project_v1()
        project["box"] = {
            "inner_dimensions_mm": {"x": 900.0, "y": 900.0, "z": 100.0},
            "usable_height_mm": 96.0,
            "lid_clearance_mm": 2.0,
        }
        project["container_groups"] = [
            {"id": f"g{index}", "name": f"Bac {index}", "wall_thickness_mm": None, "floor_thickness_mm": None}
            for index in range(50)
        ]
        project["contents"] = [
            {
                "id": f"c{index}", "name": f"Pieces {index}", "shape_kind": "square",
                "dimensions_mm": {"x": 18.0, "y": 18.0, "z": 5.0}, "quantity": 4,
                "container_group_id": f"g{index}", "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
            for index in range(50)
        ]

        result = solve_partition_plan(project)

        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertEqual(result["summary"]["placed_container_count"], 50)
        self.assertEqual(result["summary"]["final_body_count"], 50)
        self.assertEqual(result["summary"]["automatic_body_count"], 0)
        self.assertGreater(result["summary"]["candidate_count_evaluated"], 50)

    def test_preparer_package_and_recorded_human_gate_are_explicit(self) -> None:
        prepare = PREPARE_SCRIPT.read_text(encoding="utf-8")
        checker = CHECK_SCRIPT.read_text(encoding="utf-8")
        document = ACCEPTANCE_DOC.read_text(encoding="utf-8")
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

        for marker in (
            "install_addin.ps1", "check_installed_addin.ps1", "p66_preflight.py",
            "p66_mvp_complete_project.json", "p66_mvp_impossible_project.json",
            "bgig_installed_commit.txt", "bgig_project_v1.before-p66.json",
            "P66 Fusion OK 0.1.20", "CONTAINER_MINIMUM_BLOCKED",
            "Dry run: would", "Remove-Item -LiteralPath $evidenceRoot",
        ):
            self.assertIn(marker, prepare)
        self.assertIn("Assert-BgigPaletteProjectRuntime", checker)
        self.assertIn("expected 0.1.20", checker)
        self.assertIn("manifestText", checker)
        self.assertNotIn("ConvertFrom-Json", checker)
        self.assertEqual(manifest["version"], "0.1.49")
        self.assertIn("mvp-accepted", document)
        self.assertIn("P66 Fusion OK 0.1.20 - commit 6e351bb", document)
        self.assertIn("P66 Fusion OK 0.1.20 - commit <sha>", document)
        self.assertIn("P66 NON BGIG - KEEP", document)
        self.assertIn("print-validated: false", document)
        for step in range(1, 22):
            self.assertIn(f"{step}.", document)


if __name__ == "__main__":
    unittest.main()
