from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import importlib.util
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from board_game_insert_generator.external_solver_benchmark_corpus import (
    EXTERNAL_CASE_ID_PREFIX,
    ExternalSolverBenchmarkCorpusError,
    build_external_holdout_selection,
    build_external_sealed_holdout,
    build_external_solver_benchmark_manifest,
    materialize_external_benchmark_split,
    open_external_holdout_cases,
    public_source_catalog,
    validate_external_solver_benchmark_manifest,
    verify_downloaded_public_source,
    verify_external_sealed_holdout,
)
from board_game_insert_generator.incremental_project_state import canonical_digest


ROOT = Path(__file__).resolve().parents[1]
L06_FIXTURE = ROOT / "tests" / "fixtures" / "p64_l06_solver_benchmark.v1.json"
V2_FIXTURE = ROOT / "tests" / "fixtures" / "p64_l07b_solver_benchmark.v2.json"
BUILDER_SCRIPT = (
    ROOT / "scripts" / "solver" / "build_external_solver_benchmark_manifest.py"
)
FETCHER_SCRIPT = ROOT / "scripts" / "solver" / "fetch_public_solver_benchmark.py"
HOLDOUT_CREATOR_SCRIPT = (
    ROOT / "scripts" / "solver" / "create_external_solver_holdout.py"
)


def _load_script(name: str, path: Path) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILDER = _load_script("external_solver_manifest_builder", BUILDER_SCRIPT)
FETCHER = _load_script("public_solver_benchmark_fetcher", FETCHER_SCRIPT)
HOLDOUT_CREATOR = _load_script(
    "external_solver_holdout_creator", HOLDOUT_CREATOR_SCRIPT
)


