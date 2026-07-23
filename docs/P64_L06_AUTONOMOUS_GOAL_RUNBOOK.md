# P64-L06 — Runbook de campagne autonome Goal

## 1. Rôle et statut

Ce document est le contrat d'exécution du futur Goal P64-L06. Il complète
`P64_L06_SOLVER_BENCHMARK_CAMPAIGN.md` sans modifier le runtime.

Statut courant :

- `ready-for-handoff` pour la préparation ;
- `goal-launch-blocked-by-P64-L05V-R1-human-recapture` pour l'exécution ;
- `fusion-validated: false` ;
- `print-validated: false`.

Le Goal ne doit pas commencer L06A tant que les deux recaptures R1 postérieures à
l'installation du commit `e817432` ne sont pas disponibles. La préparation du
runbook n'est ni une levée de gate, ni une autorisation d'installer une
dépendance externe.

## 2. Résultat attendu du premier Goal

Le premier Goal doit, dans l'ordre :

1. vérifier et anonymiser la paire R1, puis la rejouer sans changer le solveur ;
2. construire un corpus T0/T1 stratifié avec oracles explicites ;
3. livrer un petit oracle exact interne sans dépendance et une interface
   d'adapter offline ;
4. exécuter les tiers `ci` et `extended`, puis `soak` seulement si utile ;
5. classer les lacunes et sélectionner une seule hypothèse algorithmique ;
6. intégrer au maximum une amélioration atomique qui passe toutes les gates ;
7. produire un rapport honnête même si aucune amélioration n'est intégrable.

Une absence de candidat gagnant est une conclusion valide. Le Goal ne doit
jamais modifier le solveur uniquement pour produire un diff.

## 3. Préflight bloquant

Le futur agent commence par :

1. lire `AGENTS.md`, le pilotage court, ce runbook, le programme L06, ADR-0068
   et ADR-0079 ;
2. vérifier `git status --short --branch`, `HEAD`, la branche, `origin/main` et
   `HEAD...origin/main` ;
3. travailler dans un nouveau worktree sur une branche `codex/` créée depuis
   `origin/main` ;
4. vérifier que le worktree source et tous les autres worktrees restent
   intacts ;
5. vérifier les deux derniers bundles R1 attendus dans le répertoire local
   `Documents/BGIG/projects/solver-cases`.

La paire R1 est acceptable seulement si :

- chaque bundle passe `validate_solver_case_bundle` ;
- les captures sont postérieures à l'installation R1 ;
- le premier bundle conserve
  `staged_calculation.global_void_reuse.status = global_solve_required`, sa
  raison d'arrêt et ses compteurs exacts ;
- son `minimal_layout` est `stale` ;
- le second bundle porte le même projet normalisé et le même digest de projet ;
- le second bundle observe le calcul global frais puis
  `no_solution_within_budget`, sans cache négatif ;
- aucun fichier personnel n'est écrit, renommé ou déplacé.

Si une de ces conditions manque, le Goal s'arrête avec la différence exacte. Il
ne fabrique pas de substitut synthétique et n'ouvre pas L06B.

## 4. Enveloppe globale

| Ressource | Limite du premier Goal |
| --- | ---: |
| Durée totale | 36 h maximum |
| Artefacts locaux | 2 Gio maximum |
| Répertoire temporaire | `.codex-work/p64-l06/<run-id>/` |
| Workers fonctionnels | 2 maximum, cas indépendants uniquement |
| Mesures de vitesse | 1 worker, machine et charge consignées |
| Améliorations intégrées | 1 maximum |
| Comparateurs externes | 0 par défaut ; 1 maximum si déjà autorisé |
| Formes | T0/T1 seulement |

Les 36 h sont un plafond de sécurité, pas une durée à consommer. L'objectif
central reste une clôture en 12 à 24 h. Les deux workers éventuels appartiennent
au runner de cas ; les appels shell Windows restent strictement sériels. Toute
commande longue utilise le wrapper gardé, un heartbeat de 10 s et un timeout
métier explicite.

