# ADR-0030 - Asset-fit cavity V0

Date : 2026-07-09

## Statut

Acceptee pour implementation V0, validation Fusion requise.

## Contexte

P13-ASSET-M002 a valide un sizing count-aware pour assets simples et une enveloppe `asset_fit`, mais les modules Fusion restaient des bodies pleins. P13-ASSET-M003 doit creer un premier logement reel sans introduire de solveur global, de cavites par pile, de fillets ou d'UI avancee.

## Decision

BGIG genere une seule cavite rectangulaire globale par module asset candidate place, de politique `single_asset_fit_rectangular_cavity_v0`.

La metadata coeur `asset_fit_cavity` est additive dans `metadata.executable_asset_plan`. Fusion la consomme seulement si `status: planned`, `policy: single_asset_fit_rectangular_cavity_v0` et `coordinate_frame: body.local`. La coupe reutilise `subtract_rectangular_cavity`, avec :

- origine locale : `wall_thickness_mm`, `wall_thickness_mm`, `floor_thickness_mm` ;
- taille : `asset_fit_size_mm` ;
- fond conserve : `module_size.z - asset_fit.z` ;
- murs attendus : module moins origine et asset_fit.

Les payloads `status: refused` restent reportes mais ne creent pas de coupe Fusion.

## Consequences

- Le smoke `quick_asset_box` peut verifier un module count-aware creuse par une vraie cavite top-open.
- Les assets individuels et les piles ne sont pas visualises ni coupes.
- La capacite declaree reste heuristique et non print-validee.
- Les cartes et cartes sleevees doivent recevoir une mission dediee avant cavite asset-fit.
- Le coeur Python reste sans dependance `adsk`.

## Alternatives refusees

- Generer une cavite par pile : trop proche d'un solveur/layout de contenu, hors scope M003.
- Visualiser chaque asset : hors scope et risque de complexite UI/CAD.
- Creer une nouvelle operation Fusion : inutile, `subtract_rectangular_cavity` couvre le besoin V0.
- Centrer automatiquement l'enveloppe : moins direct que l'alignement deterministe sur wall/floor et plus ambigu pour le reporting V0.
