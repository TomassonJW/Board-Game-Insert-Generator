from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "tests" / "fixtures" / "p64_l08h_scip_package_remediation.v1.json"


def _canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


class ScipPackageRemediationEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_cp314_artifacts_and_every_binary_are_locked(self) -> None:
        evidence = self.evidence
        self.assertEqual(
            evidence["schema_version"],
            "bgig.scip_package_remediation_evidence.v1",
        )
        artifacts = evidence["artifacts"]
        self.assertEqual(artifacts["product_compressed_total_bytes"], 61_937_391)
        self.assertEqual(artifacts["product_uncompressed_total_bytes"], 186_127_316)
        wheels = artifacts["product_wheels"]
        self.assertEqual([wheel["python_tag"] for wheel in wheels], ["cp314", "cp314"])
        self.assertEqual(
            [wheel["sha256"] for wheel in wheels],
            [
                "6aed03b621decb09b38f399773bf8cf2c707e965990b778a24d28c8cc90a0756",
                "24d0eb82c0541d3415a33425db64ae439dffccd7b4dbcb30e7c35120205c506a",
            ],
        )
        binaries = [binary for wheel in wheels for binary in wheel["binaries"]]
        self.assertEqual(len(binaries), 30)
        self.assertTrue(all(len(binary["sha256"]) == 64 for binary in binaries))
        self.assertTrue(evidence["redistribution_audit"]["all_binary_hashes_bound"])
        self.assertTrue(evidence["redistribution_audit"]["all_native_versions_bound"])

    def test_isolated_offline_probe_executes_exact_scip_control(self) -> None:
        probe = self.evidence["isolated_offline_probe"]
        self.assertEqual(probe["python_version"], "3.14.0")
        self.assertEqual(probe["python_cache_tag"], "cpython-314")
        self.assertTrue(probe["python_isolated_flag"])
        self.assertEqual(probe["runtime_layout"], "workspace_local_unpacked_wheels")
        self.assertEqual(probe["numpy_version"], "2.5.1")
        self.assertEqual(probe["pyscipopt_version"], "6.2.1")
        self.assertEqual(probe["scip_version"], "10.0.2")
        self.assertEqual(probe["solve_status"], "optimal")
        self.assertEqual(probe["solution_x"], 1.0)
        self.assertFalse(probe["global_install_used"])
        self.assertFalse(probe["network_required"])
        self.assertFalse(probe["holdout_read"])
        self.assertFalse(probe["corpus_read"])

    def test_candidate_choice_is_scoped_and_redistribution_fails_closed(self) -> None:
        packaging = self.evidence["packaging_decision"]
        self.assertEqual(packaging["selected_candidate"], "official_pypi_cp314_wheels")
        self.assertFalse(packaging["standalone_scip_10_0_2"]["selected"])
        self.assertFalse(packaging["standalone_scip_10_0_2"]["downloaded"])

        audit = self.evidence["redistribution_audit"]
        self.assertEqual(
            set(audit["incomplete_component_ids"]),
            {
                "scip",
                "ipopt",
                "mumps_metis",
                "intel_compiler_and_mkl_runtimes",
                "microsoft_visual_cpp_runtime",
            },
        )
        self.assertFalse(audit["all_notices_present"])
        self.assertFalse(audit["all_redistribution_terms_bound"])

        decision = self.evidence["decision"]
        self.assertTrue(decision["technical_abi_gate_passed"])
        self.assertTrue(decision["isolated_offline_execution_passed"])
        self.assertFalse(decision["redistribution_gate_passed"])
        self.assertFalse(decision["product_integration_authorized"])
        self.assertEqual(
            decision["decision_code"],
            "negative_package_redistribution_incomplete",
        )
        self.assertEqual(
            decision["blocking_reasons"],
            ["third_party_notices_incomplete", "redistribution_authority_incomplete"],
        )
        self.assertFalse(decision["fusion_gate_prepared"])
        self.assertFalse(decision["fusion_gate_installed"])

    def test_tournament_and_product_boundaries_remain_sealed(self) -> None:
        invariants = self.evidence["invariants"]
        self.assertFalse(invariants["holdout_reopened"])
        self.assertEqual(invariants["holdout_worker_invocation_count"], 0)
        self.assertFalse(invariants["benchmark_replayed"])
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
