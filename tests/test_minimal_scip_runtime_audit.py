from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "tests" / "fixtures" / "p64_l08i_minimal_scip_runtime_audit.v1.json"
AUDIT_SCRIPT = ROOT / "scripts" / "solver" / "audit_minimal_scip_runtime.py"
WORKER = ROOT / "scripts" / "solver" / "external_workers" / "scip_real_3d_worker.py"


def _canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


class MinimalScipRuntimeAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_sealed_worker_is_integer_linear_and_still_full_3d(self) -> None:
        namespace = runpy.run_path(str(AUDIT_SCRIPT))
        live = namespace["audit_worker"](WORKER)
        recorded = self.evidence["model_audit"]
        self.assertEqual(live, recorded)
        self.assertTrue(recorded["linear_integer_model_gate_passed"])
        self.assertEqual(recorded["variable_types"], ["B", "I"])
        self.assertEqual(recorded["nonlinear_products"], [])
        self.assertEqual(recorded["banned_dependency_tokens_found"], [])
        self.assertEqual(len(recorded["active_3d_semantics"]), 7)
        self.assertIn("multi_level_z_placement", recorded["active_3d_semantics"])
        self.assertIn("support_count_and_area", recorded["active_3d_semantics"])

    def test_source_and_build_inputs_are_fully_locked(self) -> None:
        sources = self.evidence["source_artifacts"]
        self.assertEqual(
            [(item["component_id"], item["version"]) for item in sources],
            [("scip", "10.0.2"), ("soplex", "8.0.2"), ("pyscipopt", "6.2.1")],
        )
        self.assertTrue(all(len(item["commit"]) == 40 for item in sources))
        self.assertTrue(all(len(item["sha256"]) == 64 for item in sources))
        self.assertTrue(all(item["size_bytes"] > 0 for item in sources))
        inputs = self.evidence["build_inputs"]
        self.assertEqual(
            [item["component_id"] for item in inputs],
            ["python-build-runtime", "cython", "setuptools", "wheel", "numpy"],
        )
        self.assertTrue(all(len(item["sha256"]) == 64 for item in inputs))
        self.assertTrue(all(item["size_bytes"] > 0 for item in inputs))

    def test_build_contract_keeps_mip_core_and_removes_non_required_native_chain(self) -> None:
        contract = self.evidence["build_contract"]
        scip = contract["scip_cmake_options"]
        soplex = contract["soplex_cmake_options"]
        self.assertEqual(scip["LPS"], "spx")
        self.assertEqual(scip["SYM"], "snauty")
        self.assertEqual(scip["LTO"], "ON")
        self.assertEqual(scip["IPOPT"], "OFF")
        self.assertEqual(scip["PAPILO"], "OFF")
        self.assertEqual(scip["TPI"], "none")
        self.assertEqual(soplex["GMP"], "OFF")
        self.assertEqual(soplex["PAPILO"], "OFF")
        excluded = set(contract["excluded_runtime_components"])
        self.assertIn("Ipopt", excluded)
        self.assertIn("MUMPS", excluded)
        self.assertIn("METIS", excluded)
        self.assertIn("Intel MKL", excluded)
        self.assertEqual(contract["python_abi"], "cp314")
        self.assertTrue(self.evidence["toolchain"]["workspace_local_build"])
        self.assertFalse(contract["account_required"])
        self.assertFalse(contract["secret_required"])
        self.assertFalse(contract["telemetry_required"])
        self.assertFalse(contract["private_holdout_allowed"])

    def test_redistribution_plan_is_fail_closed(self) -> None:
        audit = self.evidence["redistribution_contract"]
        self.assertTrue(audit["all_source_versions_bound"])
        self.assertTrue(audit["all_source_hashes_bound"])
        self.assertTrue(audit["all_source_sizes_bound"])
        self.assertGreaterEqual(len(audit["required_notices"]), 9)
        self.assertEqual(
            set(audit["forbidden_binary_families"]),
            {
                "ipopt*",
                "coinmumps*",
                "libifcoremd*",
                "libiomp5md*",
                "libmmd*",
                "svml_dispmd*",
            },
        )
        self.assertTrue(audit["fail_if_unresolved_dependency"])
        self.assertTrue(audit["fail_if_notice_missing"])

    def test_build_only_is_authorized_and_product_remains_unchanged(self) -> None:
        decision = self.evidence["decision"]
        self.assertTrue(decision["prebuild_model_gate_passed"])
        self.assertTrue(decision["minimal_build_authorized"])
        self.assertFalse(decision["product_integration_authorized"])
        self.assertFalse(decision["fusion_gate_prepared"])
        self.assertFalse(decision["fusion_gate_installed"])
        self.assertEqual(decision["decision_code"], "minimal_scip_build_audit_pass")
        invariants = self.evidence["invariants"]
        self.assertFalse(invariants["holdout_read"])
        self.assertEqual(invariants["holdout_worker_invocation_count"], 0)
        self.assertFalse(invariants["benchmark_replayed"])
        self.assertFalse(invariants["product_runtime_modified"])
        self.assertFalse(invariants["fusion_validated"])
        self.assertFalse(invariants["print_validated"])

    def test_evidence_digest_is_stable(self) -> None:
        payload = dict(self.evidence)
        expected = payload.pop("evidence_digest")
        self.assertEqual(expected, _canonical_digest(payload))


if __name__ == "__main__":
    unittest.main()
