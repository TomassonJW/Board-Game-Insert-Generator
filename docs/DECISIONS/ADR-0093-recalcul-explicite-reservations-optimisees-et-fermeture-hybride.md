# ADR-0093 — Recalcul explicite, réservations optimisées et fermeture hybride

## Statut

Acceptée explicitement par Thomas le 2026-07-27.

Cette décision ouvre le programme correctif P64-L09T. Elle ne vaut ni
validation Fusion, ni validation d'impression.

## Contexte

L'observation humaine de l'add-in 0.1.69 confirme plusieurs acquis :

- `CasLimite01` et `CasLimite02` de base sont fortement améliorés ;
- la jauge reste visible et fluide pendant les opérations ;
- les plateaux et livrets restent des réservations virtuelles ;
- la cavité orientée de `CasLimite02` conserve ses dimensions canoniques.

Les variantes locales `CasLimite01+` et `CasLimite02+` montrent cependant que
le parcours n'est pas assez robuste :

- le calcul favorise des piles compactes alors que des couches basses restent
  visiblement exploitables ;
- une absence d'origine XY est seulement interprétée comme « centré », pas
  comme une pose réellement recherchée ;
- la finition composite exige encore une partition rectangulaire brute
  complète avant de construire des annexes ;
- une fermeture composite peut être rejetée par le certificat produit après
  avoir consommé une partie du budget ;
- l'interface n'explique pas suffisamment pourquoi une recherche s'arrête
  avant son plafond ;
- l'ajout ou la modification d'un contenu peut republier automatiquement un
  plan minimal par réutilisation locale, ce qui brouille le cycle explicite ;
- une encoche de plateau proche d'une cavité peut laisser une paroi plus mince
  que l'épaisseur minimale du conteneur.

Thomas choisit une seule stratégie de finition immédiate : l'hybride
extension rectangulaire puis annexes soudées. Les cales séparées, séparateurs
sans fond et conteneurs de finition générés restent des capacités futures
distinctes.

## Options

### Option A — Corriger seulement les deux cas « + »

Cette option est rapide, mais conserverait les causes structurelles :
classement favorable aux piles, réservation seulement centrée et faux repli
composite.

### Option B — Exposer immédiatement plusieurs modes de finition

Cette option donnerait beaucoup de choix, mais multiplierait les géométries,
certificats, composants, réglages et gates physiques avant de disposer d'une
fermeture automatique fiable.

### Option C — Stabiliser un parcours automatique unique et différer les autres familles

Cette option garde une UX simple et renforce les invariants communs avant
d'ajouter de nouvelles pièces de finition.

## Décision

Retenir l'option C.

### 1. Toute édition géométrique exige un calcul explicite

Après une modification d'asset, de conteneur, de plateau, de livret, de boîte,
de jeu ou de réglage géométrique :

- le plan minimal courant devient obsolète ;
- le plan final devient obsolète ;
- aucun placement monde n'est republié automatiquement ;
- aucun message « intégré localement » n'est affiché ;
- `Calculer` est la seule action qui peut republier un plan minimal.

Les chemins produit d'ADR-0075 et ADR-0076 sont supersédés. Leurs preuves
restent historiques. Le suivi déterministe des dépendances, les statuts
`current` / `stale`, les digests, le cache exact consulté lors d'un calcul
explicite et le rejet des réponses obsolètes restent acquis.

Les futures capacités post-finalisation C01 à C03 restent verrouillées. Elles
ne pourront revenir que comme actions explicites, après une nouvelle décision
produit ; elles ne restaurent pas la réutilisation automatique supprimée ici.

### 2. Les plateaux et livrets restent virtuels mais leur pose devient une décision

Un plateau ou livret :

- ne devient jamais un conteneur ou un corps utilisateur ;
- reste une réservation supérieure non imprimable ;
- reste placé au plus haut niveau admissible ;
- reçoit une pose X/Y déterminée par le calcul global ;
- peut utiliser les orientations autorisées par sa source ;
- est placé conjointement avec les autres réservations et les conteneurs.

Les champs produit d'origine X/Y sont retirés du parcours normal. Les anciens
fichiers qui les contiennent restent lisibles, mais leur chargement migre la
réservation vers le placement automatique et rend les plans dérivés obsolètes.
La source n'est réécrite qu'à l'enregistrement explicite.

La pose résolue de chaque réservation appartient à l'identité du plan minimal.
La finition et la matérialisation doivent réutiliser exactement cette pose.

### 3. La priorité aux couches basses devient un objectif global

La faisabilité et tous les certificats restent prioritaires. Entre plans
certifiés, le classement minimise ensuite :

1. le nombre de conteneurs placés au-dessus du niveau soutenu le plus bas
   admissible ;
2. la somme de leurs bases Z et le volume élevé ;
3. la hauteur gênante sous les réservations supérieures ;
4. seulement ensuite l'encombrement, le nombre de piles et la compacité.

Cette règle compare des plans complets. Elle n'impose pas un choix glouton
irréversible « au sol d'abord ». Une pile reste autorisée lorsqu'elle est
nécessaire ou permet le meilleur plan complet certifié.

### 4. Les cavités et les réservations doivent conserver une paroi minimale

Le solveur et le certificat construisent autour de chaque cavité une enveloppe
de matière minimale dérivée de l'épaisseur de paroi déjà résolue pour son
conteneur.

Une réservation supérieure, sa coupe ou son dégagement ne peut pénétrer cette
enveloppe. Si elle le fait :

