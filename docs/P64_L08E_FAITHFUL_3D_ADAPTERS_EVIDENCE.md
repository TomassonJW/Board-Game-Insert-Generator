# P64-L08E — adaptateurs fidèles et contrôles 3D externes

Date : 2026-07-24

Statut : `done`, `automated-validated`, `no-winner-selected`, `holdout-closed`.

## Résultat

Quatre moteurs externes de quatre familles différentes ont réellement été
exécutés hors ligne sur des problèmes X/Y/Z. Chacun a produit un empilement à
deux niveaux distincts, puis BGIG a reconstruit et recertifié le monde complet.
Aucun témoin positif du corpus L08D n'est transmis aux workers.

Cette mission ne classe encore aucun moteur. Elle prouve seulement que les
entrées, sorties, refus et certificats nécessaires au tournoi L08F sont réels.
Le holdout L08D reste `opened=false` avec zéro invocation.

## Paquets verrouillés avant exécution

| Moteur | Famille | Version ou SHA exécuté | Paquet local | Gate produit |
| --- | --- | --- | --- | --- |
| PackingSolver `box` | recherche arborescente 3D spécialisée | `0cae9d04d5d361c496074ea633b1a3955b6543ec` | build MSVC x64 Release, binaire de 1 335 296 octets, SHA-256 verrouillé | `benchmark-only` jusqu'aux avis de redistribution et à l'audit final des dépendances binaires |
| LAFF | heuristique 3D par niveaux | 4.2.1, Temurin 17.0.19 | 204 015 872 octets de JAR, sources, POM et JDK portable déjà verrouillés | `benchmark-only` tant que la redistribution EPL/EDL est en revue |
| OR-Tools CP-SAT | contraintes entières / SAT | 9.15.6755 | 49 821 428 octets de wheels verrouillés | candidat hors ligne Apache-2.0 |
| SCIP via PySCIPOpt | CIP / MIP | SCIP 10.0.2, PySCIPOpt 6.2.1 | 61 194 406 octets de wheels verrouillés | `benchmark-only` tant que les avis natifs redistribués ne sont pas finalisés |

PackingSolver est construit localement depuis sa source officielle avec
`PACKINGSOLVER_BUILD_TEST=OFF`, CLP désactivé et HiGHS désactivé. Le verrou
versionné inventorie Boost 1.84, nlohmann/json 3.11.3 et les dépendances Fontan
par version ou commit et par digest de licence. L'ensemble temporaire L08E
occupe 1,755 Gio, sous la limite de 8 Gio. Aucune installation globale, aucun
compte, secret, service ou trafic réseau n'est requis à l'exécution.

Sources primaires :

