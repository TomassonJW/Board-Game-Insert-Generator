from __future__ import annotations

import json
import unittest

from context import ROOT


AUDIT = ROOT / "tests" / "fixtures" / "p64_l07a_external_solver_audit.v1.json"


def _read_audit() -> dict[str, object]:
    return json.loads(AUDIT.read_text(encoding="utf-8"))


class ExternalSolverAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = _read_audit()
        cls.candidates = cls.audit["candidates"]
        cls.by_id = {candidate["id"]: candidate for candidate in cls.candidates}

    def test_inventory_is_versioned_complete_and_unique(self) -> None:
        self.assertEqual(
            self.audit["schema_version"],
            "bgig.external_solver_audit.v1",
        )
        self.assertEqual(self.audit["status"], "done")
        self.assertGreaterEqual(len(self.candidates), 8)
        self.assertEqual(len(self.by_id), len(self.candidates))
        self.assertEqual(
            self.audit["decision"]["audited_candidate_count"],
            len(self.candidates),
        )

        allowed_decisions = {"shortlisted", "benchmark-only", "rejected"}
        for candidate in self.candidates:
            self.assertIn(candidate["decision"], allowed_decisions)
            self.assertTrue(candidate["decision_reason"])
            self.assertTrue(candidate["snapshot"]["benchmark_target"])
            self.assertRegex(
                candidate["snapshot"]["audited_head_commit"],
                r"^[0-9a-f]{40}$",
            )
            self.assertTrue(candidate["licenses"]["code"])
            self.assertTrue(candidate["licenses"]["binary"])
            self.assertTrue(candidate["licenses"]["data"])
            self.assertTrue(candidate["licenses"]["dependencies"])
            self.assertTrue(candidate["licenses"]["redistribution"])
            self.assertTrue(candidate["mapping"]["model_loss"])
            self.assertGreaterEqual(len(candidate["sources"]), 2)
            self.assertTrue(
                any(
                    source["kind"] == "official_repository"
                    for source in candidate["sources"]
                )
            )
            for source in candidate["sources"]:
                self.assertTrue(source["url"].startswith("https://"))

    def test_shortlist_passes_the_real_competition_floor(self) -> None:
        decision = self.audit["decision"]
        shortlisted = [
            candidate
            for candidate in self.candidates
            if candidate["decision"] == "shortlisted"
        ]
        shortlisted_ids = [candidate["id"] for candidate in shortlisted]
        shortlisted_families = {candidate["family"] for candidate in shortlisted}

        self.assertEqual(shortlisted_ids, decision["shortlisted_ids"])
        self.assertGreaterEqual(
            len(shortlisted),
            decision["minimum_external_competitors"],
        )
        self.assertGreaterEqual(
            len(shortlisted_families),
            decision["minimum_distinct_families"],
        )
        self.assertNotIn("bgig", shortlisted_ids)
        self.assertNotIn("internal_oracle", shortlisted_ids)
        self.assertTrue(decision["minimum_gate_passed"])
        self.assertEqual(
            decision["next_gate"],
            "lock_and_verify_artifact_sha256_before_any_l07c_execution",
        )

        for candidate in shortlisted:
            runtime = candidate["runtime"]
            self.assertTrue(runtime["offline"])
            self.assertFalse(runtime["global_install"])
            self.assertNotEqual(runtime["deadline_control"], "missing")
            self.assertTrue(runtime["memory_control"])
            self.assertNotIn("required", runtime["telemetry"])

    def test_method_claims_are_backed_by_primary_sources(self) -> None:
        primary_publications = {
            candidate["id"]
            for candidate in self.candidates
            if any(
                source["kind"] == "primary_publication"
                for source in candidate["sources"]
            )
        }
        self.assertGreaterEqual(len(primary_publications), 6)
        self.assertTrue(
            {
                "packingsolver",
                "laff",
                "ortools_cp_sat",
                "scip",
                "highs",
            }.issubset(primary_publications)
        )

    def test_license_and_packaging_exclusions_are_explicit(self) -> None:
        packing_dependencies = self.by_id["packingsolver"]["licenses"][
            "dependencies"
        ]
        self.assertIn("CLP EPL-2.0", packing_dependencies)
        self.assertIn("excluded", packing_dependencies)
        self.assertIn("Knitro", packing_dependencies)

        cbc = self.by_id["cbc"]
        self.assertEqual(cbc["decision"], "benchmark-only")
        self.assertEqual(
            cbc["licenses"]["redistribution"],
            "copyleft_human_gate_required",
        )
        self.assertEqual(self.by_id["timefold"]["decision"], "rejected")
        self.assertEqual(self.by_id["py3dbp"]["decision"], "rejected")

    def test_no_candidate_claims_native_arbitrary_3d_shapes(self) -> None:
        for candidate in self.candidates:
            complex_shapes = candidate["mapping"]["complex_shapes_3d"].lower()
            self.assertTrue(
                "unsupported" in complex_shapes
                or "no native geometry" in complex_shapes
            )


if __name__ == "__main__":
    unittest.main()
