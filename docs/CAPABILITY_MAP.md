# Capability Map

## Objectif

Ce document relie la North Star aux missions executables. Il evite que Codex
choisisse une mission seulement parce qu'elle est proche techniquement : chaque
mission doit servir une capability, un milestone et une validation claire.

Chaine de pilotage :

`North Star -> Product Pillars -> Capabilities -> Milestones -> Epics -> Missions -> Tasks -> Gates -> Validation`.

## Statuts de capability

- `planned` : cible decrite, non design detaille.
- `designed` : contrat ou strategie documente, pas encore implemente.
- `implemented-core` : implemente et teste dans le coeur Python pur.
- `implemented-cad-ir` : transporte dans la CAD IR, sans generation CAD reelle.
- `implemented-fusion` : genere par l'adaptateur Fusion, hors validation humaine.
- `fusion-validated` : inspecte et mesure manuellement dans Fusion.
- `print-validated` : imprime et mesure avec contexte documente.
- `deferred` : volontairement reporte.
- `blocked` : bloque par gate, dependance ou decision humaine.

## Product Pillars

| Pillar | Role produit | Documents de reference |
| --- | --- | --- |
| Asset-first design | Partir du materiel reel a ranger, pas seulement de modules manuels. | `docs/ASSET_MODEL_STRATEGY.md`, `docs/CONFIG_SCHEMA.md` |
| Volumetric layout | Organiser tout le volume X/Y/Z de la boite, avec etages et reservations. | `docs/VOLUMETRIC_LAYOUT_STRATEGY.md`, `docs/LAYER_AND_STACKING_MODEL.md` |
| Modular printable bodies | Produire des corps imprimables nommes, tolerancees et auditables. | `docs/GEOMETRY_MODEL.md`, `docs/TOLERANCE_MODEL.md` |
| Cavities and ergonomic features | Decrire les logements, aides de prise, fonds arrondis et futures operations. | `docs/GEOMETRY_MODEL.md` |
| CAD generation pipeline | Transporter les decisions moteur vers Fusion sans recalcul. | `docs/CAD_IR_CONTRACT.md`, `docs/FUSION_360_STRATEGY.md` |
| Human validation gates | Bloquer les decisions physiques, Fusion reelle et changements de vision. | `docs/HUMAN_GATES.md`, `docs/VALIDATION_MATRIX.md` |
| Design language and aesthetics | Ajouter labels, gravure, textures et style sans casser la fonction. | `docs/PRODUCT_SPEC.md` |

## Architecture Tracks

| Track | Role | Capabilities principales |
| --- | --- | --- |
| Product control plane | Gouvernance, autonomie, gates, validation et logs. | C-CALIBRATION, gates transverses |
| Pure engine | Donnees, validation, layout, tolerances, cavites et assets. | C-BOX, C-MODULE, C-CAVITY, C-FEATURE, C-ASSET |
| Volumetric model | X/Y/Z, layers, reservations, stacking, free volumes. | C-GRID-3D, C-LAYERS, C-RESERVATION, C-STACKING |
| CAD IR | Contrat CAD-agnostic et serialisation. | C-CAD-IR |
| Fusion adapter | Vues inspectables, commande utilisateur minimale et operations CAD autorisees. | C-FUSION-COMPACT, C-FUSION-EXPLODED, C-FUSION-CAVITIES, C-FILLETS, C-FUSION-UI |
| Physical product | Calibration, impression, ergonomie et beta utilisable. | C-CALIBRATION, C-ACCESS, C-AESTHETIC |

## Epics de reference

| Epic | Objectif | Phases principales |
| --- | --- | --- |
| E-GOV | Garder le depot autopilotable et gate-aware. | 0, 14 |
| E-CORE | Maintenir un moteur pur testable hors Fusion. | 1, 2, 3, 5 |
| E-CAD | Transporter et generer sans recalcul metier. | 4, 6, 7 |
| E-VOLUME | Passer du placement 2D a l'organisation X/Y/Z. | 8, 9, 10 |
| E-PHYSICAL | Fermer la boucle Fusion, impression, ergonomie. | 11, 12, 13, 14 |
## Capabilities

