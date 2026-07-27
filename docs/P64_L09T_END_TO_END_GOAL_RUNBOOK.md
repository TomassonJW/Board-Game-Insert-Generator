# P64-L09T — Runbook du Goal de stabilisation hybride

## 1. Rôle et statut

- Statut : `ready-for-delegated-goal-launch`.
- Décision : ADR-0093 acceptée par Thomas le 2026-07-27.
- Entrée : KO humain 0.1.69 et cas locaux `CasLimite01+` / `CasLimite02+`.
- Sortie autonome : nouvelle candidate Fusion installée et gate humaine prête.
- Sortie finale : verdict humain P64-L09T-V documenté.
- Modèle demandé : `gpt-5.6-sol`, raisonnement `xhigh`.

Le Goal est explicitement autorisé à enchaîner les missions A à G, une seule à
la fois. Chaque mission doit être testée, documentée, committée, intégrée dans
`main` et poussée avant la suivante.

## 2. Objectif exact du Goal

> Livrer un parcours BGIG robuste où toute édition exige un calcul explicite,
> où les couches basses et les plateaux/livrets automatiques participent au
> même calcul certifié, et où la finition hybride étend les corps puis soude des
> annexes au résiduel sans déplacer les cavités, avec certificat, CAD et
> diagnostics concordants.

Le parcours cible est :

```text
édition
  -> plans dérivés obsolètes
  -> Calculer explicitement
  -> plan minimal certifié
       corps + cavités + poses des réservations figés
  -> Finaliser
       extensions rectangulaires
       puis annexes soudées sur résiduel
  -> certificat composite réel et résiduel nul
  -> Matérialiser
       unions avant cavités et coupes
  -> gate Fusion humaine
```

## 3. Préflight bloquant

Avant toute mutation produit :

1. lire `AGENTS.md`, `docs/PILOTAGE_CURRENT.md`,
   `docs/NEXT_ACTIONS.md` et `docs/HUMAN_GATES.md` ;
2. lire ADR-0089, ADR-0092, ADR-0093, la preuve KO 0.1.69 et ce runbook ;
3. lire les sources et tests directement concernés par la mission active ;
4. vérifier `git status --short --branch`, `HEAD`, `origin/main`,
   `HEAD...origin/main` et `git worktree list --porcelain` ;
5. préserver tous les worktrees étrangers et ne jamais modifier celui qui
   possède localement `main` ;
6. confirmer que la mission commence depuis le SHA exact de `origin/main` ;
7. créer une branche `codex/` dédiée à la seule mission active.

Une divergence non triviale, un travail étranger menacé, un conflit ou une
preuve obligatoire impossible bloque la mutation. Un échec algorithmique borné
n'est pas une preuve d'impossibilité.

## 4. Règles communes

- Une seule mission P64-L09T active à la fois.
- Aucun GO supplémentaire entre A et G.
- Aucun benchmark, tuning ou holdout solveur.
- Aucun secret, projet personnel ou journal local versionné.
- Aucun changement de valeur physique ou de tolérance par défaut.
- Aucun corps plateau/livret utilisateur.
- Aucun `adsk` dans le cœur Python.
- Aucun package Fusion installé avant G.
- Toute édition géométrique rend minimal et final obsolètes.
- Tout échec conserve le dernier plan minimal certifié compatible.
- `fusion-validated=false` et `print-validated=false` avant la gate humaine.

Les projets locaux `CasLimite01+` et `CasLimite02+` peuvent être rejoués en
lecture seule. Le dépôt reçoit seulement des fixtures publiques ou anonymisées
qui reproduisent leurs mécanismes.

## 5. Invariants géométriques

### Plan minimal

- minima canoniques et axes Fixe immuables ;
- cavités et variantes locales certifiées ;
- poses monde des conteneurs figées après calcul ;
- réservations virtuelles au plus haut et poses X/Y certifiées ;
- enveloppe de paroi minimale entre cavité et réservation ;
- aucune encoche ni annexe dans le minimal.

### Priorité de placement

- faisabilité et certificats d'abord ;
- plans complets avec moins de conteneurs élevés préférés ;
- somme des bases Z, volume élevé et gêne sous réservation minimisés ;
- compacité et petit nombre de piles seulement ensuite ;
- aucune règle gloutonne locale ne peut bloquer une solution globale.

