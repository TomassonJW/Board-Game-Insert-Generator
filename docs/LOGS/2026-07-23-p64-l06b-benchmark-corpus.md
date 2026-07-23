# 2026-07-23 — P64-L06B corpus T0/T1

## Contexte

Le Goal P64-L06 reprend après l'inventaire réel L06A. Le lot devait construire
un benchmark large et reproductible sans dépendance externe et sans modifier le
solveur.

## Décision de mission

Un nouveau manifest enveloppe les corpus L05D1 et L06A sans changer leurs
digests. Les 192 nouveaux cas restent des recettes compactes, déterministes et
rematérialisables. Les vérités positives viennent d'une construction locale P45
puis d'un placement global indépendant ; les vérités négatives viennent de
bornes exactes de volume ou de hauteur.

Le holdout est scellé par défaut. Les tests contrôlent sa fermeture mais
n'exécutent aucun solveur sur ses cas.

## Faits vérifiés

- 8 cas de régression préservés ;
- 64 discovery, 64 tuning, 64 holdout ;
- cinq familles dans chaque split ;
- 47/46/47 faisables construits et 17/18/17 impossibles prouvés ;
- six paires incrémental/froid par split ;
- fronts P45 réels `1, 2, 4, 8` couverts ;
- aucun front P45 vide sur les cas faisables des deux splits ouverts ;
- petit cas rejoué avec solution et certificat BGIG ;
- manifest `53db786793dee3a26128f4db28cc830f68dde394262cd7ffbfad27cb895a85ee` ;
- suite complète 698/698 en 171,783 s.

## Limite explicite

Le schéma projet ne permet pas d'interdire une rotation globale. Le benchmark
porte donc cette politique séparément et exige qu'un adapter incapable de la
respecter réponde `unsupported`. Aucun changement de schéma n'est introduit.

## Effets exclus

Aucune dépendance, auto-modification, forme T2-T4, finalisation, CAD, scène
Fusion, valeur physique, budget, deadline ou certificat public n'est modifié.
`fusion-validated: false`, `print-validated: false`.

## Suite

P64-L06C ajoute l'interface de comparaison et le petit oracle exact interne,
puis L06D exécutera la campagne progressive sans ouvrir le holdout avant le
choix unique.
