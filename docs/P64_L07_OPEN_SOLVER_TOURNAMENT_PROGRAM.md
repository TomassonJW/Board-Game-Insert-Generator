# P64-L07 — programme de comparaison des meilleurs solveurs accessibles

## 1. Statut et résultat attendu

Statut : `ready-for-explicit-go`.

P64-L07 doit répondre à une question simple : parmi les meilleures solutions
libres d'utilisation réellement accessibles, laquelle améliore le plus BGIG sur
ses vrais problèmes de placement rectangulaire ?

Le résultat attendu n'est pas un classement décoratif. Le programme doit :

- chercher largement les solutions existantes ;
- en comparer au moins trois qui sont sérieuses et réellement différentes ;
- produire une mesure reproductible ;
- intégrer le meilleur choix produit ;
- intégrer jusqu'à deux choix complémentaires seulement si leur utilité propre
  est démontrée.

## 2. Correction explicite de P64-L06

P64-L06 n'était pas un benchmark de l'état de l'art. Il a comparé le solveur
BGIG courant, un petit oracle exact interne et trois variantes mineures des lanes
internes. Son résultat négatif reste une preuve valable de cette expérience,
mais il ne permet aucune conclusion sur les outils externes disponibles.

P64-L07 est un nouveau programme. Il ne réécrit pas l'histoire de L06 et ne
réutilise pas son holdout pour choisir un candidat.

## 3. Question de décision

Le tournoi doit séparer trois questions :

1. le candidat sait-il représenter le cas sans en supprimer une contrainte ?
2. trouve-t-il un placement que BGIG peut certifier ?
3. apporte-t-il assez de couverture, de qualité ou de vitesse pour justifier
   son coût d'intégration et de maintenance ?

Une réponse rapide à un problème simplifié n'est pas une victoire. Un résultat
non certifié n'est pas une solution.

## 4. Portée fonctionnelle

Le premier Goal P64-L07 reste sur les formes T0/T1 du produit courant :

- volumes rectangulaires orthogonaux ;
- boîte et réservations existantes ;
- un ou plusieurs niveaux ;
- rotations autorisées ou interdites selon le cas ;
- choix parmi les variantes locales certifiées P45 ;
- placement global P64 ;
- exécution froide et parcours incrémental lorsque le contrat le permet.

Les formes T2 à T4, la géométrie arbitraire, la finalisation, le CAD, la scène
Fusion et les valeurs physiques restent hors benchmark.

## 5. Recherche obligatoire de l'état de l'art

P64-L07A construit un inventaire d'au moins huit candidats crédibles. Les
sources prioritaires sont :

1. dépôt et documentation officiels ;
2. publication primaire décrivant la méthode ;
3. jeux de benchmark et générateurs reconnus ;
4. historique de versions, tickets ouverts et maintenance récente.

La fiche de chaque candidat contient :

- nom, version ou commit et URL officielle ;
- licence du code, des binaires, des données et des dépendances ;
- droit d'usage commercial, modification et redistribution ;
- langage, plateforme, mode d'installation et fonctionnement hors ligne ;
- famille algorithmique et type de garantie ;
- contraintes représentables et contraintes perdues ;
- coût estimé d'adaptation, taille et maintenance ;
- décision : `shortlisted`, `benchmark-only` ou `rejected`, avec raison.

La liste de départ, non limitative et non gagnante par avance, comprend :

- PackingSolver, solveur spécialisé de packing sous licence MIT ;
- `3d-bin-container-packing`, implémentation LAFF et brute force sous
  licence Apache-2.0 ;
- OR-Tools CP-SAT sous licence Apache-2.0 ;
- SCIP sous licence Apache-2.0, avec audit séparé de ses composants optionnels ;
- HiGHS sous licence MIT pour une formulation en nombres entiers ;
- d'autres implémentations et méthodes publiées découvertes pendant L07A.

## 6. Minimum de concurrence réelle

Le tournoi exige au moins trois candidats externes qui passent les filtres et
appartiennent à au moins trois approches parmi :

- solveur spécialisé de placement 3D ;
- programmation par contraintes ou SAT ;
- programmation linéaire en nombres entiers ;
- recherche exacte ou branch-and-bound spécialisée ;
- heuristique hybride ou métaheuristique reproductible.

Deux réglages du même moteur ne sont pas deux candidats. Un fork sans différence
algorithmique n'est pas un candidat distinct. Le solveur BGIG courant et le
petit oracle interne sont des références, pas des concurrents externes.

