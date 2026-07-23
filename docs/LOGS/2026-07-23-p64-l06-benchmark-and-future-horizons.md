# 2026-07-23 - Benchmark P64-L06 et horizons produit

## Contexte

Le POC Fusion est suffisamment avancé pour distinguer la correction immédiate
du solveur, sa campagne de mesure et les capacités produit futures. Les idées de
formes, poses, mécanismes et UI étaient partiellement présentes dans la roadmap,
mais pas assez précisément pour empêcher leur mélange avec P64.

## Changements

- ajout d'un registre différé des horizons V1.x à V4+ ;
- classement des responsabilités entre P45, P64, mécanismes et P69/P70+ ;
- création du programme P64-L06 avec familles T0 à T4 ;
- définition des oracles, comparateurs offline, métriques et tiers autonomes ;
- découpage L06A à L06V ;
- maintien explicite de la gate R1 et de l'interdiction d'auto-modification.

## Vérifications

- contrats P45/P64, ADR-0068/0079, roadmap et pilotage relus ;
- candidats externes vérifiés sur leurs sources officielles ;
- garde documentaire : 2/2 ;
- Ruff ciblé et py_compile : OK ;
- suite complète canonique avec `PYTHONPATH=src` : 682/682 ;
- premier lancement sans `PYTHONPATH` : KO d'environnement sur deux imports,
  puis relance corrigée verte.

## Impact

Codex pourra lancer une campagne goal bornée sans confondre benchmark,
apprentissage automatique et extension de produit. Les futures formes et UI
restent visibles, mais aucune n'est devenue `ready`.

## Suivi

- confirmer les captures R1 ;
- exécuter P64-L06A sans changement de solveur ;
- préparer L06B/L06C seulement après la classification du cas réel.
