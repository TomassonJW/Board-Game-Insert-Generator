from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
sys.path.insert(0, str(ADDIN))

import BoardGameInsertGenerator as entrypoint  # noqa: E402


class FusionPaletteQtTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = (ADDIN / "BoardGameInsertGenerator.py").read_text(encoding="utf-8")
        cls.markup = (ADDIN / "palette.html").read_text(encoding="utf-8")

    def test_ignores_only_the_qt_async_transport_acknowledgement(self) -> None:
        self.assertTrue(entrypoint._is_palette_transport_response("response"))
        for action in ("bgig_palette_project", "inspect", "clear", "expert", "export"):
            self.assertFalse(entrypoint._is_palette_transport_response(action))

    def test_transport_ack_is_ignored_before_any_outbound_notice(self) -> None:
        notify = self.source.index("def notify(self, args)")
        ignore = self.source.index("if _is_palette_transport_response(action):", notify)
        unknown = self.source.index("Action inconnue", notify)
        self.assertLess(ignore, unknown)
        self.assertIn('args.returnData = "OK"', self.source[ignore:unknown])

    def test_bootstrap_waits_until_the_python_handler_proves_readiness(self) -> None:
        self.assertEqual(
            entrypoint._palette_bootstrap_request(),
            {"schema": "bgig.palette.request.v1", "request_id": "palette-bootstrap", "action": "load_project"},
        )
        ready = self.source.index("if action == BGIG_PALETTE_READY_ACTION:")
        project = self.source.index("if action == BGIG_PALETTE_PROJECT_ACTION:")
        self.assertLess(ready, project)
        self.assertIn("setInterval(requestBootstrap,500)", self.markup)
        self.assertIn("sendFusion(READY_ACTION,true)", self.markup)
        self.assertNotIn("sendProject('load_project');sendFusion('refresh')", self.markup)

    def test_utilities_command_opens_palette_and_packages_house_icons(self) -> None:
        self.assertEqual(entrypoint.BGIG_COMMAND_NAME, "BGIG - Atelier de rangement")
        self.assertIn("created_handler = _BgigPaletteCommandCreatedHandler(addin_dir)", self.source)
        self.assertIn("_ensure_palette(self.addin_dir)", self.source)
        self.assertIn("str(resource_folder)", self.source)
        self.assertIn("control.isPromotedByDefault = True", self.source)
        self.assertNotIn('data-fusion="expert"', self.markup)
        for name in ("16x16.svg", "32x32.svg"):
            icon = ADDIN / "resources" / name
            self.assertTrue(icon.is_file())
            ET.parse(icon)
    def test_inspection_report_is_sent_only_as_collapsed_technical_detail(self) -> None:
        inspect_block = self.source[self.source.index('if action in {"refresh", "preview", "inspect"}') :]
        inspect_block = inspect_block[: inspect_block.index('if action == "clear"')]
        self.assertIn("technical_detail=result", inspect_block)
        self.assertNotIn("self.addin_dir, result)", inspect_block)

    def test_manifest_identifies_the_bootstrap_and_launcher_fix(self) -> None:
        manifest = json.loads((ADDIN / "BoardGameInsertGenerator.manifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.1.29")
    def test_uses_native_file_dialog_only_in_the_fusion_adapter(self) -> None:
        for marker in (
            "BGIG_PALETTE_DOCUMENT_ACTION",
            "if action == BGIG_PALETTE_DOCUMENT_ACTION:",
            "createFileDialog()",
            "dialog.initialDirectory",
            "dialog.showOpen()",
            "dialog.showSave()",
            "open_project_file",
            "save_project_as",
        ):
            self.assertIn(marker, self.source)
        bridge = (ADDIN / "palette_project.py").read_text(encoding="utf-8")
        self.assertNotIn("import adsk", bridge)
        self.assertIn("project_document_directory", bridge)

    def test_palette_opens_at_a_product_sized_minimum(self) -> None:
        self.assertEqual(entrypoint.BGIG_PALETTE_DEFAULT_WIDTH, 1280)
        self.assertEqual(entrypoint.BGIG_PALETTE_DEFAULT_HEIGHT, 1100)
        self.assertIn('palette.width = BGIG_PALETTE_DEFAULT_WIDTH', self.source)
        self.assertIn('palette.height = BGIG_PALETTE_DEFAULT_HEIGHT', self.source)


if __name__ == "__main__":
    unittest.main()