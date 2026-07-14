# Backlog

Derniere mise a jour : 2026-07-11

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
- Statut : `done`, `implemented-local-ui`, `implemented-loopback-adapter`, `print-validated: false`.

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
- Statut : `done`, `implemented-local-ui`, `implemented-loopback-adapter`, `print-validated: false`.

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
- Statut : `done`, `implemented-local-ui`, `implemented-loopback-adapter`, `print-validated: false`.

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
- Gate : validation humaine P12-UI-M002V7 confirmee dans Fusion apres correction registry inspect ; prochaine extension produit sous gate.
- Statut : `done`, `fusion-validated` apres P12-UI-M002V7 et validation du reporting inspect deduplique, `print-validated: false`.

### P12-UI-M002V7 - Valider registry BGIG et inspect read-only

- Capability : C-FUSION-UI.
- Milestone : M14 Usable beta.
- Objectif : lancer l'add-in dans Fusion et verifier le flux UI P12-M002V7 : le flux commence par `inspect_bgig_scene`, les entites BGIG ont des attributs `scene_id`/`role`/`module_id`, `generate` refuse toute scene/objet BGIG existant, `regenerate` remplace sans doublon et `clear_bgig_scene` supprime toute la scene BGIG en preservant l'objet non BGIG.
- Livrable : validation humaine Fusion avec generation depuis CAD IR, generation depuis config, regenerate, clear et verification que les objets non BGIG ne sont pas supprimes.
- Criteres d'acceptation : commande visible ; `compact_only` cree 1 racine BGIG et N occurrences compactes ; `compact_and_exploded` cree 1 racine BGIG, N compactes et N eclatees liees ; aucun helper source ; `Legacy bodies created: 0` ; second `generate` refuse sans doublon ; deux `regenerate` gardent exactement 1 racine BGIG ; `clear_bgig_scene` affiche `BGIG scene roots deleted`, `BGIG objects remaining after clear: 0` et preserve les objets non BGIG ; message final affiche source, action, scene roots before/created/deleted/after, suppressions, `Body sizing report` et `Print validation: false`.
- Tests : smoke test manuel Fusion, aucune validation d'impression revendiquee.
- Gate : action humaine Thomas realisee pour la validation Fusion P12-UI-M002V7 apres correction registry inspect. Inspect avant generation, generate, inspect apres generation, regenerate et clear sont valides ; ownership racine BGIG et reporting deduplique valides ; impression 3D non validee.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P12-M003 - quick_parametric_box fonctionnel

- Capability : C-FUSION-UI.
- Milestone : M14 Usable beta.
- Objectif : rendre le mode `quick_parametric_box` de la commande Fusion exploitable sans fichier de config BGIG.
- Livrable : builder CAD IR temporaire depuis champs UI, rapport Fusion des valeurs saisies, tests hors Fusion, documentation et smoke test P12-M003V.
- Criteres d'acceptation : generation via `quick_parametric_box`, `generate`/`regenerate`/`clear_bgig_scene` conserves, `Body sizing report`, `Print validation: false`, coeur Python sans `adsk`.
- Tests : unitaires hors Fusion, py_compile add-in, CLI Markdown/JSON/export CAD IR exemples P12, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : smoke test humain Fusion P12-M003V realise le 2026-07-08.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P12-M003V - Valider quick_parametric_box dans Fusion

- Capability : C-FUSION-UI.
- Milestone : M14 Usable beta.
- Objectif : verifier dans Fusion que les champs UI quick changent bien la scene generee.
- Livrable : validation humaine avec generate, regenerate, clear et rapport de sizing.
- Criteres d'acceptation : mode `quick_parametric_box` visible et actif, CAD IR temporaire creee, scene V0 generee, changements de valeurs visibles apres regenerate, clear propre, aucune validation d'impression revendiquee.
- Tests : smoke test manuel Fusion.
- Gate : action humaine Thomas realisee le 2026-07-08 pour le flux `generate` en `quick_parametric_box` / `compact_only`.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P12-M004 - Persistance des champs UI et regeneration confortable

- Capability : C-FUSION-UI.
- Milestone : M14 Usable beta.
- Objectif : rendre la commande Fusion plus confortable pour iterer sur des parametres sans ressaisie apres fermeture/reouverture.
- Livrable : persistance `bgig_ui_settings.json` de l action, input mode, generation mode, chemins CAD IR/config/root et champs parametriques P12 ; rehydratation dans `commandCreated` ; champs `quick_parametric_box` pre-remplis ; action `regenerate` preferee si une scene BGIG existe deja ; documentation et smoke test P12-M004V.
- Criteres d acceptation : valeurs retrouvees apres generation et reouverture, modification d une seule valeur puis `regenerate`, remplacement sans doublon, derniere valeur retrouvee a la reouverture, `clear_bgig_scene` preserve les objets non BGIG, coeur Python sans `adsk`.
- Tests : unitaires hors Fusion, py_compile add-in, CLI Markdown/JSON/export CAD IR exemples P12, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine Fusion P12-M004V realisee le 2026-07-08 apres `ab488dc`.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P12-M004V - Valider persistance UI et regeneration confortable dans Fusion

- Capability : C-FUSION-UI.
- Milestone : M14 Usable beta.
- Objectif : verifier dans Fusion que les valeurs `quick_parametric_box` sont restaurees apres reouverture, qu une valeur modifiee est conservee apres `regenerate`, et que `clear_bgig_scene` preserve les objets non BGIG.
- Livrable : validation humaine avec generate, reouverture, rehydratation, modification `box_inner_x_mm = 160`, regenerate, reouverture, clear et rapport registry.
- Criteres d acceptation : aucune ressaisie complete requise, scene remplacee sans doublon, derniere valeur visible, registry OK, objets non BGIG preserves, aucune validation d impression revendiquee.
- Tests : smoke test manuel Fusion.
- Gate : action humaine requise.
- Statut : `done`, `fusion-validated` apres smoke test humain confirme le 2026-07-08 sur `ab488dc`; premier essai KO apres `c6cba19` documente et corrige par settings sans BOM / lecture `utf-8-sig`; `print-validated: false`.

### P12-M004A - Automatiser la preparation des smoke tests Fusion

- Capability : C-FUSION-UI, pilotage projet.
- Milestone : M14 Usable beta.
- Objectif : supprimer les commandes PowerShell repetitives de la charge humaine avant les validations Fusion.
- Livrable : scripts `scripts/fusion/` pour installer/verifier l'add-in, preparer un smoke test CAD IR depuis config et precharger le smoke test `quick_parametric_box`, plus documentation durable.
- Criteres d acceptation : Codex peut preparer P12-M004V depuis le repo, detecte un blocage AppData sans pretendre installer, et ne fournit a Thomas que les actions Fusion restantes.
- Tests : unitaires, py_compile add-in, dry-run scripts, execution reelle si permissions AppData disponibles, `git diff --check`, absence `adsk` dans le coeur Python.
- Gate : gate humaine validee le 2026-07-08 pour automatisation locale.
- Statut : `done` apres integration, sans validation produit Fusion.
## Sprint P13 - Asset input UI V0

### P13-M001 - quick_asset_box UI V0

- Capability : C-ASSET, C-FUSION-UI, C-SOLVER.
- Milestone : M14 Usable beta.
- Objectif : permettre une premiere saisie d'assets simples depuis la commande Fusion sans ecrire de JSON a la main.
- Livrable : mode `quick_asset_box`, champ texte assets, config temporaire stricte, reuse du pipeline assets existant, reporting Fusion, persistance settings, script de smoke test.
- Criteres d'acceptation : assets lus/refuses reportes, candidats modules visibles, variante recommandee visible, modules places via CAD IR existante, limites V0 explicites (`asset_items_visualized: no`, `asset_cavities_generated: no`, `count_aware_storage_sizing: no`), generate/regenerate/clear conserves, coeur Python sans `adsk`.
- Tests : unitaires Fusion skeleton, py_compile, suite complete, CLI Markdown/JSON/export CAD IR exemples P13/P12, dry-run et preparation smoke Fusion.
- Gate : validation humaine Fusion `P13-M001V` validee le 2026-07-08.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.

### P13-M001V - Valider quick_asset_box dans Fusion

- Capability : C-ASSET, C-FUSION-UI.
- Milestone : M14 Usable beta.
- Objectif : verifier dans Fusion que `quick_asset_box` lit les assets, genere un ou plusieurs modules asset-first, persiste le texte assets et conserve regenerate/clear sans doublon.
- Livrable : smoke test humain Fusion.
- Gate : action humaine validee le 2026-07-08.
- Statut : `done`, validation Fusion V0 honnete confirmee sur `bec0352`.

### P13-ASSET-M002 - Count-aware asset storage sizing et debug visuel

- Capability : C-ASSET, C-SOLVER, C-FUSION-UI.
- Milestone : M14 Usable beta.
- Objectif : transformer le `count` asset en capacite de stockage lisible et verifier si un asset group doit produire un module plus grand, plusieurs modules ou un refus explicite.
- Livrable : regles count-aware bornees, diagnostics de capacite, eventuellement enveloppe/asset debug non imprimable.
- Criteres d'acceptation : le rapport peut dire combien d items sont effectivement contenus ou refuses; aucun module ne suggere une capacite non prouvee.
- Tests : unitaires assets -> candidates -> executable plan, py_compile add-in, smoke Fusion prepare.
- Gate : decision produit validee avant implementation; validation Fusion `P13-ASSET-M002V` confirmee le 2026-07-09 sur `357bfc1`.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.

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
- Statut : `done`, `implemented-local-ui`, `implemented-loopback-adapter`, `print-validated: false`.

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

### P13-ASSET-M002 - Count-aware storage sizing et debug visuel asset

- Capability : C-ASSET, C-SOLVER, C-FUSION-UI.
- Milestone : M14 Usable beta.
- Livrable : sizing count-aware V0 pour tokens/dice/meeples/generic, diagnostics de capacite, metadata `storage_sizing`, sketch debug asset-fit non imprimable, script smoke count-aware.
- Statut : `done`, `fusion-validated-v0` apres validation humaine Fusion `P13-ASSET-M002V` le 2026-07-09 sur `357bfc1`.
- Limites : pas d'assets Fusion individuels, pas de cavites/logements, pas de solveur global, cartes en hauteur totale de paquet, capacite heuristique non print-validee, aucune impression 3D validee.

### P13-ASSET-M002V - Valider le sizing count-aware dans Fusion

- Capability : C-ASSET, C-SOLVER, C-FUSION-UI.
- Milestone : M14 Usable beta.
- Livrable : smoke test humain Fusion confirmant `quick_asset_box`, sizing count-aware, diagnostics, debug visual, regenerate/clear et registry.
- Validation : confirmee le 2026-07-09 sur `357bfc1`.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.

### P13-ASSET-M003-GATE - Autoriser la prochaine etape asset-first

