# P64-V2H02 — Capacité théorique et vérité de recherche dense

Statut : fusion-validated. Preuve Fusion reçue le 2026-07-18 : `P64-V2H02R Fusion OK 0.1.54 - commit 42e8993`. La preuve confirme la portée bornée du lot, sans qualifier les valeurs physiques, l'impression ni la solubilité du cas dense.
Ce lot remplace la gate P64-V2H01 0.1.52 après le nouveau KO
contextuel sur le projet dense réel.

## Problème confirmé

Le projet Fusion conservé contient 11 conteneurs, 34 contenus, deux réservations
supérieures explicites et une boîte de 250 x 180 x 70 mm. Ajouter un contenu à
un conteneur disposant visuellement de place conduit encore à
`no_solution_within_budget`.

L'analyse sépare plusieurs causes :

- un conteneur multi-cavités pouvait être dérivé en une seule rangée trop large,
  puis déclaré formellement impossible avant toute recherche globale ;
- le beam rejetait un corps restant s'il ne tenait pas dans un seul espace vide
  maximal, alors qu'un corps peut couvrir plusieurs espaces s'il ne collisionne
  aucun corps et reste correctement supporté ;
- les points extrêmes initiaux ignoraient les frontières des réservations
  supérieures ;
- le préfiltre des réservations utilisait la cavité la plus profonde du
  conteneur, même sans recouvrement XY réel ;
- les profils d'effort ne diversifiaient qu'une priorité de participant et
  pouvaient donc produire les mêmes recherches sous des libellés différents ;
- la palette ne distinguait pas assez une marge de volume positive d'une preuve
  d'empilabilité orthogonale.

## Objectif borné

Le lot doit :

1. rechercher plusieurs enveloppes internes déterministes pour les conteneurs
   multi-cavités sans modifier les cavités demandées ;
2. préserver les états beam capables de franchir plusieurs espaces maximaux
   vides ;
3. rendre les réservations supérieures localisées et conscientes de
   l'orientation ;
4. rendre les budgets Rapide, Normal et Approfondi réellement distincts ;
5. publier une capacité volumique théorique signée, sur succès comme sur échec ;
6. réserver `proven_impossible` aux contradictions formelles ;
7. corriger l'occlusion de la vue de dessus et son repère écran : X reste inchangé, Y est retourné autour de l'axe X pour représenter une observation depuis le dessus.

Le lot ne change ni schéma projet, ni valeurs physiques, ni tolérances, ni
solveur exact, ni scène Fusion. Matérialiser reste explicite.

## Enveloppes internes bornées

La dérivation commence par le placement canonique historique et le conserve s'il
tient dans la boîte, directement ou après rotation. Elle n'ouvre un ensemble
déterministe et limité de candidats correctifs qu'en cas de blocage : ordres
source, largeur, hauteur, aire et côté maximal, puis étagères à colonnes égales,
next-fit et best-fit sur au plus 48 largeurs cibles par ordre. Les candidats qui
tiennent sont priorisés avant l'aire et l'aspect.

Cette recherche ne déplace aucune cavité après certification et ne constitue pas
encore le portefeuille de variantes sémantiques de P45. Elle corrige uniquement
la construction canonique manifestement trop étroite de P64.

## Capacité théorique

Chaque résultat issu du sélecteur produit expose `bgig.partition_capacity.v1` :

- volume brut utilisable de la boîte ;
- volume utilisable par le solveur après jeu périphérique ;
- somme des enveloppes minimales et compléments explicites exacts demandés ;
- volume physique informatif des éléments plats ;
- solde signé et volume théorique restant ;
- ratio d'occupation minimal ;
- contraintes non scalaires qui restent à satisfaire.

Le volume physique des plateaux et livrets est informatif. Il n'est pas soustrait
une seconde fois lorsque leur réservation est encastrée dans les enveloppes des
conteneurs : ce double comptage sous-estimerait artificiellement la capacité.

Une marge positive est une condition nécessaire, jamais une preuve de placement.
Deux ensembles de même volume peuvent rester incompatibles à cause des formes,
réservations, supports, jeux, axes fixes ou séquences de retrait. L'interface ne
doit donc jamais transformer ce solde en promesse de solution.

Sur le projet de référence du lot, le solde théorique est d'environ
693 634 mm³, soit 693,6 cm³ et 22,34 %. Malgré cette marge, aucun candidat n'est
certifié dans les budgets actuels.

