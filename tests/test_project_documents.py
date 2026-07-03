from __future__ import annotations

import unittest

from context import ROOT


REQUIRED_PROJECT_FILES = (
    "AGENTS.md",
    "docs/AUTONOMY_PROTOCOL.md",
    "docs/EXECUTION_LOOP.md",
    "docs/HUMAN_GATES.md",
    "docs/VALIDATION_MATRIX.md",
    "docs/STATUS.md",
    "docs/NEXT_ACTIONS.md",
    "docs/BACKLOG.md",
    "docs/ROADMAP.md",
    "docs/ARCHITECTURE.md",
    "docs/CALIBRATION_PROTOCOL.md",
    "docs/QUALITY_RULES.md",
    "docs/DECISIONS/ADR-TEMPLATE.md",
    "docs/DECISIONS/README.md",
    "docs/LOGS/README.md",
)

REQUIRED_SECTIONS = {
    "AGENTS.md": (
        "## Lecture obligatoire avant toute mission",
        "## Autonomous execution rules",
        "## Tests et validation",
    ),
    "docs/AUTONOMY_PROTOCOL.md": (
        "## Selection de mission",
        "## Arrets obligatoires",
        "## Rapport final",
    ),
    "docs/EXECUTION_LOOP.md": (
        "## Boucle standard",
        "## Detail operationnel",
        "## Echecs et blocages",
    ),
    "docs/HUMAN_GATES.md": (
        "## Gates obligatoires",
        "## Format minimal d'un rapport de gate",
    ),
    "docs/VALIDATION_MATRIX.md": (
        "## Niveaux de validation",
        "## Regles de statut",
    ),
    "docs/STATUS.md": (
        "## Etat global",
        "## Phase active",
        "## Tests et verifications connus",
    ),
    "docs/NEXT_ACTIONS.md": (
        "## Mission suivante recommandee",
        "## Fin de chaque mission",
    ),
    "docs/BACKLOG.md": (
        "## Phase 0 - Fondation projet",
        "### P0-M002 - Ajouter une verification documentaire de base",
    ),
    "docs/ROADMAP.md": (
        "## Phase 0 - Fondation projet",
        "## Regle de progression",
    ),
    "docs/ARCHITECTURE.md": (
        "## Frontieres non negociables",
        "## Couches logicielles",
    ),
    "docs/CALIBRATION_PROTOCOL.md": (
        "## Objectif",
        "## Coupons a preparer",
        "## Tableau de resultats",
        "## Regles d'interpretation",
    ),
    "docs/QUALITY_RULES.md": (
        "## Regles de documentation",
        "## Garde-fous documentaires automatises",
    ),
    "docs/DECISIONS/README.md": (
        "## Template ADR",
        "## Format minimal",
        "## ADR existantes",
    ),
    "docs/DECISIONS/ADR-TEMPLATE.md": (
        "## Statut",
        "## Contexte",
        "## Options",
        "## Decision",
        "## Consequences",
        "## Alternatives refusees",
        "## Suivi",
    ),
    "docs/LOGS/README.md": (
        "## Format recommande",
        "## Regles",
    ),
}


class ProjectDocumentsTests(unittest.TestCase):
    def test_required_project_control_files_exist(self) -> None:
        missing = [
            relative_path
            for relative_path in REQUIRED_PROJECT_FILES
            if not (ROOT / relative_path).is_file()
        ]

        if missing:
            self.fail("Fichiers de pilotage manquants: " + ", ".join(missing))

    def test_critical_project_control_sections_exist(self) -> None:
        missing_sections: list[str] = []

        for relative_path, required_headings in REQUIRED_SECTIONS.items():
            content = (ROOT / relative_path).read_text(encoding="utf-8")
            for heading in required_headings:
                if heading not in content:
                    missing_sections.append(f"{relative_path} -> {heading}")

        if missing_sections:
            self.fail("Sections de pilotage manquantes: " + "; ".join(missing_sections))


if __name__ == "__main__":
    unittest.main()
