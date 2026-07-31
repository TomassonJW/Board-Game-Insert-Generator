# P64-L09W-D-Q — Repli SCIP sur enveloppes minimales

Date : 2026-07-31.

Statut : `automated-validated`, `increment-retained`, `E-blocked`.

## Résultat

Un seul levier causal de recherche est retenu : après l'échec des voies
internes, un projet sans élément plat peut rejouer SCIP sur les enveloppes
extérieures minimales uniquement lorsque la recertification SCIP exacte a
refusé le candidat avec `MINIMAL_ENVELOPE_EXPANDED`.

Le délai global, les budgets de recherche, la grille `0,1 mm`, l'epsilon
`0,0001 mm`, les valeurs physiques, les certificats, la finalisation, la CAD IR
et l'ordre produit restent inchangés.

## Attribution causale

L'audit des 68 `bounded_unknown` de C isole 40 cas `common` :

- six voies internes épuisent leurs états sans solution complète ;
- SCIP trouve une solution géométrique ;
- la recertification commune refuse cette solution car les variantes retenues
  ont agrandi les enveloppes minimales ;
- 16 de ces 40 cas ne possèdent aucun élément plat.

Une sonde directe sur les 40 cas certifie 40/40 projections minimales. Le temps
SCIP maximal observé est `757,393 ms`, démarrage à froid compris ; les 39 autres
cas restent sous `68 ms`.

Deux variantes trop larges ont été rejetées pendant la découverte :

1. le repli appliqué à tous les projets modifiait le résultat de
   `p64-l09w-tuning-388-a020715e35` ;
2. le repli exécuté avant les voies internes modifiait le placement prêt de
   `p64-l09w-discovery-198-8571c434f9`.

La variante finale protège donc les projets avec éléments plats et conserve la
priorité des voies internes. Elle n'intervient qu'après leur échec réel.

## Implémentation retenue

Le solveur :

1. conserve le passage SCIP et les voies internes existants ;
2. réserve `1 000 ms` dans le délai global uniquement lorsqu'un rejet exact
   admissible est déjà connu ;
3. sur une édition incrémentale dont le témoin est refusé, attend d'abord
   l'échec interne puis exécute le diagnostic SCIP exact ;
4. rejoue SCIP sur les enveloppes minimales seulement si ce diagnostic publie
   `MINIMAL_ENVELOPE_EXPANDED` ;
5. recertifie le placement projeté contre le problème produit original.

Les métadonnées publient la projection et le digest du rejet déclencheur. Aucun
budget public n'est ajouté.

L'évaluateur des seuils conserve l'identité produit gelée pour chaque résultat
C déjà certifié. Un contrôle C borné peut toutefois devenir certifié : son
ancien digest d'échec n'est pas traité comme l'identité d'un produit prêt. Le
fichier de seuils et son digest restent inchangés.

## Panel sentinelle 16

- 16/16 gates fonctionnelles vertes ;
- cinq répétitions par cas ;
- seuils de performance gelés : `passed` ;
- digest des seuils :
  `beac00108140b72a625c7f756b9c27d70e50701ac9c34860743ab703254a4b72` ;
- gain causal :
  `p64-l09w-discovery-201-bdfe0b1cca`,
  `bounded_unknown -> certified_solution` ;
- médiane du cas causal : `1 444,059 ms`, MAD `16,923 ms` ;
- `tuning-388` conserve son identité et son placement ;
- digest du bundle de code :
  `c89b3a1735113aaaaf26912584241c6807d72495d880439895f519e38e57fa49` ;
- digest du checkpoint :
  `1a3ae40b272f87b7103cbb95dd2612dc755730526c4636e902fb30f9be783da2` ;
- digest du rapport :
  `ea938ade2b078fbefe6927d94362479bc66752bf72f5dfe85b67cb0c9699f217`.

## Panel candidat 48

- 48/48 gates fonctionnelles vertes ;
- deux répétitions par cas ;
- zéro échec de gate dure ;
- deux gains et aucun autre changement de statut :
  - `p64-l09w-discovery-069-661b906258` ;
  - `p64-l09w-discovery-201-bdfe0b1cca` ;
- digest du checkpoint :
  `8b1c5053f63578178dfb35d4950f867c86b254fab5d8758af3b3998a5daae842` ;
- digest du rapport :
  `cf8024c469321316578e7aacfae5ae8f351fd308871b01bd97f500c7a8ca3e91`.

Les panels ne sont pas des estimateurs de taux.

## Décision

L'incrément est retenu, mais il n'est pas gelé pour E.

Son rayon causal honnête couvre au plus les 16 `bounded_unknown` sans élément
plat. Même si les 16 devenaient certifiés dans les 400 ouverts, C passerait de
332 à 348 solutions certifiées, sous le seuil E de 380/400.

La campagne ouverte de 400 cas n'est donc pas exécutée. La prochaine mission
doit choisir un autre levier causal atomique pour le résiduel restant. E et F
restent bloquées.

## Holdout et validations

Le holdout n'a été ni lu, ni ouvert, ni invoqué :

- `holdout_file_read=false` ;
- `opening_count=0` ;
- `solver_invocation_count=0`.

Validations ciblées acquises avant la clôture :

- solveur minimal : 23/23 ;
- seuils de performance : 4/4 ;
- runner des panels : 6/6 ;
- solveur SCIP : 20/20, avec 1 skip prévu ;
- contrats documentaires : 11/11 ;
- `py_compile` des quatre fichiers Python modifiés : OK ;
- panel sentinelle : 16/16 ;
- panel candidat : 48/48 ;
- suite complète : 1097/1097 en `662,969 s`, avec 1 skip prévu.
