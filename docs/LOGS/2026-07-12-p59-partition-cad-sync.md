# P59 - Materialisation CAD et synchronisation Fusion

## Mission

Fermer le flux Fusion-only `projet -> P57 -> CAD IR -> adaptateur -> scene` sans
reactiver les fillers automatiques P41/P42.

## Resultat

- constructeur pur `bgig.partition_cad_build.v1` et CAD IR deterministe ;
- exactement un composant par placement demande, cavites P55 top-open ;
- complements uniquement explicites, zero corps automatique ;
- actions palette materialiser, regenerer, inspecter, effacer et exporter ;
- mode compact, registry BGIG et preservation des objets non-BGIG ;
- packaging add-in 0.1.6 avec runtime P59 obligatoire.

## Validation

Tests P59, bridge palette, entrypoint et 87 tests Fusion historiques passent.
Syntaxes Python et JavaScript valides. La validation visuelle Fusion reste
honnetement ouverte et constitue la gate P60.

## Decision

Aucune nouvelle ADR : P59 applique ADR-0052, ADR-0054 et ADR-0055 sans modifier
leur frontiere. Les anciennes routes CAD de remplissage restent historiques et
ne sont plus exposees dans le parcours produit.