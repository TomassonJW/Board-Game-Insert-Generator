# 2026-07-30 — P64-L09W-B corpus produit fermé

## Décision

ADR-0107 est implémentée sans changement du solveur. Les vérités positives sont
construites indépendamment puis recertifiées ; les impossibles gardent une
borne formelle séparée.

## Résultat

- 400 positifs ouverts ;
- 400 positifs privés dans un holdout neuf ;
- 40 contrôles négatifs ;
- baseline `regression` A référencée sans duplication ;
- minima pairwise satisfaits des deux côtés ;
- zéro collision des engagements ouvert/holdout ;
- `opening_count=0` ;
- `solver_invocation_count=0`.

Manifest public :
`04dd2bf5feed37b7d5e72e523d5d7f0cd6bc0672f9ecfb55b227d5fcb6635840`.

Sidecar privé :
`18bd401058f882b4deb2951e775b344e1a4d00b49994e5ffaa962572b876ec5a`.

La reprise a construit les 127 cas restants par lots checkpointés distincts,
sans relancer la commande monolithique.

## Validation

- test ciblé de reprise : `1/1` ;
- suite B : `10/10` ;
- suite L09W : `21/21` ;
- contrats documentaires : `11/11` ;
- suite complète : `1054/1054`, `1` skip prévu ;
- vérification finale des engagements : OK.

## Suite

P64-L09W-C devient l’unique mission `ready`. Le holdout reste fermé jusqu’à
P64-L09W-E. Aucun replay Fusion n’est requis et
`print-validated=false`.