- Capability : C-ASSET, C-FUSION-UI, C-FUSION-CAVITIES ou C-SOLVER selon decision.
- Milestone : M14 Usable beta.
- Objectif : decider si la prochaine mission traite les cavites/logements asset-first, la visualisation d'items/proxies, l'UI assets avancee ou le maintien du scope V0.
- Gate : decision humaine produit validee le 2026-07-09 pour lancer `P13-ASSET-M003 - Asset-fit cavity V0`.
- Statut : `done`.

### P13-ASSET-M003 - Asset-fit cavity V0

- Capability : C-ASSET, C-FUSION-CAVITIES, C-FUSION-UI.
- Milestone : M14 Usable beta / M5 CAD cavities.
- Objectif : convertir l'enveloppe count-aware `asset_fit` en premiere cavite rectangulaire globale reelle dans Fusion.
- Livrable : metadata `asset_fit_cavity`, conversion en `FusionCavityCutPlan`, reporting `asset_cavity_policy`, compteurs planned/generated, diagnostics fond/murs, scripts smoke M003.
- Criteres d'acceptation : module count-aware conserve, cavite top-open reelle correspondant a `asset_fit`, fond et murs coherents avec wall/floor, pas de cavites par pile, pas d'assets individuels, regenerate/clear conserves, coeur Python sans `adsk`.
- Tests : unitaires assets et Fusion skeleton, py_compile add-in, CLI Markdown/JSON/export CAD IR, scripts Fusion dry-run/reel, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine Fusion `P13-ASSET-M003V` realisee le 2026-07-09 sur `04dfdb6`.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.

### P13-ASSET-M003V - Valider la cavite asset-fit globale dans Fusion

- Capability : C-ASSET, C-FUSION-CAVITIES, C-FUSION-UI.
- Milestone : M14 Usable beta / M5 CAD cavities.
- Objectif : verifier dans Fusion que `quick_asset_box` genere un module count-aware creuse par une cavite rectangulaire asset-fit globale.
- Livrable : smoke test humain Fusion avec generate, regenerate, clear et rapport.
- Criteres d'acceptation : `asset_cavities_generated: yes`, `asset_cavity_policy: single_asset_fit_rectangular_cavity_v0`, cavite visible, fond/murs reportes, assets individuels non visualises, pas de doublon apres regenerate, non-BGIG preserve, `Print validation: false`.
- Gate : action humaine Thomas realisee le 2026-07-09.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.


### P13-ASSET-M004-GATE - Decider la prochaine etape asset-first

- Capability : C-ASSET, C-FUSION-CAVITIES, C-FUSION-UI.
- Milestone : M14 Usable beta / M5 CAD cavities.
- Objectif : choisir la prochaine mission apres validation de la cavite asset-fit globale V0.
- Gate : decision humaine produit recue le 2026-07-09 pour lancer `P13-ASSET-M004 - Asset-specific compartments V0`.
- Statut : `done`.

### P13-ASSET-M004 - Asset-specific compartments V0

- Capability : C-ASSET, C-FUSION-CAVITIES, C-FUSION-UI.
- Milestone : M14 Usable beta / M5 CAD cavities.
- Objectif : remplacer la cavite globale asset-fit par des compartiments rectangulaires par asset source quand c'est possible.
- Livrable : policy `per_source_asset_rectangular_compartments_v0`, payload de compartiments, plusieurs `FusionCavityCutPlan`, reporting par asset, outlines debug de compartiments, scripts smoke M004.
- Criteres d'acceptation : au moins deux compartiments pour deux assets tokens du smoke, fond commun coherent, mur interne reporte, regenerate/clear conserves, refus explicite si un layout ne tient pas, coeur Python sans `adsk`.
- Tests : unitaires assets et Fusion skeleton, py_compile add-in, CLI Markdown/JSON/export CAD IR, scripts Fusion dry-run/reel, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine Fusion `P13-ASSET-M004V` realisee le 2026-07-09 sur `9e050ba`.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.

### P13-ASSET-M004V - Valider les compartiments asset-specific dans Fusion

- Capability : C-ASSET, C-FUSION-CAVITIES, C-FUSION-UI.
- Milestone : M14 Usable beta / M5 CAD cavities.
- Objectif : verifier dans Fusion que `quick_asset_box` genere plusieurs cavites rectangulaires top-open correspondant aux assets sources.
- Livrable : smoke test humain Fusion avec generate, regenerate, clear et rapport.
- Criteres d'acceptation : `asset_cavity_policy: per_source_asset_rectangular_compartments_v0`, `asset_compartments_generated: yes`, deux cavites visibles pour les assets du smoke, mur interne visible/reporte, `Rectangular cavity cuts: 2`, registry OK, non-BGIG preserve, `Print validation: false`.
- Gate : action humaine Thomas realisee le 2026-07-09.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.


### P13-ASSET-M005-GATE - Decider la prochaine etape apres compartiments asset-specific V0

- Capability : C-ASSET, C-FUSION-CAVITIES, C-FUSION-UI, C-SOLVER, C-CALIBRATION ou C-FILLETS selon decision.
- Milestone : M14 Usable beta / M5 CAD cavities / M10 Solver / M11 Physical validation selon decision.
- Objectif : choisir la prochaine mission apres validation des compartiments asset-specific V0.
- Options candidates : dette UI/UX `quick_asset_box`, visualisation/proxies d'assets, cavites par pile/item, sizing capacitaire plus garanti, traitement cartes/decks, solveur/optimisation, fillets/conges, export imprimable, calibration/impression ou maintien du scope V0.
- Dette UX a prendre en compte : les champs assets, formats, unites, effets de `count`, dimensions, grille, murs, fond et clearances restent difficiles a comprendre pour un humain.
- Gate : decision humaine produit requise avant toute mission produit suivante.
- Statut : `done`, decision humaine recue le 2026-07-09 pour lancer `P13-ASSET-M005 - Per-compartment access notches V0`.

### P13-ASSET-M005 - Per-compartment access notches V0

- Capability : C-ASSET, C-ACCESS, C-FUSION-UI, C-FILLETS.
- Milestone : M14 Usable beta / M8 Ergonomic planner / M5 CAD ergonomic features.
- Objectif : ajouter une encoche d'acces rectangulaire top-open par compartiment asset-source supporte.
- Livrable : policy `per_compartment_top_open_rectangular_notch_v0`, payload `asset_access_notch`, conversion en `FusionFingerNotchCutPlan`, reporting `asset_access_*`, tests et smoke script.
- Criteres d'acceptation : deux encoches pour le smoke M005 si geometriquement possible, refus explicite si trop etroit ou non adjacent au mur avant, fond et parois preserves, regenerate/clear conserves, coeur Python sans `adsk`.
- Tests : unitaires assets et Fusion skeleton, py_compile add-in, CLI Markdown/JSON/export CAD IR, scripts Fusion dry-run/reel, `git diff --check`, `rg -n "adsk" src/board_game_insert_generator`.
- Gate : validation humaine Fusion `P13-ASSET-M005V` realisee le 2026-07-09 sur `baa7cf9`.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.

### P13-ASSET-M005V - Valider les encoches d'acces par compartiment dans Fusion

- Capability : C-ASSET, C-ACCESS, C-FUSION-UI, C-FILLETS.
- Milestone : M14 Usable beta / M8 Ergonomic planner.
- Objectif : verifier dans Fusion que `quick_asset_box` genere de vraies coupes d'encoche top-open par compartiment supporte, sans casser le fond ni la paroi interne.
- Livrable : smoke test humain Fusion avec generate, regenerate, clear et rapport.
- Criteres d'acceptation : `asset_access_features_generated`, `asset_access_policy: per_compartment_top_open_rectangular_notch_v0`, compteurs planned/generated/refused, encoches visibles comme coupes reelles, registry OK, non-BGIG preserve, `Print validation: false`.
- Gate : action humaine Thomas realisee le 2026-07-09.
- Statut : `done`, validation Fusion V0 confirmee sur `baa7cf9`, `print-validated: false`.

### P13-ASSET-M006-GATE - Decider la prochaine etape apres access notches par compartiment

- Capability : C-ASSET, C-ACCESS, C-FUSION-UI, C-SOLVER, C-CALIBRATION ou C-FILLETS selon decision.
- Milestone : M14 Usable beta / M8 Ergonomic planner / M10 Solver / M11 Physical validation selon decision.
- Objectif : choisir la prochaine mission apres validation des encoches d'acces V0 par compartiment.
- Options candidates : dette UI/UX `quick_asset_box`, visualisation/proxies d'assets, cavites par pile/item, sizing capacitaire plus garanti, traitement cartes/decks, solveur/optimisation, export imprimable, calibration/impression ou maintien du scope V0.
- Dette UX a prendre en compte : les champs, unites, effets de `count`, grille, walls, floor, clearances, modes et politiques restent difficiles a comprendre pour un humain.
- Gate : decision humaine produit requise avant toute mission produit suivante.
- Statut : `authorized-in-progress`.

### P14-USABLE-ASSET-TRAY-M001 - Robustifier le layout multi-assets quick_asset_box

- Capability : C-ASSET, C-FUSION-UI, C-SOLVER.
- Milestone : M14 Usable beta.
- Objectif : supporter proprement plusieurs compartiments asset-specific pour 3 a 5 assets compatibles dans `quick_asset_box`.
- Livrable : strategies row/column/shelf deterministes, refus `ASSET_COMPARTMENTS_DO_NOT_FIT`, suppression du fallback trompeur vers grande cavite globale si les compartiments requis ne tiennent pas.
- Tests : unitaires 2 assets existants, nouveaux tests 3 et 4 assets, rejet explicite si dimensions incompatibles.
- Statut : `done`, `implemented-core`, validation Fusion sprint P14 requise, `print-validated: false`.

### P14-USABLE-ASSET-TRAY-M002 - Printability safety report V0

- Capability : C-CALIBRATION, C-ASSET, C-FUSION-UI.
- Milestone : M14 Usable beta / M11 Physical validation.
- Objectif : ajouter un rapport de securite imprimable V0 sans revendiquer de validation physique.
- Livrable : `printability_report_v0`, checks murs externes/parois internes/fond/profondeur cavite/profondeur encoche, warnings fragilite, `printability_checked: yes`, `printability_validated_by_print: no`.
- Statut : `done`, `implemented-core`, validation Fusion sprint P14 requise, `print-validated: false`.

### P14-USABLE-ASSET-TRAY-M003 - UX quick_asset_box V0 plus lisible

- Capability : C-FUSION-UI, C-ASSET.
- Milestone : M14 Usable beta.
- Objectif : rendre la commande Fusion classique `quick_asset_box` plus comprehensible sans palette HTML.
- Livrable : sections/labels/aide courte, exemple inline, rappel des unites et explication de count/x/y/z/walls/floor/clearances, persistance conservee.
- Statut : `done`, `implemented-fusion-ui`, validation Fusion sprint P14 requise, `print-validated: false`.