| ID | Capability | Pillar | Statut | Milestone cible | Gate principale |
| --- | --- | --- | --- | --- | --- |
| C-BOX | Box model | Asset-first design | `implemented-core` | M1 Engine foundation | Aucune active |
| C-ASSET | Asset model | Asset-first design | `fusion-validated-v0` | M6 Asset-first project model | Assets charges/reportes P9-M002; module_candidates metadata P10-M004/P10-M005; grouping borne P10-M006; plan executable borne P10-M008; P13-M001/P13-M001V valide Fusion une saisie `quick_asset_box` V0 honnete avec module proxy asset-first, assets lus depuis l UI, generate/regenerate/clear et limites explicites; P13-ASSET-M002/P13-ASSET-M002V valide Fusion le sizing count-aware V0 pour assets simples, diagnostics de piles/capacite, debug visual asset-fit, regenerate sans doublon et preservation non-BGIG; P13-ASSET-M003/P13-ASSET-M003V valide Fusion une cavite rectangulaire globale asset-fit V0 via `single_asset_fit_rectangular_cavity_v0`; P13-ASSET-M004/P13-ASSET-M004V valide Fusion `per_source_asset_rectangular_compartments_v0` avec compartiments rectangulaires par asset source; P13-ASSET-M005/P13-ASSET-M005V valide Fusion `per_compartment_top_open_rectangular_notch_v0` avec deux encoches rectangulaires top-open frontales par compartiment supporte; dette UX `quick_asset_box` documentee; assets individuels, cavites par pile/item, capacite physique garantie, solveur global, UI avancee et impression restent gates |
| C-MODULE | Module model | Modular printable bodies | `implemented-core` | M1 Engine foundation | Aucune active |
| C-CAVITY | Cavity model | Cavities and ergonomic features | `implemented-cad-ir` | M4 Abstract cavities | Gate Fusion cuts |
| C-FEATURE | Ergonomic feature model | Cavities and ergonomic features | `implemented-cad-ir` | M4 Abstract cavities / M8 Ergonomic planner | Taxonomie P6-M003 implementee ; gate Fusion pour nouvelles geometries |
| C-LAYOUT-2D | 2D layout | Volumetric layout | `implemented-core` | M2 Simple layout | Aucune active |
| C-GRID-3D | 3D volumetric grid | Volumetric layout | `implemented-cad-ir` | M7 Volumetric planner | P8-M001 implemente le socle declaratif; P10-M008 utilise un placement greedy abstrait; P11-M001 est `fusion-validated` pour la consommation compacte des placements; P11-M002 est validee Fusion pour la scene multi-layer; P11-M003 corrige le sizing explicite grille / asset-fit / printable; P11-M003V2 ajoute le rapport bbox planned/actual; P11-M003V3 corrige la vraie commande UI visible; P11-M003V4 valide Fusion la scene produit non ambigue et le mapping source; print-validated: false |
| C-LAYERS | Layer / stage model | Volumetric layout | `implemented-cad-ir` | M7 Volumetric planner | Layers declaratifs P8-M001; gate impression avant support physique |
| C-RESERVATION | Board / tray / lid reservation | Asset-first design | `implemented-cad-ir` | M6 Asset-first project model | Reservations abstraites P8-M002; gate si impact dimensions publiques ou generation Fusion |
| C-ACCESS | Accessibility and removal order | Human validation gates | `fusion-validated` | M8 Ergonomic planner | Removal order abstrait P8-M002; P13-ASSET-M005/P13-ASSET-M005V valide Fusion une encoche rectangulaire top-open par compartiment supporte; validation ergonomique avancee et impression reelle non revendiquees |
| C-STACKING | Support / stacking rules | Volumetric layout | `implemented-cad-ir` | M7 Volumetric planner | Support surfaces abstraites P8-M002; gate impression reelle |
| C-COMPOSITE | Composite modules | Modular printable bodies | `planned` | M9 Composite modules | Gate modules composites |
| C-CAD-IR | CAD IR | CAD generation pipeline | `implemented-cad-ir` | M3 CAD pipeline | Gate si contrat incompatible |
| C-FUSION-COMPACT | Fusion compact view | CAD generation pipeline | `fusion-validated` | M3 CAD pipeline / M7 Volumetric planner | Blanks rectangulaires valides; vue compacte grille P11-M001 validee manuellement dans Fusion; P11-M002 validee Fusion pour multi-layer; P11-M003 change les bodies asset-first vers `printable_body_size_mm`; P11-M003V2 refuse les tailles ambigues et affiche la bbox reelle; P11-M003V3 corrige la commande UI visible; P11-M003V4 valide Fusion la scene produit non ambigue et le mapping source; print-validated: false |
| C-FUSION-EXPLODED | Fusion exploded view | CAD generation pipeline | `fusion-validated` | M5 CAD inspection views | P7-M001V4 valide la vue eclatee basique par composants uniques et occurrences compactes/eclatees liees en document Assembly-compatible; Part Design est detecte comme incompatible; le renommage direct de `Occurrence.name` est evite; P11-M002 valide une scene eclatee multi-layer; P11-M003 conserve les occurrences liees via commande UI; P11-M003V2 ajoute le rapport dimensionnel; P11-M003V3 corrige la commande UI visible; P11-M003V4 valide Fusion la scene produit non ambigue et le mapping source; print-validated: false |
| C-FUSION-UI | Fusion command UI | CAD generation pipeline | `fusion-validated` | M14 Usable beta | P11-M003 ajoute une commande Fusion minimale avec chemin CAD IR et mode compact/exploded; P11-M003V4 valide l'usage UI avec scene produit non ambigue; P12-M001 valide Fusion le bouton toolbar relancable; P12-M002V7 corrige la commande parametrique V0 avec modes `cad_ir_file`/`config_file`, action `inspect_bgig_scene`, registry BGIG, root auto-detecte/memorise, scene racine `BGIG Generated Scene`, `generate` refuse les doublons, occurrence racine unique taguee `bgig:role = scene_root`, attributs `scene_id`/`role`/`module_id`, suppression par `deleteMe()`, occurrence compacte initiale visible, occurrence eclatee liee via `addExistingComponent`, `regenerate` remplace sans doublons attendu et `clear_bgig_scene` supprime la racine; P12-UI-M002V7 validee Fusion avec inspect/generate/regenerate/clear, registry et ownership racine BGIG; reporting inspect deduplique; P12-M003V valide Fusion `quick_parametric_box` en `compact_only` avec CAD IR temporaire, registry OK, occurrence compacte visible et bbox conforme; P12-M004/P12-M004V valide Fusion la persistance complete des champs UI, la rehydratation au prochain `commandCreated`, le diagnostic `UI settings`, `generate`, `regenerate`, reouverture avec derniere valeur conservee et `clear_bgig_scene` preservant les objets non-BGIG; KO initial par settings PowerShell UTF-8 BOM documente et corrige; P13-M001/P13-M001V valide Fusion `quick_asset_box` comme premier input asset-first depuis la commande Fusion classique, avec champ texte assets persiste, config temporaire, reuse du pipeline assets existant, reporting V0 honnete, outlines bas/haut du volume boite, generate/regenerate/clear sans doublon et preservation des objets non-BGIG; P13-ASSET-M002/P13-ASSET-M002V valide Fusion le sizing count-aware V0, `storage_sizing`, diagnostics `capacity_per_stack`/`pile_count`/`declared_capacity`, sketch debug asset-fit non imprimable, regenerate count-aware et clear final; P13-ASSET-M003/P13-ASSET-M003V valide Fusion une cavite asset-fit globale dans le flux `quick_asset_box`; P13-ASSET-M004/P13-ASSET-M004V valide Fusion des compartiments asset-specific V0, reporting associe, debug outlines, generate/regenerate/clear; P13-ASSET-M005/P13-ASSET-M005V valide les compteurs et diagnostics `asset_access_*`, generate/regenerate/clear; dette UX `quick_asset_box` documentee; limites non validees : assets individuels, cavites par pile/logements detailles, capacite physique garantie, solveur global, optimisation avancee, UI avancee et impression; print-validated: false |
| C-FUSION-CAVITIES | Fusion cavities | CAD generation pipeline | `fusion-validated` | M5 CAD cavities | Cavites rectangulaires CAD IR validees Fusion; P13-ASSET-M003/P13-ASSET-M003V valide Fusion une cavite asset-fit globale V0; P13-ASSET-M004/P13-ASSET-M004V valide Fusion plusieurs cavites top-open par asset source via `per_source_asset_rectangular_compartments_v0`; print-validated: false |
| C-FILLETS | Fillets and finger notches | CAD generation pipeline | `fusion-validated` | M5 CAD ergonomic features | Encoche rectangulaire top-open P6 validee Fusion, print-validated: false ; P13-ASSET-M005/P13-ASSET-M005V valide cette coupe pour les access notches asset-first ; courbes/fillets bloques |
| C-SOLVER | Solver and scoring | Volumetric layout | `implemented-core` | M10 Semi-automatic solver | Variant comparison P10-M002 report-only; raisons de rejet structurees P10-M003; module_candidates P10-M004; variante recommandee P10-M005; grouping borne P10-M006; plan concret greedy P10-M008; P13-M001 reutilise ce pipeline sans backtracking ni optimisation globale; P13-ASSET-M002/P13-ASSET-M002V valide une heuristique count-aware bornee pour piles/footprint/refus explicite sans solveur global; gate architecture si optimiseur majeur |
| C-CALIBRATION | Calibration and print validation | Human validation gates | `designed` | M11 Physical validation | Impression reelle |
| C-AESTHETIC | Aesthetic layer | Design language and aesthetics | `planned` | M12 Design language | Gate esthetique structurante |
| C-PRODUCT-VISION | Product composition model | Product control plane | `implemented-cad-ir` | P19 BoxFillPlan V0 | P19 plan manuel valide, reporte et transporte sans Fusion source de verite; P20 greedy reste gate |

