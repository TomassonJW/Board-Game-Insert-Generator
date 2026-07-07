# Backlog

Derniere mise a jour : 2026-07-07

Le backlog transforme la North Star en missions atomiques. Chaque mission future
doit indiquer au minimum : ID, titre, capability liee, milestone lie, objectif,
livrable, criteres d'acceptation, tests, gate eventuelle et statut.

Statuts utilises : `done`, `ready`, `ready_if_gate_deferred`, `todo`, `blocked`,
`manual_validation_required`, `deferred`.

## Phase 0 - Fondation projet

### P0-M001 - Installer le systeme de pilotage projet

- Capability : pilotage projet.
- Milestone : M1 Engine foundation.
- Objectif : creer les docs de controle minimales.
- Livrable : STATUS, ROADMAP, BACKLOG, NEXT_ACTIONS, ADR/logs.
- Criteres d'acceptation : un agent peut reprendre le projet sans contexte oral.
- Tests : inspection documentaire.
- Gate : aucune.
- Statut : `done`.

### P0-M002 - Ajouter une verification documentaire de base

- Capability : pilotage projet.
- Milestone : M1 Engine foundation.
- Objectif : verifier automatiquement les fichiers et sections de pilotage.
- Livrable : tests documentaires dans la suite unitaire.
- Criteres d'acceptation : absence de fichier de controle critique detectee par test.
- Tests : `python -m unittest discover -s tests`.
- Gate : aucune.
- Statut : `done`.

### P0-M003 - Bootstrap autonomy protocol

- Capability : pilotage projet.
- Milestone : M1 Engine foundation.
- Objectif : decrire l'autonomie Codex et les arrets obligatoires.
- Livrable : protocole d'autonomie, execution loop, gates et matrice.
- Criteres d'acceptation : selection de mission et arrets lisibles.
- Tests : inspection documentaire.
- Gate : aucune.
- Statut : `done`.

### P0-M004 - Dry-run autonomous mission selection

- Capability : pilotage projet.
- Milestone : M1 Engine foundation.
- Objectif : tester la selection sans mutation produit.
- Livrable : log de dry run.
- Criteres d'acceptation : prochaine mission identifiee sans execution abusive.
- Tests : inspection documentaire.
- Gate : aucune.
- Statut : `done`.

### P0-M005 - Stabiliser le format des ADR

- Capability : pilotage projet.
- Milestone : M1 Engine foundation.
- Objectif : rendre les decisions structurantes auditables.
- Livrable : template ADR et index.
- Criteres d'acceptation : ADR futures cadrables avec contexte/options/decision.
- Tests : test documentaire.
- Gate : aucune.
- Statut : `done`.

### P0-M006 - Definir une nomenclature de versions et releases

- Capability : release future.
- Milestone : M14 Usable beta.
- Objectif : preparer une version utilisateur sans publication immediate.
- Livrable : nomenclature de versions.
- Criteres d'acceptation : statuts experimental/validated explicites.
- Tests : inspection documentaire.
- Gate : publication de release.
- Statut : `todo`.

### P0-M007 - Activer l'integration Git autonome

- Capability : pilotage projet.
- Milestone : M1 Engine foundation.
- Objectif : autoriser les operations Git normales apres mission reussie.
- Livrable : docs d'autonomie Git.
- Criteres d'acceptation : push/merge non gates si tests OK et aucun risque.
- Tests : inspection documentaire.
- Gate : decision humaine validee le 2026-07-03.
- Statut : `done`.

### P0-M008 - Corriger l'integration autonome en direct-to-main

- Capability : pilotage projet.
- Milestone : M1 Engine foundation.
- Objectif : rendre le direct-to-main obligatoire pour missions standards.
- Livrable : AGENTS, protocoles et runbook mis a jour.
- Criteres d'acceptation : PR non utilisee comme chemin normal.
- Tests : inspection documentaire.
- Gate : decision humaine validee le 2026-07-03.
- Statut : `done`.

### P0-M009 - Realigner North Star, capabilities et roadmap volumetrique

- Capability : pilotage produit.
- Milestone : M1 Engine foundation.
- Objectif : aligner North Star, piliers, capability map, roadmap 0-14, gates et autonomie.
- Livrable : documents strategiques, ADR et log de realignement.
- Criteres d'acceptation : Codex choisit les futures missions par capability/milestone/gate/validation.
- Tests : tests documentaires, CLI de non-regression et `git diff --check`.
- Gate : changement de North Star valide par la demande humaine du 2026-07-04.
- Statut : `done` apres integration de cette mission.

## Phase 1 - Moteur Python pur

| Mission | Capability | Milestone | Statut |
| --- | --- | --- | --- |
| P1-M001 - Consolidate core data models | C-BOX, C-MODULE | M1 | `done` |
| P1-M002 - Harden config loading and validation | C-BOX, C-MODULE | M1 | `done` |
| P1-M003 - Improve CLI reporting | C-BOX, C-MODULE | M1 | `done` |
| P1-M004 - Ajouter une commande CLI de diagnostic | C-BOX, C-MODULE | M1 | `done` |

## Phase 2 - Layout 2D simple

| Mission | Capability | Milestone | Statut |
| --- | --- | --- | --- |
| P2-M001 - Formalize simple rectangular layout model | C-LAYOUT-2D | M2 | `done` |
| P2-M002 - Cover row_fill edge cases | C-LAYOUT-2D | M2 | `done` |
| P2-M003 - Ajouter une strategie grille explicite | C-LAYOUT-2D | M2 | `done` |
| P2-M004 - Exporter un resume de layout comparatif | C-LAYOUT-2D | M2 | `done` |

