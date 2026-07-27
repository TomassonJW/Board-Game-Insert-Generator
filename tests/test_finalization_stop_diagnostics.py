import unittest

from board_game_insert_generator.finalization_stop_diagnostics import (
    FINALIZATION_STOP_DIAGNOSTICS_SCHEMA_V1,
    OUTCOME_CERTIFICATE_REJECTED,
    OUTCOME_DEADLINE_REACHED,
    OUTCOME_PREREQUISITE_MISSING,
    OUTCOME_PROVEN_IMPOSSIBLE,
    OUTCOME_STALE,
    OUTCOME_STRATEGY_EXHAUSTED,
    OUTCOME_SUCCESS,
    build_finalization_stop_diagnostics,
)


class FinalizationStopDiagnosticsTests(unittest.TestCase):
    def diagnostics(
        self,
        stop_reason: str,
        *,
        status: str = "no_solution_within_budget",
        elapsed_ms: int = 120,
        **report: object,
    ) -> dict[str, object]:
        return build_finalization_stop_diagnostics(
            {
                "status": status,
                "stop_reason": stop_reason,
                **report,
            },
            elapsed_ms=elapsed_ms,
            budget_cap_ms=3_000,
        )

    def test_success_is_explicit_and_never_an_impossibility(self) -> None:
        result = self.diagnostics(
            "global_finalization_certified",
            status="solution_found",
        )

        self.assertEqual(
            result["schema_version"],
            FINALIZATION_STOP_DIAGNOSTICS_SCHEMA_V1,
        )
        self.assertEqual(result["outcome_kind"], OUTCOME_SUCCESS)
        self.assertFalse(result["proof_of_impossibility"])

    def test_missing_minimal_plan_is_a_prerequisite(self) -> None:
        result = self.diagnostics("minimal_layout_missing_or_stale")

        self.assertEqual(
            result["outcome_kind"],
            OUTCOME_PREREQUISITE_MISSING,
        )
        self.assertEqual(result["phase"], "prerequis")
        self.assertIn("Calculer", result["user_summary"])
        self.assertTrue(result["stopped_before_cap"])

    def test_deadline_is_distinct_from_an_early_stop(self) -> None:
        result = self.diagnostics(
            "global_deadline_reached_before_final_certificate",
            elapsed_ms=2_500,
            deadline_reached=True,
        )

        self.assertEqual(result["outcome_kind"], OUTCOME_DEADLINE_REACHED)
        self.assertEqual(result["phase"], "certificat_final")
        self.assertTrue(result["deadline_reached"])
        self.assertFalse(result["stopped_before_cap"])
        self.assertFalse(result["proof_of_impossibility"])

    def test_slow_termination_is_separate_from_the_search_cap(self) -> None:
        result = self.diagnostics(
            "global_deadline_reached_before_final_certificate",
            elapsed_ms=4_200,
            deadline_reached=True,
        )

        self.assertEqual(result["budget_elapsed_ms"], 3_000)
        self.assertEqual(result["termination_elapsed_ms"], 1_200)
        self.assertEqual(result["wall_clock_elapsed_ms"], 4_200)
        self.assertEqual(result["wall_clock_cap_ms"], 3_000)
        self.assertTrue(result["wall_clock_cap_exceeded"])
        self.assertTrue(result["elapsed_is_search_plus_termination"])

    def test_certificate_rejection_preserves_technical_counters(self) -> None:
        result = self.diagnostics(
            "xy_composite_product_certificate_rejected",
            candidates_evaluated=4,
            rejection_codes=["top_inset_clearance_failed"],
        )

        self.assertEqual(
            result["outcome_kind"],
            OUTCOME_CERTIFICATE_REJECTED,
        )
        self.assertEqual(result["phase"], "fermeture_composite")
        self.assertEqual(result["candidate_count"], 4)
        self.assertEqual(result["rejection_count"], 1)
        self.assertEqual(
            result["rejection_codes"],
            ["top_inset_clearance_failed"],
        )

    def test_bounded_strategy_exhaustion_remains_unknown(self) -> None:
        result = self.diagnostics(
            "xy_composite_gross_partition_not_found",
            candidate_pool_count=3,
            candidate_attempt_count=3,
        )

        self.assertEqual(
            result["outcome_kind"],
            OUTCOME_STRATEGY_EXHAUSTED,
        )
        self.assertEqual(result["phase"], "fermeture_composite")
        self.assertIn("inconnu, pas impossible", result["user_summary"])
        self.assertFalse(result["proof_of_impossibility"])
        self.assertEqual(result["counters"]["candidate_pool_count"], 3)

    def test_only_an_explicit_proof_can_claim_impossibility(self) -> None:
        result = self.diagnostics(
            "printable_domain_impossible",
            status="proven_impossible",
        )

        self.assertEqual(result["outcome_kind"], OUTCOME_PROVEN_IMPOSSIBLE)
        self.assertTrue(result["proof_of_impossibility"])

    def test_stale_result_has_its_own_outcome(self) -> None:
        result = self.diagnostics(
            "finalization_result_stale",
            status="stale_or_cancelled",
        )

        self.assertEqual(result["outcome_kind"], OUTCOME_STALE)
        self.assertEqual(result["phase"], "validation_identite")
        self.assertFalse(result["proof_of_impossibility"])

    def test_known_rectangular_continuous_and_composite_stops_are_phased(
        self,
    ) -> None:
        cases = (
            (
                "global_rectangular_partition_certificate_rejected",
                OUTCOME_CERTIFICATE_REJECTED,
                "partition_rectangulaire",
            ),
            (
                "continuous_product_certificate_rejected",
                OUTCOME_CERTIFICATE_REJECTED,
                "fermeture_continue",
            ),
            (
                "global_certificate_rejected",
                OUTCOME_CERTIFICATE_REJECTED,
                "certificat_final",
            ),
            (
                "xy_composite_cad_contract_rejected",
                OUTCOME_CERTIFICATE_REJECTED,
                "fermeture_composite",
            ),
            (
                "container_variant_frontier_reconstruction_failed",
                OUTCOME_PREREQUISITE_MISSING,
                "preparation",
            ),
        )

        for stop_reason, outcome_kind, phase in cases:
            with self.subTest(stop_reason=stop_reason):
                result = self.diagnostics(stop_reason)
                self.assertEqual(result["outcome_kind"], outcome_kind)
                self.assertEqual(result["phase"], phase)
                self.assertFalse(result["proof_of_impossibility"])


if __name__ == "__main__":
    unittest.main()