## Milestones utilisateur

| ID | Milestone | Definition de valeur | Capabilities principales |
| --- | --- | --- | --- |
| M1 Engine foundation | Une config locale produit un rapport teste hors Fusion. | C-BOX, C-MODULE |
| M2 Simple layout | Des modules rectangulaires sont places en 2D avec tolerances explicites. | C-LAYOUT-2D |
| M3 CAD pipeline | Une CAD IR exportee produit des blanks mesurables dans Fusion. | C-CAD-IR, C-FUSION-COMPACT |
| M4 Abstract cavities | Les cavites et aides ergonomiques sont modelisees sans generation reelle. | C-CAVITY, C-FEATURE |
| M5 CAD cavities | Fusion genere des cavites simples controlees par gate et smoke test. | C-FUSION-CAVITIES |
| M6 Asset-first project model | L'utilisateur decrit les assets et reservations avant les modules. | C-ASSET, C-RESERVATION |
| M7 Volumetric planner | Le moteur raisonne en X/Y/Z, etages, empilement et volumes libres. | C-GRID-3D, C-LAYERS, C-STACKING |
| M8 Ergonomic planner | Le moteur expose accessibilite, ordre de retrait et aide de manipulation. | C-ACCESS, C-FEATURE |
| M9 Composite modules | Les corps soudes et formes non rectangulaires simples sont representes. | C-COMPOSITE |
| M10 Semi-automatic solver | Plusieurs propositions scorees sont comparees et expliquees. | C-SOLVER |
| M11 Physical validation | Les tolerances et geometries critiques sont calibrees par impression. | C-CALIBRATION |
| M12 Design language | Labels, gravures, motifs et decoration restent parametrables et surs. | C-AESTHETIC |
| M13 Advanced mechanisms | Couvercles, rainures, clips et empilement avance restent gate-aware. | C-STACKING, futurs mecanismes |
| M14 Usable beta | Un jeu reel peut etre documente, genere, imprime et ajuste. | C-CALIBRATION, C-AESTHETIC, C-FUSION-UI |

