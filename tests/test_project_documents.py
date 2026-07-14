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
    "docs/NORTH_STAR.md",
    "docs/PRODUCT_SPEC.md",
    "docs/CAPABILITY_MAP.md",
    "docs/ROADMAP.md",
    "docs/ARCHITECTURE.md",
    "docs/VOLUMETRIC_LAYOUT_STRATEGY.md",
    "docs/ASSET_MODEL_STRATEGY.md",
    "docs/SOLVER_STRATEGY.md",
    "docs/LAYER_AND_STACKING_MODEL.md",
    "docs/ACCESSIBILITY_MODEL.md",
    "docs/EXPLODED_VIEW_STRATEGY.md",
    "docs/CALIBRATION_PROTOCOL.md",
    "docs/CAD_IR_CONTRACT.md",
    "docs/FUSION_360_GATE_REPORT.md",
    "docs/FUSION_360_STRATEGY.md",
    "docs/QUALITY_RULES.md",
    "docs/P66_TERRA_EXECUTION_CONTRACT.md",
    "docs/P67_POST_MVP_PRIORITIZATION_CONTRACT.md",
    "docs/P68_FIRST_USE_PRINT_FEEDBACK.md",
    "docs/P69_FULL_UI_UX_REVIEW_CONTRACT.md",
    "docs/DECISIONS/ADR-TEMPLATE.md",
    "docs/DECISIONS/ADR-0061-post-mvp-sequencing-and-complement-quarantine.md",
    "docs/DECISIONS/ADR-0012-capability-driven-product-pilotage.md",
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
        "## Pilotage par capabilities",
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
        "## Statuts de capability",
        "## Regles de statut",
    ),
    "docs/STATUS.md": (
        "## Etat global",
        "## Phase active",
        "## Tests et verifications connus",
    ),
    "docs/NEXT_ACTIONS.md": (
        "## Prochaine action recommandée",
        "## Fin de chaque mission",
    ),
    "docs/BACKLOG.md": (
        "## Phase 0 - Fondation projet",
        "### P0-M002 - Ajouter une verification documentaire de base",
        "### P8-M001 - Specifier la grille volumetrique 3D et les layers",
    ),
    "docs/NORTH_STAR.md": (
        "## Formulation courte",
        "## Product Pillars",
        "## Definition du succes",
    ),
    "docs/PRODUCT_SPEC.md": (
        "## Produit cible",
        "## Product Pillars et capabilities",
    ),
    "docs/CAPABILITY_MAP.md": (
        "## Product Pillars",
        "## Architecture Tracks",
        "## Capabilities",
        "## Milestones utilisateur",
        "## Regle d'usage par Codex",
    ),
    "docs/ROADMAP.md": (
        "## Phase 0 - Gouvernance, autonomie, qualite",
        "## Phase 14 - Calibration, impression reelle, packaging et beta utilisable",
        "## Regle de progression",
    ),
    "docs/ARCHITECTURE.md": (
        "## Frontieres non negociables",
        "## Architecture Tracks",
        "## Couches logicielles",
    ),
    "docs/VOLUMETRIC_LAYOUT_STRATEGY.md": (
        "## Objectif",
        "## Concepts cibles",
        "## Gates",
    ),
    "docs/ASSET_MODEL_STRATEGY.md": (
        "## Objectif",
        "## Concepts cibles",
        "## Gates",
    ),
    "docs/SOLVER_STRATEGY.md": (
        "## Objectif",
        "## Strategie cible",
        "## Gates",
    ),
    "docs/LAYER_AND_STACKING_MODEL.md": (
        "## Objectif",
        "## Concepts cibles",
        "## Gates",
    ),
    "docs/ACCESSIBILITY_MODEL.md": (
        "## Objectif",
        "## Concepts cibles",
        "## Gates",
    ),
    "docs/EXPLODED_VIEW_STRATEGY.md": (
        "## Objectif",
        "## Strategie cible",
        "## Gates",
    ),
    "docs/CALIBRATION_PROTOCOL.md": (
        "## Objectif",
        "## Coupons a preparer",
        "## Tableau de resultats",
        "## Regles d'interpretation",
    ),
    "docs/CAD_IR_CONTRACT.md": (
        "## Objectif",
        "## Scene V0",
        "## Operations abstraites",
        "## Extensions cible sans incompatibilite",
        "## Gate suivante",
    ),
    "docs/FUSION_360_GATE_REPORT.md": (
        "## Declencheur",
        "## Etat actuel du moteur",
        "## Options techniques",
        "## Validation demandee",
    ),
    "docs/FUSION_360_STRATEGY.md": (
        "## Decision centrale",
        "## Vue compacte et vue eclatee",
        "## Gates avant elargissement Fusion",
    ),
    "docs/QUALITY_RULES.md": (
        "## Regles de documentation",
        "## Garde-fous documentaires automatises",
    ),
    "docs/P66_TERRA_EXECUTION_CONTRACT.md": (
        "## 1. Resultat attendu",
        "## 2. Clarification P44 a P50",
        "## 3. Decomposition obligatoire de P66",
        "## 8. Checklist humaine P66-V",
        "## 10. Interdits explicites",
        "## 12. Prompt court a donner a Terra",
    ),
    "docs/P67_POST_MVP_PRIORITIZATION_CONTRACT.md": (
        "## Objectif",
        "## Preconditions",
        "## Revue obligatoire",
        "## Decisions attendues",
        "## Sorties possibles",
        "## Interdits",
    ),
    "docs/P68_FIRST_USE_PRINT_FEEDBACK.md": (
        "## Role",
        "## Protocole minimal",
        "## Lien avec P67 et P44-P50",
        "## Sortie",
    ),
    "docs/P69_FULL_UI_UX_REVIEW_CONTRACT.md": (
        "## Objectif",
        "## Preconditions",
        "## Methode de revue",
        "## Livrable humain",
        "## Sortie",
        "## Interdits",
    ),
    "docs/DECISIONS/ADR-0061-post-mvp-sequencing-and-complement-quarantine.md": (
        "## Statut",
        "## Contexte",
        "## Options",
        "## Decision",
        "## Consequences",
        "## Alternatives refusees",
        "## Suivi",
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
    "docs/DECISIONS/ADR-0012-capability-driven-product-pilotage.md": (
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
