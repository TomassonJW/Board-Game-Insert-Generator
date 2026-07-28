# ADR-0105 — Conteneurs finalisés et encastrements strictement soustractifs

## Statut

Acceptée par la décision humaine explicite de Thomas du 2026-07-28 dans le
Goal P64-L09U-R8.

Cette ADR corrige un contrat interne. Elle ne change aucun jeu, aucune
épaisseur, aucune tolérance, aucun budget solveur et aucune valeur physique.
Elle ne vaut ni validation Fusion, ni validation d'impression.

## Contexte

La candidate 0.1.78 est `human-KO`, `do-not-run`.

R8-A a localisé deux défauts :

1. la finalisation transforme certaines `final_size_mm` en `cad_size_mm`
   rehaussées jusqu'au sommet de conception lorsque la cellule est couverte par
   une réservation plate ;
2. le plan Fusion conserve l'intervalle local comme métadonnée, mais place
   l'outil BRep au sommet du corps.

Sur l'artefact exact de `CasLimite02++` :

- `125 019,76 mm³` sont ajoutés au-dessus des corps dits finaux ;
- le certificat les compense par un même volume de coupe planifié ;
- trois coupes du livret sont déplacées de `[63,8 ; 65,8]` à
  `[67,8 ; 69,8]` ;
- `31 209,20 mm³` du vide demandé ne sont pas retirés.

Le modèle produit de Thomas est plus simple que ce contrat :

1. le calcul place des enveloppes minimales ;
2. la finalisation produit les conteneurs complets ;
3. une passe distincte retire les encastrements des éléments plats ;
4. un élément plat ne crée jamais de matière.

## Options comparées

### Option A — corriger seulement le plan Fusion

Le plan utiliserait le sommet de `local_interval_z_mm` comme plan de coupe.

Avantages :

- changement court ;
- correction directe des trois intervalles décalés ;
- régression facile à écrire.

Refus :

- la finalisation conserverait ses extensions positives conditionnées par les
  éléments plats ;
- le certificat continuerait à accepter une compensation de volumes ;
- l'aperçu et la CAD IR garderaient deux notions concurrentes, `final` et
  `cad` ;
- les invariants « zéro volume positif » et « zéro union liée aux éléments
  plats » resteraient impossibles à prouver.

Cette correction sera nécessaire, mais elle n'est pas une architecture
suffisante.

### Option B — conserver le modèle et durcir seulement le certificat

Le certificat simulerait les outils BRep et vérifierait l'identité spatiale des
volumes ajoutés et retirés.

Avantages :

- détecte le défaut actuel avant Fusion ;
- améliore le fail-closed ;
- ne touche pas à la recherche.

Refus :

- un plateau ou livret continuerait à déclencher une fabrication positive ;
- le succès dépendrait encore d'une annulation future ;
- le contrat resterait difficile à lire et à maintenir ;
- une égalité spatiale parfaite ne rend pas une opération positive conforme au
  modèle produit.

La simulation exacte des outils est retenue comme garde, pas comme modèle.

### Option C — finaliser les conteneurs puis appliquer une passe soustractive

La géométrie positive des conteneurs est figée une fois. Une fonction pure
produit ensuite uniquement des volumes négatifs pour les plateaux et livrets.

Avantages :

- identité produit directe ;
- responsabilité de chaque étape explicite ;
- aucun besoin de nouveau solveur ;
- certificats et tests de bout en bout simples ;
- aperçu, CAD IR, plan Fusion et BRep peuvent partager la même source.

Coûts :

- migration du schéma composite ;
- invalidation des artefacts dérivés ;
- adaptation coordonnée de la finalisation et des deux adaptateurs ;
- régressions spatiales plus fortes nécessaires.

Cette option est retenue.

### Option D — reconstruire le solveur et la fermeture globale

Refusée :

- R8-A ne prouve pas que le solveur ou l'algorithme de fermeture cause la
  matière positive ;
- le coût et le risque seraient élevés ;
- le périmètre réouvrirait budgets, corpus et recherche sans nécessité ;
- les chemins actuels savent déjà produire les poses, propriétaires et
  régions locales nécessaires.

## Décision

### 1. Identité de matière

Soit :

- `F` la matière des conteneurs finalisés, avec leurs cavités et accès
  intrinsèques, mais avant tout encastrement plat ;
- `E_i` l'ensemble des volumes négatifs attribués à l'élément plat `i`, y
  compris son empreinte, sa prise et les dégagements soustractifs nécessaires à
  la continuité d'accès ;
- `M` la matière imprimable finale.

L'unique identité admise est :

```text
M = F \ union(E_i)
```

La construction de `F` se termine avant la création des `E_i`. Une fois son
digest publié, la passe plate ne peut plus modifier, remplacer ou compléter la
géométrie positive de `F`.

### 2. Quatre frontières explicites

#### Frontière A — plan minimal

Le plan minimal contient :

