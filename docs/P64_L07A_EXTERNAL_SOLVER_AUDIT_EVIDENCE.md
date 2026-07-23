# P64-L07A — audit des solveurs externes

Date : 2026-07-23

Statut : done, automated-validated ; fusion-validated: false ;
print-validated: false.

## Résultat

Dix candidats crédibles ont été audités depuis leurs dépôts, documentations,
distributions officielles et publications primaires. Cinq passent la première
gate et restent en lice :

1. PackingSolver ;
2. `3d-bin-container-packing` / LAFF ;
3. OR-Tools CP-SAT ;
4. SCIP avec PySCIPOpt ;
5. HiGHS avec `highspy`.

Ils représentent cinq méthodes distinctes et couvrent bien le minimum de trois
concurrents externes et de trois familles exigé par ADR-0081. BGIG et son petit
oracle interne restent des références ; ils ne figurent pas dans cette liste.

L'inventaire machine relisible est
`tests/fixtures/p64_l07a_external_solver_audit.v1.json`. Son garde automatisé
vérifie le nombre de candidats, les familles, les décisions, les sources, les
licences, Windows hors ligne, les limites d'exécution et les pertes de modèle.

## Méthode

L'audit a appliqué les filtres dans cet ordre :

1. source et maintenance identifiables ;
2. licence du code, du binaire et des dépendances ;
3. chemin Windows isolé et fonctionnement hors ligne ;
4. entrée et sortie automatisables ;
5. délai et mémoire contrôlables, nativement ou par le processus parent ;
6. correspondance fidèle avec rotations, réservations, niveaux et variantes
   P45 ;
7. valeur algorithmique réellement différente ;
8. coût d'adaptation et de distribution.

Aucun binaire n'a été construit et aucun benchmark n'a été lancé pendant L07A.
Ce filtrage économise le quota avant les téléchargements et builds de L07C.

## Inventaire et décision