## Phase 3 - Tolerances, profils d'impression, clearances

| Mission | Capability | Milestone | Statut |
| --- | --- | --- | --- |
| P3-M001 - Classify exposed, internal and functional faces | C-MODULE | M2 | `done` |
| P3-M002 - Apply tolerance rules from face classification | C-MODULE | M2 | `done` |
| P3-M003 - Ajouter des profils d'impression | C-CALIBRATION | M11 | `done` |
| P3-M004 - Ajouter un protocole de calibration physique | C-CALIBRATION | M11 | `done` |

## Phase 4 - CAD IR et pipeline Fusion minimal

| Mission | Capability | Milestone | Statut |
| --- | --- | --- | --- |
| P4-M000 - Prepare Fusion 360 integration gate report | C-CAD-IR | M3 | `done` |
| P4-M001 - Definir le contrat de representation intermediaire CAD | C-CAD-IR | M3 | `done` |
| P4-M002 - Creer un squelette d'adaptateur Fusion 360 | C-FUSION-COMPACT | M3 | `done` |
| P4-M003 - Generer des blanks rectangulaires Fusion | C-FUSION-COMPACT | M3 | `done` |
| P4-M004 - Valider manuellement la generation Fusion minimale | C-FUSION-COMPACT | M3 | `done` |
| P4-M005 - Exporter une CAD IR depuis la CLI | C-CAD-IR | M3 | `done` |
| P4-M006 - Stabiliser le pipeline CAD IR vers Fusion | C-FUSION-COMPACT | M3 | `done` |

## Phase 5 - Cavites, receptacles et features ergonomiques

| Mission | Capability | Milestone | Statut |
| --- | --- | --- | --- |
| P5-M001 - Modeliser les cavites simples | C-CAVITY | M4 | `done` |
| P5-M002 - Ajouter logements de cartes et cartes sleevees | C-CAVITY | M4 | `done` |
| P5-M003 - Ajouter bacs a tokens, des et meeples | C-CAVITY | M4 | `done` |
| P5-M004 - Decrire les encoches de doigts et fonds arrondis comme features abstraites | C-FEATURE | M4 | `done` |
| P5-M005 - Gate generation Fusion reelle de cavites et features | C-FUSION-CAVITIES, C-FILLETS | M5 | `blocked` |
## Phase 6 - Generation Fusion reelle des cavites et features simples

### P6-M001 - Generer les cavites rectangulaires simples dans Fusion

- Capability : C-FUSION-CAVITIES.
- Milestone : M5 CAD cavities.
- Objectif : executer `subtract_rectangular_cavity` pour cavites rectangulaires simples.
- Livrable : add-in Fusion limite aux cuts rectangulaires, fixture CAD IR, smoke test manuel.
- Criteres d'acceptation : aucune logique metier dans Fusion, noms lisibles, dimensions controlees, absence STL/3MF.
- Tests : unitaires hors Fusion, CLI export CAD IR, `rg -n "adsk" src/board_game_insert_generator`, smoke test manuel Fusion.
- Gate : validation humaine validee le 2026-07-04 pour les cuts rectangulaires simples uniquement.
- Statut : `done`, `fusion-validated` pour les cavites rectangulaires simples, `print-validated: false`.


### P6-M001V - Valider manuellement les cavites rectangulaires Fusion

- Capability : C-FUSION-CAVITIES.
- Milestone : M5 CAD cavities.
- Objectif : lancer l'add-in P6-M001 dans Fusion avec une CAD IR de tray et mesurer blank, cavite et plancher conserve.
- Livrable : log de validation manuelle Fusion avec captures ou mesures.
- Criteres d'acceptation : message final OK, 1 blank, 1 cavity cut, dimensions et plancher conformes a la CAD IR.
- Tests : smoke test manuel Fusion, aucune validation d'impression revendiquee.
- Gate : action humaine Thomas realisee le 2026-07-04.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P6-M002 - Generer les encoches de doigts simples dans Fusion

- Capability : C-FILLETS.
- Milestone : M5 CAD ergonomic features.
- Objectif : executer les features d'encoche de doigt simples deja transportees par `describe_cavity_feature`, sans fond arrondi ni fillet.
- Livrable : add-in Fusion limite aux coupes d'encoches simples, tests hors Fusion, ADR et procedure de smoke test manuel.
- Criteres d'acceptation : aucune logique metier dans Fusion, coupe limitee au body cible, dimensions issues de la CAD IR, features courbes non revendiquees comme courbes reelles, absence STL/3MF.
- Tests : unitaires hors Fusion, CLI Markdown/JSON/export CAD IR sur `simple_tray` et `simple_finger_notch_tray`, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine fournie le 2026-07-06 pour les encoches de doigts simples uniquement.
- Statut : `done`, `fusion-validated` pour `top-open rectangular wall notch`, `print-validated: false`.

### P6-M002V - Valider manuellement les encoches de doigts Fusion

