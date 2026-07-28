from __future__ import annotations

from pathlib import Path
import json
import unittest

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.incremental_project_state import (
    canonical_digest,
)
from board_game_insert_generator.partition_cad import build_partition_cad
from board_game_insert_generator.staged_calculation import (
    ARTIFACT_KIND_FINALIZED,
    ARTIFACT_KIND_MINIMAL,
    StagedCalculationSession,
)
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)
from scripts.fusion.p64_l09t_g_fixture_cases import (
    CASE_02_VARIANTS,
    anonymized_case_01_plus_project,
    anonymized_case_02_variant,
)
from scripts.fusion.p64_l09tv_preflight import (
    ADDIN_VERSION,
    TARGETED_MATRIX,
    build_preflight,
)


ROOT = Path(__file__).resolve().parents[1]


def _content_structure(project: dict[str, object]) -> list[tuple[object, ...]]:
    return [
        (
            value["id"],
            value["container_group_id"],
            value["shape_kind"],
            tuple(sorted(value["dimensions_mm"].items())),
            value["quantity"],
            value.get("storage_orientation"),
        )
        for value in project["contents"]
    ]


def _run_end_to_end(
    project: dict[str, object],
    *,
    request_id: str,
) -> dict[str, object]:
    settings = {"method": "auto", "effort": "normal"}
    engine = IncrementalLocalAnalysisEngine(
        project,
        effort_profile="normal",
    )
    session = StagedCalculationSession(
        project,
        solver_settings=settings,
    )
    session.synchronize(
        project,
        engine.snapshot(),
        solver_settings=settings,
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )
    calculated = session.calculate_layout(
        request_id=request_id,
        request_revision=0,
    )
    if calculated["solver_result"]["status"] != "solution_found":
        raise RuntimeError(
            f"{request_id}: no certified minimal plan: "
            f"{calculated['solver_result']['status']}"
        )
    minimal = session.select_materializable_artifact(ARTIFACT_KIND_MINIMAL)
    finalized = session.finalize_volume(finishing_effort_profile="normal")
    if finalized["solver_result"]["status"] != "solution_found":
        raise RuntimeError(
            f"{request_id}: no certified final plan: "
            f"{finalized['solver_result'].get('stop_diagnostics')}"
        )
    selected = session.select_materializable_artifact(
        ARTIFACT_KIND_FINALIZED
    )
    plan = selected["partition"]
    certificate = plan["finalization"][
        "composite_materialization_certificate"
    ]
    cad = build_partition_cad(
        project,
        partition=plan,
        artifact_identity=selected,
        effort_profile="normal",
    )
    if cad["status"] != "ready_for_fusion":
        raise RuntimeError(f"{request_id}: CAD IR is {cad['status']!r}.")
    fusion = generation_plan_from_cad_ir(
        cad["cad_ir"],
        FUSION_GENERATION_MODE_COMPACT_ONLY,
    )
    return {
        "project_digest": canonical_digest(project),
        "minimal": minimal["partition"],
        "final": plan,
        "certificate": certificate,
        "cad": cad,
        "fusion": fusion,
    }