## Regle d'usage par Codex

Avant de selectionner une mission, Codex doit indiquer implicitement ou dans le
pilotage : capability servie, milestone lie, dependances, gate et validation. Une
mission `ready` qui ne sert aucune capability doit etre recadree avant execution.

Apres chaque mission significative, Codex met a jour le statut des capabilities
impactees dans ce document ou dans `docs/STATUS.md` si le changement est ponctuel.

## P13-ASSET-M002 capability update

- C-ASSET : `fusion-validated-v0` pour sizing count-aware V0 tokens/dice/meeples/generic, cartes en semantique paquet total explicite, capacite heuristique non print-validee.
- C-SOLVER : `fusion-validated-v0` pour heuristique bornee sans backtracking ; refus explicite si enveloppe impossible.
- C-FUSION-UI : `fusion-validated` pour reporting count-aware, `storage_sizing` et sketch debug asset-fit non imprimable ; P13-ASSET-M003V validee ; prochaine gate produit `P13-ASSET-M004-GATE`.

## P13-ASSET-M003 capability update

- C-ASSET : `fusion-validated-v0` pour une cavite asset-fit globale issue de l'enveloppe count-aware.
- C-FUSION-CAVITIES : `fusion-validated` pour reuse de `subtract_rectangular_cavity` sur les modules `executable_asset_plan`, sans nouvelle geometrie complexe.
- C-FUSION-UI : `quick_asset_box` valide Fusion avec reporting `asset_cavity_policy`, compteurs planned/generated et diagnostics de fond/murs.
- C-SOLVER : inchange ; aucune optimisation globale, aucun backtracking, aucune cavite par pile.


## P13-ASSET-M004 capability update

- C-ASSET : `fusion-validated-v0` pour compartiments rectangulaires par asset source dans un module count-aware unique ; assets individuels et piles restent non visualises.
- C-FUSION-CAVITIES : `fusion-validated` pour plusieurs coupes top-open `asset_compartment_cavity` generees depuis `asset_fit_cavity.compartments`.
- C-FUSION-UI : `fusion-validated` pour reporting `asset_compartments_generated`, compteurs de compartiments, debug outlines, generate/regenerate/clear ; dette UX `quick_asset_box` enregistree.
- Gate active : `P13-ASSET-M006-GATE`; aucune validation d'impression.

## P13-ASSET-M005 capability update

