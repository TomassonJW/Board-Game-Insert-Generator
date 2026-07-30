from __future__ import annotations

from pathlib import Path
import unittest

from scripts.solver import plan_p64_l09w_d_stratified_validation as planner


ROOT = Path(__file__).resolve().parents[1]


def _result(
    *,
    stratum: str,
    index: int,
) -> dict[str, object]:
    return {
        "stratum": stratum,
        "losses": [{"detail": planner.TARGET_LOSS}],
        "features": {
            "target_density_pct": (30, 65, 85, 95)[index % 4],
            "box_size": ("small", "medium", "large")[index % 3],
            "execution": (
                "cold",
                "add",
                "remove",
                "local_parameter",
                "global_parameter",
            )[index % 5],
            "layer_bucket": ("1", "2", "3", "4+")[index % 4],
            "flat_count": index % 7,
            "fragmentation_class": (
                "single-layer",
                "layered",
                "reserved-top",
            )[index % 3],
            "aspect_profile": (
                "balanced",
                "deep",
                "near-equal-xy",
                "tall",
                "wide",
            )[index % 5],
        },
        "runs": [
            {
                "timings": {
                    "calculation_ms": float(100 + index * 10),
                }
            }
        ],
    }


class P64L09WDStratifiedValidationTests(unittest.TestCase):
    def test_selection_is_deterministic_causal_and_covers_every_axis_value(
        self,
    ) -> None:
        results: dict[str, dict[str, object]] = {}
        for stratum, causal_id in zip(
            ("common", "stress"),
            planner.CAUSAL_CASE_IDS,
            strict=True,
        ):
            results[causal_id] = _result(stratum=stratum, index=0)
            for index in range(1, 16):
                results[f"{stratum}-{index:02d}"] = _result(
                    stratum=stratum,
                    index=index,
                )

            first = planner.select_stratified_target_cases(
                results,
                stratum=stratum,
            )
            second = planner.select_stratified_target_cases(
                results,
                stratum=stratum,
            )
            self.assertEqual(first, second)
            self.assertIn(causal_id, first)
            self.assertGreaterEqual(
                len(first),
                planner.MINIMUM_SAMPLE_SIZE_PER_STRATUM,
            )

            population_categories = set().union(
                *(
                    planner._case_categories(result)
                    for result in results.values()
                    if result["stratum"] == stratum
                )
            )
            selected_categories = set().union(
                *(planner._case_categories(results[case_id]) for case_id in first)
            )
            self.assertEqual(selected_categories, population_categories)

    def test_protocol_keeps_holdout_for_e_and_rejects_rate_claims_from_d(
        self,
    ) -> None:
        protocol = (
            ROOT
            / "docs/P64_L09W_D_TO_F_STRATIFIED_VALIDATION_PROTOCOL.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "361 cas",
            "non nécessaires",
            "53",
            "81",
            "sample_is_rate_estimator=false",
            "P64-L09W-E",
            "qu’une seule fois",
            "238/240",
            "380/400",
            "P64-L09W-F",
            "conditionnelle",
        ):
            self.assertIn(marker, protocol)

        source = (
            ROOT
            / "scripts/solver/plan_p64_l09w_d_stratified_validation.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("--holdout", source)


if __name__ == "__main__":
    unittest.main()
