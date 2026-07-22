# Next Actions

Dernière mise à jour : 2026-07-22

## Version active

V0.1 reste `mvp-accepted`, `fusion-validated: true` pour son périmètre
historique et `print-validated: false`. La surface MVP reste exclusivement
l’add-in Fusion 360.

P64-L04A/B/C restent automated-validated dans le package 0.1.58.
Le retour humain L04V est globalement KO mais partiellement positif. R1 corrige
le cache négatif. P64-L05A est automated-validated : exactement un nouveau
conteneur peut être inséré dans le vide global à voisins figés et plan complet
recertifié. Le manifest Fusion reste à 0.1.58. fusion-validated: false et
print-validated: false pour L05A, L05B et L05C. Le manifest reste inchange.
P64-L05B, P64-L05C et P64-L05D1/D2 sont automated-validated.

## Dernier état réel

- une édition continue de recalculer uniquement ses dérivations locales ;
- une insertion interne admissible peut republier un `minimal_layout` courant
  sans solve global ni déplacement monde ;
- exactement un nouveau conteneur peut aussi être inséré à voisins figés si le
  certificat global accepte le plan complet ;
- le fallback global reste explicite et aucune scène n’est modifiée
  automatiquement ;
- Rapide reste préfixe de Normal, Normal devient le préfixe et l’incumbent
  d’Approfondi ;
- les six lanes Normal gardent leurs caps historiques ;
- seules les trois lanes supplémentaires Deep partagent ensuite une deadline de
  30 000 ms ;
- une expiration Deep conserve l’incumbent certifié et ne le transforme plus en
  `no_solution_within_budget` ;
- sans incumbent, l’échec reste honnête ; une annulation stale reste
  `stale_or_cancelled` ;
- budgets, temps, lanes, phases, incumbent et raison d’arrêt sont observables ;
- analyse, calcul, finalisation et matérialisation exposent désormais identité,
  étape et temps écoulé sans pourcentage ni ETA inventés ;
- un second lancement du même type est bloqué ; aucune annulation décorative
  n'est exposée ;
- un bouton DEV rouge exporte un SolverCaseBundle versionne, local et filtre sans lancer de solve, finalisation, CAD ou scene ;
- un witness certifie persistant est recertifie comme incumbent sans ajouter de lane, court-circuiter la recherche ou revendiquer un cache hit ;
- le cas dense 11 × 34 ne reçoit aucune nouvelle revendication.

Preuves :
`docs/P64_L04A_INCREMENTAL_LOCAL_REUSE_EVIDENCE.md` et
[P64-L04B](P64_L04B_DEEP_ANYTIME_EVIDENCE.md) et
[P64-L04C](P64_L04C_OPERATION_ACTIVITY_EVIDENCE.md).

Preuve L05A : P64_L05A_GLOBAL_VOID_CONTAINER_REUSE_EVIDENCE.md.
Preuve L05B : P64_L05B_SOLVER_CASE_BUNDLE_EVIDENCE.md.
Preuve L05C : P64_L05C_CERTIFIED_PLAN_WITNESS_EVIDENCE.md.
Preuve L05D1 : P64_L05D1_SOLVER_CORPUS_EVIDENCE.md.

## Prochaine action recommandée

### P64-L05V-A - preparer la gate Fusion et la capture reelle

Type : preparation automatisee puis gate humaine.

Objectif : installer un package Fusion issu du commit integre, faire observer
L05A/B/C/D dans le projet reel et recuperer un premier SolverCaseBundle explicite
sans auto-apprentissage.

Codex doit d'abord :

1. cadrer la checklist L05V et les marqueurs exacts du package ;
2. preparer et installer l'add-in courant lorsque l'environnement le permet ;
3. verifier localement les fichiers installes et les settings de la palette ;
4. fournir a Thomas uniquement les actions restantes dans Fusion.

Thomas observe ensuite :

1. ajout d'un petit conteneur dans le vide global a voisins figes ;
2. conservation/rechargement d'un witness certifie apres changement d'effort ;
3. bouton DEV rouge visible et sans solve, finalisation, CAD ou scene ;
4. export d'un SolverCaseBundle sur le cas reel connu ;
5. identites, etapes, budgets, temps et raisons d'arret toujours observables.

Le bundle reste local et n'est jamais promu automatiquement. L'iteration solveur
suivante sera cadree a partir de son replay anonymise. Aucune validation
d'impression n'est impliquee.

L05D1/D2 sont automated-validated : corpus exact, gate A/B et premiere
optimisation interne. Le cas personnel reste sans completion geometrique ; aucune
revendication de resolution n'est faite.
## Lots verrouillés

