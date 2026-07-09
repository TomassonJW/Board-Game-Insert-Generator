# ADR-0031 - Asset-specific compartments V0

Date : 2026-07-09

Statut : acceptee pour implementation P13-ASSET-M004 ; validation Fusion humaine requise via `P13-ASSET-M004V`.

## Contexte

P13-ASSET-M003 a valide une cavite rectangulaire globale top-open issue de `asset_fit`. Cette cavite etait utile pour prouver la coupe Fusion, mais elle melangeait plusieurs assets sources dans un seul logement, ce qui restait peu lisible pour un flux asset-first.

## Decision

Ajouter la policy `per_source_asset_rectangular_compartments_v0` pour les modules `quick_asset_box` count-aware supportes. Le moteur garde un seul module exterieur, mais produit une liste deterministe de compartiments, un par asset source, dans le payload `asset_fit_cavity` existant pour conserver le transport CAD IR.

Chaque compartiment devient une coupe Fusion `subtract_rectangular_cavity` top-open separee, avec fond commun `floor_thickness_mm`, murs externes conserves et mur interne minimal `wall_thickness_mm` entre compartiments. Le layout V0 choisit seulement entre une orientation simple en ligne X et une orientation simple en colonne Y selon le fit et l'aire ; il ne fait pas de backtracking ni d'optimisation globale.

## Consequences

- Le rapport Fusion expose `asset_cavity_policy: per_source_asset_rectangular_compartments_v0`, `asset_compartments_generated`, `asset_compartment_cavities_planned` et des diagnostics par asset.
- `asset_fit_cavities_planned/generated` reste un compteur compatible des coupes asset-first, incluant les compartiments.
- Le debug sketch asset-fit ajoute les rectangles des compartiments, mais les assets individuels et les piles ne sont toujours pas visualises.
- Les cartes/decks et les cas non supportes restent gates ou refuses selon les policies existantes.

## Alternatives refusees

- Cavites par pile ou par item : trop large pour M004 et proche d'un solveur de rangement detaille.
- Palette/tableau HTML assets : hors scope.
- Solveur global ou optimisation de packing : gatee, non necessaire pour cette V0.
- Nouvelle geometrie avancee, fillets ou exports imprimables : hors scope et non print-valides.
