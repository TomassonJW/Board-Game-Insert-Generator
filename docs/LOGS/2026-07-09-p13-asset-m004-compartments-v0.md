# 2026-07-09 - P13-ASSET-M004 asset-specific compartments V0

Contexte : P13-ASSET-M003V a valide une cavite asset-fit globale. La mission M004 autorisee par gate produit vise a rendre le resultat asset-first plus lisible en creant des compartiments par asset source, sans solveur global ni nouvelle UI avancee.

Changements implementes :

- Nouvelle policy `per_source_asset_rectangular_compartments_v0`.
- Le sizing count-aware conserve un module exterieur unique et produit un compartiment top-open par asset source quand le type est supporte.
- Layout V0 deterministe : orientation ligne X ou colonne Y, choisie par fit et aire, sans backtracking.
- Chaque compartiment est transforme en `FusionCavityCutPlan` puis en vraie coupe `subtract_rectangular_cavity`.
- Les coupes conservent un fond commun `floor_thickness_mm`; les compartiments plus bas sont coupes jusqu'au meme fond pour eviter un plancher incoherent.
- Le rapport Fusion ajoute `asset_compartments_generated`, `asset_compartment_cavities_planned/generated`, diagnostics par asset, dimensions, origine locale, capacite declaree, piles et mur interne.
- Le sketch debug asset-fit ajoute les outlines de compartiments non imprimables.

Limites maintenues : assets individuels non visualises, cavites par pile/item non generees, pas de solveur global, pas d'optimisation avancee, pas de fillets, pas d'export STL/3MF, aucune impression 3D validee.

Gate suivante : `P13-ASSET-M004V` validation humaine Fusion obligatoire. Ne pas lancer de mission produit suivante avant validation ou decision explicite.