- C-ASSET : `fusion-validated-v0` pour metadata `asset_access_notch` par compartiment supporte apres validation Fusion P13-ASSET-M005V.
- C-ACCESS : `fusion-validated` pour la premiere aide de prise asset-first V0, rectangulaire top-open et front-wall-only.
- C-FILLETS : reuse de la coupe rectangulaire top-open existante, sans courbes, demi-lunes reelles, scoops, fillets ou conges.
- C-FUSION-UI : reporting `asset_access_*`, smoke quick_asset_box, generate/regenerate/clear valides dans Fusion ; `P13-ASSET-M006-GATE` est la gate active.

## P13-ASSET-M005V capability update

- C-ASSET : `fusion-validated-v0` pour les encoches d'acces par compartiment supporte dans le flux asset-first.
- C-ACCESS : `fusion-validated` pour aide de prise V0 rectangulaire top-open frontale par compartiment.
- C-FILLETS : reuse Fusion valide des coupes rectangulaires top-open, sans demi-lunes, courbes, scoops, fillets ou conges.
- C-FUSION-UI : `quick_asset_box` valide Fusion avec reporting `asset_access_*`, regenerate sans doublon et clear preservant les objets non-BGIG.
- Gate active suivante : `P13-ASSET-M006-GATE`; aucune validation d'impression.

## P14-USABLE-ASSET-TRAY-M001 capability update

- C-ASSET : `implemented-core` additionnel pour layout multi-assets row/column/shelf avec refus explicite si les compartiments ne tiennent pas.
- C-SOLVER : heuristique deterministe bornee, sans backtracking ni optimisation globale.
- C-FUSION-UI : benefice attendu dans `quick_asset_box`, mais validation Fusion P14 reste requise.
- Limites : pas de cavites par pile/item, pas d'assets individuels, pas d'impression validee.

## P14-USABLE-ASSET-TRAY-M002 capability update

- C-CALIBRATION : `implemented-core` pour rapport geometrique `printability_report_v0`, sans validation physique.
- C-ASSET : modules asset-first enrichis avec checks murs/fond/cavite/encoche.
- C-FUSION-UI : reporting `quick_asset_box` expose `printability_checked: yes` et `printability_validated_by_print: no`.

## P14-USABLE-ASSET-TRAY-M003 capability update

- C-FUSION-UI : `implemented-fusion-ui` pour aide inline `quick_asset_box`, exemple de saisie, rappel des unites et labels parametriques plus lisibles.
- C-ASSET : UX de saisie asset-first plus explicite, sans changement de schema ni palette HTML.

## P14-USABLE-ASSET-TRAY-M004 capability update

- C-FUSION-UI : `implemented-smoke-prep` pour presets de preparation `quick_asset_box` via script Fusion.
- C-ASSET : scenarios V0 tokens, dice/meeples/generic et cards+tokens documentes comme entrees de smoke test, sans nouveau solveur ni nouvelle geometrie.
- Validation : tests automatises OK, validation Fusion sprint P14 requise, aucune impression reelle validee.
## P14-USABLE-ASSET-TRAY-M005 capability update

- C-FUSION-UI : `gate-prepared` pour la validation Fusion sprint P14 avec add-in installe et settings `quick_asset_box` precharges.
- C-ASSET : scenario tokens P14 pret pour validation humaine, presets alternatifs disponibles mais non Fusion-valides.
- C-QUALITY : marqueurs d'add-in installes verifies par script.
- Validation : tests automatises OK, gate humaine Fusion active, aucune impression reelle validee.
## P15-M001 capability update

- C-ASSET : `specified` pour semantique tray V0 via ADR-0033.
- C-QUALITY : `done-docs` pour audit z/count/grid/grouping.
- Validation : documentaire seulement, aucun changement moteur, aucune validation Fusion ou impression.
## P15-M002 capability update

- C-ASSET : `implemented-core` additionnel pour `storage_orientation` (`auto`, `flat_tray`, `vertical_stack`) et `max_stack_height_mm` additifs dans le modele assets.
- C-SOLVER : heuristique count-aware inchangee en nature, mais le defaut tokens/dice/meeples/generic privilegie maintenant un plateau bas borne plutot que l'utilisation implicite de toute la hauteur disponible.
- C-FUSION-UI : P15-M003 expose et persiste `quick_asset_box_max_stack_height_mm` dans la commande Fusion classique ; le resume `quick_asset_box` reporte `storage_orientation`, `stack_height_policy`, `max_stack_height_mm`, `stack_height_used_mm`, `xy_expansion_used` et `z_expansion_used`.

## P15-M003 capability update

- C-ASSET : `implemented-core` exploite maintenant l'override global `quick_asset_box` en `assets[].max_stack_height_mm` dans la config temporaire.
- C-FUSION-UI : `implemented-fusion-ui` pour champ optionnel persiste, rehydratation settings et reporting stack policy ; validation Fusion P15 reste a faire.
- C-QUALITY : regression ajoutee contre constantes UI manquantes et contre sizing `max_stack_height_mm = 6`.
- Validation : tests automatises moteur OK, aucune validation Fusion ni impression reelle.