### P14-USABLE-ASSET-TRAY-M004 - Presets et scenarios quick asset

- Capability : C-FUSION-UI, C-ASSET.
- Milestone : M14 Usable beta.
- Objectif : permettre de charger rapidement des cas types `quick_asset_box` sans tableau avance.
- Livrable : presets tokens, dice/meeples/generic, eventuellement cards+tokens si la semantique reste claire, scripts smoke/documentation mis a jour.
- Statut : `done`, `implemented-smoke-prep`, validation Fusion sprint P14 requise, `print-validated: false`.

### P14-USABLE-ASSET-TRAY-M005 - Preparation gate Fusion sprint P14

- Capability : C-FUSION-UI, C-ASSET, C-QUALITY.
- Milestone : M14 Usable beta.
- Objectif : preparer un smoke test Fusion global du sprint P14 avec add-in installe, settings presets et criteres observables.
- Livrable : script smoke pret, marqueurs installes verifies, rapport d'actions Fusion restantes.
- Statut : `done`, preparation gate corrigee avec preset `p14_complete`, validation humaine Fusion sprint P14 requise.

## P15 - Tray semantics alignment sprint

### P15-M001 - Audit semantique z/grid/grouping

- Capability : C-ASSET, C-QUALITY.
- Milestone : M14 Usable beta / P15 semantics alignment.
- Objectif : documenter la semantique actuelle de `z_mm`, `count`, grid, body, cavity et grouping.
- Livrable : ADR-0033.
- Statut : `done`.

### P15-M002 - storage_orientation flat_tray V0

- Capability : C-ASSET.
- Objectif : introduire `storage_orientation` et rendre `flat_tray` defaut pour tokens/dice/meeples/generic.
- Livrable : champs JSON additifs `assets[].storage_orientation` et `assets[].max_stack_height_mm`, defaults de pile par type, `vertical_stack` explicite, diagnostics `storage_sizing` enrichis.
- Tests : unitaires assets couvrant defaut `flat_tray`, legacy `vertical_stack`, override `max_stack_height_mm`, validation loader/schema.
- Statut : `done`, `implemented-core`, validation Fusion P15 non encore realisee, `print-validated: false`.

### P15-M003 - max_stack_height_mm et reporting stack policy

- Capability : C-ASSET, C-FUSION-UI.
- Objectif : exposer la hauteur de pile maximale et la politique de stack dans `quick_asset_box`, la persistance UI et le resume Fusion.
- Livrable : champ global optionnel `Max stack height mm (quick_asset_box, optional)`, settings `quick_asset_box_max_stack_height_mm`, config temporaire enrichie avec `assets[].max_stack_height_mm`, reporting stack policy.
- Tests : unitaires Fusion skeleton couvrant rehydratation, sauvegarde, override `6 mm`, dimensions module plus basses et regression constantes UI.
- Statut : `done`, `implemented-fusion-ui`, validation Fusion P15 non encore realisee, `print-validated: false`.

### P15-M004 - Grid semantics report V0

- Capability : C-ASSET, C-FUSION-UI.
- Objectif : expliciter grid span vs body size dans reports/CAD IR/Fusion summary.
- Livrable : metadata de placements et rapports Fusion avec `grid_semantics`, `body_snap_to_grid`, `grid_span_is_reserved_space`, `body_size_may_be_smaller_than_grid_span`.
- Tests : unitaires assets et Fusion skeleton couvrant summary, placements, plan Fusion et resume `quick_asset_box`.
- Statut : `done`, `implemented-reporting`, validation Fusion P15 non encore realisee, `print-validated: false`.

### P15-M005 - Preset smoke P15 realiste

- Capability : C-FUSION-UI, C-QUALITY.
- Objectif : preparer un preset Fusion P15 realiste et bas, puis installer l'add-in et les settings.
- Livrable : preset `p15_tray_semantics`, script `prepare_quick_asset_test.ps1` par defaut sur P15, settings `quick_asset_box` avec `max_stack_height_mm = 18`, documentation de smoke.
- Tests : unittest, py_compile add-in, CLI Markdown/JSON/export CAD IR, DryRun script P15, installation add-in, check installed add-in, `git diff --check`, `rg adsk`.
- Statut : `gate-prepared`, validation humaine Fusion P15 requise, `print-validated: false`.

## P15 Validation Fusion et transition P16

### P15-TRAY-SEMANTICS-ALIGNMENT-SPRINT-V - Valider le realignement semantique tray

- Capability : C-ASSET, C-FUSION-UI, C-QUALITY.
- Milestone : M14 Usable beta.
- Validation : confirmee humainement dans Fusion le 2026-07-09 sur `648eba9`.
- Resultat : `quick_asset_box`, preset `p15_tray_semantics`, `flat_tray`, `max_stack_height_mm`, semantique grid, compartiments, encoches, regenerate et clear valides.
- Limites : packing 2D ergonomique non valide, optimisation avancee absente, UX perfectible, `print-validated: false`.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.

### P16-M001 - Documenter la strategie flat_tray_2d

- Capability : C-ASSET, C-SOLVER, C-QUALITY.
- Milestone : M14 Usable beta / M10 Semi-automatic solver borne.
- Objectif : definir `flat_tray_linear_v0`, `flat_tray_2d_v0`, `vertical_stack`, `pile_count`, `items_per_pile`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm`, `max_stack_height_mm` et la semantique grid.
- Livrable : ADR dediee packing 2D, mises a jour docs strategie.
- Tests : inspection documentaire, suite unitaire, `git diff --check`.
- Gate : aucune tant que la mission reste documentaire et additive.
- Statut : `done-docs`.

### P16-M002 - Implementer packing 2D V0 des piles

- Capability : C-ASSET, C-SOLVER.
- Milestone : M14 Usable beta.
- Objectif : remplacer le layout `flat_tray` lineaire par une organisation 2D deterministe pour tokens/dice/meeples/generic.
- Livrable : heuristique `flat_tray_2d_v0`, diagnostics de piles, tests count/ratio/longueur.
- Gate : aucune si pas de solveur global, pas de backtracking et schema additif.
- Statut : `done`.

### P16-M003 - Aligner compartiments, cavites et notches sur le packing 2D

- Capability : C-ASSET, C-FUSION-CAVITIES, C-ACCESS.
- Objectif : faire suivre les enveloppes `asset_fit`, compartiments et notches par le nouveau packing 2D sans cavites par item.
- Statut : `done`.

### P16-M004 - Clarifier UI et reporting P16

- Capability : C-FUSION-UI, C-ASSET.
- Objectif : exposer/reporting `tray_packing_policy`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm` et warning si layout lineaire inevitable.
- Livrable : champs UI optionnels persistants `Target aspect ratio` / `Max module length mm`, schema assets additif, resume Fusion enrichi.
- Statut : `done`.

### P16-M005 - Preset P16 realiste

- Capability : C-FUSION-UI, C-QUALITY.
- Objectif : ajouter `p16_ergonomic_tray_packing` et en faire le preset par defaut de gate P16.
- Livrable : preset 5 assets avec box `240 x 170 x 60`, grille `8 x 5 x 3`, `max_stack_height_mm = 18`, `target_aspect_ratio = 1.4`, `max_module_length_mm = 70`, script smoke par defaut sur P16.
- Statut : `done`.

### P16-M006 - Preparation gate Fusion P16

- Capability : C-FUSION-UI, C-QUALITY.
- Objectif : installer l'add-in, ecrire les settings P16, verifier les marqueurs et fournir les actions Fusion restantes.
- Gate : validation humaine Fusion P16.
- Statut : `done`, gate humaine active.

### P16-M001 - Strategie flat_tray_2d documentee

- Livrable : ADR-0034 et docs strategie mises a jour.
- Decision : `flat_tray_2d_v0` devient la cible par defaut pour assets simples ; `flat_tray_linear_v0` reste le nom de l'ancien comportement ; `vertical_stack` reste explicite.
- Statut : `done-docs`.

### P16-M002 - Packing 2D V0 des piles implemente

- Livrable : heuristique `flat_tray_2d_v0`, diagnostics de piles, tests tokens/dice/cubes/max stack et non-regression `vertical_stack`.
- Statut : `done`, `implemented-core`, validation Fusion P16 encore requise.

### P16-M003 - Diagnostics compartiments/cavites/notches alignes

- Livrable : diagnostics Fusion enrichis pour relier cavites et notches au packing 2D.
- Statut : `done`, `implemented-reporting`, validation Fusion P16 encore requise.

### P16-M004 - UI et reporting P16 clarifies

- Livrable : `assets[].target_aspect_ratio` et `assets[].max_module_length_mm` additifs, champs UI globaux optionnels persistants pour `quick_asset_box`, resume Fusion exposant politique, grille locale et evitement du layout lineaire.
- Statut : `done`, `implemented-fusion-ui`, validation Fusion P16 encore requise.

### P16-M005 - Preset smoke P16 realiste

- Livrable : catalogue `quick_asset_presets.json` enrichi avec `p16_ergonomic_tray_packing`, script `prepare_quick_asset_test.ps1` par defaut sur P16, settings `quick_asset_box` incluant les champs P16.
- Statut : `done`, `implemented-smoke-prep`, validation Fusion P16 encore requise.

### P16-M006 - Gate Fusion P16 preparee

- Livrable : procedure locale `prepare_quick_asset_test.ps1 -Preset p16_ergonomic_tray_packing`, marqueurs add-in P16 verifies par `check_installed_addin.ps1`, actions Fusion restantes documentees.
- Statut : `done`, `gate-prepared`, validation humaine Fusion active.


### P16-ERGONOMIC-2D-TRAY-PACKING-SPRINT-V - Validation Fusion

- Resultat : `quick_asset_box`, preset `p16_ergonomic_tray_packing`, `flat_tray_2d_v0`, grille locale de piles, target ratio, max module length, compartiments, encoches, regenerate et clear valides.
- Limites : packing heuristique, UX perfectible, export/preprint non encore valide, aucune impression 3D validee.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.

### P17-M001 - ADR export/preprint V0

- Capability : C-FUSION-EXPORT, C-QUALITY, C-CALIBRATION.
- Objectif : definir le contrat d'export V0 : formats, modules exportables, exclusions, nommage, dossier de sortie, manifestes, refus et `print-validated: false`.
- Livrable : `docs/DECISIONS/ADR-0035-printable-export-preprint-v0.md` et docs strategie.
- Decision : export Fusion-only, STL par module en V0, manifeste JSON/Markdown, refus explicites, `print_validated: false`.
- Statut : `done-docs`.

### P17-M002 - Action Fusion export_printables

