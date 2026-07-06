# ADR-0018 - Asset-first schema target

## Statut

Accepted - 2026-07-06.

## Contexte

BGIG doit passer progressivement d'un modele module-first a un modele
asset-first. P9-M001 doit specifier le schema cible sans activer trop tot un
changement public du loader.

## Options

1. Ajouter immediatement `assets` au loader.
2. Documenter le contrat cible et differer le chargement a P9-M002.
3. Continuer uniquement avec `modules` et `volumetric_grid.zones`.

## Decision

P9-M001 documente le bloc futur `assets` dans `ASSET_MODEL_STRATEGY` et
`CONFIG_SCHEMA`, mais le loader V0 refuse encore tout champ racine `assets`.

Un asset decrit du materiel reel : kind, quantite, dimensions, confiance de
mesure, intention de rangement et lien optionnel vers une reservation. Il ne
devient pas automatiquement un module imprimable.

## Consequences

La direction produit est explicite sans casser la compatibilite. P9-M002 peut
charger ce schema de facon additive avec tests stricts. Les exemples restent non
executables tant que le loader ne les accepte pas.

## Alternatives refusees

- Activation immediate du loader : trop large pour P9-M001.
- Fusion ou generation de modules : hors perimetre.

## Suivi

P9-M002 devra ajouter le chargement strict des assets ou stopper si le schema doit
changer de maniere incompatible.