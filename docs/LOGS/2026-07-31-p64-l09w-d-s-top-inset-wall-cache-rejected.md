# 2026-07-31 — P64-L09W-D-S

Mission : tester un deuxième levier causal sur les `bounded_unknown`, sans
hausse de budget ni modification de la géométrie validée.

Décision :

- classer les 52 cas non couverts par D-Q avant tout code ;
- cibler les 15 cas `stress` dont le témoin projeté est recertifié trop tard ;
- tester un cache exact des contrôles statiques de paroi ;
- retenir le gain causal isolé sur `tuning-338`, mais rejeter le candidat après
  la régression de temps de `tuning-388` ;
- arrêter les sentinelles à 13/16, retirer le code et ne pas lancer les 48 ou
  les 400 ;
- conserver le holdout E scellé.

Preuve :
`docs/P64_L09W_D_S_TOP_INSET_WALL_CACHE_REJECTION_EVIDENCE.md`.