### Finition hybride

- cœur minimal et cavités immuables ;
- extension rectangulaire tentée en premier ;
- résiduel restant découpé et attribué directement ;
- annexe connectée par vraie face verticale X/Y et bas Z commun ;
- interface interne annexe/propriétaire sans jeu ;
- tous les jeux externes conservés ;
- aucune liaison flottante, Z seule, arête ou point ;
- chaque cellule imprimable appartient exactement une fois ;
- résiduel nul avant succès.

### Matérialisation

- un composant utilisateur par conteneur final ;
- cœur puis annexes unis ;
- cavités figées appliquées après union ;
- coupes plateau/livret appliquées ensuite ;
- scène précédente conservée sur erreur ;
- même identité entre plan, certificat, CAD IR et scène.

## 6. P64-L09T-A — Recalcul explicite et suppression des réutilisations

### Objectif

Supprimer les deux chemins automatiques qui republient un plan après une
édition, tout en conservant le socle d'identité et d'invalidation.

### Travail

- retirer la réutilisation locale à enveloppe fixe du cycle automatique ;
- retirer l'insertion automatique d'un nouveau conteneur dans le vide global ;
- supprimer statuts, messages et bruit visuel associés du parcours normal ;
- après édition, marquer minimal, final et scène comme obsolètes ;
- conserver digests, dépendances, cache exact sur calcul explicite, witness
  compatible et rejet stale ;
- retirer les chemins devenus morts seulement après inventaire des appels.

### Preuves

- ajout d'un contenu : aucun plan minimal courant sans clic Calculer ;
- ajout d'un conteneur : même résultat ;
- modification de boîte, jeux ou réservation : invalidation correcte ;
- projet strictement identique puis Calculer : cache positif exact encore
  admissible ;
- aucun message « intégré localement » dans l'interface ou le journal produit.

## 7. P64-L09T-B — Diagnostics d'arrêt anticipé

### Objectif

Expliquer une fin avant le plafond sans inventer d'impossibilité.

### Travail

- transporter phase, temps écoulé, plafond, raison et compteurs utiles ;
- traduire les raisons rectangulaires, composites et certificats ;
- distinguer succès, impossible prouvé, stratégie épuisée, deadline et stale ;
- garder les détails techniques repliés ;
- rendre le message utilisateur immédiatement compréhensible.

### Preuves

- arrêt anticipé par prérequis absent ;
- rejet de certificat ;
- deadline atteinte ;
- impossible prouvé distinct ;
- succès rapide ;
- aucun cas borné inconnu présenté comme impossible.

## 8. P64-L09T-C — Pose automatique des réservations et parois minimales

### Objectif

Faire des poses X/Y des plateaux et livrets une décision du calcul.

### Travail

- remplacer `auto_center` comme unique placement automatique par une recherche
  bornée de poses X/Y ;
- placer conjointement plusieurs réservations, côte à côte ou empilées selon
  leur chevauchement et leur ordre ;
- conserver leur Z au plus haut niveau admissible ;
- retirer les origines X/Y de l'interface normale ;
- migrer les anciens projets vers le mode automatique sans réécriture avant
  sauvegarde explicite ;
- ajouter l'enveloppe de matière minimale autour de chaque cavité ;
- refuser toute pose ou coupe laissant une paroi trop mince ;
- inclure les poses résolues dans le digest minimal.

### Preuves

- plateau seul dont le centre est impossible mais une pose latérale est valide ;
- plateau et livret côte à côte ;
- éléments plats chevauchés avec ordre vertical déterministe ;
- ancienne origine explicite migrée et plans rendus obsolètes ;
- cavité proche : autre pose trouvée ou échec honnête ;
- aucune réduction ou translation silencieuse de cavité.

## 9. P64-L09T-D — Priorité globale aux couches basses

### Objectif

Corriger la préférence actuelle pour les piles compactes.

### Travail

- introduire un classement lexicographique des plans complets ;
- minimiser conteneurs élevés, somme des bases Z et volume élevé ;
- minimiser la hauteur gênante sous les réservations ;
- appliquer compacité et nombre de piles seulement après ces objectifs ;
- garder déterminisme, caps et certificat commun ;
- exposer les composantes du classement dans les diagnostics.

### Preuves

