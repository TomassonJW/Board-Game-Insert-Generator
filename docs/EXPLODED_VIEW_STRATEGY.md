# Exploded View Strategy

## Objectif

Fusion devra a terme produire deux vues utiles : une vue compacte dans la boite et
une vue eclatee ou repartie a plat pour inspecter, nommer, mesurer et exporter les
modules.

## Etat actuel

- L'add-in Fusion genere des blanks rectangulaires dans le composant racine.
- La CAD IR conserve les noms et dimensions deja resolus.
- Aucune vue eclatee n'est generee.

## Strategie cible

- `compact_view` : modules places selon le layout reel dans la boite.
- `exploded_view` : modules separes avec espacement lisible, labels et axes stables.
- `inspection_metadata` : liens entre module, asset, cavite, tolerance et operation.
- `export_group` : future selection par module ou par layer.

## Invariants

- La vue eclatee ne doit pas modifier les dimensions ou tolerances.
- Le moteur ou la CAD IR doivent fournir les positions de vue ; Fusion ne les invente pas.
- Les exports STL/3MF restent bloques par gate.

## Prochaines missions possibles

1. `P7-M001 - Ajouter une intention de vue eclatee dans la CAD IR`.
2. `P7-M002 - Generer une vue Fusion eclatee planned-only`.
3. `P7-M003 - Generer une vue eclatee Fusion de blanks uniquement`.

## Gates

- Gate Fusion si la vue cree de nouveaux composants, sketches ou bodies.
- Gate export avant toute production STL/3MF.
