from __future__ import annotations

import unittest

from context import ROOT


EVIDENCE = ROOT / "docs" / "P64_L07A_EXTERNAL_SOLVER_AUDIT_EVIDENCE.md"


class P64L07AEvidenceDocumentTests(unittest.TestCase):
    def test_evidence_document_is_complete(self) -> None:
        content = EVIDENCE.read_text(encoding="utf-8")
        for heading in (
            "## Résultat",
            "## Méthode",
            "## Inventaire et décision",
            "## Shortlist et familles réellement différentes",
            "## Correspondance BGIG et pertes de modèle",
            "## Formes complexes et limite théorique",
            "## Licences et packaging",
            "## Validation automatisée",
            "## Limites",
            "## Suite",
        ):
            self.assertIn(heading, content)


if __name__ == "__main__":
    unittest.main()
