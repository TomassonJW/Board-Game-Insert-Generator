# Journal P64-L09R-B — calcul minimal fiable

Date : 2026-07-25

## Changement

- Le support d'enveloppe XY redevient le critère dur ; le support matériel est conservé comme diagnostic.
- Les réservations supérieures restent actives et leur compensation Z nécessaire est appliquée après un placement minimal complet.
- Le plan minimal certifié est matérialisable sans finition.
- La préférence petits-dessous/grands-dessus reste souple.
- Les budgets du calcul deviennent cinq deadlines totales : 3, 10, 20, 60 et 180 secondes.
- Un timeout reste un résultat borné inconnu.

## Preuve

Le cas P66 complet, le cas de réservation localisée, P64-V2H01, le corpus CI, les réservations SCIP et le garde CAD sont couverts par les tests automatisés. La preuve détaillée est `docs/P64_L09R_B_MINIMAL_CALCULATION_EVIDENCE.md`.

## Limites

Aucun benchmark, package Fusion, réglage local, fait d'impression, tolérance ou valeur physique n'a été produit. P64-L09R-C reste le prochain lot automatisé après intégration de B.
