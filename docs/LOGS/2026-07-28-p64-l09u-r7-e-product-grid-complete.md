# 2026-07-28 — P64-L09U-R7-E grille produit complète

## Résultat

Les longueurs dérivées sont au dixième jusqu'au plan Fusion. L'audit
reproductible contrôle `5 451` valeurs sur `CasLimite02++` et `5 886` sur
`CasLimite02+`, avec zéro valeur effective hors grille.

Les sources hors grille restent possibles et ne sont pas réécrites ; un rapport
de migration expose source, effectif, direction et ticks. L'epsilon numérique
reste séparé et exclu de la résolution produit.

Le digest fonctionnel de disposition utilise des ticks. Le finaliseur v13, le
plan minimal et la CAD IR portent de nouvelles identités.

## Validation

- `77/77` tests ciblés ;
- deux replays personnels, SHA inchangés ;
- aucun gain de temps revendiqué ;
- aucun benchmark/holdout/corpus/tournoi.
