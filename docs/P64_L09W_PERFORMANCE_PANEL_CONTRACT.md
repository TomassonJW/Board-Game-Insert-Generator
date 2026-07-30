# P64-L09W — Contrat des panels permanents de performance

Date : 2026-07-30.

Statut : `preregistered`, `open-only`, `holdout-sealed`.

## Objectif

Les panels réduisent le coût quotidien sans remplacer une preuve globale :

1. 16 sentinelles détectent rapidement une régression fonctionnelle ou un
   changement de profil de performance ;
2. 48 cas confirment uniquement un candidat déjà prometteur ;
3. les 400 cas ouverts restent réservés à un changement global ou au candidat
   gelé avant E ;
4. le holdout E reste une ouverture unique et séparée.

Aucun taux global n'est déduit des panels de 16 ou 48 cas.

## Panel sentinelle — 16 cas

Le panel contient exactement 8 cas `common` et 8 cas `stress`. Il inclut :

- les deux cas causaux de la fermeture XY ;
- `p64-l09w-tuning-360-c8628c8c54` comme sentinelle de séparation entre
  produit sélectionné et trace ;
- cinq résultats C déjà prêts hors Fusion ;
- deux `bounded_unknown` ;
- les routes témoin certifié, maxrects canonique, coin historique, pont
  historique et absence de solution dans la borne ;
- toutes les valeurs observées dans les 400 cas ouverts pour :
  densité, taille de boîte, type d'exécution, nombre de couches, nombre
  d'éléments plats, fragmentation et profil d'aspect.

Le temps C estimé d'un passage est `164,007 s`. La baseline de variance utilise
cinq répétitions.

## Panel candidat — 48 cas

Le panel candidat contient les 16 sentinelles et 32 cas supplémentaires :

- 24 `common` et 24 `stress` ;
- 16 résultats C déjà prêts ;
- 13 `bounded_unknown` ;
- 16 pertes cibles de finalisation ;
- sélection déterministe maximisant la couverture nouvelle des paires d'axes,
  des routes, des statuts, des pertes et des quintiles de temps ;
- préférence de départ pour les résultats prêts et les cas bornés répartis sur
  leur plage de temps.

Le temps C estimé d'un passage est `754,152 s`. Deux répétitions sont prévues
pour confirmer un candidat, soit environ `25 min 08 s`.

## Règles de passage

### Sentinelles

Un changement commence par les 16 sentinelles. Arrêt immédiat sur :

- faux impossible ou solution non certifiée ;
- changement du produit sélectionné ;
- régression d'un résultat déjà prêt ;
- échec d'un cas causal ;
- nouveau non-déterminisme du produit ;
- incohérence de checkpoint ou tentative d'accès au holdout.

Une variation de trace seule est publiée, mais n'est pas une régression
fonctionnelle.

### Candidat 48

Les 48 cas ne sont exécutés que si les sentinelles passent leurs gates
fonctionnelles et leurs seuils de performance mesurés.

Le passage du panel 48 n'autorise aucun taux global. Il autorise seulement la
préparation d'une campagne ouverte de 400 cas si le changement est global, ou
si le candidat doit être gelé avant E.

### Campagne ouverte 400

Les 400 cas ne sont pas une routine de chaque micro-optimisation. Ils restent
obligatoires avant E pour un candidat qui prétend satisfaire les seuils
globaux, et pour tout changement dont le rayon causal dépasse honnêtement le
panel 48.

## Seuils de performance

Aucun seuil fixe de type `±5 %` n'est préenregistré.

Les limites sont calculées après cinq répétitions sentinelles à partir de la
dispersion réellement observée par cas et au niveau du panel. Elles utilisent
une borne robuste unilatérale à 99 %, corrigée par Bonferroni pour les 16 cas,
et au moins le plus grand écart supérieur observé.

## Autorités et reproductibilité

Plan versionné :
`tests/fixtures/p64_l09w_performance_panels.v1.json`.

Constructeur :
`scripts/solver/build_p64_l09w_performance_panels.py`.

Le plan engage :

- le manifest public B ;
- le checkpoint ouvert C ;
- les 48 identifiants et digests de cas ;
- les références C utiles ;
- les rôles, features, coûts et règles d'arrêt ;
- `sample_is_rate_estimator=false` ;
- zéro lecture, ouverture ou invocation holdout.

Digest du plan :
`d427e148a194d6dec66bf354e287604e6f5446eb50c7e083682419187a36e528`.

SHA-256 du fichier :
`1b8d270b526bed51a770947f291374190f2a86462f4dbe49d53367bb7904b600`.

Seuils gelés :
`tests/fixtures/p64_l09w_performance_thresholds.v1.json`.

Preuve :
`docs/P64_L09W_PERFORMANCE_SENTINEL_BASELINE_EVIDENCE.md`.