- fixture où tout tient au sol : aucune pile ;
- fixture où une pile est nécessaire : solution conservée ;
- fixture où un choix glouton au sol bloque : meilleur plan complet retenu ;
- `CasLimite01+` ou équivalent anonymisé : amélioration mesurable de la
  répartition basse sans perdre la faisabilité ;
- mêmes entrées et budget contractuel : même identité fonctionnelle.

## 10. P64-L09T-E — Fermeture hybride réelle

### Objectif

Construire des annexes directement sur le résiduel que la fermeture
rectangulaire ne couvre pas.

### Travail

- conserver les extensions rectangulaires comme phase initiale ;
- ne plus exiger une partition brute complète avant le repli composite ;
- décomposer le résiduel selon les faces du minimal, des extensions, de la
  boîte et des réservations ;
- énumérer les propriétaires adjacents admissibles ;
- annuler le jeu uniquement à la couture interne avec le propriétaire ;
- préserver tous les corridors de jeu externes ;
- choisir les annexes par connexité, nombre, coins, aire de couture, équilibre,
  plus longue face et identité stable ;
- refuser toute cellule sans propriétaire valide.

### Preuves

- trou intérieur fermé par annexe ;
- espace de bord fermé sans déplacer la cavité ;
- deux propriétaires possibles : décision déterministe et esthétique ;
- corridor de jeu externe préservé ;
- couture interne sans espace et union abstraite positive ;
- liaison Z seule, flottante, par arête ou point refusée ;
- timeout : minimal inchangé.

## 11. P64-L09T-F — Certificat composite et CAD fidèle

### Objectif

Certifier et matérialiser la géométrie réellement publiée.

### Travail

- certifier les corps composites, pas seulement la fermeture brute ;
- prouver cœur, annexes, coutures, parois, jeux, réservations et résiduel ;
- figer les cavités dans le repère du cœur minimal ;
- produire une CAD IR cœur + annexes + unions + cavités + coupes ;
- assurer une union Fusion robuste sans modifier l'enveloppe certifiée ;
- refuser la publication si certificat, CAD IR ou plan divergent ;
- enrichir les rejets persistés avec leur sous-code.

### Preuves

- `CasLimite01+` ou équivalent atteint un plan final certifié ;
- `CasLimite02+` ou équivalent ferme son trou central ;
- une annexe ne déplace aucune cavité ;
- paroi minimale entre cavité et plateau certifiée ;
- unions avant cavités et coupes ;
- un composant utilisateur par propriétaire ;
- `printable_residual_volume_mm3=0`.

## 12. P64-L09T-G — Durcissement, package et préparation de gate

### Objectif

Prouver le parcours complet et préparer la nouvelle observation Fusion.

### Matrice obligatoire

- smoke public ;
- `CasLimite01` et équivalent anonymisé de `CasLimite01+` ;
- `CasLimite02` et équivalents isolés :
  ajout d'un contenu à jeux constants, jeux seuls, puis combinaison ;
- plateau décentré automatiquement ;
- plateau proche d'une cavité ;
- plan tout au sol et plan nécessitant une pile ;
- fermeture rectangulaire ;
- fermeture par annexe ;
- rejets, stale et arrêts anticipés.

### Exécution

1. tests ciblés par frontière ;
2. suite complète autorisée avec `PYTHONPATH=src` ;
3. vérification de l'absence d'import `adsk` dans le cœur ;
4. `git diff --check` ;
5. rejeu local exact des deux projets « + » sans les modifier ;
6. intégration dans `main` et vérification distante ;
7. fabrication d'une nouvelle candidate, initialement `0.1.70` ;
8. installation automatique par les scripts Fusion ;
9. vérification version, runtime, marqueurs, settings, fixtures et preflight ;
10. arrêt à P64-L09T-V.

Si plusieurs corrections intermédiaires exigent des packages distincts, seule
la dernière candidate vérifiée est autorisée pour la gate.

## 13. P64-L09T-V — Gate Fusion humaine

Codex prépare tout l'environnement. Thomas ne lance aucun script.

Thomas vérifie :

