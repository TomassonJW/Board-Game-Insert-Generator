from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "tests" / "fixtures" / "p64_l08j_minimal_scip_runtime_build.v1.json"
REBUILD_EVIDENCE = ROOT / "tests" / "fixtures" / "p64_l08j_minimal_scip_runtime_rebuild.v1.json"
QUALIFIER = ROOT / "scripts" / "solver" / "qualify_minimal_scip_runtime.py"


def _canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


class MinimalScipRuntimeBuildEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.rebuild_evidence = json.loads(REBUILD_EVIDENCE.read_text(encoding="utf-8"))

    def test_all_locked_inputs_and_exact_cmake_contract_were_used(self) -> None:
        self.assertEqual(len(self.evidence["locked_inputs"]), 8)
        self.assertTrue(all(len(item["sha256"]) == 64 for item in self.evidence["locked_inputs"]))
        cmake = self.evidence["cmake_contract"]
        self.assertEqual(cmake["generator"], "Visual Studio 17 2022")
        self.assertEqual(cmake["platform"], "x64")
        self.assertEqual(cmake["toolset"], "v143,version=14.44")
        self.assertEqual(cmake["windows_sdk"], "10.0.26100.0")
        self.assertEqual(cmake["runtime_library"], "MultiThreadedDLL (/MD)")
        self.assertTrue(cmake["lto"])
        self.assertEqual(cmake["scip_options"]["LPS"], "spx")
        self.assertEqual(cmake["scip_options"]["SYM"], "snauty")
        self.assertEqual(cmake["scip_options"]["IPOPT"], "OFF")
        self.assertEqual(cmake["scip_options"]["PAPILO"], "OFF")

    def test_every_native_binary_is_inventoried_and_resolved(self) -> None:
        inventory = self.evidence["binary_inventory"]
        gate = self.evidence["dependency_gate"]
        self.assertEqual(len(inventory), 26)
        self.assertEqual(gate["binary_count"], 26)
        self.assertEqual(gate["dll_count"], 6)
        self.assertEqual(gate["pyd_count"], 20)
        self.assertEqual(gate["unresolved_dependency_count"], 0)
        self.assertEqual(gate["forbidden_binary_count"], 0)
        self.assertTrue(gate["all_microsoft_runtime_from_vc_redist"])
        self.assertEqual(len(gate["microsoft_provenance"]), 4)
        self.assertTrue(
            all(
                item["source_path"].startswith("VC/Redist/MSVC/14.44.35112/")
                for item in gate["microsoft_provenance"]
            )
        )
        self.assertTrue(
            all(
                dependency["classification"] != "unresolved"
                for binary in inventory
                for dependency in binary["dependencies"]
            )
        )

    def test_cp314_probe_and_all_public_3d_controls_pass(self) -> None:
        probe = self.evidence["exact_probe"]
        self.assertEqual(probe["python_abi"], "cp314")
        self.assertEqual(probe["pyscipopt_version"], "6.2.1")
        self.assertEqual(probe["scip_version"], "10.0.2")
        self.assertEqual(probe["numpy_version"], "2.5.1")
        self.assertEqual(probe["status"], "optimal")
        self.assertEqual(probe["objective"], 7.0)
        equivalence = self.evidence["public_equivalence"]
        self.assertEqual(equivalence["exact_control_count"], 6)
        self.assertEqual(equivalence["semantic_loss_count"], 0)
        self.assertEqual(equivalence["solution_loss_count"], 0)
        self.assertEqual(equivalence["certificate_loss_count"], 0)
        self.assertTrue(
            all(
                row["baseline_status"] == row["candidate_status"]
                for row in equivalence["exact_controls"]
            )
        )
        self.assertFalse(equivalence["performance"]["material_regression"])
        self.assertLessEqual(
            equivalence["performance"]["candidate_total_solve_milliseconds"],
            equivalence["performance"]["material_regression_threshold_milliseconds"],
        )

    def test_open_regression_and_holdout_boundaries_remain_honest(self) -> None:
        regression = self.evidence["public_equivalence"]["open_regression"]
        self.assertEqual(regression["status"], "unsupported")
        self.assertEqual(regression["unsupported_constraints"], ["incomplete_real_3d_problem"])
        self.assertTrue(regression["truth_pass"])
        self.assertEqual(regression["worker_invocation_count"], 0)
        invariants = self.evidence["invariants"]
        self.assertFalse(invariants["holdout_read"])
        self.assertEqual(invariants["holdout_worker_invocation_count"], 0)
        self.assertFalse(invariants["benchmark_replayed"])
        self.assertEqual(invariants["post_holdout_tuning_count"], 0)
        self.assertEqual(invariants["global_install_count"], 0)
        self.assertFalse(invariants["product_runtime_modified"])
        self.assertFalse(invariants["fusion_validated"])
        self.assertFalse(invariants["print_validated"])

    def test_notices_size_and_integration_decision_are_explicit(self) -> None:
        notices = {item["path"] for item in self.evidence["notice_inventory"]}
        self.assertIn("PySCIPOpt-MIT.txt", notices)
        self.assertIn("SCIP/LICENSE", notices)
        self.assertIn("SCIP/nauty/COPYRIGHT", notices)
        self.assertIn("SCIP/dejavu/LICENSE", notices)
        self.assertIn("SoPlex/LICENSE", notices)
        self.assertIn("NumPy/LICENSE.txt", notices)
        self.assertIn("Microsoft-Visual-Cpp-Runtime.txt", notices)
        tree = self.evidence["runtime_tree"]
        self.assertEqual(tree["size_bytes"], 56_491_565)
        self.assertLess(tree["size_bytes"], 186_127_316)
        decision = self.evidence["decision"]
        self.assertTrue(decision["minimal_runtime_build_passed"])
        self.assertTrue(decision["public_equivalence_passed"])
        self.assertTrue(decision["product_integration_authorized"])
        self.assertEqual(
            decision["decision_code"],
            "minimal_scip_runtime_build_and_public_equivalence_pass",
        )

    def test_clean_rebuild_repeats_the_qualified_result(self) -> None:
        rebuild = self.rebuild_evidence
        self.assertEqual(rebuild["locked_inputs"], self.evidence["locked_inputs"])
        rebuild_cmake = dict(rebuild["cmake_contract"])
        original_cmake = dict(self.evidence["cmake_contract"])
        for cache_digest in ("scip_cache_sha256", "soplex_cache_sha256"):
            rebuild_cmake.pop(cache_digest)
            original_cmake.pop(cache_digest)
        self.assertEqual(rebuild_cmake, original_cmake)
        self.assertEqual(rebuild["runtime_tree"]["file_count"], 1016)
        self.assertEqual(rebuild["dependency_gate"]["unresolved_dependency_count"], 0)
        self.assertEqual(rebuild["dependency_gate"]["forbidden_binary_count"], 0)
        self.assertEqual(rebuild["exact_probe"], self.evidence["exact_probe"])
        self.assertEqual(rebuild["public_equivalence"]["exact_control_count"], 6)
        self.assertEqual(rebuild["public_equivalence"]["semantic_loss_count"], 0)
        self.assertEqual(rebuild["public_equivalence"]["solution_loss_count"], 0)
        self.assertEqual(rebuild["public_equivalence"]["certificate_loss_count"], 0)
        self.assertFalse(rebuild["public_equivalence"]["performance"]["material_regression"])
        self.assertTrue(rebuild["decision"]["product_integration_authorized"])
        self.assertNotEqual(
            rebuild["built_wheel"]["sha256"], self.evidence["built_wheel"]["sha256"]
        )
        payload = dict(rebuild)
        expected = payload.pop("evidence_digest")
        self.assertEqual(expected, _canonical_digest(payload))

    def test_qualifier_rejects_pyscipopt_name_as_a_false_ipopt_positive(self) -> None:
        namespace = runpy.run_path(str(QUALIFIER))
        is_forbidden = namespace["_is_forbidden_binary_name"]
        self.assertFalse(is_forbidden("site-packages/pyscipopt/libscip.dll"))
        self.assertTrue(is_forbidden("pyscipopt.libs/ipopt-3.dll"))
        self.assertTrue(is_forbidden("libiomp5md-runtime.dll"))

    def test_evidence_digest_is_stable(self) -> None:
        payload = dict(self.evidence)
        expected = payload.pop("evidence_digest")
        self.assertEqual(expected, _canonical_digest(payload))


if __name__ == "__main__":
    unittest.main()
