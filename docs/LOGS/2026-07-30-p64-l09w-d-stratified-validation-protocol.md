# 2026-07-30 — P64-L09W-D, recadrage stratifié D à F

## Contexte

La campagne D a été arrêtée proprement après 39 cas sur 400 afin de réduire le
coût de la suite. Le checkpoint technique `2de5959d...e51f5` est intégré dans
`main`; les artefacts locaux D sont intacts et le holdout n'a jamais été lu.

## Décision

ADR-0108 remplace les 361 cas D restants par une validation causale et
stratifiée :

- deux cas causaux obligatoires, un `common` et un `stress` ;
- les 61 résultats déjà prêts de C, sans tolérance à une régression ;
- huit pertes cibles par strate couvrant les valeurs observées des axes et les
  quantiles de temps 10 %, 50 % et 90 % ;
- 67 nouveaux cas et 81 replays ;
- aucun taux dérivé de l'échantillon.

Le plan local vaut
`a5a689d0a2401d06da0ae72e2190d02461c18dfa9b62579a9d9790f8d4224469`.

## Conséquence sur E

Le correctif D courant intervient après la certification minimale. Il ne peut
pas faire progresser les 332/400 solutions certifiées de C vers 380/400, ni les
200/240 `common` vers 238/240. Le holdout E reste fermé.

Un futur candidat admissible ouvrira le holdout une seule fois. E s'arrêtera
dès le troisième échec `common`, le vingt-et-unième échec global ou une
invalidation dure. Une réussite exigera toujours les 400 cas et leur replay.

## Conséquence sur F

F est omise sans changement produit retenu ou sans verdict E positif. Aucune
candidate Fusion, installation ou recette humaine ne compense un échec E.

## Validation

- planificateur sans argument de holdout ;
- plan dérivé des checkpoints C et D ;
- sélection déterministe testée ;
- couverture de toutes les valeurs observées des axes sélectionnés testée ;
- protocole documentaire testé.

`fusion-validated=true` reste hérité de 0.1.80.
`print-validated=false`.