- Capability : C-FUSION-EXPORT.
- Objectif : ajouter une action Fusion classique qui exporte les modules imprimables BGIG si l'API Fusion le permet de facon fiable.
- Livrable : action `export_printables`, export STL par `module_body` tague BGIG, refus explicites des entites non imprimables, rapport export, `print_validated: false`.
- Limite : manifeste JSON/Markdown reporte a P17-M003 ; validation Fusion humaine requise avant statut `fusion-validated`.
- Statut : `done`, `implemented-fusion-unvalidated`.

### P17-M003 - Export manifest V0

- Capability : C-FUSION-EXPORT, C-QUALITY.
- Objectif : produire `bgig_export_manifest.json` et si utile un Markdown resumant scene, commit, settings, assets, modules, dimensions, features, printability et warnings.
- Livrable : `bgig_export_manifest.json` et `bgig_export_manifest.md` ecrits dans le dossier export par `export_printables`, avec settings, source CAD IR si disponible, assets/modules, fichiers exportes, refus, warnings et `print_validated: false`.
- Statut : `done`, `implemented-fusion-unvalidated`.

### P17-M004 - Printability blockers V0

- Capability : C-CALIBRATION, C-QUALITY.
- Objectif : enrichir `printability_report_v0` avec severites info/warning/blocker, `printability_status` et `printability_export_allowed`.
- Livrable : `issues[]`, `issue_counts`, `printability_status`, `printability_export_allowed` dans `printability_report_v0`, propagation dans le resume Fusion `quick_asset_box`.
- Statut : `done`, `implemented-core-fusion-reporting`.

### P17-M005 - Calibration coupon / preprint check V0

- Capability : C-CALIBRATION.
- Objectif : preparer un coupon/protocole preprint sans validation physique ni promesse ready-to-print.
- Livrable : `docs/PREPRINT_CHECK_PROTOCOL.md` et `examples/preprint_check_v0.json`. Pas de geometrie coupon Fusion ajoutee en V0.
- Statut : `done`, `protocol-ready`.

### P17-M006 - Gate Fusion P17 export complet

- Capability : C-FUSION-EXPORT, C-QUALITY.
- Objectif : preparer le smoke Fusion export avec preset `p17_printable_export`, add-in installe, dossier export, manifeste et actions Fusion restantes.
- Livrable : `scripts/fusion/prepare_quick_asset_test.ps1 -Preset p17_printable_export`, preset riche 5 assets, marqueurs d'installation export/manifeste et settings Fusion ecrits.
- Gate : validation humaine Fusion P17 confirmee le 2026-07-10 ; aucune impression 3D validee.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.

### P17-PRINTABLE-EXPORT-AND-PREPRINT-SPRINT-V - Validation Fusion

- Resultat : preset `p17_printable_export`, generation asset-first, compartiments, encoches, `export_printables`, STL par module BGIG imprimable, manifestes JSON/Markdown, exclusion des non-BGIG/references/debug/helpers et clear post-export valides.
- Limites : aucune impression physique, slicer, materiau, mesure dimensionnelle ou garantie `ready to print` validee.
- Statut : `done`, `fusion-validated-v0`, `print-validated: false`.

### P18-M001 - Audit de l'ecart vision vs etat reel

- Capability : C-PRODUCT-VISION, C-FUSION-UI, C-SOLVER, C-GRID-3D.
- Objectif : expliciter l'ecart entre la fondation asset-first/Fusion actuelle et le produit cible de remplissage volumetrique, variantes et UX premium.
- Livrable : `docs/VISION_GAP_ANALYSIS.md` et mises a jour de pilotage.
- Gate : aucune tant que le travail reste documentaire et ne modifie pas la North Star ni l'architecture executable.
- Statut : `done-docs`.

### P18-M002 - Redefinir l'UX cible premium

- Capability : C-FUSION-UI, C-ASSET, C-SOLVER.
- Objectif : decrire un parcours premium de la boite a l'export, sans implementation UI.
- Livrable : `docs/UX_PRODUCT_VISION.md`.
- Gate : aucune pour le contrat documentaire; gate architecture avant implementation UI lourde.
- Statut : `ready`.

### P18-M006 - Preparer la recommandation P19

- Livrable : `docs/P19_RECOMMENDATION.md`.
- Decision : recommander P19-A, plan manuel de boite avant palette ou solveur global.
- Statut : `done-docs`.

### P19-BOX-FILL-MANUAL-MODULES-SPRINT

- Capability : C-PRODUCT-VISION, C-GRID-3D, C-LAYERS, C-RESERVATION, C-SOLVER.
- Objectif : rendre un `BoxFillPlan` manuel executable dans le moteur pur avec modules, positions, reservations, collisions, couverture et `FreeVolume`.
- Dependances : contrats P18-M001 a P18-M004.
- Gate : validation humaine explicite de l'extension de modele/schema recue le 2026-07-10. ADR-0036 est acceptee pour la roadmap; une gate separee subsiste avant toute UI persistante.
- Statut : `authorized-in-progress`.

### P18-M003 - Definir le modele produit volumetrique cible

- Livrable : `docs/VOLUMETRIC_PRODUCT_MODEL.md`, contrat CAD-agnostic `GameBox` a `ExportPackage`.
- Statut : `done-docs`.

### P18-M004 - Roadmap solver et box fill

- Livrable : `docs/BOX_FILL_SOLVER_ROADMAP.md`, trajectoire V0 manuel a V5 assistant.
- Decision : recommander `box_fill_v0_manual_modules` avant greedy/variantes.
- Statut : `done-docs`.

### P18-M005 - ADR architecture UX

- Livrable : `docs/DECISIONS/ADR-0036-ux-architecture-roadmap.md`.
- Decision : commande Fusion = dev/smoke; UI persistante sous gate; app locale/web direction moyen terme.
- Statut : `accepted-roadmap`; ADR acceptee pour direction, gate humaine maintenue avant implementation UI lourde.

### P18-VISION-UX-VOLUMETRIC-REBASE-SPRINT - Validation strategique

- Resultat : livrables P18 acceptes; `BoxFillPlan` autorise comme extension additive, versionnee, CAD-agnostic et retrocompatible.
- Limite : aucune palette, app, dependance UI lourde ou changement Fusion n'est autorise par cette validation.
- Statut : `done`, `accepted`.
### P19-M001 - Contrat BoxFillPlan V0

- Capability : C-PRODUCT-VISION, C-GRID-3D, C-LAYERS, C-RESERVATION.
- Livrable : `docs/DECISIONS/ADR-0037-box-fill-plan-v0.md`.
- Decision : `box_fill_plan.v0` est optionnel, versionne, CAD-agnostic et ne remplace aucun pipeline existant.
- Statut : `done`.

### P19-M002 - Modeles et chargement additif

- Capability : C-PRODUCT-VISION.
- Objectif : charger les reservations, layers, modules et allocations dans des dataclasses pures sans comportement Fusion.
- Statut : `ready`.
### P19-M002 - Modeles et chargement additif - Resultat

- Livrables : dataclasses pures dans `models.py`, loader strict `box_fill_plan.v0`, fixture `examples/box_fill_manual_v0.json`, tests de regression.
- Statut : `done`, `implemented-core`.

### P19-M003 - Validation, coverage et FreeVolume aggregate

- Capability : C-PRODUCT-VISION, C-QUALITY, C-RESERVATION.
- Objectif : valider limites, collisions, IDs/references/allocation, couverture par asset et volume libre aggregate de `BoxFillPlan`.
- Statut : `ready`.
### P19-M003 - Validation, coverage et FreeVolume aggregate - Resultat

- Livrables : `box_fill.py`, raccordement `validate_config`, coverage explicite, FreeVolume aggregate et regressions de collisions/references.
- Statut : `done`, `implemented-core`.

### P19-M004 - Rapports et transport CAD IR BoxFillPlan

- Capability : C-PRODUCT-VISION, C-QUALITY, C-CAD-IR.
- Objectif : exposer le plan, validation, coverage et FreeVolume en Markdown/JSON et metadata CAD IR sans materialisation Fusion.
- Statut : `ready`.
### P19-M004 - Rapports et transport CAD IR BoxFillPlan - Resultat

- Livrables : sections Markdown/JSON `box_fill_plan`, metadata `cad_ir.v0`, tests de non-materialisation Fusion.
- Statut : `done`, `implemented-core`, `implemented-cad-ir-metadata`.

### P19-M005 - Cloture de sprint et prochaine gate

- Capability : C-PRODUCT-VISION, C-SOLVER.
- Objectif : consolider les preuves P19 et proposer la prochaine gate sans lancer le placement greedy ou une UI persistante.
- Statut : `ready`.
### P19-M005 - Cloture de sprint et prochaine gate - Resultat

- Resultat : sprint P19 complet; contrat executable, validation, coverage, FreeVolume aggregate, rapports et CAD IR metadata livres dans le moteur pur.
- Statut : `done`.

### P20-BOX-FILL-GREEDY-2D-SPRINT

- Capability : C-PRODUCT-VISION, C-SOLVER, C-GRID-3D, C-LAYERS, C-RESERVATION.
- Objectif : placement XY deterministe par layer des modules/candidats non verrouilles dans un BoxFillPlan valide.
- Gate : autorisation humaine explicite requise; `docs/P20_RECOMMENDATION.md` fixe le scope borne.
- Statut : `ready-gated`.
## P19 completion addendum

P19 est complet contre son contrat autorise : cellules libres AABB exactes (`exact_aabb_cells_v0`), conservation de volume, diagnostics structures, coverage par asset, CLI `validate-box-fill` / `report-box-fill` / `export-box-fill-plan`, fixtures valide et invalides, bridge explicite `derived_from_executable_asset_plan` et transport CAD IR metadata. Les cellules decrivent le residuel et ne constituent pas un placement automatique. P20 greedy reste bloque par gate humaine ; Fusion ne recalcule ni ne materialise ce plan.
## P19-M007 - Completion des metriques de rapport

Statut : `done`. Les sorties JSON et Markdown exposent maintenant les volumes modules, reservations et libres par layer, les taux occupation/reservation et la couverture item-level. Les cellules libres restent exactes et descriptives; aucun solveur P20 n'est introduit.
## P19 product acceptance - 2026-07-10

Statut : `accepted`, `implemented-core`, `implemented-cad-ir-metadata`. P19 est accepte comme contrat executable BoxFillPlan manuel : validation volumetrique, coverage item-level, cellules libres AABB, metrics par layer, CLI, fixtures, bridge et metadata CAD IR. Il reste hors Fusion, sans solveur automatique et sans validation d'impression (`print_validated: false`). La gate P20 greedy 2D est levee ; la gate ADR-0036 palette/app reste distincte.
## P20 completion - 2026-07-10

