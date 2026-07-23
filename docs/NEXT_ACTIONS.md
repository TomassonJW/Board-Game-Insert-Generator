# Next Actions

Dernière mise à jour : 2026-07-23

## Version active

V0.1 reste `mvp-accepted`, `fusion-validated: true` pour son périmètre
historique et `print-validated: false`. La surface MVP reste exclusivement
l’add-in Fusion 360.

P64-L04A/B/C restent automated-validated dans le package 0.1.58.
Le retour humain L04V est globalement KO mais partiellement positif. R1 corrige
le cache négatif. P64-L05A est automated-validated : exactement un nouveau
conteneur peut être inséré dans le vide global à voisins figés et plan complet
recertifié. Le manifest Fusion passe à 0.1.59 pour le journal automatique. fusion-validated: false et
print-validated: false pour L05A, L05B et L05C. Le solveur reste inchangé.
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
- un journal local automatique conserve clics, changements, demandes, résultats et états dédupliqués sans bouton spécial, sans solve supplémentaire, finalisation, CAD ou scène ;
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

### P64-L06C — comparateur offline et petit oracle exact

Type : mission autonome de benchmark, sans action humaine.

P64-L06B est terminée : le manifest conserve huit cas de régression et ajoute
64 cas discovery, 64 tuning et 64 holdout. Les cinq familles, les cardinalités
P45/P64, les étages, réservations, rotations et ordres adversariaux sont couverts.
Les cas faisables ont un témoin vérifié, les cas négatifs une preuve exacte, et
le holdout reste fermé.

L06C doit maintenant :

1. définir une entrée/sortie commune pour les solveurs offline ;
2. livrer un petit oracle exact interne sans dépendance externe ;
3. déclarer explicitement les contraintes non prises en charge ;
4. recertifier toute solution par le certificat BGIG commun ;
5. livrer tests, preuve, commit et intégration dans `main`, puis ouvrir L06D.

Le Goal déjà lancé reste valable. Il poursuit L06C à L06E sans nouveau GO et
sans installer de dépendance externe.

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

## Mise a jour apres P64-L05V-A (2026-07-22)

P64-L05V-A est automated-validated et installe localement : add-in 0.1.58,
commit 261f7cc, runtime L05 et fixture sont verifies. P64-L05V devient la
prochaine action, exclusivement humaine dans Fusion.

## Retour P64-L05V - ne pas confondre smoke et capacite (2026-07-22)

Le retour Fusion est positif pour l insertion dans le vide global de la fixture, la premiere persistance atomique du witness et l absence de cache revendique. La fixture est volontairement simple : elle ne mesure pas la profondeur de recherche et ne valide pas la reconstruction de `Mon insert.bgig.json`.

La prochaine action unique est humaine et courte : produire un SolverCaseBundle DEV representatif du projet complexe apres une manipulation reelle, puis fournir son chemin et son digest. En parallele, recharger le witness sur le meme projet pour observer un warm start accepte. Aucun bundle personnel n entre dans le depot avant anonymisation et revue.

La prochaine mission de code, non demarree, sera P64-L06A : anonymiser, rejouer et classifier ce premier cas reel avant de proposer une amelioration ciblee du solveur. Aucune promesse de capacite ou de vitesse n est faite avant cette preuve.

## Apres P64-L05V-R1 - recapture fidele du cas reel (2026-07-23)

Les trois bundles reels sont valides et prouvent le delta exact puis l echec global, mais le clic DEV 0.1.58 ecrasait la raison du refus incremental avant l export. R1 corrige cette instrumentation sans modifier le solveur.

Historique : cette recapture manuelle était l action demandée avant ADR-0080. Elle est maintenant remplacée par le journal automatique local.

P64-L06A est désormais prête : elle inventorie les cas réels et les journaux, puis lance le benchmark sans attendre une nouvelle manipulation humaine.

### Installation P64-L05V-R1 terminee

Historique : le commit e817432 avait été installé dans Fusion 0.1.58. La manipulation manuelle alors demandée est annulée par ADR-0080 et remplacée par le journal automatique 0.1.59.

## Cadrage de la suite P64-L06 (2026-07-23)

Le programme de benchmark et le registre des horizons produit sont désormais
documentés. Ils n'écrasent pas la prochaine action unique :

1. inventorier les cas réels et les journaux locaux ;
2. exécuter P64-L06A en lecture contrôlée : anonymisation, replay et
   classification, sans changement de solveur ;
3. seulement ensuite ouvrir L06B/L06C pour les oracles, générateurs et
   comparateurs offline ;
4. lancer une campagne autonome L06D avant de sélectionner une seule
   amélioration L06E.

Les formes complexes, couvercles avancés, couleurs, aperçu 3D et compositeur
manuel restent des horizons différés. Ils ne sont pas injectés dans le benchmark
rectangulaire T0/T1.

## Préparation P64-L06P — Goal autonome

Le paquet de reprise fixe la matrice P45/P64, les splits regression/discovery/
tuning/holdout, un oracle exact interne sans dépendance, le tournoi progressif,
les budgets, la pause sûre et les arrêts. Le premier Goal intègre au maximum une
amélioration validée ; il peut conclure sans diff si aucune hypothèse ne passe.

Cette préparation est `done-documentation`. ADR-0080 lève ensuite la gate R1 sans changer le solveur ni les règles du benchmark.