Si moins de trois candidats légaux et adaptables sont disponibles, L07A
s'arrête avec une preuve d'échec. La campagne n'est pas déclarée terminée.

## 7. Gate légale, technique et de sécurité

Avant tout benchmark coûteux, chaque candidat doit passer :

- licence claire et source officielle ;
- acquisition vérifiable par version et SHA-256 ;
- aucune clé, aucun compte et aucun service distant ;
- aucun installateur global ou modification silencieuse de la machine ;
- exécution dans un dossier isolé du workspace ;
- entrée et sortie automatisables ;
- arrêt, délai et mémoire contrôlables ;
- absence de télémétrie obligatoire ;
- chemin réaliste vers Windows et l'add-in Fusion hors ligne.

Une licence permissive compatible peut mener à l'intégration. Une licence
copyleft, ambiguë, non commerciale ou propriétaire reste `benchmark-only` ou
`rejected` tant qu'une décision humaine distincte n'a pas tranché ses
obligations.

## 8. Corpus V2 et holdout neuf

P64-L07B crée `bgig.solver_benchmark_manifest.v2`. Il conserve les régressions
utiles, mais ne recycle pas le holdout L06 comme mesure finale.

Le corpus V2 contient :

- cas BGIG générés couvrant nombreux conteneurs/un contenu, peu/nombreux,
  nombreux/nombreux, mélange de tailles et incrémental puis froid ;
- cas avec un à plusieurs niveaux, réservations et politiques de rotation ;
- cas réels anonymisés issus du journal local, seulement après revue ;
- au moins deux sources publiques indépendantes de cas 3D pertinentes, avec
  licence ou procédure de téléchargement et empreinte vérifiées ;
- une table de correspondance entre l'objectif public et l'objectif BGIG ; un
  cas dont les contraintes ne peuvent pas être traduites fidèlement reste un
  contrôle de méthode séparé et ne compte pas dans le classement produit ;
- petits cas exacts permettant de contrôler les statuts ;
- cas difficiles qui distinguent couverture, qualité et délai.

Les splits sont séparés par familles et graines :

- `regression` : non-régression obligatoire ;
- `discovery` : comparaison initiale ;
- `tuning` : réglage borné et identique dans son principe ;
- `holdout` : cas et réponses fermés jusqu'au choix final.

Les cas issus de la même graine, d'un même projet ou d'une simple permutation ne
doivent pas traverser plusieurs splits.

## 9. Interface et vérité communes

P64-L07C fournit un adapter isolé par candidat. Chaque adapter reçoit la même
entrée normalisée et publie :

- candidat, version, source et empreinte ;
- contraintes réellement appliquées ;
- limite de temps, mémoire, threads et graine ;
- statut brut et statut normalisé ;
- temps au premier placement certifiable et temps total ;
- mémoire maximale et charge de démarrage ;
- placement proposé ou raison d'absence ;
- certificat BGIG frais ;
- métriques de qualité comparables ;
- erreurs, portée non couverte et avertissements de licence.

Tout placement est reconstruit et recertifié par BGIG. Une contrainte ignorée
rend le cas `unsupported`, pas réussi. Seul un moteur exact dans la portée
déclarée peut publier `infeasible_proven`; sinon l'absence reste
`bounded_unknown`.

## 10. Mesures et équité

L'ordre de décision est :

1. aucune régression fonctionnelle ;
2. couverture des contraintes ;
3. nombre de cas faisables certifiés ;
4. qualité du placement selon les scores BGIG déjà définis ;
5. temps au premier placement certifié ;
6. temps total, mémoire et stabilité ;
7. taille distribuée, temps de démarrage et coût de maintenance.

Les candidats reçoivent une enveloppe totale comparable. Un portefeuille de
trois moteurs ne peut pas gagner simplement parce qu'il consomme trois fois les
ressources. Les résultats enregistrent temps mur, temps CPU, mémoire, threads,
graine, ordre et état froid ou chaud.

## 11. Tournoi progressif

P64-L07D exécute dans cet ordre :

1. contrôle des adapters sur petits cas exacts ;
2. régressions BGIG ;
3. `discovery` avec tous les candidats conformes ;
4. élimination documentée des candidats dominés ou invalides ;
5. `tuning` borné des candidats encore crédibles ;
6. choix scellé d'un candidat seul ou d'un portefeuille de deux ou trois ;
7. ouverture unique du nouveau `holdout` ;
8. soak seulement si les résultats montrent une instabilité à confirmer.