Statut : `done`, `implemented-core`, `implemented-cli`, `implemented-cad-ir-metadata`. Le moteur `box_fill_greedy_2d.v0` produit un nouveau BoxFillPlan sans muter la source, respecte locks, modules manuels, reservations et layers, supporte la rotation XY 90 degres et expose diagnostics, digest, metrics, rapports JSON/Markdown, preview SVG et metadata CAD IR. Aucun backtracking, solveur global, UI persistante, geometrie Fusion ou validation d impression n est ajoute. P21 reste gate et recommande les variantes/scoring.
## P20 product acceptance - 2026-07-10

Statut : `accepted`, `implemented-core`, `implemented-cad-ir-metadata`. P20 est accepte comme premier placement automatique deterministe de BoxFillPlan. Il reste hors Fusion, sans solveur global ni validation d impression (`print_validated: false`). La gate P21 variants est levee; ADR-0036 UI reste distincte.
## P21-BOX-FILL-VARIANT-PORTFOLIO-SPRINT

- Capability : C-SOLVER, C-PRODUCT-VISION, C-CAD-IR.
- Milestone : M10 Semi-automatic solver.
- Objectif : comparer un portefeuille borne de placements P20 sans introduire de solveur global ou d UI persistante.
- Livrables : `box_fill_variants.v0`, profiles de preference, deduplication, Pareto, Markdown/JSON/HTML statique, selection explicite, metadata CAD IR, fixture et tests.
- Gate : P21 etait autorise par l acceptation P20 ; aucune nouvelle gate franchie.
- Statut : `done`, `implemented-core`, `implemented-cli`, `implemented-cad-ir-metadata`, `print-validated: false`.

## P22-M001 - Rapport de gate pour la premiere surface UX persistante

- Capability : C-FUSION-UI, C-PRODUCT-VISION.
- Milestone : M14 Usable beta.
- Objectif : comparer avec preuves la palette Fusion et l app locale de composition, proposer une surface initiale, son contrat de projet et son plan de retrait sans code UI.
- Livrable : rapport de gate ADR-0036, option recommandee, limites, perimetre de spike et criteres d acceptation.
- Dependances : P21 termine.
- Gate : aucune tant que le lot reste documentaire ; la decision humaine de surface est obligatoire avant toute implementation persistante.
- Statut : `ready`.
### P22-M001 - Rapport de gate UX persistante - Resultat

- Livrable : `docs/P22_UX_SURFACE_GATE_REPORT.md`.
- Resultat : options comparees, recommandation D hybride et scope P23 borne sans implementation.
- Statut : `done-docs`; gate ADR-0036 active.

### P23-M001 - Spike app locale de composition

- Capability : C-PRODUCT-VISION, C-FUSION-UI, C-SOLVER.
- Milestone : M14 Usable beta.
- Objectif : livrer le premier parcours local boite/assets/intentions/propositions/selection/export, sans materialisation Fusion.
- Dependances : P22-M001 et validation humaine explicite de la surface/stack.
- Gate : ADR-0036 et ajout de dependances UI majeures.
- Statut : `done`, `implemented-local-ui`, `implemented-loopback-adapter`, `print-validated: false`.
### P23-M001 - Resultat

- Livrables : ADR-0040, draft versionne `bgig.local_composer.v0`, adaptateur Python loopback limite a localhost, interface React/Vite, scripts de lancement/arret, selection et CAD IR metadata-ready telechargees par le navigateur.
- Preuves : tests Python de contrat/HTTP, build TypeScript/Vite, recette loopback starter -> portefeuille -> selection -> export -> preflight CORS.
- Limites : pas de persistence serveur, pas de collaboration, pas de materialisation Fusion, pas de validation ergonomique ou d impression.

### P24-M001 - Qualite du projet local

- Capability : C-PRODUCT-VISION, C-ASSET, C-QUALITY.
- Milestone : M14 Usable beta.
- Objectif : rendre l edition locale plus fiable pour un non-expert : allocations multi-assets explicites, erreurs de draft actionnables et import/export plus robustes.
- Dependances : P23-M001 termine.
- Hors scope : nouveau solveur, persistence serveur, cloud, collaboration, Fusion ou export imprimable.
- Gate : aucune nouvelle gate architecturale si le contrat `bgig.local_composer.v0` reste retrocompatible ; ADR obligatoire si le format change de maniere incompatible.
- Statut : `done`, `implemented-local-ui`, `implemented-validation`, `print-validated: false`.
### P24-M001 - Resultat

- Livrables : prevalidation pure TypeScript, import structurel, liste d erreurs actionnables, associations multi-assets par checkboxes et blocage visuel des doublons.
- Preuves : build Vite, verification comportementale isolee du module TypeScript et test Python de serialisation multi-assets dans le portefeuille P21.
- Decision : aucun changement du schema `bgig.local_composer.v0`, du moteur ou de l architecture ; la prevalidation reste une aide UI et le moteur reste autoritaire.

### P25-M001 - Demarrage guide par modele de jeu

- Capability : C-PRODUCT-VISION, C-ASSET, C-QUALITY.
- Milestone : M14 Usable beta.
- Objectif : proposer des points de depart locaux comprehensibles (cartes, jeu mixte, boite avec plateau), sans base distante ni nouveau solveur.
- Dependances : P24-M001 termine.
- Hors scope : cloud, compte utilisateur, collaboration, persistence serveur, Fusion, export imprimable ou IA generative.
- Gate : aucune si les templates restent des drafts V0 locaux et versionnes ; ADR requise si une bibliotheque distante ou un format incompatible est introduit.
- Statut : `done`, `implemented-local-ui`, `implemented-loopback-adapter`, `print-validated: false`.

### P25-M001 - Resultat

- Livrables : catalogue local borne de trois drafts V0, endpoint loopback `/api/starters`, cartes de demarrage dans le Studio et chargement explicite en memoire.
- Preuves : chaque modele produit une recommandation P21 ; tests Python et recette HTTP/CORS locale passent.
- Decision : aucun catalogue distant, compte, telemetrie, IA, persistence serveur ou schema incompatible.

### P26-M001 - Resume de preparation avant generation

- Capability : C-PRODUCT-VISION, C-QUALITY, C-SOLVER.
- Milestone : M14 Usable beta.
- Objectif : rendre les mesures, allocations, contraintes et limites P21 visibles dans un resume novice avant la generation, sans nouveau score ni solveur.
- Dependances : P25-M001 termine.
- Hors scope : moteur de recommendation nouveau, optimisation globale, Fusion, export imprimable, cloud ou donnees utilisateur.
- Gate : aucune si le resume derive seulement du draft local et des sorties moteur existantes ; ADR requise si une nouvelle logique de decision est introduite.
- Statut : `done`, `implemented-local-ui`, `implemented-validation`, `print-validated: false`.

### P26-M001 - Resultat

- Livrables : resume derive du draft et de la prevalidation existante, compteurs assets/modules/contraintes et rappel visible des limites P21.
- Preuves : verification comportementale TypeScript et build Vite passent.
- Decision : aucun calcul de score ou de placement n est ajoute ; le resume ne fait que lire les contrats locaux existants.

### P27-M001 - Explication des compromis de proposition

- Capability : C-PRODUCT-VISION, C-SOLVER, C-QUALITY.
- Milestone : M14 Usable beta.
- Objectif : rendre les policies P21, leurs scores et la selection recommandee compréhensibles pour un novice, sans changer les scores ni la recommendation.
- Dependances : P26-M001 termine.
- Hors scope : nouveau score, IA, solveur, modele de preference, Fusion, export imprimable ou validation physique.
- Gate : aucune si le travail reste une presentation des sorties P21 existantes ; ADR requise si la decision moteur change.
- Statut : `done`, `implemented-local-ui`, `print-validated: false`.

### P27-M001 - Resultat

- Livrables : explications locales de chaque policy P21, aide par sous-score, conseil de choix, compromis et trace technique progressive.
- Preuves : build Vite et verification comportementale du catalogue de textes/fallbacks.
- Decision : aucune policy, aucun score, aucune recommendation ou sortie moteur n est modifiee.

### P28-GATE - Materialiser une selection locale dans Fusion

- Capability : C-FUSION-UI, C-CAD-IR, C-PRODUCT-VISION.
- Milestone : M14 Usable beta.
- Objectif : relier une selection P21 explicite au pipeline Fusion existant avec smoke humain, sans faire de Fusion une source de verite.
- Dependances : P23 a P27 termines ; approbation humaine de scope recue le 2026-07-11.
- Livrables : ADR-0041, composants CAD IR `rectangular_blank` traces, commande `export-local-composer-selection`, preparateur Fusion et protocole P28.
- Preuves : tests Local Composer/CLI avec plan Fusion hors API, export reel de trois modules et dry run du preparateur.
- Hors scope : nouveau solveur, changement de tolerance, cavites/parois finies, export imprimable automatique, validation d impression, cloud ou Fusion comme source de verite.
- Gate : observation humaine Fusion obligatoire ; aucune declaration `fusion-validated` ou `print-validated` avant retour humain.
- Statut : `implemented-cad-ir-selection-bridge`, `technical-path-observed`, `product-ux-rejected`, `print-validated: false`.
### P29-M001 - Redressement produit et plan d execution premium

- Capability : C-PRODUCT-VISION, C-FUSION-UI, C-CAD-IR.
- Milestone : M14 Usable beta.
- Objectif : requalifier P28, fixer Studio principal / palette Fusion secondaire et rendre la trajectoire vers bacs, parametres live, esthetique, mecanismes et validation physique executable.
- Livrables : ADR-0042, `PREMIUM_PRODUCT_EXECUTION_PLAN.md`, gate P30 et mises a jour de pilotage.
- Gate : aucune pour la documentation ; le choix visuel P30 reste humain avant code UI.
- Statut : `done-docs`, `accepted-product-direction`.

### P30-GATE - Direction visuelle et interaction principale

- Capability : C-PRODUCT-VISION, C-FUSION-UI, C-AESTHETIC.
- Milestone : M14 Usable beta.
- Objectif : valider la direction `Atelier de rangement` avant la refonte Studio : boite centrale, etapes progressives, cartes de decision, parametres de forme visibles et expert replie.
- Livrable : `docs/P30_VISUAL_DIRECTION_GATE.md`.
- Gate : decision esthetique structurante obligatoire.
- Statut : `accepted`, direction `Atelier de rangement` approuvee le 2026-07-11.
### P30-M001 - Studio vivant et parcours novice

- Capability : C-PRODUCT-VISION, C-QUALITY.
- Milestone : M14 Usable beta.
- Objectif : rendre le Studio principal progressif, lisible et visuel sans modifier le moteur ni presenter les envelopes P28 comme des bacs.
- Livrables : parcours en cinq etapes, apercu 2D de boite mis a jour a chaque modification, vue de preparation/fabrication, reglages experts replis, export technique explicitement expert et tests de contrat frontend.
- Preuves : build TypeScript/Vite, 248 tests Python, services loopback UI/API en HTTP 200 et test de contrat `test_frontend_studio.py`.
- Limite : la recette navigateur automatisee ne peut pas s ouvrir dans cet environnement a cause du sandbox Windows ; elle reste a rejouer sans que cela soit confondu avec une validation d impression.
- Hors scope : bacs physiques, parois, cavites, tolerances nouvelles, palette Fusion, couvercles, mecanismes et impression.
- Statut : `implemented-local-ui`, `browser-inspection-pending`, `print-validated: false`.
### P31-GATE - Strategie de bacs fonctionnels