- Capability : C-FILLETS.
- Milestone : M5 CAD ergonomic features.
- Objectif : lancer l'add-in P6-M002 dans Fusion avec `examples/simple_finger_notch_tray.json` exporte en CAD IR, mesurer le blank, la cavite et la coupe d'encoche.
- Livrable : log de validation manuelle Fusion avec mesures et statut explicite `print-validated: false` tant qu'aucune impression 3D n'est faite.
- Criteres d'acceptation : message final avec `Simple finger notch features planned: 1`, `Simple finger notch sketches: 1`, `Simple top-open finger notch cuts: 1` et `Finger notch topology: top-open rectangular wall cut`, morsure top-open visible dans la paroi du body cible, dimensions conformes a la CAD IR, aucune geometrie courbe revendiquee.
- Tests : smoke test manuel Fusion.
- Gate : action humaine Thomas realisee le 2026-07-06 apres `b27c2e7`.
- Statut : `done`, `fusion-validated`, `print-validated: false`.


### P6-M003 - Formaliser la taxonomie des encoches et aides de prise

- Capability : C-FEATURE, C-FILLETS, C-ACCESS.
- Milestone : M5 CAD ergonomic features / M8 Ergonomic planner.
- Objectif : sortir du terme vague "encoche" et definir une taxonomie claire des aides de prise, sans nouvelle geometrie Fusion reelle.
- Livrable : enums/modeles ou contrats coeur si necessaire, documentation de taxonomie, rapports/CAD IR clarifies, tests hors Fusion.
- Criteres d'acceptation : distinction explicite entre `top_open_rectangular_notch`, `top_open_half_moon_notch`, `through_wall_window`, `blind_internal_thumb_scoop`, `side_relief_notch` et `dual_side_card_access`; statuts implemente/futur visibles; aucune nouvelle operation Fusion.
- Tests : unitaires, CLI Markdown/JSON/export CAD IR sur `simple_tray` et `simple_finger_notch_tray`, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : aucune tant que la mission reste abstraite et CAD-agnostic; gate obligatoire avant generation Fusion reelle de courbes, scoops, fillets, fonds arrondis ou booleans avances.
- Statut : `ready`.
## Phase 7 - Vue compacte / vue eclatee

### P7-M001 - Generer une vue eclatee Fusion basique

- Capability : C-FUSION-EXPLODED, C-CAD-IR.
- Milestone : M5 CAD inspection views.
- Objectif : conserver la vue compacte et creer une vue eclatee par occurrence liee du meme composant physique, espacee a plat pour inspection.
- Livrable : mode add-in `compact_and_exploded`, composants Fusion uniques, occurrences compactes/eclatees liees, plan hors Fusion teste, ADR corrective, documentation et procedure de smoke test manuel.
- Criteres d'acceptation : Fusion ne recalcule pas le solveur ; composants sources nommes lisiblement ; occurrences compactes/eclatees liees au meme composant sans renommage direct de `Occurrence.name` ; roles compact/exploded reportes dans le message ou le plan ; dimensions issues de la CAD IR ; coeur Python sans `adsk` ; validation manuelle requise.
- Tests : unitaires hors Fusion, CLI/export CAD IR, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine fournie le 2026-07-06 pour une vue eclatee basique uniquement.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P7-M001V4 - Valider manuellement la vue eclatee Fusion basique en document Assembly-compatible

- Capability : C-FUSION-EXPLODED.
- Milestone : M5 CAD inspection views.
- Objectif : lancer l'add-in P7-M001 corrige dans un document Fusion Assembly-compatible avec `simple_asset_executable_plan` exporte en CAD IR et verifier que les occurrences compactes/eclatees referencent les memes composants sans exiger de noms exacts d'occurrences.
- Livrable : validation humaine Fusion avec message, noms, espacement, dimensions observees et verification que compact/exploded sont deux occurrences du meme composant.
- Criteres d'acceptation : vue compacte conservee, occurrences `exploded` visibles a droite de la boite, composants sources partages entre compact/exploded, composants sources nommes lisiblement, message `Occurrence direct rename attempted: no`, dimensions conformes ou acceptables, message `assembly document required` si Part Design, aucun export STL/3MF.
- Tests : smoke test manuel Fusion, aucune validation d'impression revendiquee.
- Gate : action humaine Thomas realisee le 2026-07-06.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P11-M001 - Generer une vue compacte Fusion depuis placements grille

- Capability : C-FUSION-COMPACT, C-GRID-3D, C-CAD-IR.
- Milestone : M3 CAD pipeline / M7 Volumetric planner.
- Objectif : consommer `metadata.executable_asset_plan` pour creer des modules rectangulaires positionnes X/Y/Z dans Fusion.
- Livrable : add-in Fusion enrichi, plan hors Fusion teste, ADR, procedure de smoke test manuel.
- Criteres d'acceptation : Fusion ne recalcule pas le solveur ; bodies positionnes par CAD IR ; coeur Python sans `adsk` ; validation manuelle Fusion documentee.
- Tests : unitaires hors Fusion, CLI/export CAD IR, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine fournie le 2026-07-06 pour cette generation compacte uniquement.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P11-M001V - Valider manuellement la vue compacte Fusion depuis placements grille

- Capability : C-FUSION-COMPACT, C-GRID-3D, C-CAD-IR.
- Milestone : M3 CAD pipeline / M7 Volumetric planner.
- Objectif : lancer l'add-in P11-M001 dans Fusion avec `simple_asset_executable_plan` exporte en CAD IR et verifier le module asset-first positionne par grille.
- Livrable : validation humaine Fusion avec message, position et dimensions observees.
- Criteres d'acceptation : message conforme, `Grid-positioned module bodies: 1`, zero module refuse, position `X 30.0 mm`, `Y 0.0 mm`, `Z 0.0 mm` conforme ou acceptable, taille `30.0 x 30.0 x 10.0 mm` conforme ou acceptable.
- Tests : smoke test manuel Fusion, aucune validation d'impression revendiquee.
- Gate : action humaine Thomas realisee le 2026-07-06.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P11-M002 - Generer une scene Fusion multi-layer depuis placements grille X/Y/Z

