# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055.

## Derniere mission terminee

P60-R - realignement documentaire apres revue produit dans Fusion. P59 et le
runtime P60 0.1.9 restent une base technique utile, pas une acceptance produit.

Historique conserve : P59 - materialisation CAD et synchronisation de scene est
implementee ; P60 - acceptance du vrai MVP a ete refusee par la revue produit.

## Derniere preuve humaine

Le parcours charge, calcule, affiche un Apercu utile et materialise dans Fusion.
La revue refuse cependant l acceptance P60 : diagnostic brut intrusif, editions
non reactives, pile globale de plateaux et absence de solveur multi-etages.

## Mission courante

P60-R - contrats et pilotage du MVP revise. Aucun code de production n est
autorise par cette mission.

Livrables documentaires :

- rapport `docs/P60_PRODUCT_FEEDBACK_REALIGNMENT.md` ;
- ADR-0056 a ADR-0060 proposees ;
- chemin critique P61-P66 et gates de release realignes.

## Prochaine action prete

Relire et accepter, modifier ou refuser les cinq ADR proposees :

1. ADR-0056 : etat reactif et priorite des contraintes ;
2. ADR-0057 : plateaux/livrets encastres depuis le dessus ;
3. ADR-0058 : catalogue local et orientations ;
4. ADR-0059 : solveur volumetrique borne par etages ;
5. ADR-0060 : divulgation progressive dans la palette Fusion.

## Mission suivante apres acceptation des ADR

P61 - etat reactif et architecture de palette.

P61 sera borne aux diagnostics discrets, aux etats source/derive/solve/
materialise, a l invalidation explicable et a l architecture d information. Le
solveur Z reste P64.

## Releases bloquees

P61-P65 sont bloques par la revue des ADR. P44 a P50 restent bloques jusqu a
l acceptation humaine P66. P47 a P50 restent aussi bloques jusqu a
l acceptation de P46.

## Gate humaine active

Gate d architecture ADR-0056 a ADR-0060. Aucun nouveau smoke Fusion n est demande
avant implementation de P61-P65. La future gate produit devient P66 et sera
preparee automatiquement.

## Fin de chaque mission

Documenter chaque OK/KO sans extrapoler a l impression, mettre a jour le
pilotage, committer et integrer directement dans main quand les preuves
automatisees sont vertes. print-validated: false reste obligatoire.
