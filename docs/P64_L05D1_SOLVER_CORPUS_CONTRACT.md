# P64-L05D1 - Contrat corpus solveur et gate A/B

## Statut et objectif

P64-L05D1 est le premier sous-lot de P64-L05D. Il transforme les fixtures et
SolverCaseBundle explicites en cas rejouables avant toute modification des
lanes. Il fournit une baseline fonctionnelle stable et une mesure de temps
non normative.

Ce lot ne modifie ni solveur, ni portefeuille, ni classement, ni budget, ni
deadline Deep. Il ne lance aucune scene Fusion, finalisation ou
materialisation.

## Artefacts versionnes

- manifest : `bgig.solver_case_corpus.v1` ;
- rapport de replay : `bgig.solver_case_replay.v1` ;
- rapport de comparaison : `bgig.solver_case_comparison.v1`.

Le manifest contient des projets normalises anonymises, un effort explicite,
une methode documentee, un tiers `ci` ou `extended`, les lanes attendues,
les statuts acceptes et une baseline fonctionnelle. Son digest couvre
l'integralite de ces faits.

Le corpus initial contient cinq cas CI et deux cas etendus. Un echec borne peut
devenir une solution certifiee ; il ne devient jamais une preuve
d'impossibilite.

## Import d'un SolverCaseBundle

L'import reste explicite et ephemere. Il doit :

1. valider le digest global du bundle ;
2. valider les digests du projet, de l'etat solveur, de l'analyse locale, des
   frontieres et de la trace ;
3. renormaliser le projet et verifier son digest ;
4. conserver identite de capture, projet, effort, methode et statut observe ;
5. exclure trace d'interaction et contexte client du cas rejouable.

Aucun bundle n'est promu automatiquement dans le depot. Une promotion exige
anonymisation et revue du diff.

## Replay

Le replay appelle uniquement le solveur d'agencement minimal avec l'effort du
cas. La methode est conservee comme metadonnee pour les extensions futures ;
L05D1 rejoue le parcours minimal P64.

La partition fonctionnelle observe :

- statut et raison d'arret ;
- digest de plan et de placements ;
- certificat et axes de classement ;
- prefixe exact et telemetrie des lanes ;
- nombres de candidats avant et apres deduplication.

Le `functional_digest` exclut tous les temps mur. Plusieurs repetitions doivent
produire la meme partition fonctionnelle, sinon le replay echoue ferme. Les cas
Deep dependants d'une deadline murale ne sont donc promus qu'apres preuve de
stabilite ; le corpus initial utilise Rapide et Normal.

## Gate A/B

Baseline et candidat doivent avoir le meme digest de corpus, les memes tiers et
les memes cas. La gate refuse avant toute consideration de vitesse :

- perte d'une solution connue ;
- solution sans certificat ;
- changement du prefixe de lanes ;
- degradation lexicographique d'un plan certifie ;
- violation d'une attente du corpus.

Une transition `no_solution_within_budget -> solution_found` est une
amelioration. Sans amelioration fonctionnelle, le candidat doit rester dans la
tolerance de temps explicite, 10 % par defaut. Une comparaison acceptable ne
suffit pas seule a integrer une optimisation : le gain revendique doit aussi
etre visible et explique.

## Confidentialite et effets interdits

- aucun chemin local, projet personnel, secret ou contexte client ;
- aucun auto-apprentissage, auto-edition de code ou import automatique ;
- aucun CAD, finaliseur, scene ou materiau Fusion ;
- aucun changement de certificat, budget public ou deadline ;
- aucune revendication nouvelle sur le cas dense 11 x 34.

## Validation attendue

- tests purs du manifest, de l'import, du replay et de la comparaison ;
- replay CLI du tiers CI et self-comparison ;
- Ruff, format, py_compile et suite complete ;
- controle de confidentialite et `git diff --check`.

ADR : `ADR-0079-solver-case-corpus-and-measurement-gate.md`.
