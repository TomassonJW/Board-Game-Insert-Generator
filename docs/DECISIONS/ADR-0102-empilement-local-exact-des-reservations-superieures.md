# ADR-0102 — Empilement local exact des réservations supérieures

## Statut

Acceptée dans le périmètre correctif P64-L09U-R6 à partir des observations
humaines de Thomas sur 0.1.76.

Cette décision formalise une règle déjà attendue par le produit. Elle ne change
aucune épaisseur, aucun jeu et aucune tolérance. Elle ne vaut ni validation
Fusion, ni validation d’impression.

## Contexte

Les régions minimales savent déjà décomposer les empreintes de plusieurs
plateaux et livrets. Deux pertes apparaissent ensuite :

- la fermeture utilise une garde Z conservative calculée sur l’empreinte
  globale d’un élément inférieur ;
- la matérialisation choisit une seule réservation profonde par cellule.

Cette simplification est incorrecte lorsque les empreintes sont disjointes,
partiellement recouvrantes ou imbriquées. Elle peut aussi abaisser le corps
imprimable sous une micro-partie de cavité sans abaisser la cavité elle-même.

## Décision

### 1. La règle est locale en XY

Les bords de toutes les empreintes découpent le plan XY en cellules atomiques.
Une cellule appartient uniquement aux éléments dont l’empreinte la couvre
réellement.

Un contact de bord ou de point ne compte pas. Tout chevauchement dont les deux
dimensions sont strictement supérieures à l’epsilon géométrique compte, même
s’il est plus petit qu’une paroi canonique. Aucun seuil relatif, pourcentage de
surface ou test au centre de la cavité ne peut l’annuler.

### 2. Les intervalles Z suivent l’ordre de pile

Dans chaque cellule, les éléments actifs sont ordonnés du bas vers le haut par
`stack_order`, puis par identité stable en cas d’égalité.

En partant du sommet fonctionnel :

- l’élément supérieur occupe son propre intervalle immédiatement sous le
  sommet ;
- chaque élément inférieur occupe son propre intervalle immédiatement sous
  les éléments actifs placés au-dessus ;
- la profondeur totale de vide est la somme des épaisseurs des seuls éléments
  actifs dans cette cellule.

Pour un plateau de `4 mm` sous un livret de `2 mm` :

- zone plateau seul : intervalle plateau `sommet-4 → sommet` ;
- zone livret seul : intervalle livret `sommet-2 → sommet` ;
- intersection : plateau `sommet-6 → sommet-2`, livret
  `sommet-2 → sommet`.

### 3. Les zones disjointes ne cumulent rien

Deux petits éléments côte à côte au même niveau commencent chacun au sommet
dans leur propre empreinte. Leur épaisseur n’est jamais additionnée dans la
zone de l’autre.

Une zone sans élément reste au sommet fonctionnel du corps.

### 4. La fermeture réserve l’union exacte

La fermeture composite reçoit une garde par cellule atomique égale à l’union
exacte des intervalles actifs. Elle ne reçoit plus la somme de tous les
éléments supérieurs sur l’empreinte globale d’un élément inférieur.

Cette garde reste un interdit de croissance pour la fermeture. Elle ne devient
ni corps utilisateur, ni support artificiel.

### 5. Chaque intervalle survit jusqu’à Fusion

Le plan final, l’aperçu, la CAD IR et le plan Fusion conservent pour chaque
coupe :

- l’identité de l’élément plat ;
- l’identité de la région locale ;
- la liste des éléments actifs dans la cellule ;
- le bas et le haut exacts de son intervalle Z ;
- l’ordre de retrait.

Les volumes adjacents peuvent être booléennés par lots, mais le contrat ne peut
plus remplacer plusieurs intervalles par une seule réservation responsable.

### 6. Une cavité chevauchée est ancrée contre la région réelle

Une cavité qui chevauche une région locale réelle est ancrée sous l’intervalle
le plus profond qui la recouvre. La décision utilise l’intersection exacte des
rectangles, pas le centre de la cavité et pas la seule présence d’une coupe
positive.

Si le corps imprimable arrive déjà exactement au dessous de la région, la face
locale vaut preuve de responsabilité même si le volume de coupe correspondant
est nul avant extension CAD.

La profondeur calibrée, X/Y, l’orientation et l’identité de la cavité restent
inchangées. ADR-0101 continue d’ouvrir séparément les portions hors
réservation.

## Conséquences

- Les cas imbriqués, partiellement recouvrants et disjoints partagent une même
  règle déterministe.
- La fermeture peut remplir la matière jusqu’au vrai palier local au lieu de
  conserver un manque artificiel.
- Le nombre de coupes logiques peut augmenter, sans réintroduire de Combine
  rectangulaire ni changer le chemin BRep transitoire.
- L’identité du finaliseur doit changer afin d’invalider les artefacts dérivés
  sous l’ancien contrat.

## Compatibilité

Restent inchangés :

- les épaisseurs `4 mm` et `2 mm` du cas observé ;
- tous les jeux et tolerances existants ;
- le solveur minimal, les budgets et le plafond mural ;
- les fonds, parois, appuis et enveloppes minimales ;
- ADR-0100 et ADR-0101 ;
- le rollback global et la respiration Fusion.

## Alternatives refusées

- Cumuler globalement les épaisseurs selon le seul `stack_order`.
- Forcer les éléments plats à partager la même empreinte.
- Choisir une seule réservation profonde et perdre les intervalles supérieurs.
- Ignorer un chevauchement inférieur à une paroi ou à un pourcentage arbitraire.
- Déplacer ou raccourcir la cavité pour masquer le conflit.
- Introduire une nouvelle valeur physique ou une tolérance métier.
