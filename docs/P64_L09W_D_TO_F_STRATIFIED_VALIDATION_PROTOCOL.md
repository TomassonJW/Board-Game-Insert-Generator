# P64-L09W-D à F — protocole de validation allégé et honnête

Date : 2026-07-30.

Statut : `preregistered-before-new-campaign`, `holdout-sealed`.

Autorité : ADR-0108.

## 1. État de reprise vérifié

- worktree : `C:\Users\janko\.codex\worktrees\930b\BGIG` ;
- branche de reprise : `codex/p64-l09w-d-stratified-validation` ;
- au préflight, HEAD, `main` et `origin/main` après fetch :
  `82e66c78ff9fd513e0c57016aac68cb23a20f1bc` ;
- lot de recadrage intégré dans `origin/main` :
  `2dd6f38f48c3e2b2c81bab20ff8dde2fd3af5f90` ;
- checkpoint Git D :
  `2de5959d4363e63e45b943ffff712b0de53e51f5`, ancêtre de HEAD ;
- les fichiers techniques D sont identiques entre ce checkpoint et HEAD ;
- checkpoint local D : `39/400`, `active_case_id=null` ;
- digest interne du checkpoint :
  `7a65dad456ee39bc455592e9f373dcbff4e1b9241f60ed42bd6be5d000ec2639` ;
- digest du bundle D :
  `29cceb8e20b490f364cbac548d6fcacab05e65e8d5b3d008b7e9e17c6091c029` ;
- holdout lu : `false` ; ouvertures : `0` ; invocations : `0`.

Le script historique `.codex-work/p64-l09w-d/run_d_batch.ps1` reste arrêté et
n’est pas utilisé par ce protocole.

## 2. Décision explicite sur les 361 cas

Les **361 cas D restants sont non nécessaires** pour valider le changement
courant. Ils ne sont ni supprimés, ni déclarés réussis : ils restent simplement
non exécutés.

Le changement restaure des frontières XY après la fusion des cellules
résiduelles. Il intervient après la certification du plan minimal et ne peut
donc pas améliorer le nombre de solutions minimales certifiées.

Le remplacement honnête est une preuve à trois niveaux :

1. les deux cas causaux obligatoires ;
2. la non-régression de tous les résultats C déjà prêts ;
3. un échantillon déterministe `common`/`stress` couvrant les axes et la longue
   traîne de temps.

Cette preuve décide si l’incrément de finalisation est sûr et utile. Elle ne
mesure pas un taux global : `sample_is_rate_estimator=false`.

## 3. Plan D exact

Plan local :
`.codex-work/p64-l09w-d/stratified-validation-plan.json`.

Digest :
`a5a689d0a2401d06da0ae72e2190d02461c18dfa9b62579a9d9790f8d4224469`.

### 3.1 Cas causaux obligatoires

- `common` :
  `p64-l09w-discovery-001-55d8459fc2` ;
- `stress` :
  `p64-l09w-tuning-240-ea12ccc81d`.

Les deux doivent finir sans résiduel, avec `solution_found`, certificat courant
et CAD IR prête. Le cas `common` possède déjà deux replays D checkpointés ; le
cas `stress` doit recevoir deux replays.

### 3.2 Non-régression des résultats prêts

Les 61 résultats prêts de C sont tous obligatoires :

- 55 `common` ;
- 6 `stress` ;
- 8 déjà présents dans le checkpoint D ;
- 53 à rejouer une fois.

Le résultat doit rester certifié, finalisé et prêt pour Fusion. Une divergence
fonctionnelle, une perte de finalisation ou une CAD IR non prête arrête le lot.
Un second replay sert uniquement à diagnostiquer cette divergence ; il ne
transforme jamais la régression en moyenne acceptable.

### 3.3 Échantillon causal stratifié

Le plan sélectionne huit cas `common` et huit cas `stress` parmi les 237 pertes
cibles. Dans chaque strate, la sélection :

- inclut le cas causal imposé ;
- couvre toutes les valeurs observées de densité, taille de boîte, type
  d’exécution, couche, nombre d’éléments plats, fragmentation et profil
  d’aspect ;
- ajoute les ancres de temps proches des quantiles 10 %, 50 % et 90 % ;
- départage de manière déterministe par identifiant de cas.

Deux cas `common` sélectionnés sont déjà checkpointés dans D. Les 14 autres cas
reçoivent deux replays.