- Capability : C-CAD-IR, C-CAVITY, C-FUSION-UI, C-PRODUCT-VISION.
- Milestone : M14 Usable beta.
- Objectif : choisir la premiere projection selection P21 -> bac ouvert fonctionnel, sans nouvelle logique de placement ni nouvelle tolerance.
- Livrables : `P31_FUNCTIONAL_TRAY_GATE.md`, ADR-0043 acceptee, invariants, options et preuves avant Fusion.
- Decision : un bac ouvert par module avec cavite `free` top-open, parois/fond existants et refus structure des enveloppes trop petites.
- Gate : smoke Fusion humain P31 obligatoire avant toute qualification Fusion.
- Statut : `implemented-cad-ir-open-top-trays`, `fusion-validated`, `print-validated: false`.
### P31-M001 - Resultat

- Livrables : projection `open_top_tray_from_selected_module.v0`, cavite top-open par module, diagnostics d enveloppe impossible, messages Studio/CLI et preparateur Fusion actualises.
- Preuves : 249 tests Python, build frontend, export `mixed-box` avec trois bacs et trois coupes dans le plan Fusion hors API.
- Limites : aucun smoke Fusion observe, aucune validation physique ou asset-specific.
- Statut : `implemented-cad-ir-open-top-trays`, `fusion-validated`, `print-validated: false`.
### P32-M001 - Palette Fusion secondaire concise

- Capability : C-FUSION-UI, C-PRODUCT-VISION, C-QUALITY.
- Milestone : M14 Usable beta.
- Objectif : remplacer l ouverture normale du gros dialogue technique par une palette Fusion courte en francais, sans deplacer le moteur ni dupliquer le Studio.
- Livrables : `palette.html` locale, bridge Fusion HTML, resume design/scene/fabrication, actions `Previsualiser`, `Mettre a jour la scene`, `Exporter les bacs`, acces aux reglages experts et preparateur de smoke P32.
- Preuves hors Fusion : 87 tests Fusion hors API, `py_compile`, bridge HTML teste par contrat et statut d impression explicitement non valide.
- Gate : observation humaine Fusion P32 obligatoire avant `fusion-validated`.
- Hors scope : nouveau solveur, edition de projet dans Fusion, compartiments asset-specific, formes, couvercles, mecanismes et impression.
- Statut : `implemented-fusion-palette`, `fusion-smoke-required`, `print-validated: false`.

### P32 Fusion smoke - Validation humaine

- Retour humain : `P32 Fusion OK`.
- Preuve : palette `BGIG - Atelier de rangement` observee dans Fusion apres installation automatique, avec le chemin secondaire de previsualisation, mise a jour, export et recours expert.
- Decision : P32 devient `fusion-validated`; la commande historique reste un recours expert, non la surface produit.
- Limite : cette preuve ne valide ni l ajustement des assets, ni le slicer, ni une impression physique.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

### P33-M001 - Forme et apparence parametriques V0

- Capability : C-AESTHETIC, C-PRODUCT-VISION, C-QUALITY.
- Milestone : M12 Design language / M14 Usable beta.
- Objectif : rendre les choix de forme et d apparence visibles, sauvegardes et transportes sans modifier le moteur de placement ni presenter une finition d apercu comme imprimable.
- Livrables : contrat `APPEARANCE_CONTRACT.md`, champ `appearance` versionne, validation Python, themes Studio, coins/biseaux/prises/labels de preview, compatibilite des anciens projets et metadata CAD IR non executable.
- Preuves : tests Python de bornes, transport et absence d effet sur le digest P21 ; test de contrat frontend ; TypeScript/Vite build.
- Limite : la recette visuelle automatisee ne peut pas se connecter dans ce sandbox Windows ; aucune geometrie de finition n est materialisee dans Fusion.
- Statut : `implemented-studio-preview`, `browser-inspection-pending`, `print-validated: false`.

### P34-GATE - Premier mecanisme et validation physique

- Capability : futur mecanisme, C-STACKING, C-AESTHETIC, C-CALIBRATION.
- Milestone : M13 Advanced mechanisms / M14 Usable beta.
- Objectif : choisir le premier mecanisme ferme autorise avant toute CAD IR, Fusion ou promesse d impression.
- Livrables de gate : `P34_MECHANISM_GATE.md`, ADR-0044/0045 et protocole cible.
- Decision humaine : C, couvercle coulissant, le 2026-07-11.
- Gate : validation humaine explicite obligatoire.
- Statut : `waiting-human-decision`.

### P34-M001 - Contrat experimental du couvercle coulissant

- Capability : C-STACKING, C-AESTHETIC, C-CALIBRATION, C-PRODUCT-VISION.
- Milestone : M13 Advanced mechanisms / M14 Usable beta.
- Objectif : sauvegarder, borner et rendre lisible le coulissant sans materialiser de geometrie.
- Livrables : ADR-0045, `SLIDING_LID_CONTRACT.md`, `bgig.mechanism.v0`, refus par module, transport Local Composer et Studio.
- Preuves : tests Python, tests Studio, TypeScript/Vite ; digest P21 invariant.
- Limite : rails/capot non materialises, `print-validated: false`.
- Statut : `done`, `experimental-contract`.

### P34-M002 - Coupon CAD IR coulissant a deux pieces

- Capability : C-STACKING, C-CAD-IR, C-FUSION-UI, C-CALIBRATION.
- Milestone : M13 Advanced mechanisms.
- Objectif : materialiser un bac, deux rails simples et un capot separe selon ADR-0045, sans changer le solveur ni les tolerances globales.
- Dependances : P34-M001 termine et integre.
- Gate : smoke Fusion humain obligatoire avant toute qualification Fusion ; impression et mesure restent necessaires.
- Livrables : `join_rectangular_prism`, capot unique a deux rails, coupon hors boite, CLI/preset Fusion et smoke P34.
- Statut : `done`, `implemented-cad-ir-coupon`, `implemented-fusion-adapter`, `fusion-smoke-required`, `print-validated: false`.
## Rebase canonique V0.1 -> V0.2 -> V0.3 - 2026-07-12

Les lots P33 et P34 restent dans l'historique technique, mais sont
`superseded-for-product`. Le smoke P34 est retire des actions actives. ADR-0047
impose les dependances de release suivantes.

### P36 - Rebase vision, audit et chemin critique

- Capability : C-PRODUCT-VISION, controle projet.
- Objectif : traduire la vision canonique, expliquer la derive et reconstruire
  le chemin V0.1/V0.2/V0.3.
- Livrables : vision, audit, ADR-0047, plan d'execution et pilotage aligne.
- Statut : `done-docs`, tests de pilotage passes.

### P37 - Contrat projet V0.1 et migration

- Capability : C-ASSET, C-RESERVATION, C-PRODUCT-VISION.
- Dependances : P36 integre.
- Objectif : groupes de bacs, elements plats, remplissages, jeu global et parois
  par bac dans un schema additif.
- Validation : tests de schema, migration et compatibilite des projets P23/P33/P34.
- Statut : `done`, contrat V1, migration locale, API et build verifies.

### P38 - Tables dynamiques et parcours user-first

- Dependances : P37.
- Objectif : boite, pieces, bac cible, plateaux/livrets et bouton `Construire mon
  insert`, sans jargon moteur dans le parcours principal.
- Validation : tests de contrat UI, validation TypeScript, build Vite et serveur
  local HTTP ; parcours navigateur automatise indisponible dans ce sandbox,
  sans gate humaine.
- Statut : `done`, `implemented-local-ui`, `implemented-client-validation`.

### P39 - Derivation des bacs et logements

- Dependances : P38.
- Objectif : deriver capacite, logements, dimensions internes et externes depuis
  forme, quantite et `Bac cible`.
- Validation : tests de derivation rond, carre, rectangle, cartes, cube/de,
  pion, custom, quantite elevee, blocages et API locale ; build Studio.
- Statut : `done`, `implemented-core`, `implemented-loopback-adapter`,
  `implemented-local-ui`.

### P40 - Pile superieure plateaux et livrets

- Dependances : P39.
- Objectif : reserver quantites, empreintes, hauteur et support au-dessus de tous
  les bacs sans depassement.
- Validation : tests de hauteur, empreinte, ordre, pile vide, debordements,
  support explicable, recalcul des bacs, API locale et build Studio.
- Statut : `done`, `implemented-core`, `implemented-loopback-adapter`,
  `implemented-local-ui`.

### P41 - Solveur de fermeture du volume

- Dependances : P40.
- Objectif : affecter chaque region utile a un bac, une reservation, un jeu
  technique, un bac creux, un separateur ou un remplissage plein.
- Validation : conservation du volume, absence de collision, benchmarks de
  grande cardinalite et diagnostics d'arret.
- Statut : `done`, `implemented-core`, `implemented-loopback-adapter`, `implemented-local-ui`.

### P42 - Geometrie fonctionnelle V0.1

- Dependances : P41.
- Objectif : materialiser bacs, logements, supports et remplissages resolus,
  sans apparence V0.2 ni couvercles V0.3.
- Validation : CAD IR pure, adaptateur Fusion hors API, API/CLI Studio, build
  TypeScript et test compact 50 bacs / 72 familles / 25 elements plats.
- Resultat : `bgig.functional_cad_build.v1`, route `build-cad`, commande
  `export-project-v1-cad`, bacs ouverts par logement, remplissages exacts, cellules automatiques regroupees et
  regions automatiques expliquees comme jeu technique si les parois ne tiennent
  pas.
- Statut : `done`, `implemented-core`, `implemented-loopback-adapter`,
  `implemented-local-ui`, `implemented-cad-ir`, `fusion-smoke-required`.

### P43 - Gate V0.1 rouverte

- Dependances historiques : P42. Reprise : P52 a P59.
- Etat historique : une scene Fusion de 20 pieces et 19 cavites a ete observee
  le 2026-07-12 (`Fusion P43 OK`). Cette preuve reste valide pour la geometrie
  du jeu temoin, pas pour la conformite produit.
- Statut : `reopened`, `fusion-validated-geometry-only`,
  `product-mvp-rejected`, `print-validated: false`.
- Sortie : remplacee par P60, selon `docs/MVP_V01_ACCEPTANCE_CONTRACT.md`.

### P51 - Fusion de residus automatiques

- Etat : `superseded-by-P56`.
- Raison : fusionner quelques cellules ne traite ni l utilite, ni la lisibilite,
  ni la selection des complements. Le besoin est absorbe par la qualite globale
  du plan de rangement.

