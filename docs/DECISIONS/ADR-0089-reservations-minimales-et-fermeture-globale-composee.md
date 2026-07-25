# ADR-0089 — Réservations minimales et fermeture globale composée

## Statut

Proposée, prête à être acceptée par le lancement explicite du Goal P64-L09S.

## Date

2026-07-25.

## Carte liée

- P64-L09S-P — Préparation du Goal de stabilisation de bout en bout.

## Remplace partiellement

- ADR-0088, uniquement pour la compensation Z des réservations et la stratégie
  de finition ;
- ADR-0087, pour toute obligation de créer un corps porteur sous un plateau ;
- ADR-0069, pour l'ordre des stratégies de fermeture.

Le support dur par enveloppe XY, les cinq budgets, la séparation
calcul/finition, le plan minimal conservé et le cycle UI d'ADR-0088 restent
normatifs.

## Contexte

La gate humaine P64-L09R-V a révélé que le correctif 0.1.65 résout le cas avec
plateau en déformant le plan minimal :

- le plan sans plateau culmine à 52,8 mm ;
- avec un plateau de 1 mm, `container-018`, de 23,2 × 23,2 mm, est étiré de
  31,6 à 38,4 mm en Z ;
- son sommet passe ainsi de 52,8 à 59,6 mm ;
- une encoche de 1 mm lui est ajoutée alors que sa couverture du plateau n'est
  que de 0,75 % ;
- les 6,8 mm ajoutés représentent exactement 3 660,032 mm³ retirés du résiduel.

Ce comportement provient de la passe
`_apply_required_top_inset_z_compensation` : après un solve sans plateau, elle
choisit un conteneur qui chevauche la réservation et l'allonge jusqu'au sommet
de conception. Le worker SCIP couplé impose la même idée en exigeant au moins
un support qui atteigne ce sommet.

La finition observée échoue aussi à fermer le volume. Le finaliseur appelle
d'abord une croissance gloutonne par faces. Tant que cette fermeture de base
laisse un espace, les objectifs équilibré et proportionnel ne sont jamais
essayés. Le plan minimal est correctement conservé, mais l'interface annonce
quand même `Projet accepté` et le journal publie `finalized_plan_ready`.

Un ancien solveur, présent au commit `bd0e09b`, produisait des partitions
complètes par construction : lignes 2D, partage du surplus X/Y et hauteur de
rangement commune. Son comportement de remplissage était robuste et lisible,
mais son modèle sol/ligne/couche unique ne couvre pas les placements 3D
complexes désormais résolus par SCIP.

## Options

1. Conserver le correctif 0.1.65 et améliorer seulement le choix du conteneur
   porteur ainsi que la croissance gloutonne.
2. Revenir à l'ancien solveur de partition pour retrouver une fermeture
   complète par construction.
3. Garder SCIP pour la faisabilité 3D minimale, traiter plateaux et livrets
   comme des réservations sans support artificiel, puis lancer un finaliseur
   global inspiré de la partition complète historique, avec volumes composites
   XY uniquement en repli borné.

## Décision

L'option 3 est proposée.

### 1. Le calcul minimal ne fabrique aucun support de plateau

Un plateau ou livret est un volume réservé et un ordre de retrait, pas une
demande d'allongement d'un conteneur.

Le calcul minimal doit :

1. résoudre les conteneurs à leurs enveloppes minimales ;
2. vérifier que l'épaisseur cumulée des plateaux/livrets et leur ordre tiennent
   dans la hauteur utile ;
3. vérifier qu'aucun corps minimal n'intersecte leur prisme réservé exact ;
4. si le premier incumbent intersecte une réservation localisée, réessayer avec
   ce prisme interdit en utilisant uniquement le temps restant ;
5. publier seulement un plan recertifié.

Il lui est interdit d'augmenter X, Y ou Z pour créer un porteur, de choisir un
conteneur arbitraire sous un plateau ou d'ajouter une encoche de finition.

Un espace libre entre le sommet des conteneurs minimaux et un plateau est
admissible. Le plan reste matérialisable. Un timeout sans plan certifié reste
`no_solution_within_budget`, jamais une preuve d'impossibilité.

### 2. La finition vise une fermeture globale exacte

Le domaine cible est tout le volume imprimable de la boîte après retrait :

- des jeux de boîte et entre corps déclarés ;
- des cavités d'assets ;
- des réservations plateaux/livrets et de leur retrait ;
- des prises et autres vides techniques explicitement certifiés ;
- de toute zone déclarée non imprimable par une règle produit.

Chaque cellule restante doit appartenir exactement une fois à un conteneur.
Aucun chevauchement et aucun vide imprimable oublié ne sont acceptés.

La première stratégie est une fermeture rectangulaire globale :

1. construire une décomposition orthogonale bornée depuis les faces du plan
   minimal, de la boîte et des réservations ;
2. énumérer pour chaque conteneur des enveloppes rectangulaires finales qui
   contiennent son enveloppe minimale et respectent ses axes ;
3. choisir exactement une enveloppe par conteneur ;
4. couvrir chaque cellule imprimable exactement une fois ;
5. recertifier le plan complet.

La sélection est lexicographique :

1. résiduel imprimable nul ;
2. aucune violation de contrainte ;
3. écart minimal entre les volumes ajoutés ;
4. écart minimal entre les ratios de croissance ;
5. déformation maximale et nombre d'axes modifiés minimaux ;
6. départage déterministe par identités stables.