Le répertoire `.codex-work` contient checkpoints et rapports volumineux non
versionnés. Il est supprimé après archivage des preuves utiles et vérification de
la reprise. Aucun chemin local ne doit apparaître dans un artefact versionné.

## 5. Budgets par phase

| Phase | Plafond | Sortie obligatoire |
| --- | ---: | --- |
| Préflight et L06A | 1 h 30 | paire validée, cas anonymisé, replay et classification |
| L06B | 4 h | générateur, splits, oracles, corpus et tests |
| L06C interne | 3 h | interface d'adapter et petit oracle exact interne |
| Baseline + `ci` | 1 h | rapport fonctionnel stable |
| L06D `extended` | 5 h | résultats découverte/réglage/holdout |
| L06D `soak` optionnel | 8 h | exploration ciblée, jamais obligatoire |
| L06E | 8 h | un candidat A/B ou un résultat négatif |
| Régression, documentation et Git | 3 h 30 | preuves, suite, intégration et SHA distant |

Un dépassement de phase écrit un checkpoint puis choisit entre réduire le tier
suivant ou s'arrêter. Il n'augmente jamais un budget solveur public.

## 6. Matrice T0/T1 utile

Le corpus ne réalise pas le produit cartésien complet. Il combine couverture par
paires, cas construits et adversaires ciblés.

### Axes locaux P45

- contenus par conteneur : `1, 2, 4, 8, 16, 32` ;
- variantes certifiées retenues : `1, 2, 4, 8` ;
- contenus homogènes, hétérogènes et presque égaux ;
- enveloppe ample, dense et quasi saturée ;
- un seul arrangement évident ou plusieurs variantes concurrentes.

### Axes globaux P64

- groupes conteneurs : `2, 4, 8, 12, 18, 30, 50` ;
- étages : `1, 2, 3` ;
- rotations Z permises ou non ;
- dimensions homogènes, hétérogènes et quasi symétriques ;
- réservations, appuis et ordres de retrait absents ou contraignants ;
- reconstruction froide, witness compatible, witness incompatible ;
- modification interne, nouveau conteneur et reconstruction complète.

### Familles obligatoires

| Famille | Composition | Propriété principalement stressée |
| --- | --- | --- |
| A | nombreux conteneurs, un contenu chacun | placement global P64 |
| B | peu de conteneurs, nombreux contenus | frontières et variantes P45 |
| C | nombreux conteneurs, nombreux contenus | interaction P45/P64 |
| D | mélange dense, simple et hétérogène | sélection du portefeuille Auto |
| E | modification incrémentale puis reconstruction froide | continuité et profondeur |

La densité est décrite par plusieurs faits séparés : charge volumique, marges
sur chaque axe, fragmentation des espaces et nombre de placements admissibles.
Un pourcentage de volume seul ne sert jamais d'oracle.

## 7. Construction et séparation des cas

Les cas générés reçoivent un seed explicite et un rôle stable dérivé de leur
digest :

| Split | Cible initiale | Utilisation |
| --- | ---: | --- |
| `regression` | corpus historique + paire R1 | interdiction de perdre un acquis |
| `discovery` | 60 à 80 cas | identifier les familles de lacunes |
| `tuning` | 60 à 80 cas | choisir les paramètres internes d'une hypothèse |
| `holdout` | 60 à 80 cas | accepter ou refuser le candidat final |
| `soak` | 500 à 2 000 seeds ciblés | exploration facultative |

Le `holdout` reste fermé jusqu'à la sélection d'une seule hypothèse. Un candidat
consulté sur le holdout ne peut plus être réglé puis retesté comme s'il était
neuf ; toute nouvelle itération exige un nouveau split versionné.

Les oracles sont étiquetés :