class P64L09TGReleaseGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.case_01 = _run_end_to_end(
            anonymized_case_01_plus_project(),
            request_id="p64-l09t-g-anonymized-01-plus",
        )
        cls.case_02 = {
            kind: _run_end_to_end(
                anonymized_case_02_variant(kind),
                request_id=f"p64-l09t-g-anonymized-02-{kind}",
            )
            for kind in CASE_02_VARIANTS
        }
        cls.gate_project, cls.preflight = build_preflight()

    def test_anonymized_case_01_plus_is_fully_materializable(self) -> None:
        self._assert_exact_result(self.case_01)
        self.assertGreaterEqual(
            len(self.case_01["final"]["placements"]),
            9,
        )

    def test_case_02_content_and_clearance_changes_are_isolated(self) -> None:
        self.assertEqual(
            set(self.case_02),
            {
                "base",
                "content_only",
                "clearance_only",
                "combined",
            },
        )
        for kind, result in self.case_02.items():
            with self.subTest(kind=kind):
                self._assert_exact_result(result)

        base = anonymized_case_02_variant("base")
        content = anonymized_case_02_variant("content_only")
        clearance = anonymized_case_02_variant("clearance_only")
        combined = anonymized_case_02_variant("combined")
        self.assertEqual(base["layout"], content["layout"])
        self.assertEqual(
            _content_structure(base),
            _content_structure(clearance),
        )
        self.assertNotEqual(
            _content_structure(base),
            _content_structure(content),
        )
        self.assertNotEqual(base["layout"], clearance["layout"])
        self.assertEqual(
            _content_structure(content),
            _content_structure(combined),
        )
        self.assertEqual(clearance["layout"], combined["layout"])

    def test_release_preflight_is_public_and_never_claims_human_gates(
        self,
    ) -> None:
        self.assertEqual(self.preflight["addin_version"], ADDIN_VERSION)
        self.assertEqual(ADDIN_VERSION, "0.1.70")
        self.assertEqual(
            set(self.preflight["targeted_matrix"]["required_case_ids"]),
            set(TARGETED_MATRIX),
        )
        self.assertFalse(self.preflight["holdout_opened"])
        self.assertFalse(self.preflight["benchmark_executed"])
        self.assertFalse(self.preflight["fusion_validated"])
        self.assertFalse(self.preflight["print_validated"])
        self.assertEqual(
            self.preflight["gate_status"],
            "prepared_not_human_observed",
        )
        serialized = str(self.preflight).lower()
        self.assertNotIn("caslimite01", serialized)
        self.assertNotIn("caslimite02", serialized)
        self.assertNotIn(r"c:\users", serialized)

    def test_release_sources_keep_core_independent_from_adsk(self) -> None:
        core = ROOT / "src" / "board_game_insert_generator"
        offenders = [
            path
            for path in core.rglob("*.py")
            if "import adsk" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])

    def test_historical_preparer_remains_pinned_to_the_0170_candidate(self) -> None:
        addin = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
        manifest = json.loads(
            (addin / "BoardGameInsertGenerator.manifest").read_text(
                encoding="utf-8"
            )
        )
        preparer = (
            ROOT / "scripts" / "fusion" / "prepare_p64_l09tv_gate.ps1"
        ).read_text(encoding="utf-8")
        local_replay = (
            ROOT / "scripts" / "fusion" / "p64_l09t_local_replay.py"
        ).read_text(encoding="utf-8")
        self.assertEqual(manifest["version"], "0.1.76")
        for marker in (
            'expectedVersion -ne "0.1.70"',
            "p64_l09t_local_replay.py",
            "p64_l09tv_preflight.py",
            "test_p64_l09t_g_release_gate.py",
            "install_addin.ps1",
            "check_installed_addin.ps1",
            "bgig_installed_commit.txt",
            "fusion-validated=false",
        ):
            self.assertIn(marker, preparer)
        self.assertIn("Path.home()", local_replay)
        self.assertIn("source_projects_unchanged", local_replay)
        self.assertNotIn(r"C:\Users", local_replay)

    def _assert_exact_result(self, result: dict[str, object]) -> None:
        certificate = result["certificate"]
        self.assertTrue(certificate["certified"])
        self.assertEqual(certificate["printable_residual_volume_mm3"], 0.0)
        self.assertTrue(
            certificate["cavity_calibrations_match_source_contract"]
        )
        self.assertTrue(certificate["minimum_reservation_wall_certified"])
        self.assertEqual(result["cad"]["status"], "ready_for_fusion")
        self.assertGreater(result["fusion"].module_component_count, 0)
        self.assertGreater(len(result["fusion"].cavity_cuts), 0)


if __name__ == "__main__":
    unittest.main()