La fermeture ne peut donc pas être déclarée réussie avant d'être complète.

### 3. Les volumes adaptatifs sont un repli composite, jamais des cales

Si aucune fermeture rectangulaire complète n'est trouvée dans la partie de
budget prévue, la finition peut attribuer des cellules résiduelles sous forme
d'annexes orthogonales à un conteneur voisin.

Une annexe admissible :

- appartient à un seul conteneur propriétaire ;
- partage avec lui une vraie face verticale en X ou Y ;
- possède le même bas Z que la partie adjacente du propriétaire ;
- forme avec lui un unique corps connexe après union ;
- ne tient jamais uniquement par une face horizontale, une arête ou un point ;
- ne déplace ni ne réduit la cavité d'asset ;
- préserve jeux, réservations, prises et retrait.

Le certificat minimise d'abord le nombre d'annexes, puis leur nombre de faces et
leur volume, avant de reprendre l'objectif d'équilibre. Ces annexes ne sont ni
des corps utilisateur supplémentaires, ni des micro-conteneurs, ni des cales.

Si une cellule ne peut être attribuée selon ces règles, la finition échoue
honnêtement et le plan minimal reste courant et matérialisable.

### 4. Les encoches de plateau appartiennent à la finition

Une encoche est créée uniquement sur un corps final qui :

- atteint réellement le plan du plateau ;
- chevauche son empreinte exacte ;
- conserve fond, parois et cavités ;
- respecte l'épaisseur et l'ordre de tous les plateaux/livrets concernés.

Un corps minimal n'est jamais allongé pour recevoir cette encoche. Un corps qui
n'atteint pas le plateau n'en reçoit aucune.

### 5. La matérialisation unit les composites

Le CAD IR représente explicitement le corps principal, ses annexes et leur union.
Fusion effectue l'union sur le thread autorisé, puis les cavités et encoches
certifiées. Un conteneur final reste un seul composant utilisateur.

Un échec d'union, une annexe déconnectée ou une différence entre certificat,
CAD IR et scène interdit la publication du plan final et préserve la dernière
scène valide.

### 6. L'interface ne transforme plus un échec en succès

`Finaliser` n'est un succès que si un `finalized_plan` courant et recertifié est
publié. Sinon l'interface affiche la cause réelle : timeout, résiduel restant,
certificat rejeté, résultat obsolète ou erreur.

Le message générique `Projet accepté` et le stop reason
`finalized_plan_ready` sont interdits lorsque la finition n'a rien publié.

Les trois actions possèdent une couleur de base distincte :

- `Calculer` : bleu ;
- `Finaliser` : orange ou violet ;
- `Matérialiser` : vert.

L'état désactivé reste visiblement grisé sans supprimer cette hiérarchie.

### 7. Conserver le principe historique sans restaurer ses limites

Le principe repris de `partition_solver.py` est « fermeture complète par
construction puis répartition équitable ». Son solveur de lignes 2D et sa
hauteur uniforme ne redeviennent pas le moteur global.

SCIP reste propriétaire de la faisabilité complexe X/Y/Z. Le nouveau finaliseur
travaille après ce plan minimal et ne peut déplacer un conteneur ou changer une
variante que si une mission ultérieure l'autorise explicitement.

### 8. Gate d'acceptation de l'architecture

Le lancement explicite du Goal P64-L09S par Thomas accepte cette ADR et le
premier périmètre borné des annexes composites décrit ci-dessus. Aucune autre
intervention humaine n'est requise entre P64-L09S-A et P64-L09S-F tant que ce
périmètre, les tolérances, les valeurs physiques et les mécanismes ne changent
pas.

P64-L09S-V reste une gate Fusion humaine obligatoire. Aucune impression n'est
validée implicitement.

## Conséquences

- P64-L09R-V 0.1.65 devient un KO humain, pas une gate à reprendre.
- Le correctif de rafraîchissement du budget reste acquis.
- La compensation Z de P64-L09R-B/C1 devient une dette à retirer.
- Le finaliseur actuel reste une preuve historique, mais ne peut plus revendiquer
  une finition complète.
- Le modèle composite est introduit seulement pour des annexes XY de fermeture,
  avec certificat et union CAD ; il n'ouvre pas les formes P45 générales.
- La complexité algorithmique augmente. Elle est bornée par la grille de faces,
  les deadlines existantes, une recherche progressive et un résultat négatif
  honnête.

## Alternatives refusées

- Choisir un « meilleur » conteneur porteur : la règle produit elle-même est
  incorrecte.
- Étirer tous les conteneurs jusqu'au plateau : cela détruit le caractère minimal
  et déplace la finition dans le calcul.
- Continuer la croissance gloutonne jusqu'au timeout : elle ne prouve ni fermeture
  complète ni équilibre.
- Revenir entièrement au solveur P57 : il perd les cas 3D complexes acquis.
- Créer des cales ou corps visibles automatiques : contraire au modèle produit.
- Autoriser une annexe Z seule : corps peu compréhensible et liaison mécanique
  insuffisante.

## Suivi

Le runbook `docs/P64_L09S_END_TO_END_GOAL_RUNBOOK.md` fixe les missions
atomiques, les preuves et le prompt du futur Goal.
