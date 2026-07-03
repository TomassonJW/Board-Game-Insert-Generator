from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from context import ROOT

from board_game_insert_generator.cli import main


class CliTests(unittest.TestCase):
    def test_cli_diagnose_reports_ok(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            code = main(["diagnose", str(ROOT / "examples" / "simple_box.json")])

        output = stdout.getvalue()

        self.assertEqual(code, 0)
        self.assertIn("Diagnostic OK - Simple square box V0", output)
        self.assertIn("- Generated instances: 4", output)
        self.assertIn("- Markdown report: OK", output)
        self.assertIn("- JSON report: OK", output)

    def test_cli_reports_configuration_error_category(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "config.json"
            path.write_text(json.dumps({"unexpected": True}), encoding="utf-8")
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                code = main([str(path)])

        self.assertEqual(code, 2)
        self.assertIn("Configuration error:", stderr.getvalue())
        self.assertIn("Unknown field(s) in 'root': unexpected", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
