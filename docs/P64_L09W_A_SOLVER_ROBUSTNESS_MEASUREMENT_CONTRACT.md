# P64-L09W-A — contrat de mesure de robustesse du solveur

Date : 2026-07-29.

Statut : `preregistered-before-product-optimization`.

## 1. Autorité et objectif

La candidate Fusion 0.1.80 est `human-positive`,
`fusion-validated=true`, `print-validated=false`. Son résultat fonctionnel,
son ordre, ses dispositions, son pipeline strictement soustractif et la
récupération de performance R9 restent acquis.

P64-L09W ne cherche pas à prouver que tous les placements 3D sont résolus. Il
mesure la probabilité d’obtenir une solution BGIG certifiée dans les limites
produit existantes, sur le domaine et la distribution ci-dessous.

Le futur seuil de 95 % est une gate de campagne, pas une promesse universelle.
L’objectif de 99 % ne concerne que la strate courante définie avant exécution.

## 2. Domaine de preuve rectangulaire V0.1

Le domaine couvert par la campagne est le suivant :

- projet `bgig.project.v1` accepté par le validateur courant ;
- boîte et enveloppes orthogonales, dimensions finies, positives et exprimées
  en millimètres ;
- une à 64 familles de conteneurs ;
- un à 64 enregistrements de contenu par conteneur, sans réaliser tout le
  produit cartésien ;
- au plus 512 enregistrements de contenu et 4 096 unités développées par cas
  de gate ; les cas plus grands appartiennent au soak ;
- une à plusieurs couches Z ;
- zéro à dix plateaux ou livrets gérés par les règles produit courantes ;
- variantes, orientations orthogonales, réservations, cavités, accès, parois
  et profondeurs locales déjà prises en charge ;
- calcul froid ou édition unique : ajout, retrait, dimension locale ou
  paramètre global ;
- profils d’effort produit existants, sans modification de leurs limites.

La finalisation utilise le profil `normal`, valeur par défaut du produit
0.1.80, indépendamment du profil de calcul porté par une ancienne fixture.

La preuve ne couvre pas :

- les formes avancées T2 à T4 ;
- une géométrie libre ou une rotation continue ;
- un projet rejeté par le contrat `project.v1` ;
- une taille au-delà des bornes de campagne ci-dessus ;
- la résistance mécanique ou l’imprimabilité réelle ;
- l’impression, tant qu’aucun prototype n’est mesuré.

Ces bornes limitent la revendication de campagne. Elles n’ajoutent aucune
limite physique au produit.

## 3. Distribution préenregistrée

Le nouveau holdout positif contient 400 cas faisables par construction :

- 240 cas `common` ;
- 160 cas `stress`.

La strate `common` respecte simultanément :

- occupation utile cible 30 %, 65 % ou 85 % ;
- au plus 18 conteneurs ;
- au plus 16 contenus par conteneur ;
- au plus deux éléments plats ;
- au plus trois couches ;
- aucune marge constructive par axe inférieure à 3 %.

Tout cas positif du domaine qui ne respecte pas ces six conditions appartient
à `stress`. Les recettes sont classées avant tout appel solveur.

Le plan pairwise du holdout doit contenir au moins :

| Axe | Valeurs obligatoires | Minimum par valeur |
| --- | --- | ---: |
| contenus par conteneur | 1, 2, 4, 8, 16, 32, 64 | 20 |
| conteneurs | 1, 2, 4, 8, 12, 18, 30, 50, 64 | 20 |
| occupation utile cible | 30 %, 65 %, 85 %, 95 % | 60 |
| éléments plats | 0, 1, 2, 3, 4, 5, 6, 10 | 20 |
| couches Z | 1, 2, 3, 4 ou plus | 40 |
| taille de boîte | petite, moyenne, grande | 60 |
| exécution | froide, ajout, retrait, paramètre local, paramètre global | 40 |

Une petite boîte a son plus grand axe inférieur ou égal à 150 mm ; une moyenne
est au-dessus de 150 mm et jusqu’à 300 mm ; une grande est au-dessus de 300 mm.

L’occupation utile est calculée depuis le témoin construit, après les
dégagements et réservations effectifs. Elle est accompagnée, jamais remplacée,
par :

- la marge minimale sur X, Y et Z ;
- le nombre de régions libres ;
- la fragmentation ;
- le nombre de supports et de variantes ;
- le rapport d’aspect maximal ;
- la proximité des dimensions presque égales.

Le plan est pairwise et déterministe. Les minima peuvent se chevaucher ; ils ne
forment pas un produit cartésien.

Quarante contrôles impossibles à borne formelle sont ajoutés hors du
dénominateur positif. Ils couvrent au moins le volume, une borne par axe,
l’empilement Z et une réservation incompatible.

## 4. Jeux et interdiction de fuite

- `regression` : cas publics historiques reconstructibles ;
- `discovery` : 240 nouveaux cas positifs ouverts ;
- `tuning` : 160 nouveaux cas positifs ouverts et distincts ;
- `holdout` : les 400 cas positifs ci-dessus, engagés avant tuning ;
- `negative-control` : 40 impossibles prouvés ;
- `soak` : au moins 2 000 cas déterministes, hors gate courte.

