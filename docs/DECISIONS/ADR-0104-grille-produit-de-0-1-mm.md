# ADR-0104 — Grille produit de 0,1 mm

## Statut

Acceptée par la décision humaine de Thomas du 2026-07-28.

Cette ADR fixe une résolution de disposition. Elle ne change aucune épaisseur,
aucun jeu, aucune tolérance physique et ne vaut pas validation Fusion ou
d'impression.

## Contexte

Le moteur publie actuellement des valeurs dérivées au centième ou au millième,
par exemple `78,88`, `22,24`, `4,88` et `1,18 mm`. La recherche peut également
produire des ancres issues de divisions flottantes non canoniques.

La résolution produit est désormais `0,1 mm`. Elle ne doit pas être confondue
avec l'epsilon numérique interne, nécessaire pour comparer des flottants ou
valider une topologie.

## Options comparées

### Option A — arrondir seulement à l'affichage

Refusée : les digests, certificats, CAD IR et opérations Fusion continueraient
de diverger derrière une présentation trompeuse.

### Option B — remplacer tous les floats du dépôt par `Decimal`

Refusée : changement transversal risqué, sans besoin démontré pour les calculs
hors disposition R7.

### Option C — ticks entiers de 0,1 mm aux frontières produit

Retenue : la recherche et les artefacts de disposition manipulent une identité
canonique en ticks ; les API existantes continuent à recevoir des millimètres
flottants égaux à `ticks / 10`.

## Décision

### 1. Constantes distinctes

- grille produit : `0,1 mm` ;
- un tick produit : `1` ;
- epsilon numérique interne : valeur plus petite, conservée uniquement pour les
  comparaisons et contrôles topologiques.

L'epsilon ne crée jamais une position candidate et n'apparaît jamais comme
résolution publiée.

### 2. Frontières quantifiées dans R7

Sont canoniques en ticks avant publication :

- origines candidates X/Y ;
- rotations et empreintes orientées avec jeu ;
- prises automatiques ;
- bords des cellules XY locales ;
- positions, tailles et intervalles Z dérivés ;
- enveloppes de paroi et distances certifiées ;
- prismes finaux, coupes, aperçu, CAD IR et plan Fusion issus de ces données.

Les valeurs sources physiques sont conservées dans le projet lu. R7 ne réécrit
aucun fichier source et ne remplace pas aveuglément les autres floats du dépôt.

### 3. Règles d'arrondi

- valeur produit ordinaire : dixième le plus proche, moitié vers l'extérieur
  du zéro ;
- borne minimale admissible : dixième intérieur par rapport au domaine
  autorisé ;
- empreinte de vide ou de jeu minimal : enveloppe conservatrice, bord inférieur
  vers le bas et bord supérieur vers le haut ;
- minimum de matière : jamais arrondi vers une valeur qui le diminue ;
- intersections : calculées entre bords déjà quantifiés, donc exactes en ticks.

Après conversion, tous les certificats géométriques sont relancés. L'arrondi
n'est jamais une justification pour accepter un plan autrement invalide.

### 4. Source, effectif et migration

Un ancien projet est lu sans écriture :

- les valeurs sources restent traçables ;
- les valeurs effectives de disposition sont quantifiées ;
- si une valeur source n'est pas sur la grille, le rapport de migration expose
  source, valeur effective et direction d'arrondi ;
- le calcul, le plan final, l'aperçu et la scène antérieurs deviennent
  obsolètes ;
- aucune sauvegarde automatique du projet migré n'est permise.

Les deux projets personnels R7 sont déjà exprimés au dixième pour leurs valeurs
physiques observées ; leurs SHA doivent rester identiques.

### 5. Digests et identités

Les digests fonctionnels de disposition utilisent :

- l'identifiant de grille ;
- les ticks entiers canoniques ;
- la politique d'arrondi ;
- la version de l'ordre automatique.

Les représentations flottantes intermédiaires ne participent pas directement au
digest. Les identités du plan minimal, du finaliseur, de la CAD IR et du plan
Fusion changent pour interdire toute réutilisation de l'ancien contrat.

### 6. Déploiement progressif

1. introduire et tester les conversions de grille ;
2. quantifier la génération/déduplication des candidats ;
3. quantifier les réservations et régions locales ;
4. recertifier la finalisation ;
5. contrôler l'aperçu, la CAD IR et le plan Fusion ;
6. ajouter les migrations et digests ;
7. mesurer les replays autorisés.

Aucun changement global de type numérique n'est requis.

### 7. Mesures honnêtes

Les preuves avant/après publient :

- candidats bruts ;
- candidats uniques après quantification ;
- états retenus ;
- temps de calcul et de finalisation observés ;
- digests et nombre de valeurs hors grille.

La grille n'est pas présentée comme un gain de performance tant qu'une baisse
du nombre de candidats ou du temps n'est pas observée sur les replays autorisés.
Les mesures ne sont ni un benchmark, ni un holdout, ni un tournoi solveur.

## Conséquences

- Les coordonnées et dimensions dérivées deviennent lisibles et stables.
- Les digests cessent de dépendre de petites variations flottantes.
- Certains candidats proches fusionnent lors de la déduplication.
- Une ancienne disposition peut nécessiter un recalcul explicite.
- Fusion reçoit toujours des millimètres flottants, mais uniquement issus des
  ticks canoniques.

## Alternatives refusées

- Grille au millième ou au centième.
- Arrondi uniquement lors de la sérialisation.
- Utilisation de l'epsilon comme pas de recherche.
- Réécriture automatique des projets personnels.
- Changement global et immédiat de tous les floats.
