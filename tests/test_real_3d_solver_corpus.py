from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from board_game_insert_generator.real_3d_solver_corpus import (
    FAMILIES,
    Real3DCorpusError,
    build_open_case_records,
    build_public_manifest,
    build_sealed_holdout,
    materialize_case_problem,
    materialize_positive_witness,
    validate_positive_witness,
    validate_public_manifest,
    verify_sealed_holdout,
)


ROOT = Path(__file__).resolve().parents[1]


class Real3DSolverCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.open_records = build_open_case_records()
        self.sealed = build_sealed_holdout(campaign_nonce="a" * 64)
        self.manifest = build_public_manifest(self.open_records, self.sealed)

    def test_every_required_family_has_three_tiers_and_a_negative_bound(self) -> None:
        self.assertEqual(len(self.open_records), 41)
        negative_kinds = set()
        for family in FAMILIES:
            records = [
                value
                for value in self.open_records
                if value["family"] == family
                and value["tier"] in {"small", "large", "xl", "negative"}
            ]
            self.assertEqual(
                {value["tier"] for value in records},
                {"small", "large", "xl", "negative"},
            )
            self.assertEqual(
                sum(value["expected"] == "feasible" for value in records), 3
            )
            negative = next(
                value for value in records if value["expected"] == "infeasible"
            )
            negative_kinds.add(negative["infeasibility_bound"]["kind"])
        self.assertGreaterEqual(len(negative_kinds), 7)

    def test_all_positive_witnesses_are_constructed_and_validated_in_3d(self) -> None:
        for record in self.open_records:
            if record["expected"] != "feasible":
                continue
            witness = materialize_positive_witness(record)
            self.assertTrue(witness["constructed_without_solver"])
            validate_positive_witness(record, witness)
            recipe = record["recipe"]
            if recipe["layer_count"] > 1:
                self.assertEqual(
                    len({item["z"] for item in witness["placements"]}),
                    recipe["layer_count"],
                )
            self.assertEqual(
                sum(
                    item["assigned_content_count"]
                    for item in witness["placements"]
                ),
                recipe["content_count"],
            )

    def test_family_witnesses_exercise_real_gate_a_constraints(self) -> None:
        by_family = {
            record["family"]: record
            for record in self.open_records
            if record["tier"] == "xl"
        }
        layers = by_family["layers"]["recipe"]
        self.assertEqual(layers["layer_count"], 5)
        self.assertGreater(len(set(layers["layer_heights_mm"])), 1)

        support_witness = materialize_positive_witness(by_family["support"])
        self.assertTrue(
            any(
                len(item["support_ids"]) >= 2
                for item in support_witness["placements"]
            )
        )

        reservations = by_family["reservations"]["recipe"]["reservation_volumes"]
        self.assertEqual({value["zone"] for value in reservations}, {"lower", "upper"})
        self.assertEqual(by_family["access"]["recipe"]["access_policy"], "top_down")
        self.assertEqual(
            by_family["fragmentation"]["recipe"]["fragment_gap_mm"], 2
        )
        self.assertEqual(
            by_family["variants"]["recipe"]["variant_front_cycle"],
            [1, 2, 4, 8],
        )

        variant_problem = materialize_case_problem(by_family["variants"])
        self.assertEqual(
            [len(item["variants"]) for item in variant_problem["participants"][:4]],
            [1, 2, 4, 8],
        )
        self.assertNotEqual(
            variant_problem["participants"][1]["variants"][0]["size"],
            variant_problem["participants"][1]["variants"][1]["size"],
        )

    def test_limit_families_reach_required_cardinalities(self) -> None:
        many_containers = next(
            value
            for value in self.open_records
            if value["family"] == "many-containers" and value["tier"] == "xl"
        )
        many_assets = next(
            value
            for value in self.open_records
            if value["family"] == "many-assets" and value["tier"] == "xl"
        )
        mixed = next(
            value
            for value in self.open_records
            if value["family"] == "mixed-extreme" and value["tier"] == "xl"
        )
        self.assertGreaterEqual(many_containers["recipe"]["container_count"], 64)
        self.assertEqual(many_containers["recipe"]["cell_stride_mm"], 10)
        self.assertEqual(
            many_containers["recipe"]["difficulty_profile"], "adversarial-xl"
        )
        self.assertGreaterEqual(many_assets["recipe"]["content_count"], 256)
        self.assertEqual(mixed["recipe"]["layer_count"], 5)
        self.assertEqual(mixed["recipe"]["variant_front_cycle"], [8])
        self.assertEqual(mixed["recipe"]["container_count"], 158)
        self.assertEqual(mixed["recipe"]["content_count"], 632)

    def test_real_anonymized_family_points_to_reviewed_bundle(self) -> None:
        source_fixture = json.loads(
            (
                ROOT / "tests/fixtures/p64_l06a_reviewed_real_case.v1.json"
            ).read_text(encoding="utf-8")
        )
        source_case = source_fixture["cases"][0]
        real_case = next(
            value
            for value in self.open_records
            if value["family"] == "real-anonymized" and value["tier"] == "small"
        )
        source = real_case["recipe"]["source"]
        self.assertEqual(source["case_id"], source_case["case_id"])
        self.assertEqual(
            source["bundle_digest"], source_case["source"]["bundle_digest"]
        )
        self.assertEqual(source["scale_factor"], 1)

        regression = next(
            value
            for value in self.open_records
            if value["tier"] == "reviewed-real"
        )
        self.assertEqual(regression["expected"], "bounded_unknown")
        self.assertEqual(
            regression["recipe"]["project_digest"], source_case["project_digest"]
        )
        self.assertEqual(
            materialize_case_problem(regression)["semantic_reduction"], "none"
        )

    def test_holdout_nonce_changes_problem_commitments_and_semantics(self) -> None:
        other = build_sealed_holdout(campaign_nonce="b" * 64)
        self.assertNotEqual(
            self.sealed["sealed_holdout_digest"],
            other["sealed_holdout_digest"],
        )
        first_records = {
            (value["family"], value["tier"]): value
            for value in self.sealed["case_records"]
            if value["expected"] == "feasible"
        }
        other_records = {
            (value["family"], value["tier"]): value
            for value in other["case_records"]
            if value["expected"] == "feasible"
        }
        self.assertTrue(
            all(
                first_records[key]["problem_digest"]
                != other_records[key]["problem_digest"]
                for key in first_records
            )
        )
        self.assertTrue(
            any(
                first_records[key]["recipe"]["layer_heights_mm"]
                != other_records[key]["recipe"]["layer_heights_mm"]
                or materialize_case_problem(first_records[key])["participants"][0]
                ["variants"][0]["size"]
                != materialize_case_problem(other_records[key])["participants"][0]
                ["variants"][0]["size"]
                for key in first_records
            )
        )

    def test_public_manifest_hides_complete_unused_holdout(self) -> None:
        accepted = validate_public_manifest(self.manifest)
        receipt = accepted["sealed_holdout_receipt"]
        self.assertNotIn("case_records", receipt)
        self.assertNotIn("campaign_nonce", receipt)
        self.assertEqual(receipt["case_count"], 40)
        self.assertEqual(receipt["tier_counts"], {"small": 10, "large": 10, "xl": 10})
        self.assertFalse(receipt["opened"])
        self.assertEqual(
            verify_sealed_holdout(self.manifest, self.sealed)["status"],
            "verified_closed",
        )

    def test_tampered_support_access_and_holdout_are_rejected(self) -> None:
        support_case = next(
            value
            for value in self.open_records
            if value["family"] == "support" and value["tier"] == "small"
        )
        witness = materialize_positive_witness(support_case)
        witness["placements"][2]["support_ids"] = ["container-000"]
        with self.assertRaises(Real3DCorpusError):
            validate_positive_witness(support_case, witness)

        access_case = next(
            value
            for value in self.open_records
            if value["family"] == "access" and value["tier"] == "small"
        )
        witness = materialize_positive_witness(access_case)
        elevated = next(item for item in witness["placements"] if item["z"] > 0)
        elevated["removal_rank"] = 99
        with self.assertRaises(Real3DCorpusError):
            validate_positive_witness(access_case, witness)

        tampered = deepcopy(self.sealed)
        tampered["case_records"][0]["recipe"]["container_count"] += 1
        with self.assertRaises(Real3DCorpusError):
            verify_sealed_holdout(self.manifest, tampered)

    def test_committed_manifest_validates_without_private_recipe(self) -> None:
        path = ROOT / "tests/fixtures/p64_l08d_real_3d_corpus.v1.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        accepted = validate_public_manifest(payload)
        self.assertEqual(accepted["open_case_count"], 41)
        self.assertNotIn(
            "case_records", accepted["sealed_holdout_receipt"]
        )


if __name__ == "__main__":
    unittest.main()
