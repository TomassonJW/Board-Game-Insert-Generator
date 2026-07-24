from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import unittest
import zipfile

from board_game_insert_generator.container_internal_variants import (
    derive_container_internal_variant_frontiers,
)
from board_game_insert_generator.container_variant_global_search import (
    _participants_with_variant_options,
)
from board_game_insert_generator.free_3d_plan_adapter import prepare_free_3d_problem
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import (
    _force_minimum_dimensions,
    solve_minimal_layout,
)
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.scip_product_solver import (
    SCIP_PRODUCT_ARCHIVE_SHA256,
    SCIP_PRODUCT_ARTIFACT_DIGEST,
    STATUS_INVALID_RUNTIME,
    _participant_options,
    _prepare_product_problem,
    configure_scip_product_runtime,
    scip_product_limits,
    solve_scip_product_3d,
)
from board_game_insert_generator.solver_outcome import SOLUTION_FOUND
import board_game_insert_generator.scip_product_solver as scip_product_module


ROOT = Path(__file__).resolve().parents[1]
VENDOR = (
    ROOT
    / "fusion_addin"
    / "BoardGameInsertGenerator"
    / "vendor"
    / "scip"
    / "10.0.2"
    / "windows-x86_64"
)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stacking_project() -> dict[str, object]:
    project = blank_project_v1()
    project["project_name"] = "SCIP product stacking control"
    project["box"] = {
        "inner_dimensions_mm": {"x": 70.0, "y": 70.0, "z": 55.0},
        "usable_height_mm": 55.0,
        "lid_clearance_mm": 0.0,
    }
    project["container_groups"] = [
        {
            "id": f"stack-{index}",
            "name": f"Stack {index}",
            "wall_thickness_mm": None,
            "floor_thickness_mm": None,
        }
        for index in range(3)
    ]
    project["contents"] = [
        {
            "id": f"content-{index}",
            "name": f"Content {index}",
            "shape_kind": "custom",
            "dimensions_mm": {"x": 58.0, "y": 58.0, "z": 14.0},
            "quantity": 1,
            "container_group_id": f"stack-{index}",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
        for index in range(3)
    ]
    return project


class ScipProductSolverTests(unittest.TestCase):
    def tearDown(self) -> None:
        configure_scip_product_runtime(None)

    def test_vendor_archive_and_sealed_workers_match_artifact(self) -> None:
        manifest = json.loads((VENDOR / "ARTIFACT.json").read_text(encoding="utf-8"))
        supplied_digest = manifest.pop("artifact_digest")
        self.assertEqual(supplied_digest, SCIP_PRODUCT_ARTIFACT_DIGEST)
        self.assertEqual(canonical_digest(manifest), supplied_digest)

        archive = VENDOR / str(manifest["archive"]["path"])
        self.assertEqual(_sha256(archive), SCIP_PRODUCT_ARCHIVE_SHA256)
        self.assertEqual(archive.stat().st_size, manifest["archive"]["size_bytes"])
        with zipfile.ZipFile(archive) as package:
            files = [item for item in package.infolist() if not item.is_dir()]
            self.assertEqual(len(files), manifest["runtime_tree"]["file_count"])
            self.assertEqual(
                sum(item.file_size for item in files),
                manifest["runtime_tree"]["size_bytes"],
            )
            self.assertTrue(all(item.filename.startswith("runtime/") for item in files))

        for record in manifest["worker_files"]:
            path = VENDOR / record["path"]
            self.assertEqual(path.stat().st_size, record["size_bytes"])
            self.assertEqual(_sha256(path), record["sha256"])

    def test_repeated_identical_configuration_keeps_runtime_validation_cache(self) -> None:
        configure_scip_product_runtime(
            VENDOR,
            artifact_path=VENDOR / "ARTIFACT.json",
            worker_root=VENDOR / "worker",
            scratch_root=ROOT / ".codex-work" / "scratch-a",
        )
        sentinel = ("runtime", "artifact", "worker")
        scip_product_module._validated_runtime_signature = sentinel
        configure_scip_product_runtime(
            VENDOR,
            artifact_path=VENDOR / "ARTIFACT.json",
            worker_root=VENDOR / "worker",
            scratch_root=ROOT / ".codex-work" / "scratch-b",
        )
        self.assertEqual(
            scip_product_module._validated_runtime_signature,
            sentinel,
        )

    def test_effort_limits_are_monotone_and_single_threaded(self) -> None:
        quick = scip_product_limits("quick")
        normal = scip_product_limits("normal")
        deep = scip_product_limits("deep")
        self.assertEqual(
            (quick.wall_seconds, normal.wall_seconds, deep.wall_seconds),
            (1.0, 5.0, 30.0),
        )
        self.assertEqual({quick.threads, normal.threads, deep.threads}, {1})
        self.assertEqual(
            {quick.memory_mebibytes, normal.memory_mebibytes, deep.memory_mebibytes},
            {1024},
        )
        self.assertEqual({quick.seed, normal.seed, deep.seed}, {6408})

    def test_product_model_preserves_variants_and_exact_clearances(self) -> None:
        project = _stacking_project()
        base_problem = prepare_free_3d_problem(project).problem
        self.assertIsNotNone(base_problem)
        run = derive_container_internal_variant_frontiers(
            project,
            effort_profile="quick",
            max_container_height_mm=base_problem.storage_height_mm,
        )
        participants = _participants_with_variant_options(
            base_problem.participants,
            run.frontiers,
        )
        problem = replace(
            base_problem,
            participants=participants,
            container_variant_frontiers=run.frontiers,
        )
        prepared, rejection = _prepare_product_problem(
            _force_minimum_dimensions(participants),
            problem,
        )
        self.assertEqual(rejection, "")
        self.assertIsNotNone(prepared)
        payload = prepared.payload
        self.assertEqual(payload["scale_per_mm"], 1000)
        self.assertIn("stacking", payload["active_constraints"])
        self.assertIn("support", payload["active_constraints"])
        self.assertIn("p45_variant_front", payload["active_constraints"])
        self.assertEqual(len(payload["participants"]), 3)
        self.assertTrue(all(value["variants"] for value in payload["participants"]))
        self.assertEqual(
            payload["product_clearance_padding"],
            {
                "box_xy_mm": problem.box_xy_clearance_mm,
                "between_xy_mm": problem.xy_clearance_mm,
                "between_z_mm": problem.z_clearance_mm,
                "positive_axis_padding": True,
            },
        )
        expected_world_x = round(
            (float(problem.box["x"]) - 2.0 * problem.box_xy_clearance_mm + problem.xy_clearance_mm)
            * 1000
        )
        self.assertEqual(payload["world_mm"][0], expected_world_x)

    def test_fixed_dimensions_filter_only_incompatible_local_variants(self) -> None:
        participant = {
            "id": "container:fixed",
            "role": "container",
            "name": "Fixed",
            "minimum_local_mm": {"x": 10.0, "y": 10.0, "z": 10.0},
            "dimension_modes": {"x": "fixed", "y": "fixed", "z": "fixed"},
            "target_local_mm": {"x": 12.0, "y": 12.0, "z": 12.0},
            "container_internal_variant_options_v1": [
                {
                    "variant_id": "too-large",
                    "minimum_outer_envelope_mm": {
                        "x": 13.0,
                        "y": 11.0,
                        "z": 11.0,
                    },
                    "geometry_digest": "a" * 64,
                    "canonical": False,
                },
                {
                    "variant_id": "fits",
                    "minimum_outer_envelope_mm": {
                        "x": 11.0,
                        "y": 11.0,
                        "z": 11.0,
                    },
                    "geometry_digest": "b" * 64,
                    "canonical": True,
                },
            ],
        }
        options = _participant_options(participant)
        self.assertEqual([value.variant_id for value in options], ["fits"])
        self.assertEqual(options[0].local_size_mm, (12.0, 12.0, 12.0))

    def test_localized_top_inset_is_rejected_without_approximation(self) -> None:
        preparation = prepare_free_3d_problem(_stacking_project())
        problem = replace(preparation.problem, top_inset_zones=({"id": "zone"},))
        prepared, rejection = _prepare_product_problem(
            problem.participants,
            problem,
        )
        self.assertIsNone(prepared)
        self.assertEqual(rejection, "top_inset_reservations_not_supported")

    def test_cp314_runtime_fails_closed_then_internal_solver_remains_available(self) -> None:
        configure_scip_product_runtime(
            VENDOR,
            artifact_path=VENDOR / "ARTIFACT.json",
            worker_root=VENDOR / "worker",
            scratch_root=ROOT / ".codex-work" / "test-scip-product",
        )
        preparation = prepare_free_3d_problem(_stacking_project())
        execution = solve_scip_product_3d(
            preparation.problem.participants,
            preparation.problem,
            effort_profile="quick",
        )
        self.assertEqual(execution.status, STATUS_INVALID_RUNTIME)
        self.assertEqual(
            execution.stop_reason,
            "python_abi_mismatch_expected_cp314",
        )

        plan = solve_minimal_layout(_stacking_project(), effort_profile="quick")
        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        provenance = plan["minimal_layout"]["search_provenance"]
        self.assertEqual(provenance["external_lane"]["status"], STATUS_INVALID_RUNTIME)
        self.assertTrue(provenance["lanes"])

    def test_real_cp314_integration_receipt_proves_forced_z_stacking(self) -> None:
        path = ROOT / "tests" / "fixtures" / "p64_l08k_scip_product_integration.v1.json"
        receipt = json.loads(path.read_text(encoding="utf-8"))
        supplied_digest = receipt.pop("receipt_digest")
        self.assertEqual(canonical_digest(receipt), supplied_digest)
        self.assertTrue(receipt["runs_identical"])
        self.assertEqual(receipt["scip_invocations_per_calculation"], 1)
        self.assertEqual(receipt["internal_lane_count_after_scip_solution"], 0)
        self.assertEqual(receipt["result"]["candidate_source"], "external_scip_real_3d")
        self.assertTrue(receipt["result"]["external_recertified"])
        self.assertEqual(receipt["real_3d"]["distinct_z_level_count"], 3)
        self.assertEqual(receipt["real_3d"]["supported_placement_count"], 2)
        self.assertFalse(receipt["invariants"]["fusion_validated"])
        self.assertFalse(receipt["invariants"]["print_validated"])

    def test_public_18_by_20_limit_receipt_stays_honest(self) -> None:
        path = ROOT / "tests" / "fixtures" / "p64_l08k_scip_product_limit_regression.v1.json"
        receipt = json.loads(path.read_text(encoding="utf-8"))
        supplied_digest = receipt.pop("receipt_digest")
        self.assertEqual(canonical_digest(receipt), supplied_digest)
        self.assertEqual(receipt["container_count"], 18)
        self.assertEqual(receipt["content_count"], 20)
        self.assertFalse(receipt["holdout_read"])
        self.assertFalse(receipt["interpretation"]["solution_gain_demonstrated"])
        self.assertTrue(receipt["interpretation"]["bounded_unknown_is_not_infeasible"])
        self.assertTrue(receipt["interpretation"]["human_limit_case_gate_still_required"])
        for run in receipt["runs"]:
            self.assertEqual(run["external_invocation_count"], 1)
            self.assertEqual(run["internal_lane_count"], 0)
            self.assertEqual(run["lane_prefix_ids"], [])
            self.assertEqual(run["external_status"], "bounded_unknown")
            self.assertEqual(run["result_status"], "no_solution_within_budget")

    def test_packaging_and_fusion_bootstrap_declare_scip_runtime(self) -> None:
        helper = (ROOT / "scripts" / "fusion" / "_fusion_helpers.ps1").read_text(encoding="utf-8")
        palette = (
            ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "palette_project.py"
        ).read_text(encoding="utf-8")
        manifest = json.loads(
            (
                ROOT
                / "fusion_addin"
                / "BoardGameInsertGenerator"
                / "BoardGameInsertGenerator.manifest"
            ).read_text(encoding="utf-8")
        )
        self.assertIn("Expand-BgigScipRuntime", helper)
        self.assertIn(SCIP_PRODUCT_ARCHIVE_SHA256, helper)
        self.assertIn("configure_scip_product_runtime", palette)
        self.assertIn('scip_vendor / "runtime"', palette)
        self.assertEqual(manifest["version"], "0.1.61")


if __name__ == "__main__":
    unittest.main()