| Candidat | Famille | Licence utile | Windows hors ligne | Décision | Raison courte |
| --- | --- | --- | --- | --- | --- |
| [PackingSolver](https://github.com/fontanf/packingsolver) | recherche arborescente spécialisée | MIT, build permissif imposé | CMake + MSVC | `shortlisted` | seul moteur audité avec mode `box` 3D spécialisé |
| [LAFF 4.2.1](https://github.com/skjolber/3d-bin-container-packing) | niveaux + énumération | Apache-2.0 | JDK 17, JAR isolés | `shortlisted` | boîtes, rotations, obstacles, deadline et petit brute-force |
| [OR-Tools CP-SAT 9.15](https://github.com/google/or-tools) | contraintes / SAT / relaxation linéaire | Apache-2.0 | wheel CPython 3.10 | `shortlisted` | modèle entier fidèle et statuts exacts après recherche complète |
| [SCIP 10.0.3](https://github.com/scipopt/scip) | programmation entière sous contraintes | Apache-2.0 + wrapper MIT | wheel PySCIPOpt | `shortlisted` | formulation générale, limites temps et mémoire natives |
| [HiGHS 1.15.1](https://github.com/ERGO-Code/HiGHS) | nombres entiers linéaires | MIT | wheel `highspy` | `shortlisted` | contrôle MIP compact et distinct |
| [Choco 6.0.1](https://github.com/chocoteam/choco-solver) | contraintes à domaines finis | BSD-3-Clause | JDK 17 | `benchmark-only` | secours crédible mais doublon coûteux de CP-SAT |
| [Chuffed](https://github.com/chuffed/chuffed) | génération paresseuse de clauses | MIT | CMake + MSVC | `benchmark-only` | modèle FlatZinc générique et second adapter CP coûteux |
| [CBC 2.10.13](https://github.com/coin-or/Cbc) | branch-and-cut MIP | EPL-2.0 | archives Windows | `benchmark-only` | gate copyleft humaine et recouvrement avec HiGHS |
| [Timefold 2.3.0](https://github.com/TimefoldAI/timefold-solver) | heuristiques et métaheuristiques | Apache-2.0 CE | JDK 21 | `rejected` | aucun packing 3D natif, aucune preuve d'impossibilité |
| [py3dbp 1.1.2](https://github.com/enzoruiz/3dbinpacking) | heuristique simple de boîtes | MIT | Python | `rejected` | release ancienne, faible maintenance, aucune deadline contractuelle |

`benchmark-only` signifie qu'un candidat peut servir de contrôle ou de secours,
mais n'est pas autorisé à entrer dans le produit sur la base de L07A.

## Shortlist et familles réellement différentes

La shortlist n'est pas un classement anticipé :

- PackingSolver apporte la recherche géométrique spécialisée ;
- LAFF apporte une heuristique par niveaux et une énumération pour petits cas ;
- CP-SAT apporte la propagation de contraintes, SAT et relaxation linéaire ;
- SCIP apporte la programmation entière sous contraintes ;
- HiGHS apporte un MIP plus compact et spécialisé en optimisation linéaire.

PackingSolver et LAFF restent deux moteurs externes distincts, mais ils ne
suffisent pas seuls à satisfaire la diversité. Le tournoi L07C/D doit donc
conserver au moins un moteur CP/SAT et au moins un moteur MIP/CIP tant que leur
packaging et leur modèle passent les contrôles.

## Correspondance BGIG et pertes de modèle

| Besoin BGIG | PackingSolver | LAFF | CP-SAT | SCIP | HiGHS |
| --- | --- | --- | --- | --- | --- |
| boîtes T0/T1 orthogonales | natif | natif | modèle entier | modèle CIP/MIP | modèle MIP |
| six rotations orthogonales | natif | natif | variables de choix | variables binaires | variables binaires |
| réservations rectangulaires | non en mode `box` | obstacles natifs | disjonctions | disjonctions | linéarisation |
| niveaux | Z implicite | heuristique de niveaux | règles explicites | règles explicites | règles linéarisées si fidèles |
| variantes P45 | sous-ensemble rectangulaire seulement | contrôles à prouver | modèle exact requis | modèle exact requis | modèle exact requis |
| incrémental | redémarrage froid | redémarrage froid | hints possibles | warm start possible | warm start possible |

Une possibilité théorique ne compte pas comme couverture. L'adapter doit
retourner `unsupported` dès qu'une contrainte active n'est pas traduite sans
perte. Toute sortie positive repasse ensuite dans le certificat BGIG courant.
Une limite atteinte reste `bounded_unknown`.

## Formes complexes et limite théorique

Aucun candidat retenu ne sait placer nativement des formes 3D arbitraires.
PackingSolver possède un solveur de polygones irréguliers, mais il est
strictement 2D. Les autres moteurs pourraient seulement recevoir une
décomposition finie, des voxels ou un modèle non linéaire construit par BGIG.
Cela ne crée pas une capacité géométrique native et peut faire exploser le
nombre de variables ou perdre des contraintes.

La conclusion honnête est donc :

- L07 teste les formes T0/T1 rectangulaires et leurs contraintes ;
- aucun résultat L07 ne prouve T2 à T4 ;
- aucune revendication de forme 3D complexe ne sera faite ;
- une future étude de formes complexes exigerait un programme, un corpus et des
  certificats distincts.

## Licences et packaging

La gate la plus sensible concerne PackingSolver. Son build courant active CLP
par défaut et propose Knitro en option. Le candidat L07 impose :

- `PACKINGSOLVER_USE_CLP=OFF` ;
- `PACKINGSOLVER_USE_HIGHS=ON` ;
- `PACKINGSOLVER_USE_KNITRO=OFF` ;
- tests du projet externe non distribués.

Le graphe restant observé dans le CMake officiel utilise Boost 1.84.0,
HiGHS 1.13.1 et sept bibliothèques `fontanf` verrouillées par commit. Les sept
bibliothèques déclarent MIT et sont actives ; Boost utilise BSL-1.0 et HiGHS
MIT. Cette configuration devra encore être reconstruite puis mesurée.

LAFF utilise ses modules `api`, `points` et `core` Apache-2.0. Le visualiseur et
les dépendances de test sont exclus. OR-Tools, PySCIPOpt/SCIP et `highspy`
seront téléchargés comme artefacts officiels exacts, dans des environnements
isolés, puis verrouillés par SHA-256 avant toute exécution.

CBC reste hors intégration parce que son EPL-2.0 déclenche la gate humaine
copyleft d'ADR-0081. Aucun composant commercial, service, compte, secret,
télémétrie obligatoire ou installateur global n'est accepté.

## Publications primaires consultées

- PackingSolver :
  [Fontan et Libralesso, 2020](https://arxiv.org/abs/2004.02603) ;
- packing 3D rectangulaire :
  [Martello, Pisinger et Vigo, 2000](https://doi.org/10.1287/opre.48.2.256.12386) ;
- CP-SAT-LP :
  [Perron, Didier et Gay, 2023](https://doi.org/10.4230/LIPIcs.CP.2023.3) ;
- SCIP :
  [SCIP Optimization Suite 9.0](https://optimization-online.org/2024/02/the-scip-optimization-suite-9-0/) ;
- HiGHS :
  [Huangfu et Hall, 2018](https://doi.org/10.1007/s12532-017-0130-5) ;
- Choco :
  [Prud'homme et Fages, 2022](https://doi.org/10.21105/joss.04708) ;
- Chuffed / génération paresseuse de clauses :
  [Chu, 2011](https://hdl.handle.net/11343/37821).

Ces publications décrivent les méthodes. Elles ne remplacent ni le benchmark
BGIG, ni la recertification, ni l'audit des artefacts réellement exécutés.

## Validation automatisée

- audit L07A ciblé : 5/5 tests, OK ;
- garde documentaire de la preuve : 1/1, OK ;
- reconstruction portable du manifest L06 : 9/9, OK ;
- suite complète canonique : 721/721 en 217,756 s, OK ;
- schéma et JSON : chargement déterministe, OK ;
- dix identifiants uniques : OK ;
- cinq candidats shortlistés dans cinq familles : OK ;
- minimum externe et diversité : OK ;
- sources officielles et publications primaires : OK ;
- exclusions CLP, Knitro et CBC : gardées par test ;
- absence de revendication native de formes 3D arbitraires : gardée par test.

## Limites

- aucun moteur externe n'est encore téléchargé, construit ou exécuté ;
- le constructeur du manifest L06 a reçu une correction de portabilité LF :
  sa sortie Windows redevient identique octet par octet à la fixture ;
- les SHA-256 des artefacts et leurs tailles installées restent à mesurer avant
  L07C ;
- `shortlisted` ne signifie ni gagnant, ni adopté ;
- les réservations excluent PackingSolver `box` du classement de ces cas ;
- un modèle générique exact peut devenir trop gros avant de devenir utile ;
- fusion-validated et print-validated restent false.

## Suite

P64-L07A est terminée. P64-L07B peut construire le corpus V2, intégrer au moins
deux sources publiques indépendantes et sceller un nouveau holdout sans lancer
aucun candidat dessus.