- Capability : C-FUSION-COMPACT, C-FUSION-EXPLODED, C-GRID-3D, C-CAD-IR.
- Milestone : M7 Volumetric planner / M5 CAD inspection views.
- Objectif : consommer une CAD IR asset-first avec placements grille X/Y/Z multi-layer pour creer une scene Fusion compacte + eclatee liee.
- Livrable : exemple `simple_multilayer_grid_scene.json`, compteurs multi-layer dans rapports/plan Fusion, add-in affichant modules multi-layer et Z placements, tests hors Fusion et procedure de smoke test.
- Criteres d'acceptation : un module bas, un module plus haut, un placement Z explicite, occurrences compactes/eclatees liees, Fusion sans recalcul de solveur/tolerance, coeur Python sans `adsk`.
- Tests : unitaires hors Fusion, CLI Markdown/JSON/export CAD IR, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine fournie le 2026-07-06 pour cette generation multi-layer bornee uniquement.
- Statut : `done`, `fusion-validated` pour la generation multi-layer, `print-validated: false`.

### P11-M002V - Valider manuellement la scene Fusion multi-layer

- Capability : C-FUSION-COMPACT, C-FUSION-EXPLODED, C-GRID-3D, C-CAD-IR.
- Milestone : M7 Volumetric planner / M5 CAD inspection views.
- Objectif : lancer l'add-in avec la CAD IR exportee depuis `simple_multilayer_grid_scene` et verifier les modules multi-hauteurs en vue compacte/eclatee.
- Livrable : validation humaine Fusion avec message, position Z, dimensions et verification des occurrences liees.
- Criteres d'acceptation : message `Multi-layer grid modules planned: 1`, `Grid modules with Z placement: 1`, `Grid module height variants: 2`, compact/exploded visibles, module haut a `Z 10.0 mm`, occurrences liees, aucune validation d'impression revendiquee. La validation P11-M002V a signale une ambiguite dimensionnelle corrigee ensuite par P11-M003.
- Tests : smoke test manuel Fusion, aucune validation d'impression revendiquee.
- Gate : action humaine Thomas realisee le 2026-07-07.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P11-M003 - Corriger le sizing asset-first et ajouter une commande UI Fusion minimale

- Capability : C-FUSION-COMPACT, C-FUSION-EXPLODED, C-GRID-3D, C-CAD-IR, C-FUSION-UI.
- Milestone : M7 Volumetric planner / M14 Usable beta.
- Objectif : distinguer span grille, asset-fit et taille imprimable pour les modules asset-first generes, puis lancer la generation Fusion depuis une commande UI minimale.
- Livrable : `theoretical_grid_extent_mm`, `asset_fit_size_mm`, `printable_body_size_mm`, rapports Markdown/JSON enrichis, add-in avec champ `CAD IR JSON path` et mode `compact_only` / `compact_and_exploded`, ADR et procedure de smoke test.
- Criteres d'acceptation : Fusion ne recalcule pas le solveur ; les bodies asset-first utilisent la taille imprimable ; les spans grille restent visibles comme metadata ; l'utilisateur n'a plus a editer manuellement `cad_ir_path.txt` ou `exploded_view_mode.txt` pour le flux courant ; coeur Python sans `adsk`.
- Tests : unitaires hors Fusion, CLI Markdown/JSON/export CAD IR sur exemples pertinents, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine fournie le 2026-07-07 apres P11-M002V, limitee a sizing et UI minimale.
- Statut : `done`, `fusion-validated`, corrections P11-M003V2/P11-M003V3/P11-M003V4 codees et validees humainement dans Fusion, `print-validated: false`.

### P11-M003V - Valider manuellement la commande UI Fusion et le sizing asset-first

- Capability : C-FUSION-UI, C-FUSION-COMPACT, C-FUSION-EXPLODED, C-GRID-3D.
- Milestone : M14 Usable beta / M7 Volumetric planner.
- Objectif : lancer l'add-in via la commande UI, choisir une CAD IR exportee et verifier les dimensions imprimables asset-first corrigees.
- Livrable : validation humaine Fusion avec message, chemin choisi, mode choisi, dimensions et statut `print-validated: false`.
- Criteres d'acceptation : commande `Generate Board Game Insert` visible, champ chemin utilisable, mode `compact_and_exploded` ou `compact_only` applique, `simple_asset_executable_plan` genere un module asset-first `25.6 x 25.6 x 9.8 mm`, `simple_multilayer_grid_scene` genere les modules `61.6 x 61.6 x 7.8 mm` et `37.6 x 37.6 x 17.8 mm`, spans grille visibles comme metadata/rapport, occurrences liees conservees.
- Tests : smoke test manuel Fusion, aucune validation d'impression revendiquee.
- Gate : action humaine requise.
- Statut : `done`, KO partiel : scene generee mais dimensions effectives non verifiables dans le message Fusion.

### P11-M003V2 - Valider le rapport dimensionnel Fusion planned/actual

