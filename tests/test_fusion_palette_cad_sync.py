from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
sys.path.insert(0, str(ADDIN))

import BoardGameInsertGenerator as entrypoint  # noqa: E402
from fusion_skeleton import (  # noqa: E402
    FUSION_COMMAND_ACTION_GENERATE,
    FUSION_COMMAND_ACTION_REGENERATE,
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    FUSION_INPUT_MODE_CAD_IR_FILE,
)


def response() -> dict[str, object]:
    return {
        "schema": "bgig.palette.response.v1",
        "request_id": "p59",
        "status": "ready",
        "cad_build": {
            "status": "ready_for_fusion",
            "cad_ir": {"schema_version": "cad_ir.v0", "units": "mm", "components": [], "metadata": {}},
        },
    }


class FusionPaletteCadSyncTests(unittest.TestCase):
    def test_materialize_writes_atomic_cad_ir_and_generates_compact_scene(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            entrypoint, "_execute_generation_request", return_value="generated"
        ) as execute:
            result = entrypoint._synchronize_palette_cad_response(
                response(), "materialize_project", Path(temp_dir)
            )

            request = execute.call_args.args[0]
            payload = json.loads(Path(result["cad_ir_path"]).read_text(encoding="utf-8"))
            self.assertFalse(Path(str(result["cad_ir_path"]) + ".tmp").exists())

        self.assertEqual(result["scene_status"], "synchronized")
        self.assertEqual(result["scene_result"], "generated")
        self.assertEqual(payload["schema_version"], "cad_ir.v0")
        self.assertEqual(request.action, FUSION_COMMAND_ACTION_GENERATE)
        self.assertEqual(request.generation_mode, FUSION_GENERATION_MODE_COMPACT_ONLY)
        self.assertEqual(request.input_mode, FUSION_INPUT_MODE_CAD_IR_FILE)

    def test_materialize_reports_blocked_when_generate_refuses_an_existing_scene(self) -> None:
        refused = f"Board Game Insert Generator generate refused.\n{entrypoint.BGIG_EXISTING_SCENE_MESSAGE}"
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            entrypoint, "_execute_generation_request", return_value=refused
        ):
            result = entrypoint._synchronize_palette_cad_response(
                response(), "materialize_project", Path(temp_dir)
            )

        self.assertEqual(result["scene_status"], "blocked")
        self.assertIn("generate refused", result["scene_result"])
    def test_regenerate_uses_owned_scene_replacement_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            entrypoint, "_execute_generation_request", return_value="regenerated"
        ) as execute:
            result = entrypoint._synchronize_palette_cad_response(
                response(), "regenerate_project", Path(temp_dir)
            )

        self.assertEqual(execute.call_args.args[0].action, FUSION_COMMAND_ACTION_REGENERATE)
        self.assertEqual(result["scene_status"], "synchronized")

    def test_impossible_build_never_calls_fusion(self) -> None:
        blocked = response()
        blocked["cad_build"] = {"status": "impossible", "cad_ir": None}
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            entrypoint, "_execute_generation_request"
        ) as execute:
            result = entrypoint._synchronize_palette_cad_response(
                blocked, "materialize_project", Path(temp_dir)
            )

        execute.assert_not_called()
        self.assertEqual(result["scene_status"], "blocked")

    def test_bridge_error_response_preserves_request_id_and_never_times_out(self) -> None:
        result = entrypoint._palette_project_bridge_error_response(
            {"request_id": "abc"}, RuntimeError("boom")
        )

        self.assertEqual(result["request_id"], "abc")
        self.assertEqual(result["status"], "bridge_error")
        self.assertEqual(result["scene_status"], "error")
        self.assertIn("boom", result["errors"][0])


if __name__ == "__main__":
    unittest.main()