Deux cas ne peuvent pas être dans deux jeux si leur digest de projet, de
témoin, de recette ou de séquence d’édition est identique.

Les anciens holdouts L06, L07 et L08 sont des régressions consommées. Ils ne
participent jamais au nouveau verdict fermé.

## 5. Statuts autorisés

Chaque exécution se termine par exactement un statut :

- `certified_solution` ;
- `proven_impossible` ;
- `bounded_unknown` ;
- `unsupported` ;
- `error`.

Une solution sans certificat courant est un échec. Un cas positif déclaré
impossible invalide la candidate. Un timeout ou un plafond atteint reste
`bounded_unknown`.

Une fixture historique non reconstructible reçoit
`historical_semantic_drift` avant exécution et ne contribue à aucun taux
solveur.

## 6. Mesures par cas

Le résultat publie :

- digest fonctionnel et déterminisme sur replay ;
- préparation, projection, voies internes, SCIP, certification, finalisation,
  CAD IR et matérialisation séparés ;
- temps jusqu’à la première solution certifiée ;
- candidats bruts et uniques, états explorés, essais de pose, complétions,
  rejets et appels solveur ;
- voie, moteur, limite de temps, mémoire, seed et plafond réellement utilisés ;
- mémoire de pointe du processus ;
- statut de vérité, de certificat, de finalisation et de CAD IR ;
- motif exact après édition : cache accepté, cache refusé, témoin recertifié,
  reconstruction froide ou échec.

La matérialisation est `not-measured-offline` dans la campagne hors Fusion.
Si le code produit change, P64-L09W-F mesure séparément un échantillon
stratifié de 24 cas : huit `common`, huit `stress` et huit avec trois éléments
plats ou plus. Aucun temps de matérialisation ne peut être déduit du temps CAD
IR.

La mémoire de pointe est échantillonnée au plus toutes les 50 ms dans le
processus qui contient le runtime natif. Le rapport indique la plateforme et
la méthode ; une plateforme non instrumentée publie `not_available`.

## 7. Agrégations

Les taux sont publiés globalement et pour chaque famille, densité,
cardinalité, nombre d’éléments plats, couche, taille, modification et
difficulté.

Les percentiles `p50`, `p95` et `p99` utilisent le rang supérieur :
`ceil(p × n)`, borné entre 1 et `n`. Ils portent sur les cas certifiés et sont
accompagnés du nombre total, du nombre certifié et du nombre censuré.

Aucune moyenne globale ne masque une strate en dessous de sa gate.

## 8. Critères gelés avant optimisation

Le candidat P64-L09W-E est accepté seulement si :

1. au moins 380 des 400 cas positifs du holdout sont certifiés, soit 95 % ;
2. au moins 238 des 240 cas `common` sont certifiés, soit 99,17 % ;
3. aucun cas positif n’est déclaré impossible ;
4. aucune solution publiée n’est non certifiée ;
5. aucun digest fonctionnel de régression n’est perdu ;
6. les 40 contrôles impossibles restent prouvés ou honnêtement
   `bounded_unknown`, jamais faussement certifiés ;
7. finalisation et CAD IR réussissent pour chaque solution certifiée ;
8. aucune limite publique, grille, epsilon ou valeur physique n’a augmenté ;
9. les p50, p95 et p99, la mémoire et les familles faibles sont publiés sans
   seuil de temps inventé après mesure ;
10. l’ouverture du holdout a lieu une seule fois après engagement d’un
    candidat unique.

Le seuil renforcé n’est revendiqué que pour `common`. Le taux `stress` reste
publié même s’il est inférieur à 95 %.

## 9. Baseline P64-L09W-A

La baseline 0.1.80 utilise uniquement les fixtures déjà versionnées. Avant le
solveur, chaque source passe une gate de reconstruction :

- L05 à L07 : projet et vérité reconstruits sous le code courant ;
- L08 : problème 3D et témoin reconstruits, puis résultats publiés comme
  `core-only` ;
- toute divergence de digest est isolée, jamais réécrite.

La baseline doit publier séparément :

1. couverture et trous de matrice ;
2. fixtures reconstructibles ;
3. dérives sémantiques historiques ;
4. résultats produit courants ;
5. résultats de cœur L08 ;
6. phases non mesurables hors Fusion.

Le défaut de digest SCIP découvert par l’audit bloque le replay déterministe :
le modèle engageait le temps global restant, une métrique volatile. Il peut
être corrigé dans A parce qu’il empêche l’attribution et restaure l’invariant
existant ; il ne modifie ni la géométrie, ni la recherche, ni les limites.

Le replay compare le statut, le digest certifiable, le digest de placement et
la route. Il ne compare pas le `plan_digest` complet, car celui-ci engage
l’identifiant de requête volontairement distinct de chaque action.

## 10. Décision avant P64-L09W-B

La génération et l’ouverture unique constituent une décision structurante.
ADR-0107 fixe donc les vérités reconstructibles, les classes de fixtures, les
splits, les engagements et l’autorité du holdout avant tout nouveau corpus.