## Vérité du cas dense

Une relaxation exacte de diagnostic, exécutée hors produit et sans dépendance
ajoutée au dépôt, a couvert positions continues, rotations XY, non-recouvrement
et réservations supérieures localisées. Elle conclut à l'infaisabilité de la
combinaison d'enveloppes canoniques du projet de référence avec ses origines
explicites. Ce résultat explique pourquoi augmenter seulement le temps
heuristique ne suffit pas.

Cette preuve de diagnostic n'est pas exposée comme moteur exact produit. Le
statut public reste `no_solution_within_budget` tant que le cœur embarqué ne
porte pas lui-même une preuve formelle couverte par contrat.

## Effort et méthodes

Les priorités de participants explorées par le beam deviennent :

- Rapide : 1 priorité, largeur beam 8 ;
- Normal : 2 priorités, largeur beam 24 ;
- Approfondi : 4 priorités, largeur beam 64.

Le portefeuille beam exécute deux variantes complémentaires : la recherche EMS
historique avec une priorité, qui préserve bit à bit les chemins validés de
P64-V2H01, puis la recherche multi-EMS avec le maximum 1/2/4 du profil. Les
candidats certifiés des deux variantes sont dédupliqués et classés ensemble.
L'élargissement ne remplace donc jamais silencieusement une amélioration déjà
validée.

Des résultats identiques restent possibles : un budget supérieur agrandit le
domaine exploré, il ne garantit ni une autre géométrie ni une solution.

`Auto intelligent` rend éligibles Étages et piles, le greedy 3D et le beam.
`Placement 3D libre` ne rend éligibles que greedy/beam ; le baseline historique
peut encore être évalué par l'adaptateur commun pour diagnostic et repli, mais il
ne peut pas être retenu par cette méthode. La palette affiche explicitement les
familles éligibles. Si aucun candidat n'est certifié, ou si les deux chemins
découvrent le même meilleur candidat, leur résultat visible peut légitimement
être identique.

## Vue de dessus

Les corps sont peints du bas vers le haut et les cavités sont composées avec leur
corps parent. Un corps supérieur masque ainsi les cavités inférieures au lieu de
les laisser visibles à travers ses parois. Dans la vue de dessus, la coordonnée Y métier est retournée autour de l'axe X du SVG ; X ne change pas et la coupe latérale ne change pas.

## Critères d'acceptation

- le conteneur dense de régression est dérivé dans la boîte sans faux blocage XY ;
- les réservations sont vérifiées cavité par cavité après rotation ;
- Quick, Normal et Deep exposent respectivement 1, 2 et 4 priorités ;
- tout résultat issu du sélecteur produit expose la capacité théorique ;
- le cas dense affiche une marge positive et un statut non certifié honnête ;
- aucun diagnostic de budget n'affiche une fausse impossibilité ou une mesure
  négative issue d'une branche rejetée ;
- la vue de dessus respecte l'occlusion des corps ;
- le cœur reste sans import `adsk` et aucune dépendance externe n'est ajoutée.

## Suite structurante

P64-V2H03 devra étudier un portefeuille borné de variantes d'enveloppes internes
et leur sélection globale, coordonné avec la propriété fonctionnelle de P45.
L'arbitrage est maintenant fixé par
`docs/P64_V2H03_INTERNAL_VARIANT_COORDINATION_CONTRACT.md` et ADR-0070 : P45
possède les sémantiques et le certificat local, P64 consomme paresseusement les
variantes certifiées et conserve le certificat global. Le runtime reste non
commencé.

P64-X01 demeure le futur mode exact soumis à ADR et benchmark. P64-U01 portera
une progression de calcul non modale, annulable et incapable de voler le focus ;
aucun écran bloquant n'est introduit dans ce lot.

## Gate Fusion

Préparation : `scripts/fusion/prepare_p64_v2h02_capacity_search_test.ps1`.

Retour reçu :

`P64-V2H02R Fusion OK 0.1.54 - commit 42e8993`

Un retour positif valide uniquement l'affichage, les budgets observables, la vue
et la vérité du résultat logiciel. Il ne prouve pas que le projet dense possède
une disposition, ne calibre aucune valeur physique et ne vaut pas impression
réelle. `print-validated: false`.