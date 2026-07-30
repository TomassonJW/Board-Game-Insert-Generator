# P64-L09W-D — preuve de validation stratifiée

Date : 2026-07-30.

Statut : `stopped-hard-gate`, `increment-validation-failed`,
`holdout-sealed`.

## Décision

Les 361 cas du replay D historique ne sont pas nécessaires. ADR-0108 les
remplace honnêtement par 77 cas planifiés :

- 10 résultats D réutilisés ;
- 67 nouveaux cas ;
- deux causaux obligatoires ;
- les 61 résultats prêts de C ;
- huit pertes cibles par strate `common` et `stress`.

Cette sélection n'est pas un estimateur de taux.

La campagne stratifiée s'arrête à la première divergence fonctionnelle dure.
Les 17 cas planifiés restants ne sont donc pas exécutés et ne sont pas déclarés
réussis.

## Résultat observé

Le checkpoint v4 est arrêté sans cas actif :

- cas planifiés évalués : `60/77` ;
- nouveaux cas exécutés : `50/67` ;
- cas causaux réussis : `2/2` ;
- non-régressions prêtes réussies avant l'arrêt : `56` ;
- échantillons cibles évalués : `3` ;
- pertes cibles supprimées : `3` ;
- résultats cibles prêts : `2` ;
- strate évaluée : `57 common`, `3 stress` ;
- faux impossible : `0` ;
- solution non certifiée publiée : `0`.

L'arrêt porte sur
`p64-l09w-tuning-360-c8628c8c54`. Le cas reste certifié, finalisé et prêt pour
Fusion, avec le même placement et la même route que C. Mais son payload minimal
certifiable publie une troisième empreinte :

- C replay 1 : `0d557629...f3f12` ;
- C replay 2 : `b314a432...08dc` ;
- D v3 : `b314a432...08dc` ;
- D v4 : `d0e5bb69...c554`.

La nouvelle empreinte n'appartient pas à l'ensemble observé dans C. La gate
`ready_functional_digest_regression` reste donc KO. Le fait que C soit déjà non
déterministe empêche d'attribuer causalement cette troisième sortie au seul
correctif de finalisation, mais il empêche aussi de démontrer sa
non-régression exacte.

## Preuves locales

- plan :
  `.codex-work/p64-l09w-d/stratified-validation-plan.json`,
  digest `a5a689d0...4469` ;
- checkpoint arrêté :
  `.codex-work/p64-l09w-d/stratified-checkpoint-v4.json`,
  digest `c8dd7177...3f7e` ;
- rapport :
  `.codex-work/p64-l09w-d/stratified-report-v4.json`,
  digest `a9892696...de46` ;
- checkpoint v3 conservé comme audit du replay ayant reproduit la seconde
  signature C ;
- correctif de gate du runner :
  `71b8919`.

Les checkpoints v1 à v4 restent distincts. Aucun résultat arrêté n'est réécrit
ou assimilé à une réussite.

## Conséquences D, E et F

- D : l'incrément de fermeture XY reste sauvegardé, mais n'est pas validé comme
  non-régressif.
- E : non admissible. Le correctif aval ne change pas les `332/400` solutions
  certifiées de C et D possède en plus une gate fonctionnelle KO.
- Holdout E : non lu, non ouvert et non invoqué,
  `opening_count=0`, `solver_invocation_count=0`.
- F : non lancée. Aucune candidate Fusion, installation ou recette humaine
  n'est préparée.

## Validation

- tests du plan et du runner : `7/7` ;
- garde documentaire : `11/11` ;
- préflight de l'exécuteur sous le Python 3.14 Fusion : OK ;
- `git diff --check` : OK avant le run ;
- script historique `run_d_batch.ps1` : non exécuté.

## Suite recommandée

Ouvrir une mission causale bornée sur le non-déterminisme du payload minimal du
cas public `p64-l09w-tuning-360-c8628c8c54`. Cette mission doit reproduire les
trois signatures sans holdout, identifier l'ordre ou l'état instable, ajouter
un test déterministe puis décider si l'incrément D peut être revalidé. Les
68 `bounded_unknown` ne sont traités qu'après cette fermeture, par un
changement causal distinct.

`fusion-validated=true` reste hérité de la candidate 0.1.80.
`print-validated=false`.
