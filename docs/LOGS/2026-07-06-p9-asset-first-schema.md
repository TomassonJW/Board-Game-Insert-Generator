# 2026-07-06 - P9-M001 asset-first schema target

## Mission

Specifier `P9-M001 - Specifier le schema asset-first` sans changer le loader V0.

## Livrables

- Contrat cible `assets` dans `docs/ASSET_MODEL_STRATEGY.md`.
- Note de schema non charge dans `docs/CONFIG_SCHEMA.md`.
- ADR-0018.
- Pilotage mis a jour vers `P9-M002`.

## Limites

- Le loader V0 refuse encore `assets`.
- Aucun module, layout, cavity ou CAD IR n'est derive depuis les assets.
- Aucun exemple executable n'est ajoute dans `examples/`.

## Validation attendue

Tests documentaires et non-regression CLI existante.