- les enveloppes minimales des conteneurs ;
- leurs poses et orientations ;
- les poses, ordres et régions locales des éléments plats ;
- des volumes réservés non imprimables ;
- les contraintes de paroi, d'accès et de couverture.

Il ne contient aucun corps, prisme, plaque, rail, fermeture, support, union ou
volume positif attribuable à un élément plat.

#### Frontière B — conteneurs finalisés

La finalisation absorbe le volume imprimable restant dans les conteneurs
demandés. Les réservations plates peuvent guider l'attribution des cellules et
protéger les hauteurs locales, mais elles ne deviennent pas des opérations
positives.

La sortie positive est
`bgig.finalized_container_geometry.v1`.

Chaque primitive positive porte :

- un propriétaire conteneur ;
- une origine et une taille finales ;
- une attribution `container_finalization` ;
- aucune identité de plateau ou livret.

La sortie peut conserver la fermeture source à des fins d'audit, mais cette
géométrie source est non exécutable.

#### Frontière C — passe d'encastrement

La fonction pure reçoit :

- la géométrie finalisée et figée ;
- les régions locales quantifiées ;
- les cavités, accès, fonds et parois à préserver.

Elle produit `bgig.flat_inset_subtraction_plan.v1`, composé uniquement
d'opérations `difference`.

Elle ne peut :

- créer un corps ;
- créer ou agrandir un prisme ;
- créer une union ;
- changer le digest de la géométrie positive ;
- déplacer une cavité ;
- inventer une valeur physique.

#### Frontière D — adaptateurs

L'aperçu, la CAD IR, le plan Fusion et le BRep consomment les mêmes primitives
positives finalisées et les mêmes volumes négatifs.

Ils ne recalculent ni profondeur, ni intervalle, ni propriété de corps.

### 3. Schéma composite

Le schéma exécutable devient
`bgig.xy_composite_container_body.v3`.

Il remplace l'ambiguïté `final_size_mm` / `cad_size_mm` :

- `final_origin_mm` et `final_size_mm` décrivent la primitive positive
  exécutable du conteneur ;
- `closure_origin_mm` et `closure_size_mm` peuvent décrire la source de
  fermeture pour l'audit seulement ;
- aucun champ `cad_size_mm` ne peut étendre silencieusement le final ;
- les soustractions plates vivent dans un plan séparé ;
- les cavités et accès intrinsèques restent des opérations négatives de
  conteneur.

Les unions nécessaires à un conteneur composite restent autorisées. Elles sont
attribuées au conteneur finalisé et ne portent aucun `flat_item_id`.

### 4. Attribution obligatoire des opérations

Toute opération géométrique possède une attribution contrôlable :

| Opération | Signe | Attribution admissible |
|---|---:|---|
| création du corps conteneur | positive | `container_finalization` |
| union d'annexe composite | positive | `container_finalization` |
| cavité d'asset | négative | `container_cavity` |
| accès de cavité | négative | `container_access` ou `flat_access` |
| empreinte de plateau/livret | négative | `flat_inset` |
| prise de plateau/livret | négative | `flat_grip` |

Une opération positive portant directement ou indirectement une attribution
plate est un rejet de certificat.

### 5. Profondeurs et intervalles

ADR-0102 reste autoritaire pour la partition XY atomique et l'empilement local.
ADR-0103 reste autoritaire pour l'ordre automatique
petit-dessous/grand-dessus. ADR-0104 reste autoritaire pour la grille produit.

Dans chaque cellule :

- la profondeur est la somme exacte des épaisseurs couvrantes ;
- le plateau seul retire `4 mm` ;
- le livret seul retire `2 mm` ;
- leur recouvrement retire `6 mm` ;
- chaque élément conserve son propre intervalle ordonné ;
- un contact de bord ou de point ne crée aucune intersection.

Les bornes produit sont exprimées en ticks de `0,1 mm`. L'epsilon numérique
reste réservé aux comparaisons topologiques et ne crée aucune coordonnée.

### 6. Contrat d'exécution Fusion

Pour toute soustraction plate :

```text
cut_size.z = interval.top - interval.bottom
cut_origin.z = interval.top
outil BRep = [interval.bottom ; interval.top]
```

Le plan Fusion refuse :

- un intervalle absent ;
- une origine qui ne correspond pas à son sommet ;
- une profondeur différente de la hauteur d'intervalle ;
- une coupe hors du corps cible ;
- une attribution positive plate ;
- un schéma composite v2 ancien présenté comme matérialisable.

Le BRep transitoire et la persistance unique par BaseFeature d'ADR-0098 restent
inchangés. Le rollback global reste obligatoire.

### 7. Certificat soustractif

`bgig.subtractive_flat_inset_certificate.v1` doit prouver :

```text
flat_positive_volume_mm3 = 0
flat_positive_body_count = 0
flat_positive_union_count = 0
positive_geometry_digest_before = positive_geometry_digest_after
```

Il prouve aussi :

