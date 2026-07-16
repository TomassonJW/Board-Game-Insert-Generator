# ADR-0065 - Recherche dense adaptative et équilibre spatial 3D

## Statut

Acceptée le 2026-07-17 par validation humaine explicite : la répartition
harmonieuse en X, Y et Z doit devenir la référence du mode `balanced`, et un
projet disposant encore d'un volume important ne doit pas échouer seulement
parce que ses conteneurs ne se découpent pas en groupes contigus réguliers.

## Date

2026-07-17

## Cartes liées

- P44-V - Validation projet réel dense
- P64 - Solveur volumétrique multi-étages
- P64-H01 - Recherche dense et répartition 3D équilibrée

## Contexte

Le solveur P64 énumère des groupes contigus de taille uniforme et des piles
contiguës. Sur un projet réel de 30 conteneurs et 77 éléments, l'ajout d'un
petit élément de 10 x 10 x 5 mm peut faire disparaître le seul candidat alors
que les enveloppes minimales n'occupent qu'environ 40 % du volume disponible.
Une partition non contiguë de 10 et 20 conteneurs produit pourtant deux étages
complets dans la hauteur existante.

Le classement `balanced` pénalise actuellement chaque étage supplémentaire au
nom de la simplicité. Il choisit donc un seul étage tant qu'un arrangement XY
existe, même lorsque les dimensions automatiques sont beaucoup plus étirées en
Z qu'en X et Y. Ce comportement contredit la répartition volumétrique attendue.

## Options

1. Augmenter seulement les budgets des partitions contiguës.
2. Ajouter une recherche adaptative bornée et un score explicite d'équilibre
   spatial X/Y/Z.
3. Introduire immédiatement un solveur d'optimisation externe global.

## Décision

Retenir l'option 2.

Le portefeuille ajoute des partitions adaptatives déterministes. Pour chaque
nombre d'étages borné, les enveloppes les plus contraignantes sont affectées au
groupe dont la somme d'empreintes minimales est actuellement la plus faible.
Les arrangements XY complets résultants sont ensuite validés normalement.
Ces partitions sont évaluées avant les familles contiguës historiques afin
qu'une solution dense ne soit pas affamée par le budget global de candidats.
Une borne Z optimiste élimine avant tout calcul XY les nombres d'étages qui ne
peuvent déjà plus tenir dans la hauteur disponible.

Le mode `balanced` classe d'abord les candidats complets par leur score réel,
indépendamment de la famille de recherche qui les a produits. Son score ajoute
un équilibre spatial calculé à partir du rapport entre les facteurs d'expansion
moyens de X, Y et Z par rapport aux enveloppes minimales, puis de l'équilibre
des sommes d'empreintes minimales entre étages. Les arrangements XY du mode
équilibré sont eux-mêmes choisis en tenant compte de la hauteur de leur étage.
Une composition proche d'une expansion isotrope et de charges comparables
obtient donc un meilleur score qu'un ensemble artificiellement très haut, très
large ou concentré sur un seul étage.

La simplicité reste prise en compte : un étage supplémentaire ne gagne que
s'il améliore suffisamment la répartition 3D. Le mode `compact` n'est pas
redéfini et conserve sa préférence forte pour les solutions simples.

Les dimensions fixes, cibles, minimales, tolérances, règles de support et
valeurs physiques ne changent pas. La recherche reste heuristique, bornée,
déterministe, sans dépendance externe et sans matérialisation automatique.

## Conséquences

- Les étages apparaissent progressivement en mode `balanced` quand ils rendent
  l'allocation X/Y/Z plus homogène, pas seulement quand XY est saturé.
- Les partitions de tailles variables couvrent des projets denses que les
  découpages contigus réguliers peuvent manquer.
- Les budgets et compteurs de recherche exposent séparément les partitions
  adaptatives.
- L'optimalité globale n'est toujours pas revendiquée.
- Toute adoption future de CP-SAT, MIP ou d'une autre dépendance lourde exige
  une nouvelle décision.

## Validation attendue

- Deux petits conteneurs compatibles restent sur un seul étage.
- Une série homogène plus dense crée progressivement plusieurs étages en mode
  `balanced`, tandis que `compact` conserve un seul étage s'il reste valide.
- Une fixture dense de 30 conteneurs, dérivée et anonymisée du projet réel,
  trouve une solution en deux étages dans 400 x 300 x 183 mm.
- Les budgets restent bornés, le résultat déterministe et la suite complète
  demeure verte.