- Capability : C-FUSION-UI, C-FUSION-COMPACT, C-GRID-3D.
- Milestone : M14 Usable beta / M7 Volumetric planner.
- Objectif : relancer la commande Fusion avec `simple_asset_executable_plan` et `simple_multilayer_grid_scene`, puis verifier que le message affiche pour chaque module `grid span`, `printable body planned`, `actual Fusion body bbox` et `size match yes`.
- Livrable : validation humaine Fusion avec dimensions prevues/reelles et statut `print-validated: false`.
- Criteres d'acceptation : Fusion utilise `printable_body_size_mm`; `theoretical_grid_extent_mm` reste metadata; `actual Fusion body bbox` correspond aux dimensions imprimables attendues; aucune nouvelle geometrie ou tolerance n'est ajoutee.
- Tests : smoke test manuel Fusion, aucune validation d'impression revendiquee.
- Gate : action humaine requise.
- Statut : `blocked`, remplace par `P11-M003V3` apres KO sur commande UI visible.

### P11-M003V3 - Valider la commande UI Fusion visible et le rapport planned/actual

- Capability : C-FUSION-UI, C-FUSION-COMPACT, C-GRID-3D.
- Milestone : M14 Usable beta / M7 Volumetric planner.
- Objectif : lancer l'add-in, ouvrir la boite de dialogue `Generate Board Game Insert`, renseigner `CAD IR JSON path`, choisir `compact_and_exploded`, generer la scene et verifier le `Body sizing report`.
- Livrable : validation humaine Fusion avec commande visible, chemin choisi, mode choisi, dimensions prevues/reelles et statut `print-validated: false`.
- Criteres d'acceptation : la generation normale passe par la commande UI sans modifier `cad_ir_path.txt` ni `exploded_view_mode.txt`; Fusion utilise `printable_body_size_mm`; `actual Fusion body bbox` correspond aux dimensions imprimables attendues; aucune nouvelle geometrie ou tolerance n'est ajoutee.
- Tests : smoke test manuel Fusion, aucune validation d'impression revendiquee.
- Gate : action humaine requise.
- Statut : `blocked`, remplace par `P11-M003V4` apres KO sur ambiguite scene produit/fixture.

### P11-M003V4 - Valider la scene produit asset-first non ambigue

- Capability : C-FUSION-UI, C-FUSION-COMPACT, C-GRID-3D.
- Milestone : M14 Usable beta / M7 Volumetric planner.
- Objectif : lancer l'add-in avec `simple_asset_product_scene`, verifier un seul module asset-first, aucun blank legacy, le mapping source et le sizing planned/actual.
- Livrable : validation humaine Fusion avec `Module source mapping`, `Body sizing report`, dimensions, origine et statut `print-validated: false`.
- Criteres d'acceptation : aucune generation redondante non documentee ; source `asset_candidate`, placement `grid_placement`, assets contenus, clearances peripherique/inter-module et taille imprimable lisibles ; aucune nouvelle geometrie ou tolerance n'est ajoutee.
- Tests : smoke test manuel Fusion, aucune validation d'impression revendiquee.
- Gate : action humaine Thomas realisee le 2026-07-07 apres le commit `134863c`.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P7-M002 - Generer une vue Fusion eclatee minimale

- Capability : C-FUSION-EXPLODED.
- Milestone : M5 CAD inspection views.
- Objectif : creer une vue inspectable a plat depuis une CAD IR deja resolue.
- Livrable : generation Fusion limitee aux blanks deja autorises.
- Criteres d'acceptation : pas de recalcul, noms stables, smoke test manuel.
- Tests : hors Fusion + smoke Fusion.
- Gate : validation humaine si repositionnement CAD non trivial.
- Statut : `blocked`.

## Phase 8 - Grille volumetrique 3D et etages

### P8-M001 - Specifier la grille volumetrique 3D et les layers

- Capability : C-GRID-3D, C-LAYERS.
- Milestone : M7 Volumetric planner.
- Objectif : representer une grille X/Y/Z declarative, ses layers, placements explicites, zones reservees/interdites et volumes libres.
- Livrable : modeles Python purs, bloc config `volumetric_grid`, validation, rapports Markdown/JSON, metadata CAD IR, exemple `simple_3d_grid.json`, ADR et tests.
- Criteres d'acceptation : cellule, corps imprimable, layer et reservation restent distincts ; un module peut occuper plusieurs unites X/Y/Z ; aucun solveur ni Fusion.
- Tests : unitaires, CLI Markdown/JSON/export CAD IR sur exemples existants et `simple_3d_grid`, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine fournie le 2026-07-06 pour une extension schema additive et CAD-agnostic.
- Statut : `done`, `implemented-cad-ir`.

### P8-M002 - Approfondir reservations, ordre de retrait et surfaces de support abstraites

- Capability : C-LAYERS, C-RESERVATION, C-ACCESS.
- Milestone : M7 Volumetric planner / M8 Ergonomic planner.
- Objectif : enrichir le modele pur Python avec ordre de retrait, reservations verticales plus explicites et surfaces de support abstraites, sans solveur automatique ni Fusion.
- Livrable : modeles et rapports CAD-agnostic, support_surfaces, removal_sequence, exemple `simple_3d_reservations.json`, tests unitaires, docs de contrat et ADR.
- Criteres d'acceptation : aucune promesse de support physique, aucune generation Fusion, aucune dependance lourde.
- Tests : unitaires, CLI Markdown/JSON/export CAD IR sur exemples pertinents.
- Gate : aucune si additive et non physique ; gate impression avant validation de support.
- Statut : `done`, `implemented-cad-ir`.

