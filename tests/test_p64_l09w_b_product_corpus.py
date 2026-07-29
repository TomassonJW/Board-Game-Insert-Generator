from __future__ import annotations

from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.product_solver_robustness_corpus import (
    BOX_SIZE_VALUES,
    CONTAINER_COUNT_VALUES,
    CONTENTS_PER_CONTAINER_VALUES,
    DENSITY_VALUES,
    EXECUTION_VALUES,
    FLAT_COUNT_VALUES,
    ProductRobustnessCorpusError,
    build_holdout_recipe_plan,
    build_negative_control_records,
    build_open_recipe_plan,
    build_positive_case_record,
    build_soak_recipe,
    materialize_positive_case_bundle,
    validate_negative_case_record,
    validate_positive_case_record,
    validate_public_manifest,
)
from scripts.solver import build_p64_l09w_b_product_corpus as corpus_builder


ROOT = Path(__file__).resolve().parents[1]


class P64L09WBProductCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.open_recipes = build_open_recipe_plan()
        cls.holdout_recipes = build_holdout_recipe_plan(
            campaign_nonce="a" * 64
        )

    def test_open_and_holdout_plans_meet_preregistered_pairwise_minima(
        self,
    ) -> None:
        for recipes in (self.open_recipes, self.holdout_recipes):
            self.assertEqual(len(recipes), 400)
            self.assertEqual(
                Counter(recipe["stratum"] for recipe in recipes),
                {"common": 240, "stress": 160},
            )
            requirements = (
                ("contents_per_container", CONTENTS_PER_CONTAINER_VALUES, 20),
                ("container_count", CONTAINER_COUNT_VALUES, 20),
                ("target_density_pct", DENSITY_VALUES, 60),
                ("flat_count", FLAT_COUNT_VALUES, 20),
                ("layer_bucket", ("1", "2", "3", "4+"), 40),
                ("box_size", BOX_SIZE_VALUES, 60),
                ("execution", EXECUTION_VALUES, 40),
            )
            for axis, values, minimum in requirements:
                counts = Counter(
                    recipe["axes"][axis] for recipe in recipes
                )
                for value in values:
                    self.assertGreaterEqual(
                        counts[value],
                        minimum,
                        f"{axis}={value}",
                    )

    def test_positive_truth_is_constructed_then_currently_recertified(
        self,
    ) -> None:
        recipe = self.open_recipes[50]
        record = build_positive_case_record(recipe)
        accepted = validate_positive_case_record(
            record,
            reconstruct=True,
            recertify=True,
        )

        self.assertEqual(accepted["expected"], "feasible")
        self.assertTrue(accepted["oracle_receipt"]["certified"])
        self.assertTrue(
            accepted["oracle_receipt"]["strictly_subtractive_top_insets"]
        )
        self.assertEqual(accepted["solver_invocation_count"], 0)
        self.assertEqual(
            accepted["oracle_receipt"]["solver_invocation_count"],
            0,
        )

    def test_witness_never_enters_the_project_given_to_the_solver(self) -> None:
        recipe = self.open_recipes[50]
        bundle = materialize_positive_case_bundle(recipe)

        self.assertTrue(bundle["witness"]["constructed_without_solver"])
        self.assertNotIn("witness", bundle["after_project"])
        self.assertNotIn("placements", bundle["after_project"])
        self.assertEqual(bundle["witness"]["solver_invocation_count"], 0)

    def test_edit_sequences_reconstruct_distinct_before_and_after_projects(
        self,
    ) -> None:
        by_execution = {
            execution: next(
                recipe
                for recipe in self.open_recipes
                if recipe["axes"]["execution"] == execution
            )
            for execution in EXECUTION_VALUES
        }
        cold = materialize_positive_case_bundle(by_execution["cold"])
        self.assertIsNone(cold["before_project"])
        self.assertEqual(cold["edit_sequence"]["operations"], [])

        for execution in EXECUTION_VALUES[1:]:
            bundle = materialize_positive_case_bundle(by_execution[execution])
            self.assertIsNotNone(bundle["before_project"])
            self.assertNotEqual(
                canonical_digest(bundle["before_project"]),
                canonical_digest(bundle["after_project"]),
            )
            self.assertEqual(len(bundle["edit_sequence"]["operations"]), 1)

    def test_open_and_holdout_commitments_are_distinct(self) -> None:
        for ordinal in (0, 50, 239, 240, 399):
            open_bundle = materialize_positive_case_bundle(
                self.open_recipes[ordinal]
            )
            holdout_bundle = materialize_positive_case_bundle(
                self.holdout_recipes[ordinal]
            )
            self.assertNotEqual(
                canonical_digest(open_bundle["after_project"]),
                canonical_digest(holdout_bundle["after_project"]),
            )
            self.assertNotEqual(
                canonical_digest(open_bundle["witness"]),
                canonical_digest(holdout_bundle["witness"]),
            )
            self.assertNotEqual(
                canonical_digest(open_bundle["edit_sequence"]),
                canonical_digest(holdout_bundle["edit_sequence"]),
            )

    def test_negative_controls_have_four_independent_formal_bounds(self) -> None:
        records = build_negative_control_records()

        self.assertEqual(len(records), 40)
        self.assertEqual(
            Counter(record["proof_family"] for record in records),
            {
                "volume": 10,
                "axis": 10,
                "stacking_z": 10,
                "reservation": 10,
            },
        )
        for record in records:
            accepted = validate_negative_case_record(record)
            self.assertTrue(accepted["proof"]["strict_inequality"])
            self.assertEqual(accepted["solver_invocation_count"], 0)

    def test_tampered_positive_and_negative_commitments_fail_closed(self) -> None:
        positive = build_positive_case_record(self.open_recipes[0])
        positive["project_digest"] = "0" * 64
        with self.assertRaises(ProductRobustnessCorpusError):
            validate_positive_case_record(positive)

        negative = build_negative_control_records()[0]
        negative["proof"]["facts"]["available_box_volume_mm3"] += 1.0
        with self.assertRaises(ProductRobustnessCorpusError):
            validate_negative_case_record(negative)

    def test_soak_plan_is_deterministic_distinct_and_reconstructible(self) -> None:
        first = build_soak_recipe(0)
        repeated = build_soak_recipe(0)
        last = build_soak_recipe(1_999)

        self.assertEqual(first, repeated)
        self.assertEqual(first["split"], "soak")
        self.assertNotEqual(first["case_id"], last["case_id"])
        self.assertNotEqual(canonical_digest(first), canonical_digest(last))

    def test_checkpoint_builder_limits_new_records_and_resumes(self) -> None:
        recipes = [
            {"case_id": f"case-{ordinal}", "ordinal": ordinal}
            for ordinal in range(5)
        ]

        def build_record(recipe: dict[str, object]) -> dict[str, object]:
            return {
                "case_id": recipe["case_id"],
                "recipe_digest": canonical_digest(recipe),
            }

        def validate_record(
            record: dict[str, object],
            *,
            reconstruct: bool,
        ) -> dict[str, object]:
            self.assertFalse(reconstruct)
            return record

        work_root = ROOT / ".codex-work"
        work_root.mkdir(exist_ok=True)
        with TemporaryDirectory(dir=work_root) as temporary:
            checkpoint_dir = Path(temporary) / "checkpoints"
            with (
                patch.object(
                    corpus_builder,
                    "build_positive_case_record",
                    side_effect=build_record,
                ) as build_mock,
                patch.object(
                    corpus_builder,
                    "validate_positive_case_record",
                    side_effect=validate_record,
                ),
                redirect_stdout(StringIO()),
            ):
                first = corpus_builder._build_checkpointed_records(
                    "test",
                    recipes,
                    checkpoint_dir=checkpoint_dir,
                    max_new_records=2,
                )
                second = corpus_builder._build_checkpointed_records(
                    "test",
                    recipes,
                    checkpoint_dir=checkpoint_dir,
                    max_new_records=1,
                )

        self.assertEqual(first.existing_record_count, 0)
        self.assertEqual(first.new_record_count, 2)
        self.assertEqual(first.remaining_record_count, 3)
        self.assertEqual(len(first.records), 2)
        self.assertEqual(second.existing_record_count, 2)
        self.assertEqual(second.new_record_count, 1)
        self.assertEqual(second.remaining_record_count, 2)
        self.assertEqual(len(second.records), 3)
        self.assertEqual(build_mock.call_count, 3)

    def test_committed_manifest_is_compact_and_does_not_leak_holdout(
        self,
    ) -> None:
        path = (
            ROOT
            / "tests"
            / "fixtures"
            / "p64_l09w_b_product_corpus.v1.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        accepted = validate_public_manifest(payload)
        receipt = accepted["sealed_holdout_receipt"]

        self.assertEqual(
            len(accepted["open_positive_case_records"]),
            400,
        )
        self.assertEqual(len(accepted["negative_control_records"]), 40)
        self.assertEqual(
            accepted["regression_source"]["split"],
            "regression",
        )
        self.assertFalse(
            accepted["regression_source"]["case_records_embedded"]
        )
        self.assertTrue(
            accepted["regression_source"]["legacy_holdouts_consumed"]
        )
        self.assertEqual(receipt["positive_case_count"], 400)
        self.assertFalse(receipt["opened"])
        self.assertEqual(receipt["opening_count"], 0)
        self.assertNotIn("case_records", receipt)
        self.assertNotIn("campaign_nonce", receipt)
        self.assertEqual(
            accepted["soak_plan"]["recipe_count"],
            2_000,
        )


if __name__ == "__main__":
    unittest.main()
