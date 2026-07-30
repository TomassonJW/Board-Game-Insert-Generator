from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class P64L09WGeneralSolverRobustnessHandoffTests(unittest.TestCase):
    def test_human_verdict_closes_r9_without_inventing_timings(self) -> None:
        evidence = (
            ROOT / "docs/P64_L09U_R9_V_0180_HUMAN_OK_EVIDENCE.md"
        ).read_text(encoding="utf-8")

        self.assertIn("P64-L09U-R9-V Fusion OK 0.1.80", evidence)
        self.assertIn("fusion-validated=true", evidence)
        self.assertIn("print-validated=false", evidence)
        self.assertIn("aucune durée humaine n’est inventée", evidence)

    def test_handoff_requires_a_measurable_supported_domain(self) -> None:
        handoff = (
            ROOT / "docs/P64_L09W_GENERAL_SOLVER_ROBUSTNESS_HANDOFF.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "ready-for-autonomous-goal",
            "95 %",
            "99 %",
            "faisables par construction",
            "`bounded_unknown`",
            "`discovery`",
            "`tuning`",
            "`holdout` neuf",
            "`soak`",
            "`p50`, `p95` et `p99`",
            "`0, 1, 2, 3, 4, 5, 6 et 10`",
            "P64-L09W-A",
            "sans budget de tokens inventé",
        ):
            self.assertIn(marker, handoff)

        self.assertIn("Il est interdit", handoff)
        self.assertIn("tous les cas possibles", handoff)

    def test_current_pilotage_prioritizes_causal_optimization_after_campaign(
        self,
    ) -> None:
        pilotage = {
            path: (ROOT / path).read_text(encoding="utf-8")
            for path in (
                "docs/PILOTAGE_CURRENT.md",
                "docs/NEXT_ACTIONS.md",
                "docs/HUMAN_GATES.md",
                "docs/STATUS.md",
                "docs/CAPABILITY_MAP.md",
                "docs/ROADMAP.md",
                "docs/BACKLOG.md",
            )
        }

        for text in pilotage.values():
            self.assertIn("P64-L09W", text)
        self.assertIn("P64-L09W-C", pilotage["docs/NEXT_ACTIONS.md"])
        self.assertIn("P64-L09W-D", pilotage["docs/NEXT_ACTIONS.md"])
        self.assertIn(
            "P64-L09W-C est terminée",
            pilotage["docs/NEXT_ACTIONS.md"],
        )
        self.assertIn(
            "Le holdout privé reste fermé",
            pilotage["docs/NEXT_ACTIONS.md"],
        )
        self.assertIn(
            "xy_composite_residual_owner_resolution_v1",
            pilotage["docs/BACKLOG.md"],
        )
        self.assertIn(
            "aucune gate humaine ouverte",
            pilotage["docs/HUMAN_GATES.md"],
        )
        self.assertIn(
            "Le nouveau holdout reste fermé",
            pilotage["docs/CAPABILITY_MAP.md"],
        )

    def test_reference_campaign_evidence_is_complete_and_keeps_holdout_closed(
        self,
    ) -> None:
        evidence = (
            ROOT / "docs/P64_L09W_C_REFERENCE_CAMPAIGN_EVIDENCE.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "400/400",
            "332",
            "83,00 %",
            "xy_composite_residual_owner_not_found",
            "holdout_file_read=false",
            "holdout_opening_count=0",
            "holdout_solver_invocation_count=0",
            "1061/1061",
        ):
            self.assertIn(marker, evidence)


if __name__ == "__main__":
    unittest.main()