- P64-F01A02 et F02A02 restent séparés : ils possèdent la finalisation du volume ;
- P64-C01/C02 restent post-finalisation et ne doivent pas absorber L04A ;
- P45 conserve formes, intentions et certificat local ;
- P46, P47-P50, P67-P69 et les valeurs physiques restent hors scope ;
- aucune résolution du cas dense n’est implicite.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves, committer puis
intégrer directement dans `main` lorsqu’aucune vraie gate humaine n’est active.
Une gate Fusion ne vaut jamais impression.

## Repères historiques conservés

- `P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0` ;
- P44-M007 a livré le package `0.1.37` ;
- `P64-H01 Fusion OK 0.1.42 - commit 5865645` ;
- P44-VH02 reste un retour contextuel supersédé, sans promotion
  `fusion-validated` ;
- `P64-V2H03V Fusion OK 0.1.55` ;
- `P44-V Fusion OK 0.1.55 - commit 70d45c6`.

## Mise a jour P64-L04V preparation (2026-07-22)

Le preparateur versionne scripts/fusion/prepare_p64_l04v_gate.ps1, le fixture portable et la checklist sont prets. Executer le preparateur depuis le commit integre, puis collecter le retour humain defini par docs/P64_L04V_FUSION_GATE_CHECKLIST.md.
Aucune promotion fusion-validated ne precede cette observation ; print-validated: false.

## Mise à jour après P64-L04R1 (2026-07-22)

P64-L04R1 est automated-validated : un échec ne satisfait plus une nouvelle
action explicite et seuls les plans certifiés sont réutilisés. La palette
distingue calcul frais, recherche initiale et restitution cache.

Prochaine mission unique : P64-L05A, insertion d'un nouveau conteneur dans le
vide global d'un plan minimal certifié avec voisins figés et recertification
complète. Le lot doit commencer par une ADR, car ADR-0075 exclut actuellement ce
comportement. L05B/L05C/L05D restent ensuite autorisés et ordonnés. Aucune gate
Fusion ni impression n'est revendiquée par R1.

## Mise à jour après P64-L05A (2026-07-22)

P64-L05A est automated-validated. Le producteur fixe tous les voisins, teste des
positions de contact contre les placements réels et rejoue le certificat global
commun. Il n’utilise pas les zones résiduelles affichées comme preuve et
n’appelle pas le portefeuille global.

Prochaine mission unique : P64-L05B, capture locale et versionnée d’un
SolverCaseBundle depuis un bouton DEV explicite. L05C puis L05D restent ordonnés.
Aucune validation Fusion ou impression n’est revendiquée.


## Mise a jour apres P64-L05B (2026-07-22)

P64-L05B est automated-validated. Un bouton DEV rouge produit localement un
SolverCaseBundle v1 reproductible avec etat staged observe, frontieres P45,
reglages, provenance, trace semantique filtree et identite de scene. La capture
ne declenche aucune operation de domaine et ne modifie pas le solveur.

Prochaine mission unique : P64-L05C, plan temoin certifie persistant et warm
start fail-closed. L05D reste ensuite ordonnee. Aucune validation Fusion ou
impression n'est revendiquee.

## Mise a jour apres P64-L05C (2026-07-22)

P64-L05C est automated-validated. Un sidecar exact conserve le meilleur plan
certifie par identite projet + frontieres P45. Il est recertifie comme incumbent,
les lanes courantes continuent et Deep garde son prefixe Normal historique. Un
fichier incompatible ou corrompu est rejete puis remplace apres un solve certifie.

Prochaine mission unique : P64-L05D, corpus versionne, replay borne, baseline et
optimisation mesuree des lanes. Aucune validation Fusion ou impression n'est
revendiquee.

## Mise a jour apres P64-L05D1 (2026-07-22)

P64-L05D1 est automated-validated. Le corpus versionne contient cinq cas CI et
deux extended ; les rapports separent preuves fonctionnelles et temps mur. La
gate A/B refuse une perte de solution, de certificat, de qualite ou de contrat
de lanes avant toute comparaison de vitesse.

Prochaine mission unique : P64-L05D2, premiere optimisation interne bornee et
mesuree. Aucune validation Fusion ou impression n'est revendiquee.

## Mise a jour apres P64-L05D2 (2026-07-22)

P64-L05D2 est automated-validated. Sous ordre explicite, les participants qui ne
peuvent plus entrer dans le quota de branches ne sont plus evalues. Le corpus
complet mesure 57 329 -> 31 901 essais, sans regression fonctionnelle, mais le
projet personnel reste sans solution.

Prochaine mission unique : P64-L05V-A, preparation puis installation de la gate
Fusion de capture reelle. La revue dans Fusion reste humaine.
