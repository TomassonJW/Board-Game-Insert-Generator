from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from board_game_insert_generator.container_internal_variants import (
    derive_container_internal_variant_frontiers,
)
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.solver_benchmark_corpus import (
    FAMILIES,
    FEASIBLE_BY_CONSTRUCTION,
    GENERATED_CASES_PER_SPLIT,
    PROVEN_IMPOSSIBLE_SMALL_EXACT,
    SolverBenchmarkCorpusError,
    build_holdout_selection,
    build_solver_benchmark_manifest,
    materialize_benchmark_split,
    open_holdout_cases,
    validate_solver_benchmark_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "p64_l06_solver_benchmark.v1.json"
L05D = ROOT / "tests" / "fixtures" / "p64_l05d_solver_case_corpus.v1.json"
L06A = ROOT / "tests" / "fixtures" / "p64_l06a_reviewed_real_case.v1.json"
SCRIPT = ROOT / "scripts" / "solver" / "build_solver_benchmark_manifest.py"
SPEC = importlib.util.spec_from_file_location("solver_benchmark_builder", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


def _read(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


class SolverBenchmarkCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.l05d = _read(L05D)
        cls.l06a = _read(L06A)
        cls.manifest = build_solver_benchmark_manifest(
            {"p64-l05d1": cls.l05d, "p64-l06a": cls.l06a}
        )

    def test_manifest_preserves_regression_corpora_and_split_sizes(self) -> None:
        original_l05d = deepcopy(self.l05d)
        original_l06a = deepcopy(self.l06a)
        validated = validate_solver_benchmark_manifest(self.manifest)

        self.assertEqual(self.l05d, original_l05d)
        self.assertEqual(self.l06a, original_l06a)
        self.assertEqual(validated["summary"]["regression_case_count"], 8)
        self.assertEqual(validated["summary"]["generated_case_count"], 192)
        self.assertEqual(
            [item["corpus"]["corpus_digest"] for item in validated["regression_corpora"]],
            [self.l05d["corpus_digest"], self.l06a["corpus_digest"]],
        )
        for split in ("discovery", "tuning", "holdout"):
            records = [case for case in validated["generated_cases"] if case["split"] == split]
            self.assertEqual(len(records), GENERATED_CASES_PER_SPLIT)
        self.assertEqual(validated["holdout_policy"]["status"], "sealed")
        self.assertTrue(validated["invariants"]["historical_corpus_digests_preserved"])
        self.assertFalse(
            validated["invariants"]["rotation_disable_control_exposed_by_project_v1"]
        )

    def test_each_generated_split_covers_the_required_matrix(self) -> None:
        validated = validate_solver_benchmark_manifest(self.manifest)
        for split in ("discovery", "tuning", "holdout"):
            records = [case for case in validated["generated_cases"] if case["split"] == split]
            recipes = [case["recipe"] for case in records]
            features = [case["features"] for case in records]
            with self.subTest(split=split):
                self.assertEqual({case["family"] for case in records}, set(FAMILIES))
                self.assertEqual(
                    {recipe["retained_variant_target"] for recipe in recipes},
                    {1, 2, 4, 8},
                )
                self.assertEqual({recipe["layer_count"] for recipe in recipes}, {1, 2, 3})
                self.assertEqual(
                    {recipe["content_profile"] for recipe in recipes},
                    {"homogeneous", "heterogeneous", "nearly_equal"},
                )
                self.assertEqual(
                    {recipe["density_target"] for recipe in recipes},
                    {"ample", "dense", "nearly_saturated"},
                )
                self.assertEqual(
                    {recipe["reservation_mode"] for recipe in recipes},
                    {"absent", "constraining"},
                )
                self.assertEqual(
                    {recipe["rotation_witness"] for recipe in recipes},
                    {"fixed_zero_witness", "uses_z_rotation"},
                )
                self.assertEqual(
                    {recipe["rotation_policy_target"] for recipe in recipes},
                    {"permitted", "forbidden_by_benchmark"},
                )
                self.assertEqual(
                    {feature["container_group_count"] for feature in features},
                    {2, 4, 8, 12, 18, 30, 50},
                )
                content_targets = {
                    count
                    for recipe in recipes
                    for count in recipe["contents_per_group"]
                }
                self.assertEqual(content_targets, {1, 2, 4, 8, 16, 32})
                self.assertIn(
                    FEASIBLE_BY_CONSTRUCTION,
                    {recipe["oracle_kind"] for recipe in recipes},
                )
                self.assertIn(
                    PROVEN_IMPOSSIBLE_SMALL_EXACT,
                    {recipe["oracle_kind"] for recipe in recipes},
                )

    def test_real_certified_variant_counts_cover_one_two_four_and_eight(self) -> None:
        observed: set[int] = set()
        for case_id in ("simple-quick", "variant-dead-end-quick", "multi-cavity-normal"):
            case = next(value for value in self.l05d["cases"] if value["case_id"] == case_id)
            run = derive_container_internal_variant_frontiers(
                case["project"], effort_profile=case["solver_settings"]["effort"]
            )
            observed.update(len(frontier.variants) for frontier in run.frontiers)
        generated = next(
            value
            for value in materialize_benchmark_split(self.manifest, "discovery")
            if value["case_id"] == "discovery-d-009"
        )
        run = derive_container_internal_variant_frontiers(
            generated["project"], effort_profile="normal"
        )
        observed.update(len(frontier.variants) for frontier in run.frontiers)

        self.assertTrue({1, 2, 4, 8}.issubset(observed))
    def test_discovery_and_tuning_materialize_with_valid_independent_oracles(self) -> None:
        for split in ("discovery", "tuning"):
            cases = materialize_benchmark_split(self.manifest, split)
            with self.subTest(split=split):
                self.assertEqual(len(cases), 64)
                self.assertGreater(
                    sum(case["oracle"]["kind"] == FEASIBLE_BY_CONSTRUCTION for case in cases),
                    0,
                )
                self.assertGreater(
                    sum(
                        case["oracle"]["kind"] == PROVEN_IMPOSSIBLE_SMALL_EXACT
                        for case in cases
                    ),
                    0,
                )
                self.assertTrue(
                    all(case["invariants"]["solver_invocation_count"] == 0 for case in cases)
                )
                self.assertTrue(
                    all(case["oracle"]["supplied_to_tested_solver"] is False for case in cases)
                )

    def test_small_constructed_case_is_recertified_by_the_current_solver(self) -> None:
        cases = materialize_benchmark_split(self.manifest, "discovery")
        case = next(
            value
            for value in cases
            if value["oracle"]["kind"] == FEASIBLE_BY_CONSTRUCTION
            and value["features"]["container_group_count"] == 2
        )
        result = solve_minimal_layout(case["project"], effort_profile="quick")

        self.assertEqual(result["solver"]["result"]["status"], "solution_found")
        self.assertTrue(result["minimal_layout"]["global_certificate"]["certified"])
    def test_holdout_refuses_access_before_a_valid_unique_selection(self) -> None:
        with self.assertRaisesRegex(SolverBenchmarkCorpusError, "holdout selection"):
            materialize_benchmark_split(self.manifest, "holdout")
        selection = build_holdout_selection("hypothesis-one", "a" * 64)

        self.assertEqual(selection["selected_candidate_count"], 1)
        self.assertTrue(selection["selected_before_holdout"])
        tampered = deepcopy(selection)
        tampered["selected_candidate_count"] = 2
        with self.assertRaises(SolverBenchmarkCorpusError):
            open_holdout_cases(self.manifest, tampered)

    def test_incremental_cases_form_six_exact_incremental_cold_pairs_per_split(self) -> None:
        validated = validate_solver_benchmark_manifest(self.manifest)
        for split in ("discovery", "tuning", "holdout"):
            records = [
                case
                for case in validated["generated_cases"]
                if case["split"] == split and case["family"] == "incremental_then_cold"
            ]
            by_sequence: dict[str, list[dict[str, object]]] = {}
            for record in records:
                by_sequence.setdefault(str(record["recipe"]["sequence_id"]), []).append(record)
            with self.subTest(split=split):
                self.assertEqual(len(by_sequence), 6)
                for pair in by_sequence.values():
                    self.assertEqual(len(pair), 2)
                    self.assertEqual(
                        {case["recipe"]["execution_mode"] for case in pair},
                        {"incremental", "cold"},
                    )
                    self.assertEqual(len({case["project_digest"] for case in pair}), 1)
                    self.assertEqual(len({case["previous_project_digest"] for case in pair}), 1)
                    self.assertNotEqual(
                        pair[0]["project_digest"], pair[0]["previous_project_digest"]
                    )

    def test_digest_tampering_fails_closed(self) -> None:
        tampered = deepcopy(self.manifest)
        tampered["generated_cases"][0]["seed"] += 1
        with self.assertRaisesRegex(SolverBenchmarkCorpusError, "digest mismatch"):
            validate_solver_benchmark_manifest(tampered)

    def test_checked_in_fixture_is_exactly_rebuildable_and_portable(self) -> None:
        checked_in = validate_solver_benchmark_manifest(_read(FIXTURE))
        self.assertEqual(checked_in, self.manifest)
        rendered = json.dumps(checked_in, ensure_ascii=False, sort_keys=True).lower()
        for marker in ("c:\\users", "documents\\bgig", "thomas", "client_context"):
            self.assertNotIn(marker, rendered)
        with TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "manifest.json"
            code = BUILDER.main(
                [
                    "--regression-corpus",
                    f"p64-l05d1={L05D}",
                    "--regression-corpus",
                    f"p64-l06a={L06A}",
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(code, 0)
            self.assertEqual(output.read_bytes(), FIXTURE.read_bytes())
            self.assertEqual(
                BUILDER.main(
                    [
                        "--regression-corpus",
                        f"p64-l05d1={L05D}",
                        "--regression-corpus",
                        f"p64-l06a={L06A}",
                        "--output",
                        str(output),
                        "--check-existing",
                    ]
                ),
                0,
            )


if __name__ == "__main__":
    unittest.main()