## P15-M004 capability update

- C-GRID-3D : `implemented-reporting` pour semantique explicite `placement_reservation_lattice_v0`, span reserve distinct du body imprimable, et `body_snap_to_grid: no`.
- C-FUSION-UI : resume `quick_asset_box`, `Module source mapping` et `Body sizing report` exposent la difference grid span / printable body.
- C-QUALITY : tests couvrent metadata placements, plan Fusion et summary lisible.

## P15-M005 capability update

- C-FUSION-UI : `gate-prepared` pour preset `p15_tray_semantics` par defaut, settings `quick_asset_box` et `max_stack_height_mm = 18`.
- C-ASSET : scenario 5 assets bas couvrant tokens, dice, meeples et generic sans towers hautes par defaut.
- C-QUALITY : smoke P15 documente et automatisable via `prepare_quick_asset_test.ps1 -Preset p15_tray_semantics` puis validation humaine Fusion.

## P15 validation capability update

- C-ASSET : `fusion-validated-v0` pour le realignement semantique P15 : `z_mm` et `count` clarifies, `flat_tray` par defaut pour assets simples, `max_stack_height_mm` expose et pris en compte, expansion XY avant Z.
- C-GRID-3D : `fusion-validated-v0` pour le reporting de grille comme `placement_reservation_lattice_v0`, `body_snap_to_grid: no` et span reserve distinct du body imprimable.
- C-FUSION-UI : validation Fusion du preset `p15_tray_semantics`, persistance UI, generate/regenerate/clear, compartiments/encoches et reporting P15.
- Limite active : P16 doit corriger le layout `flat_tray_linear_v0` trop allonge en X ; aucune impression 3D validee.

## P16 capability target

- C-ASSET : cible `flat_tray_2d_v0` pour assets simples, avec piles organisees en colonnes/rangees.
- C-SOLVER : heuristique deterministe bornee, sans solveur global, backtracking ni optimisation avancee.
- C-FUSION-UI : reporting attendu `tray_packing_policy`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm`, warnings si 2D impossible.
- Gate : validation humaine Fusion P16 avant statut `fusion-validated-v0`; `print-validated: false` conserve.

## P16-M001 capability update

- C-ASSET : `specified` pour `flat_tray_2d_v0`, grille locale de piles et distinction explicite avec `flat_tray_linear_v0`.
- C-SOLVER : strategie heuristique locale documentee, sans solveur global, backtracking ni dependance externe.
- C-FUSION-UI : reporting P16 cible defini, notamment `tray_packing_policy`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm` et warnings de fallback.
- Validation : documentaire seulement ; implementation moteur attendue en P16-M002 ; aucune validation Fusion ou impression.

## P16-M002 capability update

- C-ASSET : `implemented-core` pour `flat_tray_2d_v0` sur tokens/dice/meeples/generic, diagnostics de grille locale de piles et dimensions module moins lineaires.
- C-SOLVER : heuristique locale deterministe implementee sans backtracking ni solveur global.
- C-FUSION-CAVITIES / C-ACCESS : compartiments, cavites rectangulaires et notches suivent les nouvelles enveloppes asset-fit, sans cavite par item.
- Validation : tests automatises OK ; validation Fusion P16 reste a faire ; `print-validated: false`.

## P16-M003 capability update

- C-FUSION-CAVITIES : diagnostics de cavites enrichis avec la grille locale de piles source.
- C-ACCESS : diagnostics d'encoches enrichis avec la politique `flat_tray_2d_v0` du compartiment.
- C-FUSION-UI : metadata quick_asset_box prete pour reporting P16 detaille ; affichage textuel final attendu en P16-M004.

## P16-M004 capability update

- C-FUSION-UI : `implemented-fusion-ui` pour champs optionnels persistants `Target aspect ratio` et `Max module length mm` dans `quick_asset_box`, avec rehydratation settings.
- C-ASSET : schema additif `assets[].target_aspect_ratio` et `assets[].max_module_length_mm`, appliques au packing `flat_tray_2d_v0` des assets simples.
- C-QUALITY : tests de regression ajoutes pour parsing/validation, influence du packing, persistance UI et resume Fusion.
- Validation : tests automatises OK ; validation Fusion P16 reste a faire ; `print-validated: false`.

## P16-M005 capability update