### P8-M003 - Representer empilement et supports abstraits

- Capability : C-STACKING.
- Milestone : M7 Volumetric planner.
- Objectif : documenter support, charge, ordre d'empilement et surfaces porteuses.
- Livrable : modele abstrait et rapports, sans validation physique.
- Criteres d'acceptation : pas de promesse d'impression ni de resistance.
- Tests : unitaires ou documentaires selon implementation.
- Gate : impression reelle avant validation physique.
- Statut : `todo`.

## Phase 9 - Assets, plateaux, boards, regles et reservations de couches

### P9-M001 - Specifier le schema asset-first

- Capability : C-ASSET, C-RESERVATION.
- Milestone : M6 Asset-first project model.
- Objectif : decrire assets, quantites, dimensions approximatives et reservations.
- Livrable : schema cible documente dans `ASSET_MODEL_STRATEGY` et `CONFIG_SCHEMA`, exemple non executable, ADR et log.
- Criteres d'acceptation : modules et assets restent distincts ; P9-M001 ne modifie pas encore le loader.
- Tests : test documentaire et non-regression CLI.
- Gate : schema public si implementation loader.
- Statut : `done`, `designed`.

### P9-M002 - Charger des assets JSON sans generation de modules

- Capability : C-ASSET.
- Milestone : M6 Asset-first project model.
- Objectif : accepter des assets sans encore deriver de layout.
- Livrable : loader strict, validation, rapports Markdown/JSON, metadata CAD IR, exemple `simple_assets.json` et tests.
- Criteres d'acceptation : aucune regression des exemples module-first ; aucun module derive automatiquement.
- Tests : unitaires + CLI.
- Gate : si incompatibilite schema.
- Statut : `done`, `implemented-cad-ir`.

## Phase 10 - Solveur semi-automatique et scoring

### P10-M001 - Definir les criteres de scoring de variantes

- Capability : C-SOLVER.
- Milestone : M10 Semi-automatic solver.
- Objectif : documenter compacite, accessibilite, nombre de modules, printability et setup.
- Livrable : strategie et exemples de scoring, sans optimiseur lourd.
- Criteres d'acceptation : scores explicables et non magiques ; aucun solveur ni generation de variantes.
- Tests : documentaires et CLI de non-regression.
- Gate : dependance lourde si solveur externe.
- Statut : `done`, `designed`.

### P10-M002 - Enumerer quelques variantes simples hors solveur complet

- Capability : C-SOLVER.
- Milestone : M10 Semi-automatic solver.
- Objectif : comparer options deterministes simples.
- Livrable : `variant_comparison` Markdown/JSON sur strategies deja implementees, avec sous-scores et raisons.
- Criteres d'acceptation : pas d'optimiseur opaque, pas de nouvelle strategie de placement, pas de dependance lourde.
- Tests : unitaires + CLI JSON/Markdown.
- Gate : aucune si implementation simple.
- Statut : `done`, `implemented-core`.

### P10-M003 - Rapporter les variantes refusees avec raisons detaillees

- Capability : C-SOLVER.
- Milestone : M10 Semi-automatic solver.
- Objectif : enrichir les cas `rejected` avec raisons structurees et references de contraintes.
- Livrable : reporting et tests, sans nouveau solveur.
- Criteres d'acceptation : raisons actionnables, pas d'optimiseur global.
- Tests : unitaires + CLI JSON/Markdown.
- Gate : aucune si report-only.
- Statut : `done`, `implemented-core`.

### P10-M004 - Generer des candidats de modules depuis assets simples

- Capability : C-ASSET, C-SOLVER.
- Milestone : M6 Asset-first project model / M10 Semi-automatic solver.
- Objectif : produire une synthese deterministe `assets -> module_candidates` sans modifier `modules` ni lancer de solveur global.
- Livrable : rapports Markdown/JSON, metadata CAD IR additive si compatible, exemple et tests.
- Criteres d'acceptation : assets et modules restent distincts ; les candidats sont explicables, bornes et non generes dans Fusion.
- Tests : unitaires + CLI Markdown/JSON/export CAD IR sur exemples assets.
- Gate : stop si generation automatique de layout complexe, changement incompatible CAD IR ou geometrie Fusion reelle.
- Statut : `done`, `implemented-core`.

### P10-M005 - Generer des variantes simples depuis candidats assets

- Capability : C-SOLVER.
- Milestone : M10 Semi-automatic solver.
- Objectif : exposer une ou deux variantes deterministes simples construites depuis `module_candidates`, sans optimiseur global.
- Livrable : rapports Markdown/JSON, tests et documentation de limites.
- Criteres d'acceptation : variante recommandable ou rejetee avec raisons ; aucune generation Fusion et aucune mutation automatique de config.
- Tests : unitaires + CLI Markdown/JSON/export CAD IR sur exemples assets.
- Gate : stop si solveur complexe, backtracking, optimisation globale ou changement incompatible CAD IR devient necessaire.
- Statut : `done`, `implemented-core`.

### P10-M006 - Regrouper deterministiquement des assets compatibles

