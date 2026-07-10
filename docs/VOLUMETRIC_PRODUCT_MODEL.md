# Volumetric Product Model

## Role

Ce contrat cible precede toute implementation de box fill. Il reste CAD-agnostic: le moteur produit un plan abstrait; Fusion materialise un plan deja resolu.

## Objets

| Objet | Role | Ne doit pas etre confondu avec |
| --- | --- | --- |
| `GameBox` | Identite du jeu, metadonnees et `BoxVolume` | Une scene Fusion |
| `BoxVolume` | Dimensions utiles, couvercle, orientation et repere | Un module imprimable |
| `Asset` | Materiel reel, dimensions, quantite, confiance | Un item Fusion individuel |
| `AssetGroup` | Ensemble intentionnel d'assets lies | Un compartiment ou une pile |
| `StorageIntent` | Accessibilite, regroupement, orientation, priorite | Une contrainte CAD implicite |
| `Reservation` | Volume non imprime (board, rules, lid, tray existant) | Un module physique |
| `Layer` | Bande Z avec retrait/support/reservations | Une simple rangee XY |
| `ModulePlan` | Module physique propose/manuel, dimension, position, assets | Son body Fusion ou son span de grille |
| `CompartmentPlan` | Logement interne de module pour asset/groupe | Un asset ou une cavite Fusion executee |
| `AccessFeaturePlan` | Intention d'encoche/scoop associee a un compartment | Une feature automatiquement validee |
| `FreeVolume` | Espace restant qualifie et utilisable | Une zone oubliee |
| `LayoutVariant` | Une proposition complete, scoree, explicable | Un unique placement greedy |
| `BoxFillPlan` | Composition complete: layers, modules, reservations, free volumes | Une CAD IR ou une scene Fusion |
| `ExportPackage` | STL, manifestes, preprint et statuts d'une variante choisie | La preuve d'une impression reelle |

## Relations

`GameBox -> BoxVolume -> BoxFillPlan -> LayoutVariant -> Layer -> ModulePlan -> CompartmentPlan -> AccessFeaturePlan`.

Les `Asset` sont lies a zero ou plusieurs `AssetGroup`, puis a des `StorageIntent` et `CompartmentPlan`. Les `Reservation` et `FreeVolume` appartiennent directement au `BoxFillPlan`; aucun des deux ne devient implicitement un module.

## Invariants

- Chaque volume occupe est soit reservation, module ou free volume; les intersections sont refusees.
- Un `ModulePlan` a une geometrie abstraite et une position dans `BoxVolume`; `printable_body` Fusion est une projection, pas la source de verite.
- Une reservation de board/livret/couvercle reste non imprimable et peut imposer layer/removal order.
- Chaque `LayoutVariant` contient ses raisons de refus, contraintes relachees et sous-scores.
- `BoxFillPlan` permet de calculer volume libre, couverture des assets et ordre de retrait sans dependance `adsk`.

## Scoring cible

Une variante expose au minimum compacite, accessibilite, imprimabilite, nombre de modules, simplicite, temps d'impression estime et couverture des intentions. Aucun score unique opaque ne remplace les sous-scores.

## Transition depuis l'existant

`volumetric_grid` reste une representation discrete compatible; `executable_asset_plan` reste un resultat V0. P19 devra construire le premier `BoxFillPlan` manuel en les adaptant, sans migration destructive du schema public.

## P19 completion addendum

P19 est complet contre son contrat autorise : cellules libres AABB exactes (`exact_aabb_cells_v0`), conservation de volume, diagnostics structures, coverage par asset, CLI `validate-box-fill` / `report-box-fill` / `export-box-fill-plan`, fixtures valide et invalides, bridge explicite `derived_from_executable_asset_plan` et transport CAD IR metadata. Les cellules decrivent le residuel et ne constituent pas un placement automatique. P20 greedy reste bloque par gate humaine ; Fusion ne recalcule ni ne materialise ce plan.
## P20 completion - 2026-07-10

Statut : `done`, `implemented-core`, `implemented-cli`, `implemented-cad-ir-metadata`. Le moteur `box_fill_greedy_2d.v0` produit un nouveau BoxFillPlan sans muter la source, respecte locks, modules manuels, reservations et layers, supporte la rotation XY 90 degres et expose diagnostics, digest, metrics, rapports JSON/Markdown, preview SVG et metadata CAD IR. Aucun backtracking, solveur global, UI persistante, geometrie Fusion ou validation d impression n est ajoute. P21 reste gate et recommande les variantes/scoring.