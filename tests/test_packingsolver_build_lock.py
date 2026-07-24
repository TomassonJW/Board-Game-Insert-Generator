from __future__ import annotations

import json
from pathlib import Path
import unittest

from board_game_insert_generator.incremental_project_state import canonical_digest


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "tests" / "fixtures" / "p64_l08e_packingsolver_build_lock.v1.json"


class PackingSolverBuildLockTests(unittest.TestCase):
    def test_lock_binds_source_binary_and_dependency_licenses(self) -> None:
        payload = json.loads(LOCK.read_text(encoding="utf-8"))
        supplied = payload.pop("lock_digest")
        self.assertEqual(canonical_digest(payload), supplied)
        self.assertEqual(payload["candidate_id"], "packingsolver_box")
        self.assertEqual(payload["source"]["commit"], "0cae9d04d5d361c496074ea633b1a3955b6543ec")
        self.assertEqual(len(payload["build"]["binary_sha256"]), 64)
        self.assertGreater(payload["build"]["binary_byte_count"], 0)
        self.assertGreaterEqual(len(payload["dependencies"]), 9)
        self.assertTrue(
            all(len(value["license_sha256"]) == 64 for value in payload["dependencies"])
        )
        self.assertEqual(
            payload["product_gate"],
            "benchmark_only_pending_redistribution_notice_and_binary_dependency_audit",
        )
        self.assertEqual(payload["invariants"]["global_install_count"], 0)
        self.assertTrue(payload["invariants"]["offline_execution_required"])


if __name__ == "__main__":
    unittest.main()