Le réglage ne doit pas lire le holdout. Les arrêts précoces économisent du temps
sans changer la limite d'un candidat pendant une comparaison.

## 12. Règle d'intégration d'un à trois gagnants

P64-L07E intègre d'abord un gagnant principal. Un second ou un troisième moteur
est permis seulement si toutes les conditions suivantes sont réunies :

- il gagne une famille de cas nommée que le gagnant principal couvre mal ;
- le gain se répète sur tuning puis holdout ;
- le routeur choisit le moteur sans connaître la réponse du cas ;
- le portefeuille complet bat le meilleur moteur seul avec une enveloppe totale
  comparable ;
- le coût de distribution et de maintenance reste accepté par ADR-0081 ;
- le fallback vers le solveur BGIG et la vérité des statuts restent intacts.

Si ces conditions ne sont pas réunies, seul le meilleur moteur est intégré. Si
aucun moteur ne les satisfait, aucun changement produit n'est intégré.

## 13. Packaging du gagnant

Chaque dépendance intégrée reçoit une ADR factuelle dans L07E avec :

- version et empreinte verrouillées ;
- licence et avis à redistribuer ;
- dépendances transitives ;
- méthode de build ou binaire officiel ;
- fonctionnement Windows hors ligne ;
- taille installée et temps de démarrage ;
- stratégie de mise à jour et de retrait ;
- tests du fallback en absence ou échec du moteur.

Aucun paquet d'essai, cache de téléchargement ou jeu de données non distribuable
n'entre dans le dépôt.

## 14. Missions atomiques

### P64-L07A — recherche et shortlist

Livrer l'inventaire, l'audit légal/technique et au moins trois concurrents
externes distincts.

### P64-L07B — corpus public et BGIG V2

Livrer le manifest V2, les splits indépendants, les sources publiques et un
nouveau holdout scellé.

### P64-L07C — adapters isolés

Livrer les adapters d'au moins trois candidats, les petits contrôles exacts et
la recertification commune.

### P64-L07D — tournoi

Livrer les exécutions progressives, les rapports, la sélection avant holdout et
le résultat final non biaisé.

### P64-L07E — intégration mesurée

Intégrer le gagnant principal et éventuellement jusqu'à deux compléments, puis
valider le packaging, le fallback, les licences et la suite complète.

Chaque mission est testée, documentée, commitée, intégrée dans `main`, poussée
et vérifiée à distance avant la suivante.

## 15. Arrêts honnêtes

Le Goal s'arrête proprement si :

- moins de trois candidats passent le filtre initial ;
- une licence ou une chaîne de dépendances reste ambiguë ;
- aucune sortie positive ne passe le certificat BGIG ;
- une régression fonctionnelle ne peut pas être corrigée dans la mission ;
- le nouveau holdout a été ouvert trop tôt ou contaminé ;
- les ressources dépassent l'enveloppe annoncée ;
- Git diverge, un conflit apparaît ou le push de `main` est refusé.

Un arrêt produit un checkpoint et un rapport. Il ne transforme jamais
`bounded_unknown` en impossibilité.

## 16. Frontières absolues

- T0/T1 seulement dans ce premier Goal.
- Aucun SaaS, cloud, secret, compte ou télémétrie.
- Aucune auto-modification ni recherche de code par un solveur.
- Aucun changement silencieux de budget, deadline, certificat, schéma,
  tolérance, géométrie, propriété P45/P64, finalisation, CAD, scène, manifest
  Fusion ou valeur physique.
- Aucune nouvelle revendication sur le cas dense 11 × 34 sans résultat du
  nouveau protocole.
- `fusion-validated: false` et `print-validated: false` sans preuves dédiées.

## 17. Sources de départ

Ces liens lancent la recherche L07A ; ils ne remplacent pas son audit :

- PackingSolver : <https://github.com/fontanf/packingsolver>
- LAFF / 3D bin container packing :
  <https://github.com/skjolber/3d-bin-container-packing>
- OR-Tools CP-SAT :
  <https://developers.google.com/optimization/cp/cp_solver>
- SCIP : <https://www.scipopt.org/>
- HiGHS : <https://highs.dev/>
- BED-BPP :
  <https://doi.org/10.1177/02783649231193048>

ADR normative : `docs/DECISIONS/ADR-0081-open-external-solver-tournament.md`.
Runbook : `docs/P64_L07_AUTONOMOUS_GOAL_RUNBOOK.md`.