### P52 - Remise a plat de verite V0.1

- Capability : C-PRODUCT-VISION, C-QUALITY.
- Dependances : P43 reouvert.
- Livrables : audit des ecarts, contrat d acceptance, ADR-0053 et pilotage
  coherent.
- Validation : documents relus contre la vision canonique et le code actuel.
- Statut : `done-docs`.

### P53 - Contrat cavites fixes et enveloppes extensibles

- Capability : C-PRODUCT-VISION, C-SOLVER, C-CAVITY, C-QUALITY.
- Dependances : P52.
- Objectif : verrouiller que les assets dimensionnent les cavites tandis que les
  enveloppes exterieures des bacs absorbent le volume disponible.
- Livrables : ADR-0054, vision canonique, modele geometrique, contrat MVP et
  backlog alignes ; interdiction de tout corps automatique.
- Acceptation : un asset minuscule dans un bac unique produit une petite cavite
  calibree dans une grande enveloppe, jamais une cavite geante ni des micro-bacs.
- Statut : `done-docs`.

### P54-R - Realignement produit Fusion-only

- Capability : C-PRODUCT-VISION, C-FUSION-UI, C-QUALITY.
- Dependances : decision humaine Fusion uniquement.
- Objectif : superseder Studio principal / Fusion secondaire et rendre
  l add-in Fusion 360 seul produit du MVP.
- Livrables : ADR-0055, contrat Fusion-only, North Star, architecture,
  acceptance, roadmap, backlog et gates coherents.
- Acceptation : aucun document actif ne demande navigateur, Vite ou serveur
  loopback pour utiliser le MVP ; la palette embarquee est la surface principale.
- Statut : done-docs.

### P55 - Contrat executable des cavites et contraintes d expansion

- Capability : C-ASSET, C-CAVITY, C-MODULE, C-QUALITY.
- Dependances : P54 historique, semantique conservee par ADR-0055.
- Objectif : separer dans le coeur pur cavite calibree, enveloppe minimale,
  enveloppe finale et contraintes de repartition du surplus.
- Livrables : schema additif, migration, modele pur, invariants, rapports et tests.
- Acceptation : modifier l enveloppe finale ne modifie jamais les dimensions ou
  positions locales des cavites.
- Statut : done, implemented-core, print-validated: false.
- Note : la route loopback est historique ; le contrat pur est reutilise par
  le bridge de palette Fusion.

### P56 - Editeur complet embarque dans Fusion

- Capability : C-PRODUCT-VISION, C-FUSION-UI, C-ASSET, C-RESERVATION, C-QUALITY.
- Dependances : P54-R et P55.
- Objectif : transformer la palette P32 en editeur principal complet sans
  navigateur externe, localhost, Vite ni JSON manuel.
- Livrables : six vues Boite/Pieces/Plateaux/Bacs/Fabrication/Resultat, tables
  dynamiques, mode simple/avance, projet bgig.project.v1, sauvegarde/import,
  validation, timeout/retry et bridge JSON versionne vers le coeur.
- Acceptation : projets vide, simple, multi-bacs, avec plateaux et grande
  cardinalite editables dans Fusion ; aucune logique metier en JavaScript ;
  CommandInputs uniquement sous Reglages experts.
- Tests : DOM/bridge hors Fusion, absence de dependance runtime web, tests Python
  complets, puis smoke palette Fusion prepare automatiquement.
- Statut : `implemented`, `automated-validated`, `fusion-smoke-prepared`, `fusion-validated: false`, `print-validated: false`.
- Preuves : bridge pur et atomique, 6 tests bridge, 5 tests DOM, 87 tests Fusion existants, syntaxe JavaScript, packaging autonome et installation AppData verifies. Le controle visuel Fusion reste non observe car le controle Windows est bloque par `apply deny-read ACLs`.

### P57 - Solveur de partition et expansion des bacs

- Capability : C-SOLVER, C-RESERVATION, C-MODULE, C-QUALITY.
- Dependances : P56 integre.
- Objectif : partitionner le volume sous les plateaux entre les seuls bacs et
  complements explicitement demandes, puis absorber le surplus dans parois/fonds.
- Livrables : solveur pur borne X/Y/Z, alignements, support de pile, score de
  simplicite, diagnostics et message de bridge palette.
- Invariants : corps final = groupes constructibles + complements explicites ;
  aucun automatic filler ; jeux externes conserves comme vides.
- Acceptation : une solution impossible est expliquee dans la palette au lieu de
  generer lamelles ou micro-volumes.
- Statut : `implemented`, `automated-validated`, `fusion-validated: false`, `print-validated: false`.
- Preuves : solveur bgig.partition_plan.v1, 9 tests coeur, bridge palette solve_project, diagnostics francais, 50 bacs et complements exacts. Aucun CAD ni scene Fusion n est produit.

### P58 - Resultat premium dans la palette Fusion

- Capability : C-PRODUCT-VISION, C-SOLVER, C-FUSION-UI, C-QUALITY.
- Dependances : P57.
- Objectif : afficher dans la palette le plan moteur reel avant CAD.
- Livrables : vue dessus/coupe depuis placements, bacs/contenus,
  cavite/minimum/final, surplus, pile, alertes et actions modifier/recalculer/
  materialiser.
- Acceptation : aucun dessin indicatif n est presente comme solution ; le
  resultat montre zero corps automatique et devient obsolete apres modification.
- Statut : `implemented`, `automated-validated`, `fusion-validated: false`, `print-validated: false`.
- Preuves : bgig.partition_result_view.v1, 5 tests projections, 4 tests palette, bridge et syntaxe JavaScript. Le controle visuel Fusion reste reserve a la gate P60.

### P59 - Materialisation CAD et synchronisation de scene

- Capability : C-CAD-IR, C-CAVITY, C-FUSION-UI, C-QUALITY.
- Dependances : P58.
- Objectif : materialiser depuis la palette les enveloppes finales, soustraire
  les cavites fixes et synchroniser la scene BGIG.
- Livrables : plan -> CAD IR -> adaptateur, noms/metadata, generate/regenerate/
  inspect/clear/export, zero doublon et preservation non-BGIG.
- Acceptation : Fusion contient exactement les corps du plan courant, sans
  micro-remplissage ; la palette affiche scene synchronisee ou erreur avec retry.
- Statut : `implemented`, `automated-validated`, `fusion-validated: false`, `print-validated: false`.
- Preuves : constructeur `partition_cad.py`, bridge versionne, synchronisation generate/regenerate compacte, inspect/clear/export, packaging 0.1.6 et tests ciblés.

### P60 - Tentative historique d acceptance V0.1 Fusion-only

- Capability : C-QUALITY, C-PRODUCT-VISION, C-FUSION-UI.
- Dependances : P59.
- Objectif : executer tous les scenarios du contrat Fusion-only depuis add-in
  installe jusqu a scene et export.
- Preuves automatiques : moteur, DOM, bridge, packaging, CAD IR, correspondance
  plan/scene, zero corps auto, regeneration et absence de localhost runtime.
- Gate : observation humaine unique dans Fusion apres preparation automatique.
- Acceptation : editeur complet dans Fusion, cavites calibrees, volume absorbe
  par les bacs demandes, scene fidele, aucun serveur ou navigateur externe ;
  print-validated: false reste honnete.
- Statut : `product-review-ko`, `technical-baseline-useful` ; remplace comme gate de sortie par P66.

### P44 a P46 - V0.2 formes et ergonomie

- Dependances : P66 accepte.
- Scope : arrondis, chanfreins, encoches et fonds faciles a vider, avec impact
  reel sur volume, parois et fabrication.
- Statut : `deferred-until-v0.1`.

### P47 a P50 - V0.3 couvercles

- Dependances : P46 accepte.
- Scope : couvercle encastrable puis couvercle coulissant dans trois rainures
  interieures, entree ouverte, chanfreins et jeu 0 a 0,2 mm.
- Statut : `deferred-until-v0.2`.

### P60-UX-01 - Presets, corps pleins et dimensions de bac

- Capability : C-FUSION-UI, C-SOLVER, C-CAVITY, C-QUALITY.
- Dependances : runtime P60 0.1.8 fonctionnel jusqu a la materialisation.
- Livrables : palette 1280 x 1100, presets purs, Bac vide, Bloc plein / cale,
  Separateur et verrouillage X/Y/Z visible en mode simple.
- Statut : implemented, automated-validated, fusion-retest-required,
  print-validated: false.
- Gate renforcee : fixture 3 corps / 1 complement / 3 cavites / 0 automatique,
  Bac jetons X = 80 mm, cale solid sans cavite et sauvegarde projet locale.

### P61 historique - Empilement vertical explicite

- Capability : C-STACKING, C-LAYERS, C-GRID-3D, C-SOLVER, C-FUSION-UI.
- Dependances : P60 accepte.
- Objectif : definir plusieurs bacs en hauteur sans dupliquer implicitement les
  contenus ni confondre quantite de pieces, nombre de corps et nombre d etages.
- Premier livrable obligatoire : ADR, contrat pur et diagnostics pour ordre
  bas/haut, hauteur cumulee, support et depassement de boite.
- Validation cible : tests moteur et resultat palette, puis gate Fusion dediee.
- Statut : `superseded-by-p61-p65`, aucune implementation revendiquee.

### P60-R - Realignement produit apres revue Fusion

- Capability : C-PRODUCT-VISION, C-SOLVER, C-RESERVATION, C-FUSION-UI, C-QUALITY.
- Dependances : retour humain P60 du 2026-07-12.
- Objectif : expliquer les ecarts observes, challenger les options et redefinir
  un chemin V0.1 coherent sans modifier le runtime.
- Livrables : rapport de realignement, ADR-0056 a ADR-0060 proposees, roadmap,
  backlog, capability map, gates, visions et regles qualite realignes.
- Acceptation : chaque retour utilisateur est classe, les contradictions P40/
  P57 sont explicites et aucune implementation n est revendiquee.
- Statut : `done-docs`, `product-review-ko`, `technical-baseline-useful`.

### P61 - Etat reactif et architecture de palette

- Capability : C-FUSION-UI, C-PROJECT, C-QUALITY.
- Dependances : P60-R et acceptation ADR-0056/ADR-0060.
- Objectif : rendre toute mesure editable, recalculer les derives, distinguer
  plan obsolete et scene materialisee, et supprimer les diagnostics intrusifs.
- Livrables : etats/digests, invalidation, ancien apercu grise, parcours cible,
  listes compactes/detaillees, barre persistante et tiroir technique.
- Acceptation : inspect sain silencieux ; aucune scene Fusion ne change sans
  action ; les transitions et le DOM sont testes.
- Hotfix 0.1.11 : `Materialiser` cree la premiere scene ou regenere l unique
  scene BGIG saine ; verification du registre apres execution et blocage des
  scenes ambigues sans suppression.