- Capability : C-ASSET, C-SOLVER.
- Milestone : M6 Asset-first project model / M10 Semi-automatic solver.
- Objectif : grouper uniquement des assets compatibles par kind, intent et confiance de mesure, sans optimiser globalement.
- Livrable : `module_candidates` enrichis avec groupes simples et raisons.
- Criteres d'acceptation : regroupement borne, explicable et reversible ; aucun placement complexe ni Fusion.
- Tests : unitaires + CLI Markdown/JSON/export CAD IR sur exemple assets dedie si necessaire.
- Gate : stop si grouping heterogene complexe, solveur global ou changement incompatible du schema devient necessaire.
- Statut : `done`, `implemented-core`.

### P10-M007 - Couvrir une variante asset rejetee par dimensions

- Capability : C-SOLVER.
- Milestone : M10 Semi-automatic solver.
- Objectif : ajouter un exemple et des tests ou une variante asset candidate est rejetee avec raison structuree.
- Livrable : exemple JSON, tests, rapports Markdown/JSON et CAD IR metadata.
- Criteres d'acceptation : rejet explicite `DOES_NOT_FIT` ou `DIMENSIONS_INCOMPATIBLE`; aucune generation Fusion.
- Tests : unitaires + CLI Markdown/JSON/export CAD IR sur le nouvel exemple.
- Gate : aucune si report-only; stop si cela demande un solveur complexe.
- Statut : `done`, `implemented-core`.

### P10-M008 - Generer un plan concret asset-first et placement grille greedy

- Capability : C-ASSET, C-SOLVER, C-GRID-3D, C-CAD-IR.
- Milestone : M6 Asset-first project model / M7 Volumetric planner / M10 Semi-automatic solver.
- Objectif : transformer la variante asset recommandee en modules generes abstraits puis les placer dans une grille 3D par heuristique greedy bornee.
- Livrable : `executable_asset_plan` Markdown/JSON, metadata CAD IR additive, exemple produit `simple_asset_product_scene.json`, fixture technique `simple_asset_executable_plan.json` et tests.
- Criteres d'acceptation : positions X/Y/Z en unites, dimensions millimetres derivees de la grille, refus actionnables, aucune generation Fusion reelle.
- Tests : unitaires + CLI Markdown/JSON/export CAD IR sur exemples assets et grille.
- Gate : stop si solveur complexe, backtracking, optimisation globale, schema incompatible ou generation Fusion devient necessaire.
- Statut : `done`, `implemented-cad-ir`.

### P10-GATE - Autoriser un solveur plus automatique

- Capability : C-SOLVER.
- Milestone : M10 Semi-automatic solver.
- Objectif : decider si BGIG doit passer d'heuristiques bornees a un solveur plus automatique.
- Livrable : rapport de gate avant optimisation globale, backtracking, modules composites ou generation Fusion reelle.
- Criteres d'acceptation : perimetre explicite, risques et validations attendues.
- Tests : inspection documentaire.
- Gate : architecture/produit obligatoire avant solveur complexe ou comportement automatique opaque.
- Statut : `blocked`.

## Phase 11 - Modules composites et formes soudees

### P11-C001 - Representer les modules composites par primitives soudees

- Capability : C-COMPOSITE.
- Milestone : M9 Composite modules.
- Objectif : decrire primitives soudees et faces internes sans jeu.
- Livrable : modele pur, tests de faces internal/welded.
- Criteres d'acceptation : aucun jeu inter-primitives soudees.
- Tests : unitaires tolerance/faces.
- Gate : modules composites.
- Statut : `todo`.

### P11-C002 - Generer les unions Fusion pour composites simples

- Capability : C-COMPOSITE, C-FUSION-COMPACT.
- Milestone : M9 Composite modules.
- Objectif : creer une premiere union CAD simple depuis CAD IR.
- Livrable : generation Fusion sous gate.
- Criteres d'acceptation : smoke test manuel, aucune logique metier Fusion.
- Tests : hors Fusion + Fusion manuel.
- Gate : obligatoire.
- Statut : `blocked`.

## Phase P12-UI - Interface Fusion utilisable

### P12-UI-M001 - Stabiliser le bouton toolbar Fusion relancable

- Capability : C-FUSION-UI.
- Milestone : M14 Usable beta.
- Objectif : permettre de rouvrir BGIG depuis Fusion sans redemarrer l'add-in.
- Livrable : constantes UI centralisees, plan de lancement testable, bouton toolbar documente, commande classique conservee.
- Criteres d'acceptation : `run(context)` ouvre encore la commande au premier lancement ; le bouton `Generate Board Game Insert` est ajoute dans `Design workspace > Utilities > Add-Ins` ; cliquer le bouton rouvre la commande ; les fichiers `cad_ir_path.txt` et `exploded_view_mode.txt` restent seulement des defaults/fallbacks ; coeur Python sans `adsk`.
- Tests : unitaires hors Fusion, py_compile add-in, CLI/export CAD IR exemples P12, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine fournie pour sprint P12-UI ; smoke test Fusion requis avant `fusion-validated`.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P12-UI-M001V - Valider manuellement le bouton toolbar relancable

- Capability : C-FUSION-UI.
- Milestone : M14 Usable beta.
- Objectif : lancer l'add-in dans Fusion, verifier le bouton toolbar, fermer ou defocaliser la commande, puis la rouvrir sans redemarrer l'add-in.
- Livrable : validation humaine Fusion avec emplacement observe, reouverture et generation depuis UI.
- Criteres d'acceptation : bouton visible, commande rouvrable, champ `CAD IR JSON path`, choix de mode, generation `simple_asset_product_scene`, `Body sizing report` conserve, vues compact/exploded liees conservees.
- Tests : smoke test manuel Fusion, aucune validation d'impression revendiquee.
- Gate : action humaine Thomas realisee le 2026-07-07 apres le commit `a12ef42`.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P12-UI-M002+ - UI Fusion parametrique V0

