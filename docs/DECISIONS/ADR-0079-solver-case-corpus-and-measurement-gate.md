# ADR-0079 - Corpus solveur versionne et gate de comparaison fonctionnelle

## Statut

Acceptee le 2026-07-22 dans P64-L05D1, apres SolverCaseBundle L05B et witness
certifie L05C automated-validated.

Cette decision cree les artefacts de developpement necessaires aux futures
optimisations. Elle ne modifie aucune lane dans L05D1 et ne vaut ni validation
Fusion, ni validation d'impression.

## Contexte

Les cas limites reels montrent deux ecarts distincts :

- un plan connu peut etre conserve incrementiellement sans etre reconstruit par
  le solveur depuis zero ;
- les temps observes varient selon machine et charge, alors que statut,
  certificat, lanes, digests et qualite doivent rester comparables.

Un journal libre ou une collection de projets sans expectations ne suffit pas.
A l'inverse, figer un temps mur comme preuve deterministe produirait des faux
regressions. Une optimisation appliquee directement apres un seul cas humain
risquerait de perdre des solutions deja certifiees ailleurs.

## Options

### A - Optimiser directement sur le dernier cas humain

Rapide a essayer, mais aucune non-regression globale et aucun historique
fonctionnel stable.

### B - Enregistrer uniquement des temps mur

Facile a tracer, mais non reproductible et incapable de distinguer gain de
capacite, changement de plan et bruit de machine.

### C - Corpus exact, replay borne et comparaison fonctionnelle prioritaire

Chaque cas porte projet normalise, effort, attentes, prefixe de lanes et baseline.
Le replay separe faits fonctionnels deterministes et echantillons de temps. Une
gate A/B refuse toujours une regression fonctionnelle avant de regarder la
performance.

## Decision

Retenir l'option C.

Deux schemas sont crees :

- `bgig.solver_case_corpus.v1` pour le manifest portable ;
- `bgig.solver_case_replay.v1` pour un run courant ;
- `bgig.solver_case_comparison.v1` pour la gate A/B.

Le corpus initial contient sept fixtures anonymisees : cinq cas CI et deux cas
etendus. Il fige deux solutions certifiees et cinq limites
`no_solution_within_budget`. Ce statut est une baseline, jamais une preuve
d'impossibilite ; une transition vers `solution_found` est une amelioration
admise.

Le manifest ne contient aucun chemin local, evenement d'interaction, contexte
client ou projet personnel. Son digest couvre chaque projet, source, reglage,
expectation et baseline.

Un SolverCaseBundle peut etre importe ephemerement seulement apres validation du
digest global et de tous ses digests de composants. Le corpus extrait projet,
reglages, statut observe et identite du bundle, mais exclut trace et contexte
client. Aucun import automatique vers le depot n'existe.

Le replay execute uniquement le solveur minimal explicite. Il produit :

- statut, raison d'arret, certificat et digests ;
- prefixe et rapports de lanes, etats, essais et candidats ;
- axes de qualite lexicographiques ;
- un `functional_digest` qui exclut tout temps mur ;
- des echantillons de performance clairement marques non normatifs.

La comparaison A/B refuse : perte d'une solution connue, certificat absent,
changement de prefixe, qualite certifiee moins bonne ou expectation du corpus
violee. Les temps ne peuvent jamais compenser ces regressions. Sans amelioration
fonctionnelle, un candidat doit rester dans la tolerance de performance explicite.

## Workflow

1. capturer explicitement un cas dans Fusion avec le bouton DEV ;
2. rejouer le bundle localement sans l'ajouter au depot ;
3. anonymiser et faire relire le cas avant toute promotion dans le corpus ;
4. produire une baseline avant modification ;
5. executer le candidat sur le meme digest de corpus et les memes tiers ;
6. comparer les deux rapports ;
7. integrer seulement si la gate fonctionnelle passe et si le gain est mesure.

Les scripts canoniques sont :

- `scripts/solver/replay_solver_case_corpus.py` ;
- `scripts/solver/compare_solver_case_replays.py`.

## Invariants

- aucun auto-apprentissage ni auto-edition de code ;
- aucune scene, finalisation ou CAD declenchee ;
- aucun chemin ou projet personnel dans le corpus versionne ;
- aucun temps mur dans le digest fonctionnel ;
- aucun statut `proven_impossible` deduit d'un budget heuristique ;
- aucune modification des certificats, budgets publics ou deadline Deep ;
- le cas dense 11 x 34 reste sans nouvelle revendication.

## Consequences

### Positives

- chaque changement de lane devient comparable et reversible ;
- les cas humains peuvent etre exploites sans exposer leur trace ni les committer
  automatiquement ;
- capacite, qualite et vitesse ne sont plus melangees ;
- une optimisation rapide mais regressante est automatiquement refusee.

### Limites

- le corpus initial est petit et surtout mecanique ;
- les temps observes ne sont pas des seuils produit ;
- aucun placement connu du projet personnel n'est encore disponible sous forme
  de bundle ou witness ;
- L05D1 ne modifie pas le solveur ; L05D2 porte la premiere optimisation A/B.

## Alternatives refusees

- committer automatiquement les captures Fusion ;
- conserver chemins, valeurs d'interaction ou contexte client dans le corpus ;
- accepter un gain de temps qui perd une solution ou degrade son classement ;
- transformer cinq echecs bornes en impossibilites ;
- ajuster silencieusement les budgets pour faire passer un benchmark.

## Validation

Contrat : `docs/P64_L05D1_SOLVER_CORPUS_CONTRACT.md`.
Preuve : `docs/P64_L05D1_SOLVER_CORPUS_EVIDENCE.md`.

fusion-validated: false. print-validated: false.
