from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
sys.path.insert(0, str(ADDIN))

import BoardGameInsertGenerator as entrypoint  # noqa: E402


class FusionPaletteQtTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = (ADDIN / "BoardGameInsertGenerator.py").read_text(encoding="utf-8")

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

    def test_manifest_identifies_the_qt_runtime_fix(self) -> None:
        manifest = json.loads((ADDIN / "BoardGameInsertGenerator.manifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.1.7")
    def test_palette_opens_at_a_product_sized_minimum(self) -> None:
        self.assertEqual(entrypoint.BGIG_PALETTE_DEFAULT_WIDTH, 1120)
        self.assertEqual(entrypoint.BGIG_PALETTE_DEFAULT_HEIGHT, 760)
        self.assertIn('palette.width = BGIG_PALETTE_DEFAULT_WIDTH', self.source)
        self.assertIn('palette.height = BGIG_PALETTE_DEFAULT_HEIGHT', self.source)


if __name__ == "__main__":
    unittest.main()