- Capability : C-FUSION-UI.
- Milestone : M14 Usable beta.
- Objectif : faire evoluer la commande Fusion relancable vers une premiere UI parametrique V0 sans palette HTML large ni nouvelle geometrie.
- Livrable : champs CAD IR/config/projet, overrides boite/grille/epaisseurs/clearances/profil, actions `generate`, `regenerate`, `clear_bgig_scene`, config temporaire -> CAD IR temporaire, tagging BGIG pour nettoyage conservateur, tests hors Fusion, ADR et documentation.
- Criteres d'acceptation : le mode CAD IR direct reste fonctionnel ; le mode config peut generer une CAD IR temporaire si le repo BGIG est accessible ; regenerate nettoie uniquement les objets BGIG tagues ; clear refuse de supprimer les objets non tagues ; coeur Python sans `adsk` ; validation Fusion manuelle requise.
- Tests : unitaires hors Fusion, py_compile add-in, CLI Markdown/JSON/export CAD IR exemples P12, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine fournie le 2026-07-07 pour P12-UI-M002+ ; smoke test Fusion requis avant `fusion-validated`.
- Statut : `done`, `implemented-fusion`, `manual_validation_required`, `print-validated: false`.

### P12-UI-M002V - Valider manuellement l'UI Fusion parametrique V0

- Capability : C-FUSION-UI.
- Milestone : M14 Usable beta.
- Objectif : lancer l'add-in dans Fusion et verifier le flux UI P12-M002+.
- Livrable : validation humaine Fusion avec generation depuis CAD IR, generation depuis config, regenerate, clear et verification que les objets non BGIG ne sont pas supprimes.
- Criteres d'acceptation : commande visible ; champs `CAD IR JSON path`, `BGIG config JSON path`, `BGIG project root`, action, mode et parametres visibles ; `generate` fonctionne ; `regenerate` nettoie/recree les objets BGIG tagues ; `clear_bgig_scene` supprime uniquement les objets tagues ; message final affiche source, action, overrides, `Body sizing report` et `Print validation: false`.
- Tests : smoke test manuel Fusion, aucune validation d'impression revendiquee.
- Gate : action humaine requise.
- Statut : `manual_validation_required`.
## Phase 12 - Couvercles, mecanismes et empilement avance

### P12-M001 - Modeliser les couvercles poses

- Capability : C-STACKING, futurs mecanismes.
- Milestone : M13 Advanced mechanisms.
- Objectif : decrire couvercle simple, jeu vertical et contraintes de retrait.
- Livrable : modele abstrait et tests.
- Criteres d'acceptation : pas de mecanisme imprime declare valide.
- Tests : unitaires/CLI.
- Gate : mecanismes et impression reelle.
- Statut : `todo`.

### P12-M002 - Ajouter couvercles coulissants, rainures, clips ou charnieres

- Capability : futurs mecanismes.
- Milestone : M13 Advanced mechanisms.
- Objectif : etudier puis implementer un mecanisme a la fois.
- Livrable : ADR + mission limitee par mecanisme.
- Criteres d'acceptation : validation physique requise.
- Tests : unitaires + impression future.
- Gate : obligatoire.
- Statut : `blocked`.

## Phase 13 - Esthetique, embossage, gravure, textures, decorations

### P13-M001 - Definir le langage visuel parametrique

- Capability : C-AESTHETIC.
- Milestone : M12 Design language.
- Objectif : cadrer labels, gravures, motifs et decoration sans casser la fonction.
- Livrable : strategie esthetique et contraintes epaisseur/printability.
- Criteres d'acceptation : couche optionnelle, desactivable et gate-aware.
- Tests : inspection documentaire.
- Gate : decision esthetique structurante.
- Statut : `todo`.

### P13-M002 - Ajouter texte, labels et gravure abstraite

- Capability : C-AESTHETIC, C-CAD-IR.
- Milestone : M12 Design language.
- Objectif : transporter l'intention de labels sans generation Fusion reelle.
- Livrable : CAD IR additive et rapports.
- Criteres d'acceptation : aucune geometrie Fusion sans gate.
- Tests : unitaires CAD IR.
- Gate : si generation CAD.
- Statut : `todo`.

## Phase 14 - Calibration, impression reelle, packaging et beta utilisable

### P14-M001 - Creer des exemples reels complets

- Capability : C-CALIBRATION.
- Milestone : M14 Usable beta.
- Objectif : choisir un jeu reel et documenter une configuration complete.
- Livrable : exemple, rapport, CAD IR, checklist Fusion et impression.
- Criteres d'acceptation : limites et validations affichees, pas de promesse non testee.
- Tests : CLI + Fusion/print selon gate.
- Gate : impression reelle et release.
- Statut : `todo`.

### P14-M002 - Definir le processus de release stable

- Capability : release future.
- Milestone : M14 Usable beta.
- Objectif : cadrer versioning, changelog, packaging et distribution.
- Livrable : checklist release.
- Criteres d'acceptation : aucun statut stable sans preuves.
- Tests : inspection documentaire.
- Gate : publication de release.
- Statut : `todo`.