- `feasible_by_construction` : placements source reconstruits et certifiés ;
- `proven_impossible_small_exact` : petit oracle exact exhaustif dans son modèle ;
- `known_certified_witness` : plan BGIG recertifié ;
- `bounded_unknown` : aucune preuve après budget ;
- `invalid_input` : contrat d'entrée rejeté.

Un cas faisable par construction conserve son placement oracle séparément du
solveur testé. Le solveur ne reçoit pas ce placement comme warm start sauf dans
une expérience explicitement étiquetée.

## 8. Comparaison efficace

La campagne utilise un tournoi progressif :

1. une passe `ci` élimine toute régression fonctionnelle ;
2. `discovery` classe les lacunes par famille et mesure les lanes gagnantes ;
3. trois hypothèses maximum passent dans `tuning` ;
4. une seule hypothèse est sélectionnée avant ouverture du `holdout` ;
5. `soak` n'est lancé que si le holdout passe et si une incertitude précise
   demeure ;
6. L06E implémente seulement l'hypothèse retenue.

Les comparaisons de vitesse utilisent les mêmes digests, la même machine et un
ordre alterné baseline/candidat. Les runs froids et chauds restent séparés. Une
différence de temps ne devient une revendication que si elle est répétée et
qu'aucune vérité fonctionnelle, qualité ou stabilité ne régresse.

La sortie conserve un vecteur de caractéristiques déterministe par cas :
cardinalité, variantes, étages, symétrie, charge, fragmentation, réservations,
warm start et lane gagnante. Ces données peuvent proposer plus tard un routage
Auto explicite. Aucun modèle opaque n'est entraîné dans ce Goal.

## 9. Oracles et comparateurs

L06C commence par un petit oracle exact interne en bibliothèque standard. Son
périmètre est volontairement réduit aux instances T0 qu'il peut terminer sous un
cap explicite. Il sert à prouver de petits cas, pas à remplacer le solveur
produit.

L'interface d'adapter offline doit pouvoir accueillir :

1. l'oracle exact interne ;
2. PackingSolver `box` ;
3. LAFF ou brute force du projet `3d-bin-container-packing` ;
4. CP-SAT si une ADR et un GO de dépendance sont acceptés plus tard.

PackingSolver, Java/LAFF et CP-SAT ne sont pas installés automatiquement. Un
exécutable déjà disponible peut être utilisé en lecture contrôlée après
identification de sa version et de sa licence. Toute sortie externe repasse par
le certificat BGIG ; les contraintes non représentées sont déclarées
`unsupported`, jamais ignorées.

L'indisponibilité d'un moteur externe ne bloque donc ni L06B, ni L06D, ni L06E.

## 10. Checkpoint et pause

Après chaque cas, le runner écrit atomiquement :

- `run_id`, SHA de base et branche ;
- digest du corpus et versions des producers ;
- phase, split et cas terminé ;
- budget consommé et budget restant ;
- digests des résultats et chemins relatifs ;
- PID enfant éventuel ;
- prochaine action exacte ;
- raison d'arrêt si la campagne s'interrompt.

Avant une pause demandée par Thomas :

1. ne plus lancer de nouveau cas ;
2. attendre ou arrêter coopérativement le cas courant ;
3. vérifier l'état de tout processus enfant ;
4. écrire puis relire le checkpoint ;
5. publier un résumé en français courant ;
6. seulement alors confirmer `safe_to_pause`.

À la reprise, l'agent vérifie Git, le digest du corpus, les fichiers du
checkpoint et l'absence de processus orphelin. Il ne rejoue pas un cas marqué
terminé sans expliquer pourquoi.

## 11. Missions et intégration

Chaque lot L06A à L06E reste une mission distincte :

1. branche dédiée depuis `origin/main` ;
2. changement borné ;
3. tests ciblés puis suite proportionnée au risque ;
4. documentation et preuve ;
5. commit atomique ;
6. fetch et contrôle de divergence ;
7. intégration directe dans `main` si non conflictuelle ;
8. push et vérification du SHA distant ;
9. nouvelle branche propre pour la mission suivante.