- Statut : `done`, `implemented`, `automated-validated`, `fusion-retest-required`.

### P62 - Catalogue d elements et orientations

- Capability : C-ASSET, C-CAVITY, C-FUSION-UI.
- Dependances : P61 integre et ADR-0058 acceptee.
- Objectif : formats nommes, sleeves, orientations a plat/debout/auto et presets
  personnels locaux sans masquer les dimensions resolues.
- Acceptation : surcharge explicite prioritaire, aller-retour preset et impact
  d orientation verifies dans le coeur et la palette.
- Livrable : package 0.1.12, catalogue local, dimensions physiques/resolues,
  epaisseur mesuree ou comptee et presets personnels atomiques hors package.
- Statut : `done`, `implemented`, `automated-validated`, `fusion-retest-required`.

### P63 - Reservations superieures encastrees

- Capability : C-RESERVATION, C-STACKING, C-CAD-IR, C-FUSION-UI.
- Dependances : P62 et acceptation ADR-0057 qui remplace ADR-0050.
- Objectif : creuser localement plateaux/livrets depuis le dessus, avec ordre de
  retrait, appui et zone de prise, sans reduire toute la hauteur des conteneurs.
- Acceptation : intersections, non-percement, vues et coupe Fusion prouvent un
  plateau affleurant ; aucune ergonomie courbe V0.2 n est revendiquee.
- Livrable : package 0.1.13, contrat `bgig.top_inset_reservations.v1`, coupes
  CAD IR/Fusion distinctes et Apercu localise.
- Statut : `done`, `implemented`, `automated-validated`, `fusion-retest-required`.

### P64 - Solveur volumetrique multi-etages

- Capability : C-SOLVER, C-GRID-3D, C-STACKING, C-QUALITY.
- Dependances : P63 et acceptation ADR-0059.
- Objectif : arrangements XY par etage, composition Z, supports/retraits,
  Auto/Cible/Fixe, surplus pondere, residuels et suggestions explicites.
- Invariant : aucun corps automatique ; une suggestion de cale ne mute rien.
- Acceptation : fixtures multi-etages, conservation, collisions, support,
  retrait et budget de recherche deterministe testes.
- Livrable : `bgig.volumetric_stage_solver.v1`, CAD IR a origines Z, apercu
  d etages/residuels, blocage des propositions partielles et package 0.1.15.
- Durcissement : piles verticales hybrides, limites locales apres rotation,
  profondeur de cavite compensee sous plateaux et noms Fusion uniques.
- Statut : done, implemented, automated-validated, runtime-hardened,
  fusion-retest-required, print-validated: false.

### P65 - Conteneurs, reglages et apercu integres

- Capability : C-FUSION-UI, C-MODULE, C-TOLERANCE, C-QUALITY.
- Dependances : P64 integre et ADR-0060 acceptee.
- Objectif : centraliser les corps explicites, tailles min/cible/calculee,
  estimation, jeux et minima ; traduire le resultat et ses sous-scores.
- Acceptation : aucun code moteur au premier niveau ; Materialiser est primaire,
  persistant et garde par une solution complete/a jour ; les tolerances restent
  experimentales et leurs valeurs par defaut ne sont pas recalibrees.
- P65-M001 : done - jeux X-Y/Z separes, heritage compatible, budget Z solve,
  CAD IR, palette 0.1.16 et action de materialisation persistante.
- P65-M002 : done, implemented, automated-validated, fusion-retest-required -
  jeux boite/conteneur et inter-conteneurs separes :
  perimetre X-Y par cote, ecart X-Y total, ecart Z total et marge Z superieure.
  Le fond reste ancre a Z=0 ; aucune cale ou geometrie de support n est creee.
  Les deux sketches de reference de boite restent presents et tagues, mais sont
  masques par defaut apres materialisation et regeneration.
- P65-M003 : done, implemented, automated-validated,
  fusion-retest-required - package 0.1.18. La projection Python
  `bgig.container_sizing_view.v1` distingue minimum derive, demande
  Auto/Cible/Fixe, taille calculee depuis le plan, surplus et raisons par axe.
  `Estimer les tailles` reutilise `solve_project`, bloque les doubles calculs
  et ne mute ni projet, ni scene Fusion. Interdits respectes : nouvel estimateur,
  changement de solveur/tolerance/geometrie et corps automatique.
- P65-M004 : done, implemented, automated-validated,
  fusion-retest-required - package 0.1.19. bgig.preview_explanations.v1 traduit
  score comparatif, appuis, ordre de retrait, residuels et suggestions sans
  modifier plan, score, materialisabilite, solveur ou geometrie. Apercu ne
  duplique ni Recalculer ni Materialiser ; Exporter les imprimables est primaire.
- Statut : `done`, `implemented`, `automated-validated`, `fusion-retest-required`, `print-validated: false`.

### P66 - Acceptance V0.1 revisee Fusion-only

- Capability : C-QUALITY, C-PRODUCT-VISION, C-FUSION-UI, C-SOLVER.
- Dependances : P61 a P65-M004 implementes et automatises.
- Objectif : valider dans Fusion un projet reel avec plateaux encastres,
  orientations de cartes, plusieurs etages, edition/recalcul, regeneration,
  export et preservation des objets non BGIG.
- Gate : observation humaine preparee automatiquement.
- Preparation : P66-M000 met en quarantaine la creation des complements
  experimentaux ; P66-M001 construit et installe ensuite le projet canonique
  sans complement ainsi que sa checklist.
- Correctifs : uniquement P66-Hxx bornes si une observation est KO ; aucune
  ouverture V0.2 avant un nouveau passage vert puis l atelier humain P67.
- Statut : `done`, `mvp-accepted`, `fusion-validated`, `print-validated: false`.

La carte historique P61 `Empilement vertical explicite` ci-dessus est remplacee
par P61-P65 : ajouter seulement un nombre d etages ne corrigerait ni P40 ni P57.
P44-P46 dependent desormais de P66 puis P67 ; P47-P50 restent dependants de P46.

#### P66-M000 - Quarantaine des complements experimentaux

- Contrat : `docs/P66_TERRA_EXECUTION_CONTRACT.md` et ADR-0061.
- Livrables : retirer du parcours normal les actions `Bac vide`, `Bloc plein /
  cale` et `Separateur`, retirer les complements des presets et de la fixture
  canonique P66, conserver schema, loader, coeur et materialisation historiques.
- Compatibilite : un ancien projet contenant un complement explicite reste
  chargeable, sauvegardable et regenerable ; aucune migration destructive.
- Interdit : aucun changement de solveur, tolerance, geometrie, nombre de corps
  automatique ou semantique future des complements.
- Preuves : tests DOM, roundtrip projet, bridge/materialisation historique,
  package 0.1.20 et absence d action normale de creation.
- Statut : `done`, `implemented`, `automated-validated`, `fusion-retest-required`.

#### P66-M001 - Preparation automatisee

- Dependances : P66-M000 integree et package 0.1.20 verifie.
- Contrat : `docs/P66_TERRA_EXECUTION_CONTRACT.md`.
- Livrables : fixtures complete sans complement et impossible, test de
  preparation, preflight pur Python, preparateur PowerShell idempotent, package
  du commit exact, marqueurs et checklist Fusion de 21 etapes.
- Interdit : aucun correctif opportuniste du solveur, de l UI, des tolerances ou
  de la geometrie pour faire passer la fixture.
- Sortie : `gate-prepared`, jamais `fusion-validated`.
- Statut : `done`, `automated-validated`, `gate-prepared`, `p66-v-accepted`, `print-validated: false`.
#### P66-V - Gate humaine Fusion

- Dependances : P66-M001 integree, suite complete et installation reelle vertes.
- Resultat : `P66 Fusion OK` ou KO numerote avec attendu, observe et message.
- Une seule etape KO refuse toute l acceptance et ouvre un P66-Hxx borne.
- Statut : `done`, `fusion-validated`, `print-validated: false`.

#### P66-Hxx - Hotfix conditionnel

- Une cause par mission, reproduction automatisee quand possible, aucune
  extension V0.2/V0.3 et nouvelle gate complete apres correction.
- Statut : `conditional-on-p66-ko`.

#### P66-CLOSE - Cloture V0.1

- Dependances : retour humain explicite P66 OK.
- Mettre le pilotage a `mvp-accepted`, `fusion-validated`,
  `print-validated: false`, rendre P67 `ready` et P68 `planned-after-p66`.
- Ne rendre aucune mission P44 `ready` avant la decision humaine P67.
- Publication/tag et debut P44 restent des decisions/missions separees.
- Statut : `done`, `mvp-accepted`, `fusion-validated`, `print-validated: false`.

### P67 - Atelier humain de priorisation post-MVP

- Capability : C-PRODUCT-VISION, C-QUALITY, C-FUSION-UI.
- Dependances : P66 OK ; premieres observations d usage P68 disponibles si
  possible, sans en faire une condition bloquante.
- Objectif : redefinir humainement l ordre, les criteres et le perimetre de
  P44-P50 avant toute implementation V0.2.
- Livrable : decisions explicites sur formes/ergonomie, complements, vrais
  inserts prioritaires, niveau de preuve et ordre des missions.
- Sortie : P44-M001 peut devenir `ready` seulement apres acceptation du compte
  rendu P67 ; P67 ne remplace pas la revue UI/UX exhaustive P69.
- Contrat : `docs/P67_POST_MVP_PRIORITIZATION_CONTRACT.md`.
- Statut : `ready`, `human-review-required`, `no-runtime-change`.

### P68 - Boucle de premiers inserts reels

- Capability : C-QUALITY, C-FUSION-UI, C-MODULE, C-TOLERANCE.
- Dependances : P66 OK et une impression volontaire de l utilisateur.
- Objectif : recueillir des faits d usage, de Fusion et d impression sans
  modifier silencieusement les valeurs par defaut ni revendiquer une calibration.
- Livrable : fiches par insert avec projet/commit, observations, mesures,
  irritants, severite et candidats backlog.
- Contrat : `docs/P68_FIRST_USE_PRINT_FEEDBACK.md`.
- Statut : `planned-after-p66`, `print-validated: false`.

### P69 - Revue UI/UX exhaustive avant P70+

- Capability : C-PRODUCT-VISION, C-FUSION-UI, C-QUALITY.
- Dependances : P50 acceptee ; retours P68 disponibles si des impressions ont ete realisees.
- Objectif : revue humaine complete, capturee et tres commentee de tout le
  parcours Fusion apres les briques P44-P50.
- Livrable : audit par ecran/etat/profil, problemes classes, alternatives,
  recommandations et backlog P70+ ; aucun correctif runtime dans la revue.
- Contrat : `docs/P69_FULL_UI_UX_REVIEW_CONTRACT.md`.
- Statut : `blocked-by-p50`.
