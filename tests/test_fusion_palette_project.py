import json
import sys
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from board_game_insert_generator.project_v1 import blank_project_v1


ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / "fusion_addin" / "BoardGameInsertGenerator"

sys.path.insert(0, str(ADDIN))

import palette_project as palette_project_module  # noqa: E402
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

    def test_explicit_save_is_atomic_but_next_session_starts_blank(self) -> None:
        project = blank_project_v1()
        project_name = "Éléments d’été — boîte à dés"
        project["project_name"] = project_name
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            path = Path(temp_dir) / "projet-explicite.bgig.json"
            saved = handle_palette_request(
                request(
                    "save_project_as",
                    project=project,
                    document_path=str(path),
                ),
                ADDIN,
                ROOT,
            )
            loaded = handle_palette_request(request("load_project"), ADDIN, ROOT)
            raw = path.read_text(encoding="utf-8")

            self.assertTrue(path.is_file())
            self.assertFalse(path.with_suffix(path.suffix + ".tmp").exists())
            self.assertIn(project_name, raw)
            self.assertEqual(json.loads(raw)["project_name"], project_name)
            self.assertFalse((Path(temp_dir) / CURRENT_PROJECT_FILENAME).exists())

        self.assertTrue(saved["saved"])
        self.assertFalse(saved["recovery_saved"])
        self.assertNotEqual(loaded["project"]["project_name"], project_name)
        self.assertEqual(loaded["document"]["current_path"], "")
        self.assertEqual(
            loaded["document"]["session_start_policy"],
            "fresh_unsaved_project",
        )

    def test_open_migrates_historical_flat_origin_without_rewriting_named_source(self) -> None:
        project = blank_project_v1()
        project["flat_items"] = [
            {
                "id": "board",
                "name": "Plateau",
                "kind": "board",
                "dimensions_mm": {"x": 100.0, "y": 80.0, "z": 2.0},
                "quantity": 1,
                "stack_order": None,
                "origin_mm": {"x": 12.0, "y": 8.0},
                "rotation_deg_z": 0,
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            "os.environ",
            {"BGIG_USER_DATA_DIR": temp_dir},
        ):
            source = Path(temp_dir) / "historique.bgig.json"
            source.write_text(json.dumps(project), encoding="utf-8")
            before = source.read_text(encoding="utf-8")

            loaded = handle_palette_request(
                request(
                    "open_project_file",
                    document_path=str(source),
                ),
                ADDIN,
                ROOT,
            )

            self.assertEqual(source.read_text(encoding="utf-8"), before)

        self.assertTrue(loaded["migrated"])
        self.assertIsNone(loaded["project"]["flat_items"][0]["origin_mm"])
        self.assertEqual(loaded["lifecycle"]["derived"], "current")
        self.assertTrue(
            any("placement automatique" in warning for warning in loaded["warnings"])
        )

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

    def test_validate_returns_local_analysis_without_invoking_global_solver(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {
                "id": "g",
                "name": "Bac",
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
            }
        ]
        project["contents"] = [
            {
                "id": "c",
                "name": "Pieces",
                "shape_kind": "square",
                "dimensions_mm": {"x": 12, "y": 12, "z": 3},
                "quantity": 2,
                "container_group_id": "g",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
        ]
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}),
            patch(
                "board_game_insert_generator.partition_solver.solve_partition_plan"
            ) as global_solver,
        ):
            response = handle_palette_request(
                request("validate_project", project=project),
                ADDIN,
                ROOT,
            )

        global_solver.assert_not_called()
        self.assertEqual(
            response["local_analysis"]["schema_version"],
            "bgig.contextual_local_analysis.v1",
        )
        self.assertIsNone(response["partition"])
        self.assertEqual(
            response["local_analysis"]["invariants"][
                "global_solver_invocation_count"
            ],
            0,
        )
        self.assertFalse(
            response["local_analysis"]["reactive_global_bounds"][
                "placement_performed"
            ]
        )

    def test_validate_reuses_untouched_container_analysis_between_edits(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {
                "id": group_id,
                "name": group_id,
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
            }
            for group_id in ("g1", "g2")
        ]
        project["contents"] = [
            {
                "id": asset_id,
                "name": asset_id,
                "shape_kind": "square",
                "dimensions_mm": {"x": 12, "y": 12, "z": 3},
                "quantity": 2,
                "container_group_id": group_id,
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
            for asset_id, group_id in (("a1", "g1"), ("a2", "g2"))
        ]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            "os.environ", {"BGIG_USER_DATA_DIR": temp_dir}
        ):
            first = handle_palette_request(
                request("validate_project", project=project),
                ADDIN,
                ROOT,
            )
            changed = deepcopy(project)
            changed["contents"][0]["quantity"] = 3
            second = handle_palette_request(
                request("validate_project", project=changed),
                ADDIN,
                ROOT,
            )

        before = {
            value["container_group_id"]: value["frontier_digest"]
            for value in first["local_analysis"]["containers"]
        }
        after = {
            value["container_group_id"]: value["frontier_digest"]
            for value in second["local_analysis"]["containers"]
        }
        incremental = second["local_analysis"]["incremental"]
        self.assertEqual(
            incremental["recomputed_frontier_group_ids"],
            ["g1"],
        )
        self.assertEqual(
            incremental["recomputed_context_group_ids"],
            ["g1"],
        )
        self.assertIn("g2", incremental["reused_frontier_group_ids"])
        self.assertEqual(before["g2"], after["g2"])
        self.assertNotEqual(before["g1"], after["g1"])

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

    def test_validate_new_container_stales_plan_until_explicit_calculation(self) -> None:
        project = blank_project_v1()
        project["box"]["inner_dimensions_mm"] = {
            "x": 120.0,
            "y": 120.0,
            "z": 30.0,
        }
        project["box"]["usable_height_mm"] = 30.0
        project["container_groups"] = [
            {
                "id": "g",
                "name": "Bac",
                "wall_thickness_mm": 2.0,
                "floor_thickness_mm": 2.0,
            }
        ]
        project["contents"] = [
            {
                "id": "a",
                "name": "A",
                "shape_kind": "rectangle",
                "dimensions_mm": {"x": 40.0, "y": 40.0, "z": 10.0},
                "quantity": 1,
                "container_group_id": "g",
                "content_clearance_mm": 0.0,
                "measurement_confidence": "exact",
            }
        ]
        changed = deepcopy(project)
        changed["container_groups"].append(
            {
                "id": "g2",
                "name": "Nouveau bac",
                "wall_thickness_mm": 2.0,
                "floor_thickness_mm": 2.0,
            }
        )
        changed["contents"].append(
            {
                "id": "b",
                "name": "B",
                "shape_kind": "rectangle",
                "dimensions_mm": {"x": 8.0, "y": 8.0, "z": 8.0},
                "quantity": 1,
                "container_group_id": "g2",
                "content_clearance_mm": 0.0,
                "measurement_confidence": "exact",
            }
        )
        settings = {"method": "auto", "effort": "quick"}
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            "os.environ",
            {"BGIG_USER_DATA_DIR": temp_dir},
        ):
            solved = handle_palette_request(
                request("solve_project", project=project, solver_settings=settings),
                ADDIN,
                ROOT,
            )
            with patch(
                "board_game_insert_generator.minimal_layout_solver.solve_minimal_layout",
                side_effect=AssertionError("validate must not run the global solver"),
            ):
                invalidated = handle_palette_request(
                    request(
                        "validate_project",
                        project=changed,
                        solver_settings=settings,
                    ),
                    ADDIN,
                    ROOT,
                )

        self.assertIsNotNone(solved["partition"])
        self.assertIsNone(invalidated["partition"])
        staged = invalidated["staged_calculation"]
        self.assertEqual(staged["minimal_layout"]["status"], "stale")
        self.assertEqual(staged["finalized_plan"]["status"], "not_finalized")
        self.assertEqual(staged["next_action"], "calculate_layout")
        self.assertTrue(staged["invariants"]["automatic_plan_reuse_disabled"])
        self.assertNotIn("local_reuse", staged)
        self.assertNotIn("global_void_reuse", staged)
        self.assertEqual(
            invalidated["operation_activity"]["stop_reason"],
            "local_analysis_ready",
        )

    def test_validate_added_content_stales_plan_without_republishing_placements(self) -> None:
        project = blank_project_v1()
        project["box"]["inner_dimensions_mm"] = {
            "x": 120.0,
            "y": 120.0,
            "z": 30.0,
        }
        project["box"]["usable_height_mm"] = 30.0
        project["container_groups"] = [
            {
                "id": "g",
                "name": "Bac",
                "wall_thickness_mm": 2.0,
                "floor_thickness_mm": 2.0,
            }
        ]

        def content(identifier: str, dimensions: tuple[float, float, float]) -> dict[str, object]:
            return {
                "id": identifier,
                "name": identifier.upper(),
                "shape_kind": "rectangle",
                "dimensions_mm": dict(zip(("x", "y", "z"), dimensions)),
                "quantity": 1,
                "container_group_id": "g",
                "content_clearance_mm": 0.0,
                "measurement_confidence": "exact",
            }

        project["contents"] = [
            content("a", (40.0, 40.0, 10.0)),
            content("b", (10.0, 20.0, 10.0)),
        ]
        changed = deepcopy(project)
        changed["contents"].append(content("c", (8.0, 16.0, 8.0)))
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            "os.environ",
            {"BGIG_USER_DATA_DIR": temp_dir},
        ):
            handle_palette_request(
                request(
                    "solve_project",
                    project=project,
                    solver_settings={"method": "auto", "effort": "quick"},
                ),
                ADDIN,
                ROOT,
            )
            with patch(
                "board_game_insert_generator.minimal_layout_solver.solve_minimal_layout",
                side_effect=AssertionError("validate must not run the global solver"),
            ):
                response = handle_palette_request(
                    request(
                        "validate_project",
                        project=changed,
                        solver_settings={"method": "auto", "effort": "quick"},
                    ),
                    ADDIN,
                    ROOT,
                )

        self.assertIsNone(response["partition"])
        staged = response["staged_calculation"]
        self.assertEqual(staged["minimal_layout"]["status"], "stale")
        self.assertEqual(staged["next_action"], "calculate_layout")
        self.assertTrue(staged["invariants"]["automatic_plan_reuse_disabled"])
        self.assertNotIn("local_reuse", staged)
        self.assertNotIn("global_void_reuse", staged)
    def test_solve_project_returns_the_minimal_layout_without_saving_implicitly(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [{"id": "c", "name": "Pieces", "shape_kind": "square", "dimensions_mm": {"x": 12, "y": 12, "z": 3}, "quantity": 2, "container_group_id": "g", "content_clearance_mm": None, "measurement_confidence": "exact"}]
        project_before = deepcopy(project)
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("solve_project", project=project), ADDIN, ROOT)
            cached = handle_palette_request(request("solve_project", project=project), ADDIN, ROOT)
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
        staged = response["staged_calculation"]
        self.assertEqual(staged["global_layout"]["status"], "current")
        self.assertTrue(staged["global_layout"]["placement_certified"])
        self.assertEqual(staged["finalized_plan"]["status"], "not_finalized")
        self.assertEqual(staged["next_action"], "materialize_minimal_in_fusion")
        self.assertTrue(response["result_view"]["materializable"])
        self.assertTrue(
            response["result_view"]["invariants"][
                "minimal_materialization_without_finalization"
            ]
        )
        self.assertFalse(response["partition"]["invariants"]["residual_distributed"])
        self.assertFalse(response["saved"])
        self.assertEqual(
            response["operation_activity"]["result_timing"]["result_source"],
            "fresh_search",
        )
        self.assertEqual(
            cached["operation_activity"]["result_timing"]["result_source"],
            "certified_cache",
        )
        self.assertEqual(
            cached["operation_activity"]["result_timing"]["search_elapsed_ms"],
            response["operation_activity"]["result_timing"]["search_elapsed_ms"],
        )
        self.assertIsInstance(
            cached["operation_activity"]["result_timing"]["retrieval_elapsed_ms"],
            int,
        )

    def test_materialize_and_regenerate_return_the_same_explicit_minimal_plan(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [{"id": "c", "name": "Pieces", "shape_kind": "square", "dimensions_mm": {"x": 12, "y": 12, "z": 3}, "quantity": 2, "container_group_id": "g", "content_clearance_mm": None, "measurement_confidence": "exact"}]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            solved = handle_palette_request(request("solve_project", project=project), ADDIN, ROOT)
            generated = handle_palette_request(
                request("materialize_project", project=project, artifact_kind="minimal_layout"),
                ADDIN,
                ROOT,
            )
            regenerated = handle_palette_request(
                request("regenerate_project", project=project, artifact_kind="minimal_layout"),
                ADDIN,
                ROOT,
            )

        self.assertEqual(solved["staged_calculation"]["finalized_plan"]["status"], "not_finalized")
        self.assertEqual(generated["cad_build"]["status"], "ready_for_fusion")
        self.assertEqual(generated["cad_build"]["materialization"]["component_count"], 1)
        self.assertEqual(generated["cad_build"]["materialization"]["automatic_body_count"], 0)
        self.assertEqual(generated["cad_build"]["cad_ir_digest"], regenerated["cad_build"]["cad_ir_digest"])
        self.assertEqual(generated["partition"]["plan_digest"], generated["cad_build"]["source_plan_digest"])
        self.assertEqual(generated["cad_build"]["artifact_identity"]["artifact_kind"], "minimal_layout")
        self.assertEqual(generated["result_view"]["artifact_kind"], "minimal_layout")
        self.assertTrue(generated["result_view"]["materializable"])
        self.assertTrue(
            generated["result_view"]["invariants"]["selected_artifact_identity_exact"]
        )
        self.assertEqual(
            generated["cad_build"]["artifact_identity"],
            generated["cad_build"]["cad_ir"]["metadata"]["artifact_identity"],
        )

    def test_finalize_then_materialize_uses_exact_finalized_artifact(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {
                "id": "g",
                "name": "Bac",
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
            }
        ]
        project["contents"] = [
            {
                "id": "c",
                "name": "Pieces",
                "shape_kind": "square",
                "dimensions_mm": {"x": 12, "y": 12, "z": 3},
                "quantity": 2,
                "container_group_id": "g",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            "os.environ", {"BGIG_USER_DATA_DIR": temp_dir}
        ):
            handle_palette_request(
                request("solve_project", project=project), ADDIN, ROOT
            )
            finalized = handle_palette_request(
                request(
                    "finalize_project",
                    project=project,
                    finishing_effort="long",
                ),
                ADDIN,
                ROOT
            )
            materialized = handle_palette_request(
                request(
                    "materialize_project",
                    project=project,
                    artifact_kind="finalized_plan",
                ),
                ADDIN,
                ROOT,
            )

        self.assertEqual(finalized["status"], "ready")
        self.assertEqual(
            finalized["operation_activity"]["stop_reason"],
            "finalized_plan_ready",
        )
        self.assertEqual(
            finalized["operation_activity"]["result_timing"][
                "schema_version"
            ],
            "bgig.finalization_stop_diagnostics.v1",
        )
        self.assertEqual(
            finalized["operation_activity"]["result_timing"][
                "outcome_kind"
            ],
            "success",
        )
        self.assertEqual(
            finalized["staged_calculation"]["finalized_plan"]["status"],
            "current",
        )
        self.assertEqual(
            finalized["staged_calculation"]["finalized_plan"][
                "finishing_effort_profile"
            ],
            "long",
        )
        self.assertEqual(
            finalized["partition"]["finalization"]["budget"]["limits"][
                "max_total_elapsed_ms"
            ],
            60_000,
        )
        self.assertEqual(finalized["result_view"]["artifact_kind"], "finalized_plan")
        self.assertTrue(
            finalized["result_view"]["invariants"][
                "coupled_finalization_globally_certified"
            ]
        )
        self.assertEqual(materialized["cad_build"]["status"], "ready_for_fusion")
        self.assertEqual(
            materialized["cad_build"]["artifact_identity"]["artifact_kind"],
            "finalized_plan",
        )
        self.assertEqual(
            materialized["partition"]["finalization"][
                "global_resolve_invocation_count"
            ],
            1,
        )
        certificate = materialized["partition"]["finalization"][
            "global_partition_certificate"
        ]
        self.assertTrue(certificate["certified"])
        self.assertTrue(certificate["partition_complete_by_construction"])
        self.assertEqual(certificate["printable_residual_volume_mm3"], 0.0)

    def test_finalization_without_minimal_returns_explainable_ready_result(
        self,
    ) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {
                "id": "g",
                "name": "Bac",
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
            }
        ]
        project["contents"] = [
            {
                "id": "c",
                "name": "Pieces",
                "shape_kind": "square",
                "dimensions_mm": {"x": 12, "y": 12, "z": 3},
                "quantity": 2,
                "container_group_id": "g",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            "os.environ", {"BGIG_USER_DATA_DIR": temp_dir}
        ):
            response = handle_palette_request(
                request(
                    "finalize_project",
                    project=project,
                    finishing_effort="quick",
                ),
                ADDIN,
                ROOT,
            )

        self.assertEqual(response["status"], "ready")
        self.assertIsNone(response["partition"])
        self.assertEqual(
            response["operation_activity"]["stop_reason"],
            "minimal_layout_missing_or_stale",
        )
        diagnostics = response["solver_result"]["stop_diagnostics"]
        self.assertEqual(
            diagnostics["outcome_kind"],
            "prerequisite_missing",
        )
        self.assertEqual(
            response["operation_activity"]["result_timing"],
            diagnostics,
        )
        self.assertEqual(diagnostics["elapsed_ms"], 0)
        self.assertEqual(diagnostics["budget_cap_ms"], 3_000)
        self.assertTrue(diagnostics["stopped_before_cap"])
        self.assertFalse(diagnostics["proof_of_impossibility"])

    def test_materialization_is_rejected_without_an_explicit_minimal_calculation(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [{"id": "c", "name": "Pieces", "shape_kind": "square", "dimensions_mm": {"x": 12, "y": 12, "z": 3}, "quantity": 2, "container_group_id": "g", "content_clearance_mm": None, "measurement_confidence": "exact"}]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            response = handle_palette_request(request("materialize_project", project=project), ADDIN, ROOT)

        self.assertEqual(response["status"], "invalid")
        self.assertIsNone(response["cad_build"])
        self.assertIn("calcule", " ".join(response["errors"]).lower())

    def test_bridge_import_and_materialize_an_explicit_legacy_complement_in_session(self) -> None:
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
            handle_palette_request(
                request("solve_project", project=imported["project"]),
                ADDIN,
                ROOT,
            )
            materialized = handle_palette_request(
                request("materialize_project", project=imported["project"]),
                ADDIN,
                ROOT,
            )

        legacy = imported["project"]["fill_elements"]
        self.assertEqual(imported["status"], "ready")
        self.assertEqual(legacy[0]["id"], "legacy-solid")
        self.assertEqual(legacy[0]["kind"], "solid")
        self.assertEqual(legacy[0]["mode"], "exact")
        self.assertEqual(materialized["cad_build"]["status"], "ready_for_fusion")
        self.assertEqual(materialized["cad_build"]["materialization"]["explicit_complement_component_count"], 1)

    def test_fixed_minima_can_close_the_residual_and_materialize(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [{"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}]
        project["contents"] = [{"id": "c", "name": "Pieces", "shape_kind": "square", "dimensions_mm": {"x": 12, "y": 12, "z": 3}, "quantity": 2, "container_group_id": "g", "content_clearance_mm": None, "measurement_confidence": "exact"}]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            baseline = handle_palette_request(request("solve_project", project=project), ADDIN, ROOT)
            minimum = baseline["partition"]["placements"][0]["minimum_outer_envelope_mm"]
            project["container_groups"][0]["expansion_axes"] = {"x": False, "y": False, "z": False}
            project["container_groups"][0]["locked_outer_dimensions_mm"] = minimum
            response = handle_palette_request(request("solve_project", project=project), ADDIN, ROOT)
            finalized = handle_palette_request(request("finalize_project", project=project), ADDIN, ROOT)
            materialized = handle_palette_request(
                request("materialize_project", project=project, artifact_kind="minimal_layout"),
                ADDIN,
                ROOT,
            )

        self.assertEqual(response["partition"]["summary"]["status"], "constructed")
        self.assertTrue(response["result_view"]["materializable"])
        self.assertFalse(response["partition"]["invariants"]["residual_distributed"])
        self.assertEqual(response["partition"]["residuals"]["status"], "unassigned")
        self.assertEqual(finalized["status"], "ready")
        self.assertEqual(
            finalized["operation_activity"]["stop_reason"],
            "finalized_plan_ready",
        )
        self.assertIsNotNone(finalized["partition"])
        self.assertEqual(
            finalized["staged_calculation"]["finalized_plan"]["status"],
            "current",
        )
        self.assertTrue(
            finalized["staged_calculation"]["finalized_plan"]["materializable"]
        )
        self.assertEqual(
            finalized["solver_result"]["status"],
            "solution_found",
        )
        self.assertTrue(
            finalized["partition"]["invariants"]["residual_distributed"]
        )
        self.assertEqual(
            finalized["partition"]["residuals"]["residual_volume_mm3"],
            0.0,
        )
        self.assertEqual(materialized["cad_build"]["status"], "ready_for_fusion")

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
            document_path = Path(temp_dir) / "projet-valide.bgig.json"
            handle_palette_request(
                request(
                    "save_project_as",
                    project=valid,
                    document_path=str(document_path),
                ),
                ADDIN,
                ROOT,
            )
            invalid = dict(valid)
            invalid["project_name"] = ""
            response = handle_palette_request(
                request("save_document", project=invalid),
                ADDIN,
                ROOT,
            )
            persisted = json.loads(document_path.read_text(encoding="utf-8"))

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

        self.assertFalse(imported["saved"])
        self.assertFalse(imported["recovery_saved"])
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

    def test_bridge_rejects_same_kind_already_active(self) -> None:
        from board_game_insert_generator.operation_activity import (
            begin_operation_activity,
        )

        active = begin_operation_activity(
            action="validate_project",
            operation_id="analysis-active",
            source_revision=4,
            started_at_ms=900,
        ).activity
        key = (str(ADDIN.resolve()), "local_analysis")
        with palette_project_module._ACTIVE_OPERATION_LOCK:
            palette_project_module._ACTIVE_OPERATIONS[key] = active
        try:
            response = handle_palette_request(
                request(
                    "validate_project",
                    project=blank_project_v1(),
                    source_revision=4,
                    operation_started_at_ms=1_000,
                ),
                ADDIN,
                ROOT,
            )
        finally:
            with palette_project_module._ACTIVE_OPERATION_LOCK:
                palette_project_module._ACTIVE_OPERATIONS.pop(key, None)

        activity = response["operation_activity"]
        self.assertEqual(response["status"], "busy")
        self.assertEqual(activity["status"], "rejected")
        self.assertEqual(
            activity["stop_reason"],
            "same_operation_already_active",
        )
        self.assertEqual(
            activity["conflicting_operation_id"],
            "analysis-active",
        )

    def test_operation_reason_exposes_scip_timeout_instead_of_generic_portfolio(self) -> None:
        response = {
            "status": "ready",
            "solver_result": {
                "status": "no_solution_within_budget",
                "telemetry": {"stop_reason": "bounded_portfolio_exhausted"},
            },
            "partition": {
                "solver": {
                    "search": {
                        "external_lane": {"status": "bounded_unknown"},
                    }
                }
            },
        }
        self.assertEqual(
            palette_project_module._operation_stop_reason("solve_project", response),
            "scip_3d_time_limit_without_certified_solution",
        )
    def test_bridge_exposes_exact_terminal_activity_without_fake_progress(self) -> None:
        project = blank_project_v1()
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}),
            patch("palette_project._now_ms", return_value=1_300),
        ):
            response = handle_palette_request(
                request(
                    "validate_project",
                    project=project,
                    source_revision=4,
                    operation_started_at_ms=1_000,
                ),
                ADDIN,
                ROOT,
            )

        activity = response["operation_activity"]
        self.assertEqual(activity["schema_version"], "bgig.operation_activity.v1")
        self.assertEqual(activity["operation_id"], "test-validate_project")
        self.assertEqual(activity["operation_kind"], "local_analysis")
        self.assertEqual(activity["source_revision"], 4)
        self.assertEqual(activity["status"], "completed")
        self.assertEqual(activity["elapsed_ms"], 300)
        self.assertTrue(activity["stop_reason"])
        self.assertFalse(activity["cancel_supported"])
        self.assertNotIn("percentage", activity)
        self.assertNotIn("eta", activity)

    def test_rejects_unversioned_and_unknown_messages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            malformed = handle_palette_request([], ADDIN, ROOT)
            missing_id = handle_palette_request({"schema": PALETTE_REQUEST_SCHEMA, "action": "load_project"}, ADDIN, ROOT)
            missing_schema = handle_palette_request({"request_id": "x", "action": "load_project"}, ADDIN, ROOT)
            unknown = handle_palette_request(request("delete_everything"), ADDIN, ROOT)
            autosave = handle_palette_request(
                request("autosave_project", project=blank_project_v1()),
                ADDIN,
                ROOT,
            )

        self.assertEqual(malformed["status"], "invalid")
        self.assertEqual(missing_id["status"], "invalid")
        self.assertEqual(missing_schema["status"], "invalid")
        self.assertEqual(unknown["status"], "invalid")
        self.assertEqual(autosave["status"], "invalid")


    def test_named_document_save_preserves_accents_but_restart_is_blank(self) -> None:
        project = blank_project_v1()
        project["project_name"] = "Éléments d’été — boîte à dés"
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            document_path = Path(temp_dir) / "Été jeux.bgig.json"
            saved_as = handle_palette_request(
                request("save_project_as", project=project, document_path=str(document_path)), ADDIN, ROOT
            )
            changed = deepcopy(saved_as["project"])
            changed["project_name"] = "Été jeux — révision"
            saved = handle_palette_request(request("save_document", project=changed), ADDIN, ROOT)
            loaded = handle_palette_request(request("load_project"), ADDIN, ROOT)

            self.assertTrue(document_path.is_file())
            self.assertEqual(json.loads(document_path.read_text(encoding="utf-8"))["project_name"], changed["project_name"])
            self.assertFalse((Path(temp_dir) / CURRENT_PROJECT_FILENAME).exists())
            self.assertEqual(loaded["document"]["current_path"], "")
            self.assertEqual(loaded["document"]["current_name"], "")
            self.assertIn(str(document_path.resolve()), [item["path"] for item in loaded["document"]["recent_documents"]])

        self.assertTrue(saved_as["saved"])
        self.assertFalse(saved_as["recovery_saved"])
        self.assertTrue(saved["saved"])
        self.assertFalse(saved["recovery_saved"])
        self.assertNotEqual(loaded["project"]["project_name"], changed["project_name"])

    def test_new_project_clears_current_named_document_without_overwriting_it(self) -> None:
        project = blank_project_v1()
        project["project_name"] = "Projet à préserver"
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            document_path = Path(temp_dir) / "à préserver.bgig.json"
            handle_palette_request(
                request("save_project_as", project=project, document_path=str(document_path)), ADDIN, ROOT
            )
            new_project = handle_palette_request(request("new_project"), ADDIN, ROOT)
            attempted_save = handle_palette_request(
                request("save_document", project=new_project["project"]), ADDIN, ROOT
            )
            persisted = json.loads(document_path.read_text(encoding="utf-8"))

        self.assertEqual(new_project["document"]["current_path"], "")
        self.assertEqual(attempted_save["status"], "invalid")
        self.assertEqual(persisted["project_name"], "Projet à préserver")

    def test_open_recent_document_is_restricted_to_known_documents_and_preserves_named_file(self) -> None:
        original = blank_project_v1()
        original["project_name"] = "Original nommé"
        opened = blank_project_v1()
        opened["project_name"] = "Document externe"
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            named_path = Path(temp_dir) / "original.bgig.json"
            external_path = Path(temp_dir) / "externe.bgig.json"
            external_path.write_text(json.dumps(opened, ensure_ascii=False), encoding="utf-8")
            handle_palette_request(
                request("save_project_as", project=original, document_path=str(named_path)), ADDIN, ROOT
            )
            opened_response = handle_palette_request(
                request("open_project_file", project=original, document_path=str(external_path)), ADDIN, ROOT
            )
            recent_response = handle_palette_request(
                request("open_recent_project", project=opened_response["project"], document_path=str(named_path)), ADDIN, ROOT
            )
            unknown = handle_palette_request(
                request("open_recent_project", project=opened_response["project"], document_path=str(Path(temp_dir) / "inconnu.bgig.json")),
                ADDIN,
                ROOT,
            )

            self.assertEqual(json.loads(external_path.read_text(encoding="utf-8"))["project_name"], "Document externe")
            self.assertEqual(recent_response["project"]["project_name"], "Original nommé")

        self.assertEqual(opened_response["project"]["project_name"], "Document externe")
        self.assertEqual(opened_response["document"]["current_path"], str(external_path.resolve()))
        self.assertEqual(unknown["status"], "invalid")


    def test_p64_h08_persists_solver_choices_locally_without_project_autosave(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {"id": "g", "name": "Bac", "wall_thickness_mm": None, "floor_thickness_mm": None}
        ]
        project["contents"] = [{
            "id": "asset", "name": "Pions", "shape_kind": "custom",
            "dimensions_mm": {"x": 20, "y": 20, "z": 10}, "quantity": 1,
            "container_group_id": "g", "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}):
            saved_settings = handle_palette_request(
                request("save_solver_settings", solver_settings={"method": "stage_stack", "effort": "deep"}),
                ADDIN,
                ROOT,
            )
            saved_finishing = handle_palette_request(
                request(
                    "save_finishing_settings",
                    project=project,
                    finishing_effort="long",
                ),
                ADDIN,
                ROOT,
            )
            raw_state = json.loads((Path(temp_dir) / "bgig_document_state_v1.json").read_text(encoding="utf-8"))
            solved = handle_palette_request(
                request(
                    "solve_project",
                    project=project,
                    solver_settings={"method": "stage_stack", "effort": "deep"},
                ),
                ADDIN,
                ROOT,
            )
            reloaded = handle_palette_request(request("load_project"), ADDIN, ROOT)

            self.assertFalse((Path(temp_dir) / CURRENT_PROJECT_FILENAME).exists())
        self.assertEqual(saved_settings["solver_settings"], {"method": "stage_stack", "effort": "deep"})
        self.assertEqual(raw_state["solver_settings"], {"method": "stage_stack", "effort": "deep"})
        self.assertEqual(saved_finishing["finishing_effort"], "long")
        self.assertEqual(raw_state["finishing_effort"], "long")
        self.assertEqual(solved["solver_settings"], {"method": "stage_stack", "effort": "deep"})
        self.assertEqual(solved["partition"]["solver"]["kind"], "bounded_minimal_layout_solver")
        self.assertEqual(solved["partition"]["minimal_layout"]["search_provenance"]["effort_profile"], "deep")
        self.assertEqual(reloaded["solver_settings"], {"method": "stage_stack", "effort": "deep"})
        self.assertEqual(reloaded["finishing_effort"], "long")

    def test_cross_session_certified_witness_reuse_and_storage_are_disabled(self) -> None:
        project = blank_project_v1()
        project["project_name"] = "Calcul frais"
        project["container_groups"] = [
            {
                "id": "g",
                "name": "Bac",
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
            }
        ]
        project["contents"] = [
            {
                "id": "asset",
                "name": "Pions",
                "shape_kind": "square",
                "dimensions_mm": {"x": 12, "y": 12, "z": 3},
                "quantity": 2,
                "container_group_id": "g",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
        ]
        settings = {"method": "auto", "effort": "quick"}
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch.dict("os.environ", {"BGIG_USER_DATA_DIR": temp_dir}),
        ):
            first = handle_palette_request(
                request(
                    "solve_project",
                    project=project,
                    solver_settings=settings,
                    source_revision=1,
                ),
                ADDIN,
                ROOT,
            )
            palette_project_module._STAGED_CALCULATION_SESSIONS.clear()
            palette_project_module._LOCAL_ANALYSIS_ENGINES.clear()
            second = handle_palette_request(
                request(
                    "solve_project",
                    project=project,
                    solver_settings=settings,
                    source_revision=2,
                ),
                ADDIN,
                ROOT,
            )
            self.assertEqual(first["status"], "ready")
            self.assertEqual(second["status"], "ready")
            self.assertEqual(
                first["certified_plan_witness"]["load"],
                second["certified_plan_witness"]["load"],
            )
            self.assertEqual(
                first["certified_plan_witness"]["load"]["status"],
                "disabled",
            )
            self.assertEqual(
                first["certified_plan_witness"]["store"]["status"],
                "disabled",
            )
            self.assertEqual(
                second["staged_calculation"]["minimal_layout"][
                    "calculation_timing"
                ]["result_source"],
                "fresh_search",
            )
            self.assertFalse(
                (Path(temp_dir) / "certified-witnesses").exists()
            )
        palette_project_module._STAGED_CALCULATION_SESSIONS.clear()
        palette_project_module._LOCAL_ANALYSIS_ENGINES.clear()

    def test_p64_l05b_captures_a_local_solver_case_without_domain_operations(self) -> None:
        from board_game_insert_generator.staged_calculation import (
            StagedCalculationSession,
        )

        project = blank_project_v1()
        project["project_name"] = "Mon insert"
        project["container_groups"] = [
            {
                "id": "g",
                "name": "Bac",
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
            }
        ]
        project["contents"] = [
            {
                "id": "asset",
                "name": "Pions",
                "shape_kind": "square",
                "dimensions_mm": {"x": 12, "y": 12, "z": 3},
                "quantity": 2,
                "container_group_id": "g",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
        ]
        settings = {"method": "auto", "effort": "quick"}
        interaction_events = [
            {
                "sequence": 1,
                "event_type": "field_changed",
                "ui_field": "contents.quantity",
                "object_id": "asset",
                "source_revision": 7,
                "elapsed_ms": 25,
                "value": "private",
                "password": "private",
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            "os.environ", {"BGIG_USER_DATA_DIR": temp_dir}
        ):
            solved = handle_palette_request(
                request(
                    "solve_project",
                    project=project,
                    solver_settings=settings,
                    source_revision=7,
                ),
                ADDIN,
                ROOT,
            )
            self.assertEqual(solved["status"], "ready")
            self.assertIsNotNone(solved["partition"])
            changed = deepcopy(project)
            changed["container_groups"].append(
                {
                    "id": "g2",
                    "name": "Bac hors limite",
                    "wall_thickness_mm": None,
                    "floor_thickness_mm": None,
                }
            )
            changed["contents"].append(
                {
                    "id": "oversized",
                    "name": "Hors limite",
                    "shape_kind": "square",
                    "dimensions_mm": {"x": 1000, "y": 1000, "z": 1000},
                    "quantity": 1,
                    "container_group_id": "g2",
                    "content_clearance_mm": None,
                    "measurement_confidence": "exact",
                }
            )
            rejected = handle_palette_request(
                request(
                    "validate_project",
                    project=changed,
                    solver_settings=settings,
                    source_revision=8,
                ),
                ADDIN,
                ROOT,
            )
            self.assertEqual(
                rejected["staged_calculation"]["minimal_layout"]["status"],
                "stale",
            )
            with (
                patch.object(
                    StagedCalculationSession,
                    "calculate_layout",
                    side_effect=AssertionError("capture invoked global solve"),
                ),
                patch.object(
                    StagedCalculationSession,
                    "finalize_volume",
                    side_effect=AssertionError("capture invoked finalization"),
                ),
                patch.object(
                    StagedCalculationSession,
                    "select_materializable_artifact",
                    side_effect=AssertionError("capture selected CAD artifact"),
                ),
                patch(
                    "board_game_insert_generator.partition_cad.build_partition_cad",
                    side_effect=AssertionError("capture invoked CAD build"),
                ),
            ):
                captured = handle_palette_request(
                    request(
                        "capture_solver_case",
                        project=changed,
                        solver_settings=settings,
                        source_revision=8,
                        captured_at_ms=123456,
                        interaction_events=interaction_events,
                        client_context={
                            "scene_present": True,
                            "dirty": False,
                            "solved_stale": False,
                            "document_path": "C:/private/Mon insert.bgig.json",
                            "scene_artifact_identity": {
                                "schema_version": "bgig.artifact_identity.v1",
                                "artifact_kind": "minimal_layout",
                                "artifact_digest": "a" * 64,
                                "partition_plan_digest": solved["partition"]["plan_digest"],
                                "cad_ir_digest": "b" * 64,
                                "source_revision": 7,
                                "document_path": "C:/private/scene.f3d",
                            },
                        },
                    ),
                    ADDIN,
                    ROOT,
                )
            bundle_path = Path(captured["export_path"])
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))

            self.assertEqual(bundle_path.parent, Path(temp_dir) / "solver-cases")
            self.assertTrue(bundle_path.is_file())
            self.assertFalse(bundle_path.with_suffix(bundle_path.suffix + ".tmp").exists())

        self.assertEqual(captured["status"], "ready")
        self.assertEqual(
            captured["operation_activity"]["operation_kind"],
            "solver_case_capture",
        )
        self.assertEqual(
            captured["operation_activity"]["stop_reason"],
            "solver_case_bundle_exported",
        )
        self.assertIsNone(captured["partition"])
        self.assertIsNone(captured["cad_build"])
        self.assertEqual(
            captured["solver_case_capture"]["schema_version"],
            "bgig.solver_case_bundle.v1",
        )
        self.assertTrue(captured["solver_case_capture"]["has_observed_partition"])
        self.assertTrue(captured["solver_case_capture"]["has_certified_plan"])
        self.assertFalse(
            captured["solver_case_capture"]["automatic_solver_modification"]
        )
        self.assertEqual(bundle["project"]["project_name"], "Mon insert")
        captured_staged = bundle["solver_case_state"]["staged_calculation"]
        self.assertEqual(captured_staged["minimal_layout"]["status"], "stale")
        self.assertNotIn("local_reuse", captured_staged)
        self.assertNotIn("global_void_reuse", captured_staged)
        self.assertEqual(bundle["interaction_trace"]["event_count"], 1)
        self.assertEqual(
            set(bundle["interaction_trace"]["events"][0]),
            {
                "sequence",
                "event_type",
                "ui_field",
                "object_id",
                "source_revision",
                "elapsed_ms",
            },
        )
        encoded = json.dumps(bundle, sort_keys=True).lower()
        self.assertNotIn("password", encoded)
        self.assertNotIn("c:/private", encoded)
        self.assertFalse(bundle["invariants"]["automatic_solver_modification"])

if __name__ == "__main__":
    unittest.main()