- le calcul cherche une autre pose X/Y ou une autre disposition ;
- la cavité n'est ni réduite ni déplacée silencieusement ;
- la finition ne rabote pas la paroi ;
- sans plan conforme, le résultat reste inconnu dans le budget.

Aucune nouvelle valeur physique ou tolérance par défaut n'est introduite :
l'épaisseur existante du conteneur reste l'autorité.

### 5. Le plan minimal fige les corps, les cavités et les réservations

Le plan minimal certifié devient l'entrée immuable de la finition :

- dimensions et poses monde des corps minimaux figées ;
- variantes et cavités figées ;
- poses et ordre des réservations figés ;
- axes Fixe et minima canoniques figés.

La finition ne replace aucun contenu et ne redistribue aucune cavité. Elle peut
uniquement ajouter de la matière à l'extérieur du cœur minimal.

### 6. La finition automatique suit une seule stratégie hybride

La finition exécute dans cet ordre :

1. tenter les extensions rectangulaires globales admissibles ;
2. découper le résiduel imprimable restant en cellules orthogonales bornées ;
3. attribuer chaque cellule admissible à un conteneur adjacent ;
4. unir les cellules attribuées sous forme d'annexes au propriétaire ;
5. appliquer les cavités figées puis les coupes de réservations ;
6. certifier le plan final, les unions et le résiduel nul.

Le repli composite ne peut plus exiger une fermeture rectangulaire brute
complète avant de créer ses annexes.

### 7. Une annexe soudée n'a pas de jeu interne

Lorsqu'une annexe appartient à un conteneur :

- l'interface annexe / propriétaire est interne au même corps ;
- son jeu produit est nul ;
- la construction CAD doit produire une union robuste par face commune ou
  chevauchement de construction borné ;
- ce chevauchement ne modifie pas l'enveloppe extérieure certifiée.

Les jeux restent obligatoires entre deux corps utilisateurs distincts, entre
le corps composite et la boîte, autour des réservations, des prises, des
cavités et de tous les vides techniques.

Une annexe ne peut pas consommer un corridor de jeu externe puis prétendre que
les deux corps sont encore séparés.

### 8. L'attribution des annexes reste déterministe et lisible

Une annexe doit :

- partager une vraie face verticale X ou Y avec son propriétaire ;
- posséder le même bas Z que la partie adjacente ;
- être soutenue et former un corps connexe ;
- respecter les enveloppes de paroi, cavités, réservations et retraits.

Le classement minimise :

1. le nombre d'annexes ;
2. le nombre de ruptures et de coins ;
3. l'aire de couture visible ;
4. le déséquilibre de volume ajouté ;
5. puis utilise la plus longue face commune et les identités stables pour
   départager.

Les volumes flottants, les liaisons Z seules et les connexions par arête ou
point restent refusés.

### 9. Le certificat porte sur les vrais corps composites

Un succès exige une certification concordante de :

- la source minimale immuable ;
- la pose des réservations ;
- l'enveloppe de paroi autour des cavités ;
- l'affectation de chaque cellule imprimable ;
- les contacts et unions des annexes ;
- les jeux externes ;
- les coupes de réservations ;
- le CAD IR ;
- `printable_residual_volume_mm3=0`.

La recertification ne peut pas utiliser seulement la partition rectangulaire
brute lorsque le corps publié est composite.

### 10. Un arrêt anticipé devient explicable

Le budget reste un plafond. Une opération peut s'arrêter plus tôt après succès,
épuisement de sa stratégie bornée, absence de prérequis ou rejet de certificat.

L'interface doit afficher :

- temps écoulé et plafond ;
- phase atteinte ;
- motif traduit ;
- nombre de candidats et rejets utiles ;
- distinction entre impossibilité prouvée et recherche bornée sans solution.

`xy_composite_gross_partition_not_found` ou un rejet de certificat ne doit
jamais être présenté comme une impossibilité générale.

### 11. Les autres familles de finition sont différées

Le pilotage conserve trois capacités futures :

1. cales solides imprimées comme pièces séparées ;
2. séparateurs sans fond ;
3. conteneurs de finition générés automatiquement.

Elles apparaîtront dans une future surface « Pièces de finition », jamais
silencieusement dans « Conteneurs et éléments ». Chacune exigera son contrat,
sa représentation, son certificat, son UX et sa gate physique. Elles ne sont
pas incluses dans P64-L09T.

## Conséquences

- 0.1.69 est classée `human-KO` avec acquis partiels conservés.
- Le cycle produit redevient entièrement explicite après une édition.
- Les projets historiques à origines XY restent lisibles, mais devront être
  recalculés.
- Le calcul peut coûter plus cher parce qu'il cherche aussi les poses de
  réservations et compare mieux les étages.
- La finition composite devient fidèle à l'intention initiale d'ADR-0089.
- La géométrie publiée correspond enfin à la géométrie certifiée.
- Les futures pièces de finition ne gonflent pas le correctif courant.

## Alternatives refusées

- Conserver « auto » comme simple centrage.
- Transformer un plateau en conteneur imprimable.
- Déplacer seulement les cavités proches du plateau pendant la finition.
- Imposer une règle gloutonne irréversible de remplissage du fond.
- Considérer le budget comme une durée minimale.
- Ajouter immédiatement six modes visibles de finition.
- Créer silencieusement des cales, séparateurs ou conteneurs.
- Conserver les réutilisations automatiques avec un libellé différent.

## Suivi

Le programme séquentiel, les preuves et la gate sont définis dans
`docs/P64_L09T_END_TO_END_GOAL_RUNBOOK.md`.