### 3.4 Coût borné

- nouveaux cas : `67` ;
- nouveaux replays : `81` ;
- estimation depuis les temps C : `632,376 s` de calcul cumulé ;
- comparaison historique : `722` replays auraient été nécessaires pour les
  361 cas restants.

L’estimation n’est ni un timeout, ni une promesse de durée mur. Les cas sont
exécutés par petits lots checkpointés avec heartbeat et timeout métier.

## 4. Arrêts anticipés D

Arrêt immédiat et rapport KO sur :

- échec d’un des deux cas causaux ;
- régression d’un résultat déjà prêt ;
- faux impossible ;
- solution publiée sans certificat ;
- erreur candidate ;
- nouveau non-déterminisme par rapport à C, ou divergence de la signature
  solveur/placement canonique d’un cas stratifié ;
- mismatch de checkpoint, binding ou bundle ;
- toute tentative d’accès au holdout.

Les autres cas de l’échantillon peuvent conserver une autre perte aval
explicitement nommée. Un gain n’est compté que si le résiduel cible disparaît
et si la chaîne finale reste certifiée.

Le premier essai de l’exécuteur s’est arrêté avant tout nouveau solve sur
`p64-l09w-discovery-014-0ef6e517d6`. L’audit prouve que ce cas était déjà
non déterministe dans C. Son premier digest fonctionnel et son placement sont
identiques dans C et D ; seule la perte aval passe du propriétaire résiduel au
certificat d’ancrage final. La gate est donc corrigée pour refuser une
régression de déterminisme, jamais pour réattribuer à D une dette C existante.

## 5. Gate avant P64-L09W-E

E reste fermée après le seul incrément courant.

La référence C vaut :

- `332/400` solutions certifiées, alors que la gate exige `380/400` ;
- `200/240` solutions `common`, alors que la gate exige `238/240`.

Comme D ne change que la finalisation, ces deux comptes ne peuvent pas
augmenter. Après la validation stratifiée, D peut retenir ce correctif aval,
mais doit encore traiter causalement les 68 `bounded_unknown` avant qu’un
candidat E soit raisonnable.

Un futur candidat E doit être gelé par commit, configuration, limites et digest.
Le holdout ne peut être ouvert qu’une seule fois.

## 6. Exécution allégée de P64-L09W-E

L’économie E provient seulement des arrêts mathématiquement sûrs :

1. écrire le reçu irréversible puis ouvrir le holdout une fois ;
2. exécuter le replay primaire dans un ordre engagé et indépendant des
   résultats ;
3. arrêter dès le troisième échec `common`, le vingt-et-unième échec global,
   un faux impossible, une solution non certifiée, une erreur, ou une
   finalisation/CAD IR invalide ;
4. si le candidat peut encore passer après 400 cas, exécuter le second replay ;
5. arrêter le second passage à la première divergence fonctionnelle.

Une réussite exige toujours les 400 cas et leur replay. Une validation
stratifiée ne remplace jamais les seuils 380/400 et 238/240.

## 7. P64-L09W-F reste conditionnelle

P64-L09W-F est **conditionnelle** aux changements réellement retenus et à un
verdict E autorisant une candidate :

- aucun changement produit retenu : F omise ;
- candidat rejeté : aucune candidate Fusion, aucune installation, aucune
  recette humaine ;
- candidat accepté avec code produit modifié : une seule suite complète
  autorisée, les replays de bout en bout pertinents et l’échantillon de
  matérialisation de 24 cas prévu par le contrat A ;
- aucun temps de matérialisation n’est déduit de la CAD IR ;
- `print-validated=false` reste obligatoire.

## 8. Prochaine action

L'exécuteur D distinct du script historique est versionné dans
`scripts/solver/run_p64_l09w_d_stratified_validation.py`. Son préflight Python
3.14 valide le plan, les deux checkpoints, le bundle courant, le manifest et le
reçu runtime avant toute écriture.

Exécuter maintenant cet exécuteur par petits lots. Il est lié au digest du plan
et sait :

- réutiliser les 39 résultats D sans les réécrire ;
- exécuter les 67 nouveaux cas dans l’ordre des gates ;
- appliquer les répétitions `1` ou `2` du plan ;
- checkpoint après chaque cas ;
- arrêter selon la section 4 ;
- produire un rapport compact sans aucune surface d’accès holdout.