- C-FUSION-UI : `implemented-smoke-prep` pour preset par defaut `p16_ergonomic_tray_packing` et settings quick_asset_box incluant `target_aspect_ratio` / `max_module_length_mm`.
- C-ASSET : scenario 5 assets oriente validation ergonomique du packing `flat_tray_2d_v0`, sans nouvelle geometrie.
- C-QUALITY : catalogue de presets teste comme configs valides ; preparation gate Fusion attendue en P16-M006.
- Validation : tests automatises OK ; validation Fusion P16 reste a faire ; `print-validated: false`.

## P16-M006 capability update

- C-FUSION-UI : `gate-prepared` pour validation Fusion P16 avec preset `p16_ergonomic_tray_packing` et settings UI P16.
- C-QUALITY : scripts Fusion de preparation et verification add-in couvrent les marqueurs `quick_asset_box`, `target_aspect_ratio`, `max_module_length_mm` et diagnostics P16.
- Gate : validation humaine Fusion P16 active ; aucune impression reelle validee.


## P16 validation capability update

- C-ASSET : `fusion-validated-v0` pour `flat_tray_2d_v0` sur assets simples, piles organisees en colonnes/rangees et modules moins lineaires.
- C-FUSION-UI : validation Fusion du preset `p16_ergonomic_tray_packing`, persistance des champs P16, generate/regenerate/clear et reporting `linear_layout_avoided`.
- C-FUSION-CAVITIES / C-ACCESS : compartiments asset-specific et encoches top-open conserves avec les enveloppes 2D.
- Limite active : P17 doit traiter export/preprint ; aucune impression 3D validee.

## P17 capability target

- C-FUSION-EXPORT : nouvelle cible pour exporter des modules imprimables BGIG depuis Fusion, avec exclusions explicites des references/debug/helpers/non-BGIG.
- C-QUALITY : manifeste export JSON/Markdown, nommage deterministe, dossier de sortie et audit des modules refuses.
- C-CALIBRATION : printability blockers V0 et preparation preprint/coupon sans validation physique.
- Gate : validation humaine Fusion P17 avant tout statut `fusion-validated-v0` d'export ; `print-validated: false` conserve.


## P17-M001 capability update

- P17-M001 : `ADR-0035` accepte le contrat export/preprint V0.
- C-FUSION-EXPORT : statut `planned-contract`, export Fusion-only, STL par module V0, 3MF reporte sauf API simple.
- C-QUALITY : manifeste JSON/Markdown requis, noms deterministes, refus explicites.
- C-CALIBRATION : `print_validated: false` obligatoire ; aucune impression physique validee.


## P17-M002 capability update

- C-FUSION-EXPORT : statut `implemented-fusion-unvalidated` pour action `export_printables` STL V0 par `module_body` tague BGIG.
- C-QUALITY : rapport export avec compteurs, chemins et refus ; manifeste complet reporte a P17-M003.
- C-CALIBRATION : `print_validated: false` maintenu ; aucune impression physique validee.


## P17-M003 capability update

- C-QUALITY : statut `implemented-fusion-unvalidated` pour manifeste export JSON/Markdown V0.
- C-FUSION-EXPORT : `export_printables` renseigne chemins manifeste et fichiers exportes dans le rapport Fusion.
- C-CALIBRATION : le manifeste garde `print_validated: false` et warnings preprint ; aucune impression physique validee.


## P17-M004 capability update

- C-CALIBRATION : statut `implemented-core-fusion-reporting` pour blockers/warnings printability V0.
- C-QUALITY : `printability_report_v0` contient `issues[]`, `issue_counts`, `printability_status`, `printability_export_allowed`.
- C-FUSION-UI : `quick_asset_box` affiche statut printability et export allowed ; `print_validated: false` reste obligatoire.


## P17-M005 capability update

- C-CALIBRATION : statut `protocol-ready` pour protocole preprint V0 et fiche JSON remplissable.
- C-QUALITY : la validation preprint part du manifeste export et des issues printability, sans changer les tolerances.
- Gate : aucune impression physique validee ; `print_validated: false` maintenu.

## P17-M006 capability update

- C-FUSION-EXPORT : `gate-prepared` pour validation Fusion P17 avec preset `p17_printable_export` et action `export_printables`.
- C-QUALITY : preparation couvre manifestes JSON/Markdown, refus non-printables, `printability_export_allowed` et `print_validated: false`.
- Gate : validation humaine Fusion P17 confirmee le 2026-07-10 ; aucune impression physique validee.
## P17 validation capability update

- C-FUSION-EXPORT : `fusion-validated-v0` pour l'export Fusion-only STL par `module_body` BGIG, avec registry et exclusions fonctionnellement verifies dans Fusion.
- C-QUALITY : `fusion-validated-v0` pour les manifestes export JSON/Markdown et le reporting preprint V0; ils restent des traces d'audit, non des preuves physiques.
- C-CALIBRATION : le protocole preprint est exploitable apres export, mais `print-validated: false` reste obligatoire.
- Limite active : P17 valide une chaine technique export/preprint, pas une garantie d'impression ni le produit de remplissage volumetrique cible.

