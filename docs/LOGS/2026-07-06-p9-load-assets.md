# 2026-07-06 - P9-M002 load assets without module generation

## Mission

Implementer `P9-M002 - Charger des assets JSON sans generation de modules`.

## Livrables

- Dataclasses `Asset`, `AssetQuantity` et enums associees.
- Loader JSON strict pour `assets[]`.
- Validation des ids, quantites, dimensions, `reservation_ref` et `module_hint`.
- Rapports Markdown/JSON et metadata CAD IR `assets` avec `status: loaded_only`.
- Exemple executable `examples/simple_assets.json`.
- Tests unitaires dedies.

## Limites

- Aucun module n'est derive depuis les assets.
- Aucun layout, cavity, tolerance ou operation Fusion n'est recalcule depuis les assets.
- Les assets restent des donnees passives jusqu'a une mission de derivation explicite.