Le Goal ne conserve pas cinq missions non intégrées sur une seule branche.

## 12. Gate d'acceptation L06E

Le candidat final est accepté seulement si :

- aucune solution connue n'est perdue ;
- chaque plan retenu possède le certificat BGIG commun ;
- aucune qualité lexicographique ne régresse ;
- le préfixe Rapide/Normal/Approfondi et les budgets publics restent conformes ;
- les résultats fonctionnels sont stables sur répétition ;
- le `holdout` passe sans réglage postérieur ;
- la paire R1 progresse ou la lacune ciblée est objectivement améliorée ;
- les tests ciblés, la gate A/B L05D1 et la suite complète passent ;
- Ruff ciblé, `py_compile`, frontière `adsk` et `git diff --check` passent.

Un gain uniquement observé sur `tuning`, une fixture triviale ou le temps mur
bruité est refusé.

## 13. Arrêts obligatoires

Le Goal s'arrête sur :

- paire R1 absente, invalide ou incohérente ;
- régression fonctionnelle ;
- corpus ou checkpoint corrompu ;
- dépendance externe nécessaire mais non autorisée ;
- décision d'architecture ou comportement public non couvert ;
- conflit Git, divergence non triviale ou risque de perte de travail ;
- dépassement des 36 h ou des 2 Gio ;
- trois hypothèses `tuning` sans candidat acceptable ;
- tests rouges dont la correction sortirait de L06 ;
- demande de Thomas.

Il ne transforme jamais cet arrêt en réussite partielle silencieuse.

## 14. Livrables finaux

- cas R1 anonymisé et rapport de classification ;
- générateur T0/T1 et manifest versionné ;
- splits regression/discovery/tuning/holdout ;
- petit oracle exact et protocole d'adapter ;
- baseline et rapports de campagne ;
- tableau des familles de lacunes et lanes gagnantes ;
- rapport A/B du candidat ou décision de ne rien intégrer ;
- preuve de tests et SHAs intégrés ;
- backlog des hypothèses non retenues ;
- statut explicite de L06V, Fusion et impression.

Les rapports destinés à Thomas commencent par : ce qui fonctionne mieux, ce qui
reste refusé, le coût réel, et ce qui doit être observé dans Fusion.

## 15. Prompt `/goal` canonique

Dans la nouvelle tâche préparée pour P64-L06, Thomas peut lancer :

```text
/goal
Exécute P64-L06 selon docs/P64_L06_AUTONOMOUS_GOAL_RUNBOOK.md, pendant 36 h
maximum. Avance une mission atomique à la fois de L06A à L06E, avec tests,
preuve, commit et intégration dans main avant la suivante. Ne commence pas si
la paire R1 post-e817432 manque ou est incohérente. Sans nouveau GO, utilise
l'oracle exact interne et les composants déjà présents ; n'installe aucune
dépendance externe. Sépare regression, discovery, tuning et holdout ; garde le
holdout fermé jusqu'au choix d'une seule hypothèse. Recertifie chaque plan par
BGIG et arrête toute variante qui régresse fonctionnellement. Intègre au maximum
une amélioration algorithmique ciblée qui passe A/B, holdout et suite complète ;
sinon conclus honnêtement sans forcer de changement. Reste strictement en T0/T1,
préserve les budgets, deadlines, certificats, schémas, géométrie, Fusion, CAD,
finalisation, valeurs physiques et travaux étrangers. Checkpointe atomiquement,
reprends sans double exécution et rends compte en français courant.
```

Le lancement de ce prompt constitue le GO d'exécution. Le futur agent ne doit
pas demander une seconde autorisation de démarrage ; il s'arrête seulement sur
une gate réelle définie ci-dessus.