## P18-M001 capability update

- C-PRODUCT-VISION : `designed` par l'audit d'ecart; la boite complete, les intentions, reservations, variantes et l'edition de layout sont identifies comme le prochain niveau de produit.
- C-FUSION-UI : son statut d'adaptateur valide reste inchange; `quick_asset_box` est explicitement une UI de test/developpement, non l'UX finale.
- C-SOLVER / C-GRID-3D : les heuristiques locales et la lattice de reservation restent valides comme fondation, mais ne sont pas un remplissage intelligent global.

## P18-M002 capability update

- C-FUSION-UI : UX cible definie; commande classique = dev/smoke, palette persistante/app = prochaines surfaces possibles sous gate.
- C-ASSET / C-SOLVER : inventaire et variantes deviennent les objets UX principaux, sans changement de code.

## P18-M003 capability update

- C-PRODUCT-VISION : contrat GameBox a ExportPackage defini; BoxFillPlan devient la future source de verite CAD-agnostic.
- C-GRID-3D / C-LAYERS / C-RESERVATION : leurs concepts existants sont conserves et raccordes au modele produit cible.

## P18-M004 capability update

- C-SOLVER : roadmap en six etapes acceptee comme trajectoire documentaire; aucun solveur global n'est implemente.
- C-PRODUCT-VISION : ox_fill_v0_manual_modules est recommande comme premier increment verificable.

## P18-M005 capability update

- C-FUSION-UI : ADR-0036 propose de conserver CommandInputs pour dev/smoke; palette ou app restent bloquees par gate humaine.
- C-PRODUCT-VISION : la future UX consomme BoxFillPlan, pas une structure Fusion parallele.

## P18-M006 capability update

- C-PRODUCT-VISION : P19-A est recommande pour rendre BoxFillPlan verificable avant palette ou solveur global.
- Gate : extension additive de modele/schema P19 et choix UX ADR-0036 attendent validation humaine.

## P18 strategic validation capability update

- C-PRODUCT-VISION : `authorized-implementation` pour `box_fill_v0_manual_modules`; `BoxFillPlan` peut devenir le contrat executable CAD-agnostic du moteur pur.
- C-FUSION-UI : ADR-0036 est `accepted-roadmap`; CommandInputs reste dev/smoke, et palette/app restent bloquees avant une gate d'implementation specifique.
- C-SOLVER : aucun solveur global n'est autorise par P19; le prochain increment est manuel, deterministe et explicable.
## P19-M001 capability update

- C-PRODUCT-VISION : contrat `box_fill_plan.v0` accepte via ADR-0037; l'implementation peut commencer comme extension additive du moteur pur.
- C-GRID-3D / C-LAYERS / C-RESERVATION : les contrats existants seront adoptes par references et non remplaces.
## P19-M002 capability update

- C-PRODUCT-VISION : `implemented-core` pour le chargement versionne et retrocompatible de `box_fill_plan.v0` dans le moteur pur.
- C-ASSET : les allocations sont explicites et ne peuvent pas etre deduites d'une simple apparition d'asset dans un module.
- C-FUSION-UI : aucun comportement Fusion, palette ou UI persistante n'est ajoute.
## P19-M003 capability update

- C-PRODUCT-VISION : `implemented-core` pour la validation d'un plan manuel de boite complete et le FreeVolume aggregate explicable.
- C-RESERVATION / C-GRID-3D : bornes et collisions 3D sont verifiees dans le volume utile, sans redefinition de `volumetric_grid`.
- C-ASSET : couverture de quantite explicite; non-couverture et sur-allocation sont refusees avec des messages actionnables.
## P19-M004 capability update

- C-PRODUCT-VISION : le plan manuel est maintenant lisible et exportable comme contrat JSON/Markdown/CAD IR metadata.
- C-CAD-IR : `implemented-cad-ir-metadata` pour BoxFillPlan; aucune operation CAD/Fusion n'est derivee du plan manuel.
- C-FUSION-UI : inchangée; Fusion reste adaptateur futur et ne recalcule pas le plan.
## P19-M005 capability update

- C-PRODUCT-VISION : `implemented-cad-ir` pour BoxFillPlan V0, valide et transporte en metadata CAD IR sans Fusion comme source de verite.
- C-GRID-3D / C-LAYERS / C-RESERVATION : P19 valide l'occupation volumetrique manuelle et les collisions dans le moteur pur; le placement automatique reste non implemente.
- C-SOLVER : prochaine etape recommandee `box_fill_v1_greedy_2d`, bloquee par gate produit; aucun solveur global n'est autorise.