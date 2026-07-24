from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "tests" / "fixtures" / "p64_l08g_scip_product_gate.v1.json"


def _canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


class ScipProductGateEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_runtime_artifacts_and_native_dependencies_are_locked(self) -> None:
        evidence = self.evidence
        self.assertEqual(
            evidence["schema_version"],
            "bgig.scip_product_gate_evidence.v1",
        )
        self.assertEqual(evidence["candidate"]["candidate_id"], "scip")
        artifacts = evidence["artifacts"]
        self.assertEqual(artifacts["compressed_total_bytes"], 61_194_406)
        self.assertEqual(artifacts["uncompressed_total_bytes"], 187_848_352)
        wheels = artifacts["wheels"]
        self.assertEqual(len(wheels), 2)
        self.assertTrue(all(wheel["python_tag"] == "cp310" for wheel in wheels))
        dlls = [dll for wheel in wheels for dll in wheel["dlls"]]
        self.assertEqual(len(dlls), 10)
        self.assertTrue(all(len(dll["sha256"]) == 64 for dll in dlls))
        self.assertEqual(
            wheels[0]["sha256"],
            "d83d1cc9cc6d9a840cee71f4b19174cf01a54f004148a29725e2464e17011f59",
        )
        self.assertEqual(
            wheels[1]["sha256"],
            "f0fd6321b839904e15c46e0d257fdd101dd7f530fe03fd6359c1ea63738703f3",
        )

    def test_product_gate_fails_closed_for_abi_and_redistribution(self) -> None:
        fusion = self.evidence["fusion_runtime_observation"]
        self.assertEqual(fusion["fusion_version"], "2704.1.36")
        self.assertEqual(fusion["python_tag"], "cp314")
        self.assertEqual(fusion["candidate_python_tag"], "cp310")
        self.assertFalse(fusion["abi_compatible"])

        audit = self.evidence["redistribution_audit"]
        self.assertEqual(
            set(audit["incomplete_component_ids"]),
            {
                "scip",
                "ipopt",
                "coinmumps",
                "intel_compiler_runtimes",
                "microsoft_visual_cpp_runtime",
            },
        )
        self.assertFalse(audit["all_native_versions_bound"])
        self.assertFalse(audit["all_notices_present"])
        self.assertFalse(audit["all_redistribution_terms_bound"])

        decision = self.evidence["decision"]
        self.assertFalse(decision["product_integration_authorized"])
        self.assertEqual(
            decision["decision_code"],
            "negative_no_product_integrable_winner",
        )
        self.assertEqual(
            decision["blocking_reasons"],
            [
                "python_abi_mismatch",
                "native_component_versions_incomplete",
                "third_party_notices_incomplete",
                "redistribution_authority_incomplete",
            ],
        )
        self.assertFalse(decision["fusion_gate_prepared"])
        self.assertFalse(decision["fusion_gate_installed"])

    def test_gate_does_not_reopen_or_change_the_tournament(self) -> None:
        invariants = self.evidence["invariants"]
        self.assertFalse(invariants["holdout_reopened"])
        self.assertEqual(invariants["holdout_worker_invocation_count"], 0)
        self.assertEqual(invariants["post_holdout_tuning_count"], 0)
        self.assertFalse(invariants["benchmark_selection_changed"])
        self.assertFalse(invariants["product_runtime_modified"])
        self.assertFalse(invariants["fusion_validated"])
        self.assertFalse(invariants["print_validated"])

    def test_evidence_digest_is_stable(self) -> None:
        payload = dict(self.evidence)
        expected = payload.pop("evidence_digest")
        self.assertEqual(expected, _canonical_digest(payload))


if __name__ == "__main__":
    unittest.main()