def _read(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _selection(manifest: dict[str, object]) -> dict[str, object]:
    return build_external_holdout_selection(
        primary_candidate_id="candidate-main",
        complementary_candidate_ids=["candidate-complement"],
        router_digest="1" * 64,
        candidate_bundle_digest="2" * 64,
        open_corpus_digest=str(manifest["open_corpus_digest"]),
        settings_digest="4" * 64,
        total_budget_seconds=600,
    )


def _synthetic_source(
    payload: bytes,
    *,
    source_id: str = "synthetic-public",
) -> dict[str, object]:
    source: dict[str, object] = {
        "source_id": source_id,
        "license": {"spdx": "MIT"},
        "artifact": {
            "kind": "text",
            "byte_count": len(payload),
            "sha256": sha256(payload).hexdigest(),
            "selected_members": [],
        },
        "objective_mapping": {
            "benchmark_role": "public_method_control_only",
            "product_ranking_eligible": False,
        },
        "download_url": "https://example.invalid/public-source.txt",
    }
    source["source_digest"] = canonical_digest(source)
    return source


class ExternalSolverBenchmarkCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.l06 = _read(L06_FIXTURE)
        cls.sealed_holdout = build_external_sealed_holdout(
            seed_base=6_407_990_001,
            split_offset=13,
            campaign_nonce="a" * 64,
        )
        cls.manifest = build_external_solver_benchmark_manifest(
            cls.l06,
            cls.sealed_holdout,
        )

    def test_v2_preserves_regressions_and_replaces_the_consumed_holdout(self) -> None:
        validated = validate_external_solver_benchmark_manifest(self.manifest)

        self.assertEqual(validated["summary"]["regression_case_count"], 8)
        self.assertEqual(validated["summary"]["bgig_generated_case_count"], 192)
        self.assertEqual(validated["summary"]["open_bgig_generated_case_count"], 128)
        self.assertEqual(validated["summary"]["holdout_case_count"], 64)
        self.assertEqual(len(validated["bgig_generated_cases"]), 128)
        self.assertNotIn(
            "holdout",
            {case["split"] for case in validated["bgig_generated_cases"]},
        )
        self.assertFalse(validated["holdout_policy"]["recipes_embedded_in_manifest"])
        self.assertFalse(
            validated["holdout_policy"]["seed_material_embedded_in_manifest"]
        )
        self.assertEqual(
            validated["historical_baseline"]["l06_holdout_status_for_l07"],
            "consumed_open_regression_archive_only",
        )
        self.assertFalse(
            validated["historical_baseline"]["eligible_as_final_arbitrator"]
        )
        self.assertNotEqual(
            validated["holdout_policy"]["case_commitment_digest"],
            self.l06["holdout_policy"]["case_commitment_digest"],
        )
        self.assertTrue(
            all(
                case["case_id"].startswith(EXTERNAL_CASE_ID_PREFIX)
                for case in validated["bgig_generated_cases"]
            )
        )

    def test_generated_families_and_projects_do_not_leak_between_splits(self) -> None:
        validated = validate_external_solver_benchmark_manifest(self.manifest)
        split_records = {
            "discovery": [
                case
                for case in validated["bgig_generated_cases"]
                if case["split"] == "discovery"
            ],
            "tuning": [
                case
                for case in validated["bgig_generated_cases"]
                if case["split"] == "tuning"
            ],
            "holdout": list(self.sealed_holdout["case_records"]),
        }
        for records in split_records.values():
            self.assertEqual(len(records), 64)
            self.assertEqual(
                {case["family"] for case in records},
                set(validated["matrix"]["families"]),
            )
            self.assertEqual(
                {
                    case["recipe"]["reservation_mode"]
                    for case in records
                },
                {"absent", "constraining"},
            )
            self.assertEqual(
                {
                    case["recipe"]["rotation_policy_target"]
                    for case in records
                },
                {"forbidden_by_benchmark", "permitted"},
            )
            self.assertEqual(
                {case["recipe"]["layer_count"] for case in records},
                {1, 2, 3},
            )
            self.assertEqual(
                {case["recipe"]["execution_mode"] for case in records},
                {"cold", "incremental"},
            )
        for field in ("case_id", "seed", "project_digest", "previous_project_digest"):
            values = {
                split: {
                    case[field]
                    for case in records
                    if case.get(field) is not None
                }
                for split, records in split_records.items()
            }
            self.assertFalse(values["discovery"] & values["tuning"])
            self.assertFalse(values["discovery"] & values["holdout"])
            self.assertFalse(values["tuning"] & values["holdout"])

    def test_public_sources_are_pinned_and_excluded_from_product_ranking(self) -> None:
        validated = validate_external_solver_benchmark_manifest(self.manifest)
        sources = validated["public_sources"]

        self.assertEqual(len(sources), 2)
        self.assertEqual(
            {source["source_id"] for source in sources},
            {"orlib-thpack9", "q4realbpp-v1"},
        )
        self.assertEqual(
            {source["license"]["spdx"] for source in sources},
            {"MIT", "GPL-3.0-only"},
        )
        self.assertTrue(
            all(
                source["objective_mapping"]["product_ranking_eligible"] is False
                for source in sources
            )
        )
        self.assertTrue(
            all(len(source["artifact"]["sha256"]) == 64 for source in sources)
        )
        controls = validated["public_method_controls"]
        self.assertEqual(len(controls), 8)
        self.assertEqual({case["split"] for case in controls}, {"discovery", "tuning"})
        self.assertTrue(
            all(case["product_ranking_eligible"] is False for case in controls)
        )
        self.assertTrue(all(case["holdout_eligible"] is False for case in controls))

    def test_small_controls_cover_positive_and_negative_truths(self) -> None:
        validated = validate_external_solver_benchmark_manifest(self.manifest)
        controls = validated["small_exact_controls"]

        self.assertEqual(len(controls), 4)
        for split in ("discovery", "tuning"):
            split_controls = [case for case in controls if case["split"] == split]
            self.assertEqual(
                {case["expected_truth"] for case in split_controls},
                {"feasible", "impossible"},
            )
            self.assertTrue(
                all(case["container_group_count"] <= 4 for case in split_controls)
            )
            self.assertTrue(
                all(case["supplied_to_tested_solver"] is False for case in split_controls)
            )

    def test_open_splits_materialize_with_verified_independent_oracles(self) -> None:
        for split in ("discovery", "tuning"):
            cases = materialize_external_benchmark_split(self.manifest, split)
            with self.subTest(split=split):
                self.assertEqual(len(cases), 64)
                self.assertEqual(
                    {case["oracle"]["expected_truth"] for case in cases},
                    {"feasible", "impossible"},
                )
                self.assertTrue(
                    all(case["invariants"]["solver_invocation_count"] == 0 for case in cases)
                )
                self.assertTrue(
                    all(case["oracle"]["supplied_to_tested_solver"] is False for case in cases)
                )

    def test_holdout_refuses_implicit_access_then_opens_after_selection(self) -> None:
        with self.assertRaisesRegex(
            ExternalSolverBenchmarkCorpusError,
            "holdout selection",
        ):
            materialize_external_benchmark_split(self.manifest, "holdout")

        selection = _selection(self.manifest)
        with self.assertRaisesRegex(
            ExternalSolverBenchmarkCorpusError,
            "sidecar",
        ):
            open_external_holdout_cases(self.manifest, selection, None)

        verified = verify_external_sealed_holdout(
            self.manifest,
            self.sealed_holdout,
        )
        self.assertEqual(verified["case_count"], 64)
        opened = open_external_holdout_cases(
            self.manifest,
            selection,
            self.sealed_holdout,
        )

        self.assertEqual(len(opened["cases"]), 64)
        self.assertEqual(opened["selection"]["selected_candidate_count"], 2)
        self.assertFalse(opened["invariants"]["post_open_tuning_allowed"])
        tampered = deepcopy(selection)
        tampered["selected_candidate_ids"].append("late-candidate")
        with self.assertRaises(ExternalSolverBenchmarkCorpusError):
            open_external_holdout_cases(
                self.manifest,
                tampered,
                self.sealed_holdout,
            )
        tampered_sidecar = deepcopy(self.sealed_holdout)
        tampered_sidecar["case_records"][0]["seed"] += 1
        with self.assertRaises(ExternalSolverBenchmarkCorpusError):
            open_external_holdout_cases(
                self.manifest,
                selection,
                tampered_sidecar,
            )
        wrong_corpus_selection = build_external_holdout_selection(
            primary_candidate_id="candidate-main",
            complementary_candidate_ids=[],
            router_digest="1" * 64,
            candidate_bundle_digest="2" * 64,
            open_corpus_digest="f" * 64,
            settings_digest="4" * 64,
            total_budget_seconds=600,
        )
        with self.assertRaisesRegex(
            ExternalSolverBenchmarkCorpusError,
            "not bound",
        ):
            open_external_holdout_cases(
                self.manifest,
                wrong_corpus_selection,
                self.sealed_holdout,
            )
        with self.assertRaises(ExternalSolverBenchmarkCorpusError):
            build_external_holdout_selection(
                primary_candidate_id=7,  # type: ignore[arg-type]
                complementary_candidate_ids=[],
                router_digest="1" * 64,
                candidate_bundle_digest="2" * 64,
                open_corpus_digest=str(self.manifest["open_corpus_digest"]),
                settings_digest="4" * 64,
                total_budget_seconds=600,
            )

    def test_manifest_tampering_fails_closed(self) -> None:
        tampered = deepcopy(self.manifest)
        tampered["bgig_generated_cases"][0]["seed"] += 1

        with self.assertRaisesRegex(
            ExternalSolverBenchmarkCorpusError,
            "digest mismatch",
        ):
            validate_external_solver_benchmark_manifest(tampered)

    def test_checked_in_fixture_is_sealed_and_portable(self) -> None:
        checked_in = validate_external_solver_benchmark_manifest(_read(V2_FIXTURE))

        self.assertEqual(len(checked_in["bgig_generated_cases"]), 128)
        self.assertTrue(
            all(
                case["split"] in {"discovery", "tuning"}
                for case in checked_in["bgig_generated_cases"]
            )
        )
        rendered = json.dumps(checked_in, ensure_ascii=False, sort_keys=True).lower()
        for marker in (
            "c:\\users",
            "documents\\bgig",
            "thomas",
            "client_context",
            "campaign_nonce",
            "\"seed_base\":",
        ):
            self.assertNotIn(marker, rendered)
        with TemporaryDirectory() as temp_dir:
            sealed_path = Path(temp_dir) / "sealed-holdout.json"
            sealed_path.write_text(
                json.dumps(self.sealed_holdout, ensure_ascii=False),
                encoding="utf-8",
            )
            output = Path(temp_dir) / "manifest.json"
            arguments = [
                "--historical-l06-manifest",
                str(L06_FIXTURE),
                "--sealed-holdout",
                str(sealed_path),
                "--output",
                str(output),
            ]
            self.assertEqual(BUILDER.main(arguments), 0)
            self.assertEqual(
                validate_external_solver_benchmark_manifest(_read(output)),
                self.manifest,
            )
            self.assertEqual(
                BUILDER.main([*arguments, "--check-existing"]),
                0,
            )

    def test_holdout_creator_is_fresh_and_emits_a_verifiable_sidecar(self) -> None:
        with TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "sealed-holdout.json"
            self.assertEqual(
                HOLDOUT_CREATOR.main(["--output", str(output)]),
                0,
            )
            sealed = _read(output)
            manifest = build_external_solver_benchmark_manifest(self.l06, sealed)
            self.assertEqual(
                verify_external_sealed_holdout(manifest, sealed)["case_count"],
                64,
            )
            with self.assertRaises(FileExistsError):
                HOLDOUT_CREATOR.main(["--output", str(output)])

    def test_public_source_verifier_checks_text_and_selected_zip_members(self) -> None:
        payload = b"public benchmark control\n"
        source = _synthetic_source(payload)
        with TemporaryDirectory() as temp_dir:
            text_path = Path(temp_dir) / "source.txt"
            text_path.write_bytes(payload)
            verified = verify_downloaded_public_source(source, text_path)
            self.assertEqual(verified["status"], "verified")

            zip_path = Path(temp_dir) / "source.zip"
            member_payload = b"selected public case\n"
            with ZipFile(zip_path, "w") as archive:
                archive.writestr("cases/one.txt", member_payload)
            zip_source = _synthetic_source(zip_path.read_bytes(), source_id="synthetic-zip")
            zip_source["artifact"] = {
                "kind": "zip",
                "byte_count": zip_path.stat().st_size,
                "sha256": sha256(zip_path.read_bytes()).hexdigest(),
                "selected_members": [
                    {
                        "path": "cases/one.txt",
                        "byte_count": len(member_payload),
                        "sha256": sha256(member_payload).hexdigest(),
                    }
                ],
            }
            zip_source.pop("source_digest")
            zip_source["source_digest"] = canonical_digest(zip_source)
            zip_verified = verify_downloaded_public_source(zip_source, zip_path)
            self.assertEqual(len(zip_verified["selected_members"]), 1)

    def test_fetcher_uses_a_fresh_path_and_can_recheck_without_network(self) -> None:
        payload = b"bounded public source\n"
        source = _synthetic_source(payload)
        with TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "source.txt"
            with (
                patch.object(FETCHER, "public_source_catalog", return_value=[source]),
                patch.object(FETCHER, "urlopen", return_value=io.BytesIO(payload)),
            ):
                self.assertEqual(
                    FETCHER.main(
                        [
                            "--source-id",
                            str(source["source_id"]),
                            "--output",
                            str(output),
                        ]
                    ),
                    0,
                )
            self.assertEqual(output.read_bytes(), payload)
            with (
                patch.object(FETCHER, "public_source_catalog", return_value=[source]),
                patch.object(
                    FETCHER,
                    "urlopen",
                    side_effect=AssertionError("network must stay unused"),
                ),
            ):
                self.assertEqual(
                    FETCHER.main(
                        [
                            "--source-id",
                            str(source["source_id"]),
                            "--output",
                            str(output),
                            "--check-existing",
                        ]
                    ),
                    0,
                )

    def test_catalog_matches_the_verified_external_metadata(self) -> None:
        sources = {source["source_id"]: source for source in public_source_catalog()}

        self.assertEqual(
            sources["orlib-thpack9"]["artifact"]["sha256"],
            "a4f5e3a748709217cdc749f7d27940f15b9f2a31b3e840e725642237036f82cc",
        )
        self.assertEqual(
            sources["q4realbpp-v1"]["artifact"]["sha256"],
            "dd3825b8abac54e04e748777d654065e176bb6ddf5e479cbeb638630fdb22fb4",
        )
        self.assertEqual(
            len(sources["q4realbpp-v1"]["artifact"]["selected_members"]),
            4,
        )


if __name__ == "__main__":
    unittest.main()