1. après une édition, aucun plan n'est réutilisé automatiquement ;
2. Calculer republie explicitement le minimal ;
3. les plateaux/livrets choisissent automatiquement leur position ;
4. les couches basses sont préférées lorsqu'un plan complet le permet ;
5. les parois entre cavités et encoches restent assez épaisses ;
6. `CasLimite01+` calcule, finalise et matérialise ;
7. `CasLimite02+` calcule, finalise et matérialise ;
8. les annexes sont soudées, sans jeu interne, mais gardent les jeux externes ;
9. les cavités ne se déplacent pas ;
10. un arrêt anticipé explique temps, plafond, phase et motif ;
11. jauge, composants, unions, coupes et résiduel sont conformes.

La gate ne valide aucune impression. Les cales séparées, séparateurs sans fond
et conteneurs générés ne font pas partie de cette observation.

## 14. Certificat final obligatoire

Le certificat porte au minimum :

- digest du projet et du plan minimal ;
- minima, axes, variantes et poses monde ;
- poses et ordre des réservations ;
- enveloppes de paroi autour des cavités ;
- domaine imprimable et vides techniques ;
- extensions rectangulaires ;
- cellules résiduelles et propriétaire ;
- coutures internes sans jeu ;
- jeux externes ;
- connexité et unions ;
- cavités et coupes ;
- résiduel final nul ;
- méthode, budget contractuel, temps, phase et arrêt ;
- digest du plan final et du CAD IR.

## 15. Horizons explicitement hors scope

P64-L09T n'implémente pas :

- cales solides séparées ;
- séparateurs sans fond ;
- conteneurs de finition générés ;
- volumes flottants ou annexes liées seulement en Z ;
- nouvelles valeurs de tolérance ;
- formes P45 nouvelles ;
- couvercles ou mécanismes ;
- validation d'impression.

Ces capacités sont conservées dans le programme futur P64-F03.

## 16. Arrêts honnêtes

Le Goal s'arrête seulement pour :

- conflit Git ou risque de perte de travail étranger ;
- protection de branche ou authentification bloquante ;
- échec non réparable dans la mission atomique ;
- nécessité démontrée de changer une valeur physique, une tolérance ou le
  périmètre composite accepté ;
- preuve automatisée fidèle impossible ;
- gate humaine P64-L09T-V.

Un résultat borné négatif est une sortie honnête de test, mais ne clôt pas le
Goal si les parcours positifs exigés restent absents.

## 17. Clôture Git de chaque mission

```text
status
-> tests ciblés
-> suite pertinente puis complète
-> git diff --check
-> revue du diff
-> commit atomique
-> fetch origin --prune
-> vérification origin/main
-> rebase seulement si nécessaire et sans conflit
-> push fast-forward HEAD:main
-> vérification du SHA distant
-> suppression de la branche intégrée
-> nouvelle branche depuis origin/main pour la mission suivante
```

Le worktree étranger qui possède `main` n'est jamais modifié.

## 18. Prompt Goal canonique

```text
Crée et exécute le Goal P64-L09T décrit par
docs/P64_L09T_END_TO_END_GOAL_RUNBOOK.md.

Objectif : livrer le cycle explicite et la finition hybride certifiée acceptés
par ADR-0093 : aucune réutilisation automatique après édition, réservations
plateaux/livrets automatiquement placées, priorité globale aux couches basses,
paroi minimale préservée autour des cavités, extensions rectangulaires puis
annexes soudées sans jeu interne, jeux externes conservés, cavités figées,
certificat composite réel, CAD fidèle, diagnostics d'arrêt honnêtes et
préparation de la gate Fusion P64-L09T-V.

Travaille une mission à la fois, A à G. Après chaque mission : tests,
documentation, commit, intégration directe dans main, push et vérification du
SHA distant. Ne redemande aucun GO dans ce périmètre. Préserve tous les
worktrees étrangers. N'exécute aucun benchmark ou holdout. Ne change aucune
valeur physique ou tolérance. N'implémente pas les trois familles P64-F03
différées. Installe Fusion seulement pendant G et arrête-toi à V pour
l'observation humaine de Thomas.
```

## 19. Modèle conseillé

- Modèle : `gpt-5.6-sol`.
- Raisonnement : `xhigh` (« très élevé »).
- Justification : le Goal croise recherche combinatoire, géométrie composite,
  certificat, migration de projet, CAD IR, Fusion et validation longue.
- Option économique : `gpt-5.6-terra` en `high` seulement pour une mission
  documentaire ou UI strictement isolée, avec relecture par `gpt-5.6-sol`.
