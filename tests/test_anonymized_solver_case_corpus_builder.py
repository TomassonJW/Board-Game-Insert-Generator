from __future__ import annotations

from contextlib import redirect_stderr
from copy import deepcopy
import importlib.util
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.solver_case_bundle import build_solver_case_bundle
from board_game_insert_generator.solver_case_corpus import (
    build_solver_case,
    build_solver_case_corpus,
    replay_solver_case_corpus,
    validate_solver_case_corpus,
)
from board_game_insert_generator.solver_outcome import NO_SOLUTION_WITHIN_BUDGET
from p64_h04_fixture_cases import simple_success_project


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "solver" / "build_anonymized_solver_case_corpus.py"
SPEC = importlib.util.spec_from_file_location("anonymized_corpus_builder", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class AnonymizedSolverCaseCorpusBuilderTests(unittest.TestCase):
    def test_builds_separate_valid_candidate_without_personal_labels(self) -> None:
        project = simple_success_project()
        project["project_name"] = "Projet personnel PrivateOwner"
        project["container_groups"][0]["name"] = "Bac PrivateOwner"
        project["contents"][0]["name"] = "Pièce PrivateOwner"
        engine = IncrementalLocalAnalysisEngine(project, effort_profile="normal")
        bundle = build_solver_case_bundle(
            project,
            solver_settings={"method": "auto", "effort": "normal"},
            solver_case_state={
                "staged_calculation": {
                    "minimal_layout": {
                        "solver_result_status": NO_SOLUTION_WITHIN_BUDGET,
                        "stop_reason": "hard_budget_reached",
                    }
                }
            },
            local_analysis=engine.snapshot(),
            container_frontiers=engine.certified_frontiers(),
            interaction_events=[],
            client_context={},
            capture_id="local-capture",
            captured_at_ms=1,
            source_revision=1,
        )
        manifest = build_solver_case_corpus(
            [
                build_solver_case(
                    "existing-case",
                    simple_success_project(),
                    solver_settings={"method": "auto", "effort": "quick"},
                )
            ]
        )
        original_manifest = deepcopy(manifest)
        original_bundle = deepcopy(bundle)

        candidate = BUILDER.build_anonymized_corpus_candidate(
            manifest,
            bundle,
            case_id="real-layout-normal-001",
            source_id="reviewed-local-bundle-001",
        )
        validated = validate_solver_case_corpus(candidate)
        imported = next(
            case for case in validated["cases"] if case["case_id"] == "real-layout-normal-001"
        )
        rendered = json.dumps(imported, ensure_ascii=False, sort_keys=True)

        self.assertEqual(manifest, original_manifest)
        self.assertEqual(bundle, original_bundle)
        self.assertEqual(validated["summary"]["case_count"], 2)
        self.assertEqual(imported["execution_tier"], "extended")
        self.assertEqual(imported["source"]["id"], "reviewed-local-bundle-001")
        self.assertEqual(imported["project"]["project_name"], "Cas solveur anonymisé")
        self.assertNotIn("PrivateOwner", rendered)
        self.assertNotIn("interaction_trace", imported)
        self.assertNotIn("client_context", imported)

    def test_cli_refuses_to_overwrite_either_input(self) -> None:
        with TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / "manifest.json"
            bundle = Path(temp_dir) / "bundle.json"
            for protected in (manifest, bundle):
                with self.subTest(protected=protected), redirect_stderr(StringIO()):
                    with self.assertRaises(SystemExit) as raised:
                        BUILDER.main(
                            [
                                "--manifest",
                                str(manifest),
                                "--bundle",
                                str(bundle),
                                "--case-id",
                                "case-001",
                                "--source-id",
                                "source-001",
                                "--output",
                                str(protected),
                            ]
                        )
                self.assertEqual(raised.exception.code, 2)

    def test_checked_in_real_case_is_anonymous_and_replays_stably(self) -> None:
        path = ROOT / "tests" / "fixtures" / "p64_l06a_reviewed_real_case.v1.json"
        corpus = json.loads(path.read_text(encoding="utf-8"))
        validated = validate_solver_case_corpus(corpus)
        report = replay_solver_case_corpus(
            validated,
            include_tiers=("extended",),
        )
        rendered = json.dumps(validated, ensure_ascii=False, sort_keys=True)

        self.assertEqual(
            validated["corpus_digest"],
            "dafc18a5610fce524f69756c6001b652ac36c397ed17f2075ed5c760cb2a01e5",
        )
        self.assertEqual(validated["summary"]["case_count"], 1)
        self.assertTrue(report["summary"]["all_expectations_met"])
        self.assertEqual(
            report["cases"][0]["functional"]["status"],
            NO_SOLUTION_WITHIN_BUDGET,
        )
        for personal_marker in ("PrivateOwner", "mrv", "C:\\Users"):
            self.assertNotIn(personal_marker.lower(), rendered.lower())


if __name__ == "__main__":
    unittest.main()