- [PackingSolver `box`](https://fontanf.github.io/packingsolver/box.html) :
  coordonnées 3D libres, rotations indépendantes et certificat CSV ;
- [PackingSolver source](https://github.com/fontanf/packingsolver) : build CMake
  et licence MIT ;
- [LAFF](https://github.com/skjolber/3d-bin-container-packing) : placement 3D
  par niveaux, rotations, obstacles et licence Apache-2.0 ;
- [OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver) :
  variables et contraintes entières avec statuts exacts ;
- [PySCIPOpt](https://github.com/scipopt/PySCIPOpt) : interface officielle SCIP.

## Protocole 3D

Le nouveau protocole `bgig.real_3d_worker_input.v1` transporte :

- monde entier en millimètres `X/Y/Z` ;
- tous les participants, contenus affectés, variantes et rotations autorisées ;
- collisions 3D et limites monde ;
- étages, hauteurs hétérogènes et appuis ;
- appui multiple et couverture complète ;
- réservations basses et hautes ;
- régions disjointes et fragmentation ;
- politique d'accès et rang de retrait ;
- caps de temps, mémoire, thread et graine.

OR-Tools et SCIP utilisent deux formulations indépendantes : disjonctions
pairwise entières, choix de variantes, réservations, cellules fragmentées et
relations d'appui explicites. PackingSolver et LAFF passent par leur moteur 3D
natif. Toute règle non traduite produit `unsupported` avant l'appel externe.
Une sortie ne compte comme solution qu'après recertification indépendante BGIG :
identités, tailles, variantes, rotations, limites, collisions, contenus,
réservations, plan d'appui, couverture, fragmentation et accès.

## Contrôles exécutés

Six vérités publiques sont utilisées :

1. empilement faisable à hauteurs 3 mm + 5 mm ;
2. empilement impossible à hauteur totale 9 mm dans 8 mm ;
3. charge 10 × 10 portée par deux supports 5 × 10 ;
4. trois boîtes contraintes par une réservation basse et une réservation haute ;
5. deux régions disjointes quasi saturées ;
6. choix obligatoire d'une variante et d'une rotation admissibles.

| Moteur | Appels | Solutions certifiées | Impossibilités prouvées | `bounded_unknown` | `unsupported` |
| --- | ---: | ---: | ---: | ---: | ---: |
| OR-Tools CP-SAT | 6 | 5 | 1 | 0 | 0 |
| SCIP | 6 | 5 | 1 | 0 | 0 |
| PackingSolver `box` | 2 | 1 | 0 | 1 | 4 |
| LAFF | 2 | 1 | 0 | 1 | 4 |

Les quatre empilements certifiés ont réellement deux coordonnées Z :
OR-Tools `0/5`, SCIP `0/3`, PackingSolver `0/5` et LAFF `0/5`.
PackingSolver et LAFF ne revendiquent jamais une preuve d'impossibilité. Ils
refusent ici multi-appui, réservations, fragmentation et variantes, au lieu de
les ignorer.

Les temps de ces petits contrôles servent seulement à vérifier l'isolation :
OR-Tools 344–379 ms, SCIP 122–155 ms, PackingSolver 60–1 075 ms et LAFF
218–314 ms par processus complet. Les pics observés restent sous 73 Mio. Ces
nombres ne sont pas un classement de performance sur les cas limites.

## Artefacts de preuve

- `src/board_game_insert_generator/real_3d_solver_adapters.py` : contrat,
  fidélité, appels isolés et recertification ;
- `scripts/solver/external_workers/*real_3d_worker*` : quatre workers externes ;
- `scripts/solver/run_real_3d_adapter_controls.py` : acquisition vérifiée,
  build LAFF et campagne reproductible ;
- `tests/fixtures/p64_l08e_packingsolver_build_lock.v1.json` : source, build,
  binaire et licences PackingSolver ;
- `tests/fixtures/p64_l08e_real_3d_adapter_controls_receipt.v1.json` : 24 lignes
  candidat/contrôle, digest
  `a3c35ee1bddc5578aeb41e79639c507e1d8236d470a39769ace77d2303192d76` ;
- tests unitaires : contrats, refus, recertification, verrous et reçu.

## Validations

- `ruff check` sur les modules, workers, runner et tests L08E : OK ;
- tests ciblés `test_real_3d_*.py` : 19/19 ;
- verrou PackingSolver : 1/1 ;
- garde documentaire : 2/2 ;
- alignement Fusion-only : 6/6 ;
- suite complète : 785/785 en 261,996 s ;
- `git diff --check` : OK.
## Limites et suite

- Les petits contrôles ne désignent aucun gagnant et ne prouvent aucune montée
  en charge.
- PackingSolver et LAFF ne classeront que les familles qu'ils représentent ;
  leurs refus ne seront jamais transformés en mauvais scores ou en solutions.
- OR-Tools et SCIP ne pourront publier `infeasible_proven` sur la campagne
  adversariale que si la complétude du modèle concerné est démontrée ; sinon le
  statut reste `bounded_unknown`.
- `fusion-validated=false` et `print-validated=false`.

P64-L08F doit maintenant exécuter régressions, discovery puis tuning sur les cas
ouverts, sceller code, versions, caps, critères et sélection, et seulement alors
ouvrir le holdout privé une fois. Aucun moteur n'est intégré avant ce verdict.
