# P64-L09T-C — preuve des réservations supérieures automatiques

Date : 2026-07-27.

Statut : `automated-validated`.

`fusion-validated=false`, `print-validated=false`.

## Objectif vérifié

La mission C supprime l'origine XY manuelle des plateaux et livrets plats. Le
calcul résout désormais leur pose automatiquement, les maintient au sommet en Z,
fige la décision dans le plan minimal et la réutilise exactement pendant la
finition.

La recherche est jointe, bornée et déterministe. Elle compare les rotations,
les placements côte à côte et les chevauchements ordonnés. Une pose candidate
est rejetée avant classement si elle viole l'enveloppe, l'appui supérieur, le
fond minimal, un prisme déjà réservé ou la paroi minimale existante autour
d'une cavité.

## Contrat livré

- Les champs normaux d'origine X/Y ont disparu de la palette.
- Un ancien projet portant une origine explicite est normalisé en mémoire vers
  la pose automatique. Son fichier source n'est pas réécrit avant une
  sauvegarde explicite.
- La recherche est limitée à 64 états, 10 positions par axe et 24 poses par
  état.
- Le classement minimise d'abord les violations dures, puis la profondeur
  cumulée depuis le sommet, les chevauchements, la distance au centre et enfin
  une signature stable.
- Le plan minimal transporte la pose automatique résolue. La finition reçoit
  ce plan figé et ne relance pas une recherche indépendante.
- La paroi demandée vient de `wall_thickness_mm` sur le groupe ou du default
  projet déjà existant. Aucune nouvelle valeur physique n'est introduite.
- Une bande de matière réellement séparatrice plus mince que cette valeur est
  refusée. Un chevauchement entre cavité et réservation est déclaré comme vide
  partagé, pas comme une paroi.
- La recherche ne réduit, ne translate et ne réoriente aucune cavité.
- Une absence de pose certifiable devient un blocage borné explicite ; elle
  n'est pas transformée en preuve d'impossibilité.

## Preuves automatisées

| Cas | Preuve |
| --- | --- |
| Le centre est invalide mais une pose latérale est possible | la recherche retient la pose latérale certifiée |
| Plateau et livret peuvent tenir côte à côte | la pose jointe disjointe est retenue |
| Le chevauchement est nécessaire | l'ordre Z et le résultat sont déterministes |
| Une ancienne origine manuelle est chargée | la pose passe en automatique, le marqueur de migration est exposé et la source reste inchangée |
| Une pose longe une cavité | la bande de matière est mesurée et une autre pose est choisie si nécessaire |
| Aucune pose ne respecte support, fond ou paroi | le calcul renvoie un blocage honnête sans déplacer la cavité |
| Le plan minimal est finalisé | les origines, rotations, dimensions et profondeurs des réservations restent identiques |

## Fichiers de comportement concernés

- `src/board_game_insert_generator/top_inset_reservation.py`
- `src/board_game_insert_generator/free_3d_plan_adapter.py`
- `src/board_game_insert_generator/coupled_finalization.py`
- `src/board_game_insert_generator/partition_solver.py`
- `src/board_game_insert_generator/partition_cad.py`
- `src/board_game_insert_generator/project_v1.py`
- `fusion_addin/BoardGameInsertGenerator/palette.html`
- `fusion_addin/BoardGameInsertGenerator/palette_project.py`
- `scripts/fusion/p64_l09v_preflight.py`

## Validation exécutée

- Suites ciblées réservation/projet/palette/minimal/staged : `135/135`, OK.
- Suite solveur de partition : `17/17`, OK en `36.546 s`.
- Suites API projet/résultat/CAD/synchronisation Fusion/CAD IR : `47/47`, OK.
- Contrats documentaires et pilotage : `10/10`, OK.
- JavaScript extrait de la palette : `node --check`, OK.
- Gate globale autorisée hors benchmark, corpus et tournoi solveur :
  `859/859`, OK en `282.881 s`, avec un test SCIP natif ignoré.

Onze modules benchmark/corpus/tournoi ont été exclus conformément à la frontière
explicite du Goal. Leurs artefacts canoniques ne sont ni recalculés ni présentés
comme recertifiés par C. La tentative initiale de découverte brute a donc été
remplacée par cette gate autorisée explicite ; elle ne constitue pas une preuve
benchmark.

## Limites et suite

- La version 0.1.69 reste `human-KO`, `do-not-run`.
- Aucun paquet ni add-in Fusion n'est installé pendant C.
- L'observation Fusion et l'impression réelle restent absentes.
- La mission D doit maintenant imposer la priorité lexicographique
  « plancher d'abord » entre plans complets certifiés.
