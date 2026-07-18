import importlib.util
import json
from pathlib import Path
import unittest

from p64_h04_fixture_cases import simple_success_project
from p64_v2h03c_fixture_cases import multi_container_variant_dead_end_project


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fusion" / "p64_v2h03v_preflight.py"
VARIANT_FIXTURE = ROOT / "scripts" / "fusion" / "p64_v2h03v_variant_project.json"
CONTROL_FIXTURE = ROOT / "scripts" / "fusion" / "p64_v2h03v_simple_control_project.json"
PREPARER = ROOT / "scripts" / "fusion" / "prepare_p64_v2h03v_variant_gate.ps1"


def _load_preflight_module():
    spec = importlib.util.spec_from_file_location("p64_v2h03v_preflight", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load P64-V2H03V preflight module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class P64V2H03VFusionGateTests(unittest.TestCase):
    def test_checked_in_variant_fixture_matches_the_automated_h03c_case(self) -> None:
        expected = multi_container_variant_dead_end_project()
        expected["project_name"] = "P64-V2H03V multi-container variant dead end"
        actual = json.loads(VARIANT_FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)

    def test_checked_in_control_matches_the_canonical_fast_path_fixture(self) -> None:
        expected = simple_success_project()
        expected["project_name"] = "P64-V2H03V simple canonical control"
        actual = json.loads(CONTROL_FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)

    def test_preflight_proves_variant_fallback_and_canonical_control(self) -> None:
        module = _load_preflight_module()
        report = module.build_preflight(
            json.loads(VARIANT_FIXTURE.read_text(encoding="utf-8")),
            json.loads(CONTROL_FIXTURE.read_text(encoding="utf-8")),
        )
        self.assertEqual(report["schema_version"], "bgig.p64_v2h03v.preflight.v1")
        self.assertEqual(report["variant"]["selected_family_id"], "free_3d_beam")
        self.assertEqual(report["variant"]["selected_variant_count"], 2)
        self.assertTrue(report["variant"]["all_selected_variants_noncanonical"])
        self.assertTrue(report["variant"]["global_certificate"])
        self.assertEqual(report["control"]["selected_family_id"], "stage_stack")
        self.assertTrue(report["control"]["variant_trace_absent"])
        self.assertFalse(report["fusion_materialized"])
        self.assertFalse(report["print_validated"])

    def test_preparer_keeps_the_gate_bounded_and_observable(self) -> None:
        script = PREPARER.read_text(encoding="utf-8")
        for marker in (
            "0.1.55",
            "p64_v2h03v_variant_project.json",
            "p64_v2h03v_simple_control_project.json",
            "p64_v2h03v_preflight.py",
            "containerVariantTraceDetails",
            "container_variant_global_execution_to_dict",
            "solver_settings",
            "auto",
            "quick",
            "bgig_installed_commit.txt",
            "P64-V2H03V Fusion OK 0.1.55",
            "no_solution_within_budget",
            "aucune scene",
            "print-validated: false",
        ):
            self.assertIn(marker, script)


if __name__ == "__main__":
    unittest.main()
