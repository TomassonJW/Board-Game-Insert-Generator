# ADR-0029 - Count-aware asset storage sizing V0

Date : 2026-07-08
Statut : acceptee

## Contexte

P13-M001V a valide `quick_asset_box` comme UI asset-first V0 honnete, mais le `count` etait seulement lu/reporte. Un module pouvait donc rester une simple enveloppe du plus grand asset, sans representer la quantite annoncee.

## Decision

Pour `tokens`, `dice`, `meeples` et `generic`, BGIG interprete `z_mm` comme epaisseur unitaire et utilise `count` pour produire une enveloppe count-aware : capacite par pile, nombre de piles XY, enveloppe asset-fit et taille module. L'heuristique reste deterministe, bornee et sans backtracking.

Pour `cards` et `sleeved_cards`, BGIG interprete `z_mm` comme hauteur totale fournie du paquet/deck. `count` reste reporte mais n'est pas multiplie. Le reporting doit rendre cette limitation explicite.

La capacite declaree est une garantie heuristique d'enveloppe, pas une validation de logement physique ni d'impression. P13-ASSET-M002 ne genere pas de cavites et ne dessine pas les items individuels.

## Consequences

- Les modules asset-first peuvent changer de taille quand `count` change.
- Les fixtures trop petites peuvent etre refusees proprement au lieu de produire un proxy trompeur.
- `metadata.storage_sizing` devient le support de reporting pour `policy`, `derivation`, diagnostics par asset, piles, capacite declaree et warnings.
- Fusion ajoute seulement un sketch debug non imprimable d'enveloppe asset-fit.

## Alternatives refusees

- Multiplier silencieusement `z_mm` par `count` pour les cartes : trop ambigu entre epaisseur unitaire et hauteur de deck.
- Ajouter un solveur global/backtracking : hors scope P13-ASSET-M002.
- Generer des cavites/logements : mission separee et gate produit/Fusion future.