- l'attribution complète de toutes les opérations ;
- l'union spatiale exacte des volumes négatifs ;
- la correspondance de chaque intervalle métier, CAD IR, Fusion et BRep ;
- les profondeurs locales `4/2/6 mm` du cas forcé ;
- la conservation des cavités calibrées, fonds, parois et accès ;
- l'absence de rebouchage d'une cavité ;
- l'absence de corps imprimable pour un élément plat.

Il est interdit de conclure à zéro volume positif par soustraction entre un
volume ajouté et un volume négatif prévu.

### 8. Ordre des opérations

L'ordre exécutable est :

1. créer les primitives positives du conteneur finalisé ;
2. unir les seules annexes de ce conteneur ;
3. retirer les cavités et accès intrinsèques ;
4. appliquer les soustractions plates ;
5. persister le corps résultat.

Aucune opération positive n'est admise après le début de l'étape 3.

### 9. Échec et publication

Une divergence à n'importe quelle frontière :

- rejette le plan final ;
- publie `materializable=false` ;
- ne publie aucune CAD IR partielle ;
- ne synchronise aucune scène ;
- conserve le plan minimal courant ;
- déclenche le rollback si Fusion avait commencé.

Un succès de volume amont ne peut pas couvrir un échec spatial aval.

### 10. Identités et migration

Les identités du finaliseur, de la géométrie composite, de la CAD IR et du plan
Fusion changent.

Les artefacts dérivés v2 sont invalidés et recalculés. Les projets source ne
sont pas réécrits. Les deux projets personnels restent strictement en lecture
seule.

Il n'y a pas de migration silencieuse d'un corps v2 vers v3 au moment de la
matérialisation.

### 11. Coût

R8 n'ajoute aucun solveur ni recherche globale :

- les poses et régions restent celles du plan minimal certifié ;
- l'attribution de la géométrie positive reste dans la finalisation existante ;
- la passe soustractive parcourt un ensemble borné de primitives et de régions ;
- les unions de volumes négatifs utilisent les frontières déjà quantifiées.

La correction n'est pas présentée comme un gain de performance. Les temps sont
mesurés sur les replays autorisés, sans benchmark, holdout, corpus ou tournoi.

## Découpage d'implémentation

### R8-C — frontière minimale séparée

- certificat explicite de zéro géométrie positive plate ;
- réservations non imprimables seulement ;
- suppression de toute compensation Z attribuée à une réservation ;
- tests ciblés sans changement de solveur.

### R8-D — conteneurs finalisés

- géométrie positive v1 et composite v3 ;
- primitives finales sans extension `cad_*` ;
- attribution complète aux conteneurs ;
- digest positif figé avant les soustractions.

### R8-E — passe soustractive

- plan de soustraction pur ;
- certificat `0/0/0` ;
- intervalle Fusion exécutable exact ;
- outil BRep identique à l'intervalle.

### R8-F — fidélité de bout en bout

- même contrat dans aperçu, certificat, CAD IR, Fusion et BRep ;
- régressions de recouvrement `4/2/6 mm` ;
- cavités et accès R6, parois R7, grille `0,1 mm`, BRep transitoire et rollback
  préservés ;
- replays personnels en lecture seule.

### R8-G — candidate

- suite autorisée avec les douze modules interdits exclus avant import ;
- intégration directe dans `main` ;
- package, installation locale et marqueurs vérifiés ;
- nouvelle gate humaine seulement après préparation complète.

## Compatibilité et précédence

Restent inchangés :

- ADR-0098 pour l'identité du minimum sélectionné, le BRep transitoire et la
  persistance unique ;
- ADR-0099 à ADR-0101 pour profondeurs, cavités et accès ;
- ADR-0102 pour les cellules et intervalles locaux ;
- ADR-0103 pour la pose et l'ordre automatique ;
- ADR-0104 pour la grille `0,1 mm`.

Sont remplacés :

- dans ADR-0098, l'exécution depuis `cad_origin_mm` / `cad_size_mm` ;
- dans ADR-0102, la notion d'une coupe « nulle avant extension CAD » ;
- tout certificat qui assimile compensation volumique et absence de matière
  positive.

ADR-0095 à ADR-0097 restent différées.

## Conséquences

- Le modèle interne correspond au modèle produit expliqué par Thomas.
- Les plaques ou rails ne peuvent plus être une étape intermédiaire normale
  attribuée aux éléments plats.
- Les adaptateurs deviennent plus simples à auditer.
- Les anciens artefacts finalisés doivent être recalculés.
- Le nombre total d'unions de conteneurs peut rester supérieur à zéro, mais
  aucune ne peut être liée à un plateau ou à un livret.
- Une gate Fusion reste nécessaire après la validation automatisée.

## Alternatives refusées

- Correctif de rendu seulement.
- Correction Fusion sans séparation du modèle.
- Compensation entre volume ajouté et volume coupé.
- Corps, plaque, rail, pont, fermeture ou support pour un élément plat.
- Nouvelle valeur physique.
- Nouveau solveur, benchmark, holdout, corpus ou tournoi.
- Placement manuel dans R8.
- Réouverture d'ADR-0095 à ADR-0097.
