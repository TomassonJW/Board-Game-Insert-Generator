# Capability Map

## Objectif

Ce document relie la North Star aux missions executables. Il evite que Codex
choisisse une mission seulement parce qu'elle est proche techniquement : chaque
mission doit servir une capability, un milestone et une validation claire.

## Priorite de release - rebase du 2026-07-12

La carte ne constitue plus a elle seule un ordre d'execution. ADR-0047 impose le
chemin critique suivant : V0.1 fonctionnelle, puis V0.2 ergonomique, puis V0.3
couvercles. La table suivante est le snapshot historique P52-P60 ; le rebase
actif P61-P66 est defini en fin de document.

| Blocker V0.1 | Etat reel | Prochaine preuve |
| --- | --- | --- |
| Editeur Fusion embarque complet | palette P32 minimale fusion-validated | P56 |
| Tableau pieces et Bac cible dans Fusion | contrat et coeur reutilisables | P56 |
| Cavites calibrees par forme, quantite et jeu | P39 reutilisable | P55 |
| Pile plateaux/livrets | P40 reutilisable | P57 |
| Parois/fonds minimaux et tolerances | partiellement implementes | P55 |
| Enveloppes exterieures extensibles | absent | P55/P57 |
| Partition complete sans corps automatique | absent | P57 |
| Resultat et apercu issus du vrai plan | absent | P58 |
| Scene Fusion fidele et palette principale fiable | palette minimale seulement | P56/P59 |
| Parcours V0.1 accepte | P60 refuse comme acceptance | P66 |
`C-AESTHETIC` est `deferred` jusqu'a P66. Les mecanismes/couvercles sont
`deferred` jusqu'a P46. Les paragraphes historiques P33/P34 ci-dessous decrivent
du code existant, pas un statut de release acquis.

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
| C-GRID-3D | 3D volumetric grid | Volumetric layout | `implemented-cad-ir` | M7 Volumetric planner | P8-M001 implemente le socle declaratif; P10-M008 utilise un placement greedy abstrait; P11-M001 est `fusion-validated` pour la consommation compacte des placements; P11-M002 est validee Fusion pour la scene multi-layer; P11-M003 corrige le sizing explicite grille / asset-fit / printable; P11-M003V2 ajoute le rapport bbox planned/actual; P11-M003V3 corrige la vraie commande UI visible; P11-M003V4 valide Fusion la scene produit non ambigue et le mapping source; P64 ajoute les etages calcules, leurs origines Z et les residuels non imprimables ; observation Fusion P66 requise, print-validated: false |
| C-LAYERS | Layer / stage model | Volumetric layout | `implemented-cad-ir` | M7 Volumetric planner | Layers declaratifs P8-M001; P64 calcule une composition par etages et transporte ses origines Z en CAD IR ; gate Fusion P66 et impression avant portance physique |
| C-RESERVATION | Board / tray / lid reservation | Asset-first design | `implemented-cad-ir` | M6 Asset-first project model | Reservations abstraites P8-M002; gate si impact dimensions publiques ou generation Fusion |
| C-ACCESS | Accessibility and removal order | Human validation gates | `fusion-validated` | M8 Ergonomic planner | Removal order abstrait P8-M002; P13-ASSET-M005/P13-ASSET-M005V valide Fusion une encoche rectangulaire top-open par compartiment supporte; validation ergonomique avancee et impression reelle non revendiquees |
| C-STACKING | Support / stacking rules | Volumetric layout | `implemented-cad-ir` | M7 Volumetric planner | Support surfaces abstraites P8-M002; P64 verifie la couverture d appui minimale et le retrait top-down sans support automatique ; gate Fusion P66 et impression reelle |
| C-COMPOSITE | Composite modules | Modular printable bodies | `planned` | M9 Composite modules | Gate modules composites |
| C-CAD-IR | CAD IR | CAD generation pipeline | `implemented-cad-ir` | M3 CAD pipeline | Gate si contrat incompatible |
| C-FUSION-COMPACT | Fusion compact view | CAD generation pipeline | `fusion-validated` | M3 CAD pipeline / M7 Volumetric planner | Blanks rectangulaires valides; vue compacte grille P11-M001 validee manuellement dans Fusion; P11-M002 validee Fusion pour multi-layer; P11-M003 change les bodies asset-first vers `printable_body_size_mm`; P11-M003V2 refuse les tailles ambigues et affiche la bbox reelle; P11-M003V3 corrige la commande UI visible; P11-M003V4 valide Fusion la scene produit non ambigue et le mapping source; print-validated: false |
| C-FUSION-EXPLODED | Fusion exploded view | CAD generation pipeline | `fusion-validated` | M5 CAD inspection views | P7-M001V4 valide la vue eclatee basique par composants uniques et occurrences compactes/eclatees liees en document Assembly-compatible; Part Design est detecte comme incompatible; le renommage direct de `Occurrence.name` est evite; P11-M002 valide une scene eclatee multi-layer; P11-M003 conserve les occurrences liees via commande UI; P11-M003V2 ajoute le rapport dimensionnel; P11-M003V3 corrige la commande UI visible; P11-M003V4 valide Fusion la scene produit non ambigue et le mapping source; print-validated: false |
| C-FUSION-UI | Fusion command UI | CAD generation pipeline | `fusion-validated` | M14 Usable beta | P11-M003 ajoute une commande Fusion minimale avec chemin CAD IR et mode compact/exploded; P11-M003V4 valide l'usage UI avec scene produit non ambigue; P12-M001 valide Fusion le bouton toolbar relancable; P12-M002V7 corrige la commande parametrique V0 avec modes `cad_ir_file`/`config_file`, action `inspect_bgig_scene`, registry BGIG, root auto-detecte/memorise, scene racine `BGIG Generated Scene`, `generate` refuse les doublons, occurrence racine unique taguee `bgig:role = scene_root`, attributs `scene_id`/`role`/`module_id`, suppression par `deleteMe()`, occurrence compacte initiale visible, occurrence eclatee liee via `addExistingComponent`, `regenerate` remplace sans doublons attendu et `clear_bgig_scene` supprime la racine; P12-UI-M002V7 validee Fusion avec inspect/generate/regenerate/clear, registry et ownership racine BGIG; reporting inspect deduplique; P12-M003V valide Fusion `quick_parametric_box` en `compact_only` avec CAD IR temporaire, registry OK, occurrence compacte visible et bbox conforme; P12-M004/P12-M004V valide Fusion la persistance complete des champs UI, la rehydratation au prochain `commandCreated`, le diagnostic `UI settings`, `generate`, `regenerate`, reouverture avec derniere valeur conservee et `clear_bgig_scene` preservant les objets non-BGIG; KO initial par settings PowerShell UTF-8 BOM documente et corrige; P13-M001/P13-M001V valide Fusion `quick_asset_box` comme premier input asset-first depuis la commande Fusion classique, avec champ texte assets persiste, config temporaire, reuse du pipeline assets existant, reporting V0 honnete, outlines bas/haut du volume boite, generate/regenerate/clear sans doublon et preservation des objets non-BGIG; P13-ASSET-M002/P13-ASSET-M002V valide Fusion le sizing count-aware V0, `storage_sizing`, diagnostics `capacity_per_stack`/`pile_count`/`declared_capacity`, sketch debug asset-fit non imprimable, regenerate count-aware et clear final; P13-ASSET-M003/P13-ASSET-M003V valide Fusion une cavite asset-fit globale dans le flux `quick_asset_box`; P13-ASSET-M004/P13-ASSET-M004V valide Fusion des compartiments asset-specific V0, reporting associe, debug outlines, generate/regenerate/clear; P13-ASSET-M005/P13-ASSET-M005V valide les compteurs et diagnostics `asset_access_*`, generate/regenerate/clear; dette UX `quick_asset_box` documentee; limites non validees : assets individuels, cavites par pile/logements detailles, capacite physique garantie, solveur global, optimisation avancee, UI avancee et impression; print-validated: false |
| C-FUSION-CAVITIES | Fusion cavities | CAD generation pipeline | `fusion-validated` | M5 CAD cavities | Cavites rectangulaires CAD IR validees Fusion; P13-ASSET-M003/P13-ASSET-M003V valide Fusion une cavite asset-fit globale V0; P13-ASSET-M004/P13-ASSET-M004V valide Fusion plusieurs cavites top-open par asset source via `per_source_asset_rectangular_compartments_v0`; print-validated: false |
| C-FILLETS | Fillets and finger notches | CAD generation pipeline | `fusion-validated` | M5 CAD ergonomic features | Encoche rectangulaire top-open P6 validee Fusion, print-validated: false ; P13-ASSET-M005/P13-ASSET-M005V valide cette coupe pour les access notches asset-first ; courbes/fillets bloques |
| C-SOLVER | Solver and scoring | Volumetric layout | `implemented-core` | M10 Semi-automatic solver | Variant comparison P10-M002 report-only; raisons de rejet structurees P10-M003; module_candidates P10-M004; variante recommandee P10-M005; grouping borne P10-M006; plan concret greedy P10-M008; P13-M001 reutilise ce pipeline sans backtracking ni optimisation globale; P13-ASSET-M002/P13-ASSET-M002V valide une heuristique count-aware bornee pour piles/footprint/refus explicite sans solveur global; P64 remplace le chemin produit par un portefeuille XY/Z borne, Auto/Cible/Fixe, score pondere et residuels explicites ; gate architecture si optimiseur majeur |
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
- C-FUSION-UI : inchangee ; Fusion reste adaptateur futur et ne recalcule pas le plan.
## P19-M005 capability update

- C-PRODUCT-VISION : `implemented-cad-ir` pour BoxFillPlan V0, valide et transporte en metadata CAD IR sans Fusion comme source de verite.
- C-GRID-3D / C-LAYERS / C-RESERVATION : P19 valide l'occupation volumetrique manuelle et les collisions dans le moteur pur; le placement automatique reste non implemente.
- C-SOLVER : prochaine etape recommandee `box_fill_v1_greedy_2d`, bloquee par gate produit; aucun solveur global n'est autorise.
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
## P21 variant portfolio update

- C-SOLVER : `implemented-core` pour un portefeuille borne P21 de policies deterministes, deduplication geometrique, front Pareto, sous-scores et recommandation explicable sans recherche globale.
- C-PRODUCT-VISION : `implemented-cad-ir-metadata` pour la selection explicite d'une variante ; la CAD IR transporte la selection et ne recalcule pas le layout.
- C-FUSION-UI : inchange. Le dashboard P21 est un artefact HTML statique hors Fusion, pas une palette ni une app persistante.
## P22 UX surface gate update

- C-FUSION-UI : aucun changement executable. La commande Fusion reste `fusion-validated` pour smoke/export ; une palette persistante reste bloquee.
- C-PRODUCT-VISION : trajectoire recommandee documentee vers une app locale de conception + adaptateur Fusion, sans validation d architecture executable.
## P23 local composer update

- C-PRODUCT-VISION : `implemented-local-ui` pour un parcours local versionne `bgig.local_composer.v0`, de la boite a la selection explicite, sans seconde logique de placement.
- C-ASSET : les assets, dimensions et intentions sont editables localement et convertis vers les contrats moteurs ; l edition multi-assets par module reste P24.
- C-SOLVER : P20/P21 sont appeles par l adaptateur Python ; l UI ne duplique ni solveur ni score.
- C-CAD-IR : `implemented-cad-ir-metadata` pour l export d une selection P21 explicite ; aucune materialisation n est autorisee.
- C-FUSION-UI : inchangee. Fusion reste l adaptateur futur et la commande actuelle conserve son role de smoke/export.
- C-QUALITY : contrat HTTP loopback, validation stricte du draft, CORS borne et build frontend couverts ; inspection visuelle navigateur a rejouer lorsque le runtime local est disponible.
## P24 project quality update

- C-PRODUCT-VISION : `implemented-local-ui` pour une edition qui explique les erreurs avant generation, sans seconde logique de planification.
- C-ASSET : `implemented-local-ui` pour plusieurs assets explicitement associes a un module ; doublons et assets inconnus sont signales avant moteur.
- C-QUALITY : `implemented-validation` pour import structurel, prevalidation pure TypeScript, build frontend et regression moteur multi-assets.
- C-SOLVER / C-CAD-IR / C-FUSION-UI : inchanges ; P24 ne modifie ni placement, ni projection CAD, ni Fusion.

## P25 guided starters update

- C-PRODUCT-VISION : `implemented-local-ui` pour trois points de depart explicites et remplaçables, sans imposer un JSON brut au premier usage.
- C-ASSET : les templates expliquent des cas cartes, jetons, des et reservation plateau avec des dimensions ajustables.
- C-QUALITY : catalogue borne, drafts V0 resolus par P21 et route loopback CORS couverts par tests et recette HTTP.
- C-SOLVER / C-CAD-IR / C-FUSION-UI : inchanges ; les templates sont des entrees du moteur existant, pas une nouvelle logique de decision.

## P26 generation readiness update

- C-PRODUCT-VISION : `implemented-local-ui` pour une lecture novice de ce qui est pret avant toute proposition.
- C-QUALITY : `implemented-validation` pour un resume derive des erreurs et allocations existantes, avec verification comportementale TypeScript.
- C-SOLVER / C-CAD-IR / C-FUSION-UI : inchanges ; P26 ne modifie aucune policy, score, projection ou operation CAD.

## P27 proposal explanations update

- C-PRODUCT-VISION : `implemented-local-ui` pour une comparaison novice des compromis P21 sans masquer la trace technique.
- C-SOLVER : presentation plus lisible des policies et sous-scores existants ; aucun changement de score, ordre ou recommendation.
- C-QUALITY : textes explicatifs bornes et fallback verifies par test TypeScript.
- C-FUSION-UI / C-CAD-IR : inchanges ; P28 reste une gate humaine avant toute materialisation Fusion de selection.

## P28 local composer selection bridge update

- C-CAD-IR : `implemented-selection-bridge` pour la projection explicite d une selection P21 en composants CAD IR standards, avec trace de variante et sans nouvelle geometrie metier.
- C-FUSION-UI : `technical-path-observed`, `product-ux-rejected` : le pipeline add-in consomme les blanks P28, mais le dialogue et le resultat ne sont pas acceptables comme experience produit ; P31/P32 les remplacent.
- C-PRODUCT-VISION : le Studio conserve une selection explicite et le moteur Python reste source de verite ; aucun calcul ne migre vers Fusion.
- C-QUALITY : tests de contrat local/CLI et dry run de preparation Fusion couvrent le raccord hors Fusion.
- C-PRINT / C-ERGONOMICS : inchanges, `print-validated: false` ; les envelopes P28 ne sont pas des bacs finis.
## P29 premium product recovery update

- C-PRODUCT-VISION : orientation historique Studio, remplacee pour le MVP par ADR-0055 et l add-in Fusion comme surface unique.
- C-FUSION-UI : la commande CommandInputs reste `fusion-validated` comme outil expert/smoke, mais elle est retiree de la cible UX produit ; la palette P32 est prevue sous gate Fusion.
- C-CAD-IR : P28 reste `implemented-selection-bridge` uniquement ; il ne prouve pas une projection de bac fonctionnel.
- C-AESTHETIC / C-STACKING : formes, labels et mecanismes sont inclus dans le plan mais restent `planned` / `experimental` jusqu aux gates P33-P35.
## P30 living Studio update

- C-PRODUCT-VISION : `implemented-local-ui` pour un parcours principal en cinq etapes, une boite visuelle centrale et un langage sans jargon dans le flux novice.
- C-QUALITY : build TypeScript/Vite, test de contrat frontend et services locaux HTTP OK ; `browser-inspection-pending` car le sandbox Windows bloque la connexion de recette avant ouverture.
- C-CAD-IR / C-FUSION-UI : le telechargement P28 demeure cache dans le mode expert et explicitement non productif ; aucune nouvelle scene Fusion, cavite ou promesse de bac n est ajoutee.
- C-PRINT / C-ERGONOMICS : `print-validated: false` ; l interface expose le chemin de fabrication mais ne valide aucune etape physique.
## P31 functional tray gate update

- C-CAD-IR / C-CAVITY : strategie proposee `open_top_tray_from_selected_module.v0`, non implementee ; elle reutilise le corps rectangulaire et la cavite top-open existants.
- C-FUSION-UI : aucune mutation P31 avant validation ; le smoke humain de cavite P21 restera requis apres code.
- C-PRODUCT-VISION : le prochain resultat cible est un bac ouvert vrai, jamais un blank P28 promu comme produit.
- C-PRINT : `print-validated: false` maintenu.
## P31 open-top tray update

- C-CAD-IR / C-CAVITY : `implemented-cad-ir-open-top-trays` pour une cavite `free` top-open par module P21, avec parois/fond existants, metadata de tracabilite et refus structure des envelopes impossibles.
- C-FUSION-UI : `fusion-smoke-required` ; le plan Fusion hors API contient une coupe par bac mais aucune scene P31 n est encore observee.
- C-PRODUCT-VISION : le Studio et la CLI nomment des bacs ouverts a verifier dans Fusion, sans promesse asset-specific ni imprimable.
- C-PRINT / C-ERGONOMICS : `print-validated: false` maintenu.
## P31 Fusion smoke validation

- C-FUSION-UI / C-CAVITY : `fusion-validated` pour les trois bacs ouverts P31 du smoke `mixed-box` observes par Thomas le 2026-07-11.
- C-PRINT / C-ERGONOMICS : inchanges, `print-validated: false` ; le smoke ne couvre ni fit asset-specific ni impression.
## P32 Fusion palette update

- C-FUSION-UI : `implemented-fusion-palette`, `fusion-smoke-required` pour une palette HTML locale en francais, avec resume design/scene/fabrication, bridge `incomingFromHTML` et actions de preview, mise a jour et export.
- C-PRODUCT-VISION : Studio reste la source du parcours ; la palette ne modifie ni projet, ni solveur, ni tolerances et replie le dialogue CommandInputs en mode expert.
- C-QUALITY : tests de contrat du bridge et statut fabrication honnete (`impression non validee`) passent hors Fusion.
- C-PRINT : inchange, `print-validated: false` ; P32 ne remplace pas une impression mesuree.

## P32 Fusion palette smoke validation

- C-FUSION-UI : `fusion-validated` pour la palette `Atelier de rangement`, sa lecture de scene et son bridge vers les actions existantes de mise a jour/export, selon retour humain `P32 Fusion OK` du 2026-07-11.
- C-PRODUCT-VISION : la palette est acceptee comme surface secondaire ; le Studio reste la surface de conception et la commande technique reste repliee en expert.
- C-PRINT : inchange, `print-validated: false` ; P32 ne valide ni fit physique, ni impression.

## P33 form and appearance update

- C-AESTHETIC : `implemented-studio-preview` pour `bgig.appearance.v0`, themes, labels et intentions de forme sauvegardes et visibles dans le Studio ; aucune finition physique ou Fusion n est declaree.
- C-PRODUCT-VISION : l apercu est non destructif : le plan P21, dimensions, placement et tolerances restent inchanges et les anciens projets recoivent le style par defaut.
- C-CAD-IR : la preference est transportee comme metadata `stored_for_preview_only_not_materialized`, sans operation CAD nouvelle.
- C-QUALITY : bornes et enums valides, digest P21 invariant, build Studio OK ; `browser-inspection-pending` dans le sandbox Windows.
- C-PRINT : inchange, `print-validated: false`.

## P34 sliding lid coupon

- C-STACKING / futur mecanisme : implemented-cad-ir-coupon pour un seul coupon coulissant a deux pieces, hors boite.
- C-CAD-IR : le capot porte deux operations join_rectangular_prism, bornees au body local.
- C-FUSION-UI : implemented-fusion-adapter, fusion-smoke-required ; le rapport annonce les rails jointes.
- C-PRODUCT-VISION : le Studio sauvegarde le choix sans modifier solveur, digest ou selection.
- C-CALIBRATION : un coupon imprime et mesure reste obligatoire avant toute qualification physique.
- C-AESTHETIC : aucun style ou finition Fusion supplementaire n est declare.

## P37 project V1 update

- C-PRODUCT-VISION : `implemented-core` pour le contrat utilisateur
  `bgig.project.v1`, distinct des candidats/layers moteur et migrable depuis P23.
- C-ASSET : `implemented-core` pour les lignes forme/quantite/bac cible ; les
  logements et tailles de bacs restent P39.
- C-RESERVATION : `implemented-core` pour les plateaux/livrets quantifies comme
  elements plats ; la pile superieure reste P40.
- C-QUALITY : validation stricte, migration non destructive, API loopback et cas
  72 pieces / 50 bacs / 25 elements plats testes.
- C-AESTHETIC et mecanismes : options conservees mais `deferred` jusqu'aux
  releases correspondantes.

## P38 user-first Studio update

- C-PRODUCT-VISION : `implemented-local-ui` pour la saisie lisible de la boite,
  des pieces, des bacs cibles, des plateaux/livrets et des remplissages.
- C-ASSET et C-RESERVATION : les donnees V1 sont editees et pre-validees dans le
  Studio ; les logements et la pile superieure restent respectivement P39 et P40.
- C-QUALITY : validation client, build Vite et routes locales V1 verifies ;
  aucune validation Fusion ou impression n est declaree.
- C-AESTHETIC et mecanismes : absents du parcours V0.1 et toujours `deferred`.

## P39 derived container plan update

- C-PRODUCT-VISION : `implemented-local-ui` pour un bouton Construire qui montre
  des dimensions de bacs et des blocages compréhensibles.
- C-ASSET : `implemented-core` pour les sept formes de saisie, les piles
  comptees et les logements derives par famille de pieces.
- C-MODULE : `implemented-core` pour les dimensions internes/externes minimales,
  parois, fond et cloisons internes de chaque bac derive.
- C-QUALITY : tests unitaires de formes, cartes, cardinalite elevee, blocages,
  API loopback et build Studio ; aucune validation Fusion ou impression.
- C-RESERVATION et C-SOLVER : toujours P40 et P41 ; P39 ne place aucun bac et
  n applique pas le jeu entre bacs.

## P40 upper flat-stack update

- C-RESERVATION : `implemented-core` pour la pile superieure, son ordre,
  empreinte, hauteur et reservation non imprimable.
- C-MODULE : les bacs P39 sont recalcules sous la hauteur restante.
- C-ACCESS : l ordre de pile est explicite ; le support physique reste P41.
- C-QUALITY : piles vides/heterogenes, debordements, support, API loopback et
  build Studio sont verifies ; aucune validation Fusion ou impression.
- C-SOLVER : P41 reste responsable du placement X/Y/Z, du support continu et du
  volume restant.

## P41 global closure update

- C-SOLVER : implemented-core pour placement X/Y/Z, collisions et conservation de volume.
- C-RESERVATION : pile superieure placee comme reservation non imprimable.
- C-QUALITY : 50 bacs, 72 familles, 25 plats, remplissages exacts et API testes.
- C-FUSION : reste P42.
## P42 functional CAD update

- C-CAD-IR / C-CAVITY : `implemented-cad-ir` pour les bacs V0.1 ouverts, un
  logement top-open par famille, les remplissages demandes et les supports
  conservant parois et fond minimaux.
- C-FUSION-UI : `fusion-smoke-required` ; la scene est lue par l adaptateur hors
  API mais aucune execution Fusion P42 n est encore observee.
- C-PRODUCT-VISION : le Studio construit une geometrie fonctionnelle et explique
  les blocages ou jeux techniques sans exposer le jargon CAD dans le parcours.
- C-AESTHETIC / C-STACKING : restent `deferred` jusqu aux gates P60 puis P46.
- C-PRINT : `print-validated: false` maintenu.

## P43 historical Fusion update

- C-FUSION-UI / C-CAD-IR / C-CAVITY : `fusion-validated-geometry-only` pour la
  scene fonctionnelle du jeu temoin observee le 2026-07-12 (`Fusion P43 OK`).
- C-PRODUCT-VISION : aucune acceptance MVP n est deduite de ce smoke ; le Studio
  reste la surface principale et sa conformite runtime/visuelle reste a prouver.
- C-SOLVER / C-QUALITY : le nombre de composants du jeu temoin ne qualifie pas
  leur utilite ; la planification des residus est reprise en P56.
- C-PRINT : `print-validated: false` maintenu.
## Correction P43 - conformite produit reouverte

- C-FUSION-UI : `fusion-validated-geometry-only` pour le jeu temoin P43 ; la
  palette observee bloquee sur `Chargement...` est `product-ux-rejected`.
- C-PRODUCT-VISION : le Studio reste la surface principale par ADR-0042, mais
  son ergonomie runtime/visuelle n est pas encore validee.
- C-SOLVER / C-QUALITY : conservation de volume et absence de collision sont
  `implemented-core`; une liste de residus de grille n est pas une qualite de
  rangement acceptee. P56 doit apporter utilite et justification.
- C-PRINT : `print-validated: false` maintenu.

## P53 fixed-cavity expandable-envelope update

- C-PRODUCT-VISION : `accepted-product-semantics` pour l editeur premium complet
  et le remplissage par expansion des bacs demandes.
- C-CAVITY : les enveloppes calibrees P39 restent `implemented-core` comme bornes
  utiles a preserver.
- C-MODULE / C-SOLVER : `redesign-required` pour distinguer enveloppe minimale et
  finale, puis partitionner le volume sans corps automatique.
- C-RESERVATION : la pile superieure P40 reste `implemented-core`.
- C-CAD-IR / C-FUSION-UI : l ancien chemin de remplissages automatiques est
  `superseded-for-product`; P59 materialisera seulement le plan final.
- C-AESTHETIC / C-STACKING : toujours `deferred` jusqu a P60.
- C-PRINT : `print-validated: false` maintenu.

## P54 premium editor UX reference update

- C-PRODUCT-VISION : `implemented-reference` pour le parcours complet de l
  editeur premium, du projet vide au resultat.
- C-QUALITY : test de contrat sur couverture, invariant zero corps automatique,
  responsive et encodage ; inspection visuelle runtime encore manquante.
- C-FUSION-UI : role de passerelle secondaire confirme, aucune implementation
  Fusion modifiee.
- C-ASSET / C-RESERVATION / C-MODULE : composants et champs UX specifies ; le
  contrat executable reste P55.

## P55 executable expandable-envelope update

- C-ASSET / C-CAVITY : implemented-core pour les sept formes V0.1, leurs jeux,
  quantites et cavites calibrees conservees dans un repere local stable.
- C-MODULE : implemented-core pour la distinction minimum_outer_envelope /
  final_outer_envelope, les axes extensibles, verrous et preferences de surplus.
- C-QUALITY : invariant cavity_layout immuable pendant l expansion, zero corps
  automatique, erreurs actionnables, migration additive et API testes.
- C-SOLVER / C-RESERVATION : P57 reste responsable de la partition globale,
  des jeux entre bacs, alignements et support de pile.
- C-CAD-IR / C-FUSION-UI : inchanges ; aucune validation Fusion ou impression
  n est revendiquee.
## P54-R Fusion-only alignment update

- C-PRODUCT-VISION : `accepted-product-direction` pour add-in Fusion unique.
- C-FUSION-UI : la palette P32 devient la surface principale a etendre en P56.
- C-ASSET / C-RESERVATION / C-MODULE : restent dans le coeur pur et seront editables par bridge depuis la palette.
- C-QUALITY : nouveaux contrats interdisent localhost, Vite, navigateur externe et logique metier JavaScript dans le runtime MVP.
- C-CAD-IR : frontiere inchangee ; la scene Fusion reste une projection.
- Prototype web P23-P30 : `superseded-for-mvp`, conserve historiquement.
## P56 embedded Fusion editor update

- C-FUSION-UI : `implemented`, palette principale a six vues, mode simple/avance et etats bornes ; smoke visuel prepare, `fusion-validated: false`.
- C-ASSET : `implemented-ui-bridge`, ajout, duplication, suppression, sept formes, quantite et bac cible sans cardinalite arbitraire.
- C-RESERVATION : `implemented-ui-bridge`, pile plate editee et resume P40 calcule par le coeur.
- C-MODULE : `implemented-ui-bridge`, groupes stables et contraintes P55 editables sans recalcul JavaScript.
- C-QUALITY : bridge JSON versionne, persistance atomique update-safe, import/export, timeout/retry et moteur pur package dans l add-in.
- C-SOLVER : P57 devient `ready`; aucun placement global n est revendique par P56.
## P57 partition solver update

- C-SOLVER : `implemented-core`, solveur borne de partitions en rangees, ordres et rotations avec score de simplicite et digest deterministe.
- C-MODULE : `implemented-core`, enveloppes finales conjointes revalidees par P55 ; cavites locales inchangees.
- C-RESERVATION : `implemented-core`, hauteur P40 respectee et faces superieures alignees comme supports demandes.
- C-QUALITY : `automatic_body_count = 0`, jeux non materialises, diagnostics actionnables, aucune optimalite globale revendiquee.
- C-FUSION-UI : `implemented-bridge`, action solve_project et synthese construit/impossible ; rendu geometrique complet reste P58.
- C-CAD-IR : inchange, P59 seul materialisera le plan.

## P58 real partition result update

- C-FUSION-UI : `implemented-result`, vue dessus, coupe X/Z, details corps/contenus, pile, supports, diagnostics et actions modifier/recalculer.
- C-SOLVER : plan P57 affiche par digest sans recalcul JavaScript ; impossible et obsolete sont des etats explicites.
- C-CAVITY / C-MODULE : projections derivees des repères P55 et placements P57, rotations 0/90 testees.
- C-QUALITY : `indicative_geometry: false`, zero corps automatique visible, aucune solution impossible dessinee.
- C-CAD-IR : P59 devient `ready`; materialisation reste desactivee dans la palette P58.
## P59 partition CAD and Fusion scene update

- C-CAD-IR : `implemented-core`, `partition_cad.py` derive une CAD IR
  deterministe du seul plan P57 courant et refuse toute partition obsolete.
- C-CAVITY / C-MODULE : `implemented-cad-ir`, enveloppes finales materialisees,
  cavites P55 top-open inchangees et complements uniquement explicites.
- C-FUSION-UI : `implemented-bridge`, actions palette materialize/regenerate/
  inspect/clear/export et etats synchronized/blocked/error.
- C-QUALITY : correspondance exacte plan/composants, mode compact_only, zero
  corps automatique, preservation non-BGIG et reponse versionnee sans timeout.
- Validation : preuves automatisees vertes ; `fusion-validated: false` jusqu a
  l observation P60.
## P60 bootstrap and Utilities launcher update

- C-FUSION-UI : `implemented-bootstrap`, handshake readiness avant chargement
  projet, retry borne et aucun bouton projet silencieux.
- C-FUSION-UI : `implemented-toolbar-launcher`, bouton Utilities promu ouvrant
  uniquement la palette produit avec icone maison SVG.
- C-QUALITY : ancien dialogue retire du parcours normal, ressources packagees
  et tests de course de demarrage.
- Validation : `fusion-retest-required` ; aucune acceptation P60 ni impression
  n est encore revendiquee.

## P60 UX creation and sizing update

- C-FUSION-UI : package 0.1.9 avec palette 1280 x 1100, presets de creation
  fournis par le coeur, corps pleins explicites et dimensions finales par bac en
  mode simple.
- C-SOLVER / C-CAVITY : aucun solveur JavaScript ajoute ; les presets et
  dimensions passent par les contrats Python P55/P57 existants.
- C-STACKING : P61 planifie apres acceptation P60 ; aucune promesse
  d empilement vertical dans le runtime courant.
- Validation : preuves automatisees vertes ; observation Fusion partielle du
  runtime 0.1.8, retest 0.1.9 requis, print-validated: false.

## Rebase de capability apres revue P60

La preuve P60 conserve `C-FUSION-UI` comme base technique utilisable, mais pas
comme experience acceptee. Les blockers V0.1 actifs deviennent :

| Blocker V0.1 revise | Etat reel | Prochaine preuve |
| --- | --- | --- |
| Etat source/derive/solve/materialise | implemente et teste dans la palette 0.1.10 | observation P66 |
| Diagnostics discrets et parcours progressif | socle P61 implemente ; finition P65 | P65 |
| Catalogue et orientations de rangement | implemente et teste par P62 | observation P66 |
| Reservations superieures localisees | implementees et testees par P63 ; P40 superseded | observation P66 |
| Placement multi-etages Z | P64 implemente et teste dans le coeur, CAD IR et palette | observation Fusion P66 |
| Surplus pondere et Auto/Cible/Fixe | P64 implemente et teste ; finition de lisibilite P65 | observation Fusion P66 |
| Conteneurs/reglages/apercu explicables | socle P56-P58 a reprendre | P65 |
| Parcours V0.1 accepte | non accepte | P66 |

`C-RESERVATION`, `C-STACKING`, `C-GRID-3D` et `C-SOLVER` redeviennent des
blockers de convergence. Les implementations P40/P57 restent historiques et
testees, mais sont `superseded-for-product` pour la semantique cible. Les formes
de cavite V0.2 restent differees apres P66.

## P61 reactive palette update

- C-FUSION-UI : `implemented-reactive-state`, parcours et barre d actions P61,
  densites Compact/Detaille et details locaux sans mode avance global.
- C-PROJECT : digest source Python, derives recalcules apres debounce, ancien
  plan conserve comme obsolete et scene materialisee distincte.
- C-QUALITY : inspect sain silencieux, rapport brut replie, codes moteur retires
  du premier niveau et plan obsolete non materialisable.
- Validation : tests automatises verts ; observation Fusion reportee a P66,
  `print-validated: false`.
- Prochaine capability : C-ASSET par P62, ADR-0058 acceptee.

## P62 capability update

- C-ASSET : `implemented-core` pour formats locaux, sleeves, epaisseur de paquet
  mesuree ou comptee et orientations de rangement resolues avant cavite.
- C-CAVITY : dimensions physiques et dimensions XYZ resolues sont distinctes ;
  la cavite consomme seulement l enveloppe resolue.
- C-FUSION-UI : `implemented`, `fusion-retest-required` pour edition compacte et
  detaillee, dimensions resolues visibles et presets personnels hors package.
- C-QUALITY : migration additive et 401 tests automatises ; aucune validation
  Fusion ou impression n est revendiquee.


## P63 capability update

- C-RESERVATION : `implemented-core` pour empreintes locales, composition Z des
  plats qui se chevauchent, ordre de retrait, appui et prise rectangulaire.
- C-STACKING : la pile globale P40 est `superseded-for-product`; les conteneurs
  gardent leur sommet de conception hors reservations.
- C-CAD-IR / C-FUSION-UI : operations de coupe superieure distinctes des cavites,
  vues de dessus/coupe et generation Fusion preparee dans le package 0.1.13.
- C-QUALITY : non-percement du corps et des fonds de cavite, determinisme et
  408 tests ; `fusion-retest-required`, `print-validated: false`.
- Prochaine capability : C-SOLVER/C-GRID-3D par P64, ADR-0059 acceptee.

## P64 capability update

- C-SOLVER / C-GRID-3D : `implemented-core` pour un portefeuille borne,
  deterministe et non optimal garanti d arrangements XY composes par etages Z.
- C-STACKING / C-ACCESS : supports par recouvrement, retrait top-down et
  reservations P63 localisees sur l etage effectivement traverse.
- C-CAD-IR / C-FUSION-UI : positions Z, etages, sous-scores, residuels et
  suggestions sont transportes ; une proposition partielle est visible mais
  bloquee avant Fusion.
- C-SOLVER / C-GRID-3D : repli hybride borne ou un corps haut traverse des
  intervalles Z a cote de piles courtes ; les plans historiques restent prioritaires.
- C-MODULE / C-CAD-IR : limites locales conscientes des rotations, profondeur
  utile compensee sous plateaux et noms techniques Fusion uniques.- C-QUALITY : 428 tests automatises, aucun corps automatique, `fusion-retest-required`,
  `print-validated: false`.
- Prochaine capability : C-FUSION-UI/C-MODULE/C-TOLERANCE par P65, ADR-0060 acceptee.


## P65-M001 - Jeux anisotropes et action Fusion persistante

- C-TOLERANCE : layout_clearance_mm reste le jeu X-Y ;
  container_z_clearance_mm reserve un vide vertical reel et herite du X-Y pour
  les projets historiques.
- C-SOLVER / C-GRID-3D : les compositions globales et les piles hybrides
  consomment le jeu Z entre corps, sans creer un faux etage ni un corps support.
- C-CAD-IR : le parametre Z et les origines separees sont transportes jusqu au
  plan Fusion.
- C-FUSION-UI : le reglage Z est editable et l unique action de materialisation
  est persistante, adjacente a Recalculer et gardee par l etat solve.
- C-QUALITY : couverture automatisee ciblee puis complete requise ;
  usion-retest-required, print-validated: false.

## P65-M002 - Frontieres de jeu explicites

- C-TOLERANCE : `container_box_xy_clearance_mm` est le jeu par cote de boite ;
  `layout_clearance_mm` et `container_z_clearance_mm` restent les jeux totaux
  entre conteneurs ; `box.lid_clearance_mm` demeure la marge haute.
- C-SOLVER / C-GRID-3D : perimetre X-Y, ecarts entre voisins et espaces Z sont
  valides separement, sans jeu sous les bacs ni support ajoute.
- C-CAD-IR : les quatre roles sont explicites jusqu au plan Fusion.
- C-FUSION-UI : palette 0.1.17 a quatre libelles uniques ; les contours de
  reference restent inspectables mais caches par defaut.
- C-QUALITY : 434 tests executes verts ; fusion-retest-required,
  print-validated: false.

## P65-M003 - Tailles et estimation des conteneurs

- C-FUSION-UI : implemented pour minimum, demande, taille calculee, statut,
  surplus et etage dans les cartes Conteneurs Compact/Detaille. Un unique CTA
  local Estimer les tailles reutilise solve_project.
- C-MODULE : projection additive par identifiant stable de groupe ; aucune
  formule de cavite ou geometrie ne change.
- C-SOLVER : la taille calculee, les motifs par axe et le statut complete/
  partiel/impossible sont transportes sans estimateur, score ou budget nouveau.
- C-QUALITY : projet et scene restent inchanges par estimation ; les etats
  perimes et les propositions partielles restent non materialisables.
- Package : palette 0.1.18 ; 440 tests automatises, syntaxe JS, compilation et
  dry-run Fusion verts ; fusion-retest-required, print-validated: false.
- Suite : P65-M004 implemente ; prochaine mission P66-M000 puis P66-M001 et gate humaine P66.

## P65-M004 - Explications et actions de l Apercu

- C-FUSION-UI : implemented pour une projection Python de presentation du score,
  des appuis, de l ordre de retrait, des residuels et suggestions ; export
  imprimable primaire et aucune duplication de Recalculer ou Materialiser.
- C-QUALITY : implemented pour les invariants de non-mutation, de score
  inchange, d absence de corps automatique et d absence de codes solveur dans
  le premier niveau de palette.
- Package : palette 0.1.19 ; 445 tests automatises, syntaxe JS et compilation
  verts ; fusion-retest-required, print-validated: false.
- Suite : P66-M000 de quarantaine, puis P66-M001 de preparation et gate humaine P66.

## P66 - Contrat de preuve et gate V0.1

- C-QUALITY / C-PRODUCT-VISION : contrat d execution delegable dans
  `docs/P66_TERRA_EXECUTION_CONTRACT.md`, sans nouvelle capability produit.
- C-FUSION-UI : P66-M000 est implemented : les actions et presets normaux de
  creation de complements sont absents, tandis que les projets historiques
  restent visibles, sauvegardables et regenerables.
- C-SOLVER / C-RESERVATION : aucun changement de solveur, tolerance, geometrie
  ou semantique future ; les complements explicites historiques restent sans
  creation automatique.
- Validation : P66-M000 et P66-M001 `done`, puis P66-V accepte humainement
  le 2026-07-14 (package 0.1.20, commit `6e351bb`) ; `mvp-accepted`,
  `fusion-validated`, `print-validated: false`.
- Releases : P44-M001 est `ready` apres P67-V ; les autres missions P44 et
  P45/P46 suivent leurs dependances. P47-P50 restent bloques jusqu a P46 et
  P69 jusqu a P50.

## P67-P69 - Pilotage humain et apprentissage post-MVP

- P67 n implemente aucune capability : P67-M000 capture la revue et P67-V
  accepte ADR-0062 ainsi que D67-01 a D67-11.
- C-FUSION-UI : aucune promotion runtime. La fondation P44 est `designed` et
  P44-M001 est la seule mission `ready`.
- C-PROJECT : la persistance atomique du slot courant est implementee ; Nouveau,
  Ouvrir, Enregistrer sous, recents et recuperation sont acceptes mais planifies.
- C-ASSET / C-MODULE : la composition Conteneur parent -> Elements enfants est
  acceptee comme projection UI sur les identifiants existants, sans schema recursif.
- C-TOLERANCE : jeux herites puis surchargeables X/Y/Z acceptes comme besoin ;
  roles, formules, defaults et migration restent a cadrer par P44-M008.
- C-SOLVER : le calcul hybride adaptatif est accepte pour experimentation ; les
  poids, budgets et heuristiques restent inchanges et la scene reste explicite.
- C-RESERVATION : modes plateau dessous ou fermeture restent futurs ; le top
  inset actuel ne change pas pendant P67.
- P68 augmente la preuve locale d usage et d impression sans promouvoir une
  capability globale ni modifier les tolerances par defaut.
- P69 audite exhaustivement C-FUSION-UI apres P50 et produit le cadrage P70+ ;
  elle evalue la fondation P44 sur le produit enrichi et ne corrige rien pendant
  la revue.

## P66-M001 - Preparation de gate V0.1

- C-QUALITY : `gate-prepared` pour les fixtures deterministes complete et
  impossible, leurs digests, les preuves de non-materialisation et le cas de 50
  conteneurs conserve hors gate humaine.
- C-FUSION-UI : `gate-prepared` pour le package 0.1.20 installe par le
  preparateur unique, son runtime palette et ses marqueurs verifies ; les
  complements historiques restent compatibles sans creation nouvelle.
- C-SOLVER / C-RESERVATION : `implemented-cad-ir`, aucune formule, tolerance,
  geometrie ni semantique produit n est modifiee par P66-M001.
- Gate : P66-V est acceptee humainement ; le MVP est `mvp-accepted`, `fusion-validated`, `print-validated: false`.

## P66-CLOSE - Acceptance Fusion V0.1

- C-PRODUCT-VISION / C-QUALITY / C-FUSION-UI : `mvp-accepted`,
  `fusion-validated` pour le parcours Fusion-only observe par Thomas le
  2026-07-14, package 0.1.20, commit `6e351bb`.
- C-SOLVER / C-RESERVATION : les preuves automatees et la gate humaine
  confirment le comportement V0.1 sans requalifier les tolerances ou la
  geometrie physique.
- Limite : `print-validated: false` ; aucune capability V0.2/V0.3 n est
  promue. P67 est `in-review`, P67-V est la prochaine gate, P68 reste `planned-after-p66`, P44 reste bloque.

## P67-V capability update

- C-PRODUCT-VISION : `accepted-priority` pour l option C ; P44 porte la
  fondation UX, P45 les geometries et P46 la gate V0.2.
- C-FUSION-UI : `designed`, avec P44-M001 seule mission `ready` pour stabiliser
  focus, details et scroll ; aucune promotion runtime par la gate documentaire.
- C-PROJECT : cycle document nomme et recuperation acceptes pour P44, encore
  non implementes.
- C-ASSET / C-RESERVATION / C-MODULE : motif UX commun `Herite du projet` puis
  override X/Y/Z accepte, mais roles physiques distincts.
- C-TOLERANCE : `accepted-product-intent`, pas `designed` pour les jeux par
  objet. P44-M008 doit fixer formules, defaults, sources et migration avant
  P44-M009 ; aucune valeur actuelle ne change.
- C-FUSION-UI / C-MODULE : mode global discret, mode unique par conteneur,
  `Personnalise` legacy, solidite visible et calculs secondaires replies sont
  planifies dans P44-M002/P44-M004.
- C-SOLVER / C-CAD-IR : inchanges ; calcul adaptatif accepte en surface, scene
  toujours explicite et aucune formule JavaScript.
- C-QUALITY : P67-V est une preuve humaine de priorite, pas une preuve
  d implementation, de tolerance physique ou d impression.
- Prochaine preuve : tests puis observation Fusion de P44-M001.
- `print-validated: false`.

## P44-M001 - Stabilite UI implementee

- C-FUSION-UI : `implemented`, `automated-validated`, `fusion-retest-required`
  pour la palette 0.1.21. Les cartes et controles recoivent des identifiants UI
  derives des identifiants metier ; focus, caret, details, carte active et scroll
  sont restaures apres un rendu pertinent.
- C-PROJECT / C-QUALITY : une revision source accompagne les requetes derivees.
  Les validations et calculs obsoletes sont ignores, sans nouvelle logique metier
  JavaScript, mutation de projet, appel de scene Fusion ou changement de
  serialisation.
- Preuves : 453 tests, DOM/bridge incluant cinquante conteneurs, syntaxe
  JavaScript, exemple CLI, `compileall`, controle `adsk` et diff-check passes ;
  observation Fusion encore requise. `print-validated: false`.
- Suite : P44-M002 seulement apres integration P44-M001 dans `main`.

## P44-M002 - Cartes compactes accessibles

- C-FUSION-UI : `implemented`, `automated-validated`,
  `fusion-retest-required` pour la palette 0.1.22 : le mode Compact conserve
  les champs de cartes, les grilles s adaptent aux contenus et les actions de
  cartes gardent une cible de 40 px minimum.
- C-FUSION-UI : `implemented` pour la divulgation progressive des conteneurs :
  `Solidite` et ses deux minima restent visibles ; `Details calcules` replie
  taille, etage, appui, surplus et raisons par axe sans mutation.
- C-QUALITY : tests DOM explicites ; aucune logique metier JavaScript, mutation
  de schema, calcul, tolerance, geometrie, CAD IR ou scene Fusion automatique.
- Preuves : 454 tests, syntaxe JavaScript, exemple CLI, `compileall`, controle
  `adsk` et diff-check passes ; observation Fusion encore requise.
  `print-validated: false`.
- Suite : P44-M003 seulement apres integration P44-M002 dans `main`.

## P44-M002V2 - Densite technique corrective

- C-FUSION-UI : `implemented`, `automated-validated`,
  `fusion-validation-required` pour la palette 0.1.23.
- Le KO humain 0.1.22 est conserve comme preuve que la seule presence de grilles
  responsives ne suffit pas a qualifier la compacite.
- L hybride A+B combine bandes semantiques et grille technique dense, avec
  nombres bornes, cibles de 40 px, sections essentielles visibles et calculs
  secondaires replies.
- C-QUALITY : contrats DOM aux seuils 760/560 px, syntaxe JavaScript, suite
  complete (455 tests), exemple CLI, compileall, frontiere `adsk` et
  diff-check passes.
- Aucun changement de schema, calcul, tolerance, geometrie ou scene Fusion.
- Suite : P44-M003 reste `blocked-by-p44-m002v` jusqu a validation humaine du
  package 0.1.23. `print-validated: false`.

## P44-M002V - Densité validée et qualité linguistique

- C-FUSION-UI : `fusion-validated` pour la densité hybride A+B du package
  0.1.23, preuve humaine `P44-M002V Fusion OK 0.1.23 - commit 2f78a99`.
- C-FUSION-UI : P44-M003 devient `ready-after-p44-m002v`.
- C-QUALITY : exigence `accepted-product-requirement` pour le français
  correctement accentué dans les textes utilisateur.
- Application incrémentale dès P44-M003 ; audit exhaustif dans P44-M006.
- Identifiants techniques ASCII, contenu humain UTF-8 sans BOM ni mojibake.
- Cette gate ne change ni schéma, solveur, tolérance, géométrie ou statut
  d’impression. `print-validated: false`.


## P44-M003 - Navigation et interversion X/Y

- C-FUSION-UI : `implemented`, `automated-validated`,
  `human-fusion-gate-required` pour quatre onglets primaires, sections
  Boîte/plateaux/livrets et Conteneurs/éléments regroupées, sans composition
  parent/enfant encore.
- C-QUALITY : interversions locales testées ; boîte, élément, plateau/livret
  et contrat X/Y complet de conteneur. Origines, Z, bridge, solveur et scène
  restent inchangés.
- Compatibilité : `rotation_deg_z` historique est préservé ; aucun schéma ou
  migration n’est introduit.
- Prochaine preuve : P44-M003V dans Fusion pour le package 0.1.24 ;
  `print-validated: false`.


## P44-M003V et P44-M004 capability update

- C-FUSION-UI : P44-M003 est fusion-validated pour les quatre onglets et
  l’interversion X/Y ; P44-M004 est implemented, automated-validated, en
  attente de P44-M004V pour sa projection parent/enfant et ses modes de taille.
- C-MODULE : la relation conteneur/contenu est projetée depuis les identifiants
  existants, sans schéma récursif, migration, solveur ou géométrie nouvelle.
- C-QUALITY : identifiants DOM stables sous cartes enfants, compatibilité
  historique par axe, absence de bridge additionnel et package 0.1.25 testés.
- print-validated: false ; aucune capability physique ou géométrique n’est
  promue.

## P44-M004V2 — densité structurelle hybride C

- C-FUSION-UI : la surface embarquée utilise la largeur Fusion, une barre unique
  et des rangées techniques parent/enfants responsives.
- C-QUALITY : le contrat DOM impose une seule commande de densité, des cibles de
  40 px, trois seuils de repli et la conservation des identifiants métier.
- C-MODULE : la projection reste fondée sur container_group_id, sans arbre
  récursif ni migration.
- C-SOLVER / C-TOLERANCE / C-CAD-IR : inchangées.
- Statut : implemented, automated-validated, human-fusion-gate-required,
  fusion-validated: false, print-validated: false.

## P44-M004V2 — gate UX Fusion acceptée

- C-FUSION-UI : fusion-validated pour la densité hybride C, la comparaison
  conteneur / éléments, les contrôles Créer et Plateaux et livrets collants et
  les notifications temporisées du package 0.1.27 ; preuve "P44-M004V2 Fusion OK 0.1.27 - commit 80c1a6c".
- C-MODULE : la projection continue de s’appuyer sur container_group_id, sans
  arbre récursif ni migration ; aucune nouvelle capability de modèle n’est
  promue.
- C-SOLVER / C-TOLERANCE / C-CAD-IR : inchangées et non qualifiées par cette
  gate UX.
- print-validated: false. P44-M005 devient ready-for-explicit-go.

## P44-M005 — création et presets explicites

- C-FUSION-UI : implemented, automated-validation-required pour une création
  compacte preset + destination + Ajouter, avec raccourci local dans un
  conteneur et sans calcul automatique.
- C-ASSET : les starters existants et les presets personnels restent des
  brouillons éditables ; aucun nouveau format, type ou champ métier.
- C-MODULE : la destination réutilise exclusivement container_group_id ; aucun
  conteneur imbriqué ni complément.
- C-QUALITY : DOM, bridge existant, roundtrip et gate Fusion dédiés.
- print-validated: false.

## P44-M005 acceptée — gate Fusion 0.1.28

Preuve humaine : "P44-M005 Fusion OK 0.1.28 - commit b8cf884".

Statut : done-human-gate, fusion-validated pour le parcours UX P44-M005 ;
print-validated: false.

La validation couvre la barre de création persistante, le preset et la
destination explicite (nouveau conteneur lié ou existant), les presets
personnels, le raccourci local "+", leur suppression locale et l'absence de
complément, calcul ou scène Fusion automatique. Elle ne qualifie ni schéma,
bridge, solveur, tolérance, géométrie, CAD IR ou impression.

P44-M006 devient ready-for-explicit-go et ne commence pas sans GO explicite.


## P44-M006 capability update

- C-FUSION-UI : fusion-validated pour le cycle de document nommé, la
  récupération locale, les réglages lisibles et le diagnostic replié.
- C-QUALITY : audit UTF-8, anti-mojibake, tests DOM et roundtrip de nom accentué
  validés dans le package 0.1.30.
- C-SOLVER, C-TOLERANCE, C-GEOMETRY et C-CAD-IR : inchangés.
- Validation : P44-M006 Fusion OK 0.1.30 - commit d82def6 ;
  print-validated: false.

## P44-M008 - Contrat propose de tolerance par objet - 2026-07-15

- C-TOLERANCE : proposed-human-gate-open, pas encore designed.
- C-ASSET / C-RESERVATION / C-MODULE : roles et sources documentes, runtime inchange.
- C-QUALITY : matrice de non-regression definie pour P44-M009.
- C-SOLVER / C-CAD-IR / C-FUSION-UI : inchanges. print-validated: false.

## P44-M009 - Capability update (2026-07-16)

- C-TOLERANCE : implemented et automated-validated pour roles, heritage X/Y/Z,
  zero explicite, provenance et vecteurs conteneur ; aucune recalibration.
- C-ASSET / C-RESERVATION / C-MODULE : cavity et top inset consomment les
  vecteurs effectifs ; projets historiques compatibles.
- C-SOLVER / C-CAD-IR : voisinage et perimetre sont par conteneur, les paires
  utilisent max et la CAD IR expose la provenance.
- C-FUSION-UI / C-QUALITY : palette, DOM, roundtrip, bridge et materialisation
  historique testes. fusion-validated: false, print-validated: false.
- Suite : P44-M007 est ready-for-explicit-go ; P44-V reste une gate humaine.

## P44-M009H01 - Capability update (2026-07-16)

- C-FUSION-UI : présentation des volets et saisie X/Y observée le 2026-07-16,
  mais validation fonctionnelle révoquée après anomalie sur 0.1.32.
- C-TOLERANCE : inchangée côté moteur ; les vecteurs et provenances X/Y/Z
  restent compatibles et les projets anisotropes ne sont pas migrés.
- C-QUALITY : 473 tests, transport Qt, syntaxe JavaScript, compileall,
  frontière adsk et diff-check passés ; observation Fusion 0.1.32 acceptée.
- Suite : état remplacé par P44-M009H02 ; P44-M007 est de nouveau bloquée.
- print-validated: false.

## P44-M009H02 - Capability update (2026-07-16)

- C-FUSION-UI : implemented pour la synchronisation des defaults par rôle, la
  lecture des dernières valeurs dérivées, l’aide pairwise et le grisage de la
  hauteur de conception ; fusion-validated: false.
- C-TOLERANCE : contrat inchangé et mieux prouvé : override explicite prioritaire
  même inférieur, héritage sinon, max uniquement entre deux voisins.
- C-QUALITY : 476 tests passent, dont isolation asset et trois conteneurs ;
  syntaxe JavaScript et DOM passent.
- Suite : P44-M009H02V avant P44-M007 ; print-validated: false.

## P44-M009H03 - Capability update (2026-07-16)

- C-TOLERANCE : les jeux externes des conteneurs sont exclusivement globaux ; les anciens overrides par bac sont compatibles mais inactifs. Les overrides asset et plat restent locaux.
- C-FUSION-UI : Réglages adopte une surface dense et structurée en épaisseurs, tableau de jeux X/Y–Z et comportement. Les cartes de conteneurs ne portent plus de volet « Jeu externe ».
- C-COMPATIBILITY : aucun champ historique n’est supprimé et aucun projet n’est migré destructivement.
- C-QUALITY : 474 tests, syntaxe JavaScript et DOM passés ; compileall, frontière adsk et `git diff --check` passés.
- Suite : P44-M009H03V avant P44-M007 ; fusion-validated: false ; print-validated: false.

## P44-M009H04 - Capability update (2026-07-16)

- C-FUSION-UI : Réglages est borné et aligné à gauche ; les dimensions Cible/Fixe sont intégrées à l’en-tête des conteneurs.
- C-USABILITY : nombre d’éléments sous le nom, minimum et mode compacts, épaisseurs explicitement nommées, interversion X/Y contextualisée.
- C-TOLERANCE et C-GEOMETRY : aucun changement fonctionnel.
- C-QUALITY : 474 tests, syntaxe JavaScript, DOM, transport Qt, `compileall` et frontière `adsk` passés.
- Suite : P44-M009H04V avant P44-M007 ; fusion-validated: false ; print-validated: false.

## P44-M009H05 - Capability update (2026-07-16)

- C-FUSION-UI : cartes distribuées gauche/droite et commande globale intégrée à la ligne Conteneurs.
- C-USABILITY : le mode global expose son état réel, y compris Mixte, puis applique un choix unique aux trois axes de tous les conteneurs.
- C-TOLERANCE et C-GEOMETRY : aucun changement fonctionnel.
- C-QUALITY : 475 tests, syntaxe JavaScript, DOM, transport Qt, compileall et frontière adsk passés ; preuve Fusion reçue le 2026-07-16 (package 0.1.36, commit 7c76ba0).
- Suite : C-FUSION-UI et C-USABILITY sont fusion-validated pour H05 ; P44-M007 est ready-for-explicit-go ; print-validated: false.

## P44-M007 - Capability update (2026-07-16)

- C-FUSION-UI : calcul hybride adaptatif implemented ; validation dérivée à 350 ms, solve complet à 1 500 ms, fallback manuel et état de cycle lisible.
- C-USABILITY : statut et projections de l’Aperçu précèdent les alertes et détails ; `Hauteur de conception` est explicitement dérivée, grisée et non éditable.
- C-QUALITY : réponses obsolètes rejetées par révision source et dernière identité de requête ; une seule action de matérialisation explicite ; package 0.1.37 et gate reproductible.
- C-SOLVER / C-TOLERANCE / C-GEOMETRY / C-CAD-IR : aucun changement fonctionnel, aucune recalibration et aucun appel adaptatif de scène.
- Suite : P44-M007 est implemented et automated-validated, fusion-validated: false ; P44-M007V est la seule action suivante ; print-validated: false.

## P44-M007H01 - Capability update corrective (2026-07-16)

- C-FUSION-UI : les réponses de fond ne remplacent plus le DOM éditable ; focus,
  sélection et saisie rapide deviennent des invariants de la gate 0.1.38.
- C-USABILITY : champs cartes conditionnels, deltas sleeves visibles et
  conteneurs repliables avec en-tête permanent.
- C-PROJECT-CONTRACT : deux champs sleeves optionnels et additifs ; absence
  préservée au roundtrip pour les projets historiques.
- C-QUALITY : 481 tests, garde d’obsolescence conservée, rendu complet limité
  aux mutations structurelles et gate P44-M007H01V reproductible.
- Limites : valeurs de départ sleeves non validées physiquement ; solveur,
  tolérances, géométrie et scène inchangés ; fusion-validated: false ;
  print-validated: false.
- Suite : P44-M007H01V est supersédée avant observation par P44-M007H02V.

## P44-M007H02 - Capability update corrective (2026-07-16)

- C-FUSION-UI : preset `Cartes` non sleevé, méthode de mesure placée avant le
  menu et champs conditionnels réellement absents quand ils sont inactifs.
- C-USABILITY : deltas sleeves 3 mm X/Y et 0,19 mm/carte visibles dans les deux
  méthodes ; quantité estimée grisée en épaisseur paquet.
- C-PROJECT-CONTRACT : `card_stack_declared_thickness_mm` additif sépare le Z
  saisi du Z résolu et empêche tout cumul au roundtrip.
- C-ASSET : estimation déterministe demi-supérieure sur la base de 0,31 mm par
  carte ; surcharge Z appliquée par carte seulement lorsque les sleeves et le
  delta explicite sont actifs.
- C-QUALITY : 483 tests passent et gate P44-M007H02V reproductible ; anciens
  projets sans deltas préservés.
- C-SOLVER / C-TOLERANCE / C-GEOMETRY / C-CAD-IR : aucune modification du
  placement, aucune recalibration et aucune scène automatique.
- Limites : valeurs sleeves non validées physiquement ; fusion-validated: false ;
  print-validated: false.
- Suite : P44-M007H02V est la seule action suivante autorisée. Les dispositions
  non-cartes sont candidates de P45, pas de P44.

## P44-M007H03 - Capability update corrective (2026-07-16)

- C-ASSET : X/Y manuels déclarés séparément dans `card_declared_xy_mm` ; delta
  sleeve X/Y appliqué une seule fois lorsque `Sleeves` est actif.
- C-PROJECT : champ additif roundtrippable ; anciens projets sans champ ni delta
  conservés sans migration destructive.
- C-UX : faits cartes invalidés explicitement par `À recalculer`, ligne cartes
  plus compacte, `Nb cartes`, repli global et individuel, placeholders
  `Défaut`, modes de densité supprimés.
- C-QUALITY : reproduction automatisée du cas 66 × 88 × 27 + deltas 3/0,19,
  résultat 69 × 91 × 43,53 et roundtrip sans cumul ; 484 tests passent.
- C-SOLVER / C-TOLERANCE / C-GEOMETRY / C-CAD-IR : aucune modification du
  placement, aucune recalibration et aucune scène automatique.
- Limites : fusion-validated: true ; print-validated: false ; valeurs sleeves
  non validées physiquement. Preuve Fusion : `P44-M007H03 Fusion OK 0.1.40 - commit 92f07c8`.
- Suite : P0-M010 est la seule action suivante autorisée. Les dispositions
  non-cartes restent candidates de P45 ; aucune mission produit suivante n’est
  ouverte par cette validation.

## P0-M010 - Capability update documentaire (2026-07-16)

- C-QUALITY : `PILOTAGE_CURRENT.md` fournit une reprise courte, une vue terminé/prêt/bloqué et des renvois explicites vers les sources canoniques.
- C-AUTONOMY : les instructions distinguent lecture minimale et consultation détaillée conditionnelle, sans réduire l’autorité des contrats, ADR, gates ou preuves.
- Limites : aucun runtime, solveur, schéma, valeur physique, géométrie ou scène Fusion n’est modifié ; `print-validated: false`.
- Suite : P44-VP est la seule mission `ready`, pour préparer P44-V avant P45.

## P44-VP - Capability update de préparation (2026-07-16)

- C-FUSION-UI / C-USABILITY : P44-V dispose d’une recette unique couvrant parcours novice/expert, densité, clavier, conteneurs, import et scène préservée.
- C-QUALITY : package 0.1.40 installable et contrôlé avant observation humaine.
- Limites : P44-VP n’est pas une validation Fusion ; `print-validated: false`.
- Suite : retour humain P44-V, puis seulement P45 si la gate est acceptée.


## P44-VH01 - Cohérence hauteur dérivée et calcul volumétrique

- C-USABILITY : la hauteur visible dans Réglages est exactement celle transmise au cœur après édition de Z ou du jeu sous couvercle.
- C-LAYOUT : la capacité multi-étages existante est couverte par une régression à 24 conteneurs avec réservation supérieure et hauteur abondante.
- C-QUALITY : aucun état caché usable_height_mm divergent ne traverse validation, solve, autosave ou sauvegarde nommée depuis la palette.
- C-FUSION-UI : package 0.1.41 automated-validated ; gate P44-VH01V supersédée par P64-H01V sans revendication fusion-validated.
- Limites : solveur, budgets, tolérances, géométrie et valeurs physiques inchangés ; fusion-validated: false, print-validated: false.


## P64-H01 - Recherche dense et équilibre volumétrique

- C-LAYOUT : partitions adaptatives d'empreintes variables et arrangements XY
  évalués avec leur hauteur d'étage.
- C-SOLVER : le mode balanced classe les candidats complets par qualité X/Y/Z,
  charge des étages, support, cibles, matière et simplicité ; compact reste
  orienté vers le nombre minimal de compositions.
- C-QUALITY : budgets publics, borne Z, déterminisme, fixture dense de 30 corps
  et progression automatisée 1/2/3 étages.
- C-FUSION-UI : package 0.1.42 fusion-validated par `P64-H01 Fusion OK 0.1.42 - commit 5865645`.
- Limites : heuristique non globalement optimale ; schéma, tolérances, valeurs
  physiques, géométrie et scène inchangés ; fusion-validated: true,
  print-validated: false.


## P44-VH02 - Suppression directe et nommage incrementiel

- C-USABILITY : suppression visible par element, confirmation transactionnelle des conteneurs non vides et noms de conteneurs non ambigus.
- C-QUALITY : aucun schema, bridge, solveur, geometrie ou scene automatique ne change.
- C-FUSION-UI : package 0.1.43 automated-validated ; gate P44-VH02V requise.
- Limites : fusion-validated: false, print-validated: false.
## P64-H02 — Reprise diversifiée après cul-de-sac

- C-LAYOUT / C-SOLVER : le portefeuille canonique reste prioritaire ; six ordres
  diversifiés au maximum sont activés seulement après un échec de recherche ou
  de validation finale compatible avec une reprise.
- C-QUALITY : ordre SHA-256 stable par identifiant métier, un seul ordre par
  portefeuille, budget et compteurs publics, fixture localisée et reproduction
  exacte de l’autosauvegarde Fusion.
- C-USABILITY : le cas sauvegardé passe de `Calcul impossible` à 8 conteneurs sur
  2 niveaux ; le menu `...` et la croix restent sur la même ligne.
- C-FUSION-UI : package 0.1.47 automated-validated ; P64-H03R contextual-KO,
  aucune preuve Fusion OK.
- Limites : aucune promotion physique ou géométrique ; recherche heuristique,
  fusion-validated: false, print-validated: false ; trajectoire supersédée par
  P64-A01 puis P64-H04.

## P64-A01 — Programme multi-solveurs et finition volumique

- C-SOLVER : trajectoire acceptée vers `stage_stack`, `free_3d_greedy`,
  `free_3d_beam`, `portfolio_auto` et un `exact_proof` futur sous gate.
- C-QUALITY : distinction obligatoire entre solution, épuisement heuristique,
  impossibilité prouvée, entrée invalide et réponse obsolète ; télémétrie
  structurée avant nouvel algorithme.
- C-LAYOUT / C-GRID-3D : EP/EMS et points extrêmes deviennent la seconde famille ;
  les grilles uniformes restent expérimentales et non canoniques.
- C-USABILITY : méthode, effort, classement et finition sont quatre réglages
  séparés ; diagnostic secondaire sans perte de focus.
- C-ASSET : P45 reste propriétaire des variantes internes non-cartes ; P64
  prépare seulement leur interface future.
- C-GEOMETRY : finition continue/modulaire planifiée après P46 ; aucun filler ni
  cale automatique.
- État : P64-H03R/H04/H05/H06/H07 intégrés (baseline dirigée, résultats honnêtes,
  contrat commun, greedy et beam 3D, portefeuille Auto interne). P64-H08 est
  intégrée dans 0.1.51 ; P64-V2 est un KO contextuel et P64-V2H01 0.1.52 est
  contextual-KO et supersédée par P64-V2H02R 0.1.54.
- Validation : dernière preuve inchangée P64-H01 0.1.42 ; P64-H02/H03 non
  fusion-validées ; `print-validated: false`.

## Mise à jour P64-H07 — 2026-07-17

- C-SOLVER : `free_3d_beam` et `portfolio_auto` sont `implemented` et
  `automated-validated` derrière la frontière interne ; profils monotones,
  timeout/annulation et déduplication testés.
- C-LAYOUT / C-GRID-3D / C-STACKING : enveloppes finales cherchées dans EP/EMS,
  fermeture sans résiduel arbitraire et topologie multi-niveaux certifiée.
- C-QUALITY : correspondance candidat/plan ajoutée au certificat autoritaire ;
  seuls les plans complets certifiés sont classés.
- C-USABILITY (état historique H07) : aucun réglage visible encore ; P64-H08 devait exposer
  méthode, effort et diagnostic sans perte de focus.
- Validation : aucune preuve Fusion ou impression nouvelle ; dernière preuve
  solveur P64-H01 0.1.42, `print-validated: false`.

## Mise à jour P64-H08 — 2026-07-17

- C-SOLVER : `implemented`, `automated-validated` pour la sélection publique
  Auto / Étages et piles / Placement 3D libre, bornée par les profils H07 et
  classée seulement parmi les plans complets certifiés.
- C-USABILITY : méthode, effort et classement mesuré sont visibles dans Fusion ;
  préférences locales additives, diagnostic repliable et mises à jour silencieuses
  sans reconstruction du DOM éditable.
- C-QUALITY : résultat, matérialisabilité et proposition résiduelle restent
  cohérents ; aucun budget épuisé ne devient une impossibilité prouvée.
- Validation : P64-V2 0.1.51 est un KO contextuel ; dernière preuve
  solveur Fusion inchangée P64-H01 0.1.42 ; `print-validated: false`.

## Mise à jour P64-V2H01 — 2026-07-17

- C-SOLVER : implemented, automated-validated. Le beam v2 place d'abord les
  minima, conserve plusieurs états et délègue la fermeture continue avant le
  certificat commun.
- C-LAYOUT / C-GRID-3D : implemented. Le cas anonymisé réel produit 9 corps sur
  plusieurs niveaux, sans résiduel imprimable ni corps automatique.
- C-QUALITY : implemented. Les réservations plateau/livret sont conditionnelles
  et les fonds/cavités restent contrôlés par le validateur commun.
- C-USABILITY : automated-validated seulement. Les méthodes donnent des
  résultats effectivement différents sur la fixture, mais l'observation Fusion
  0.1.52 est désormais supersédée par la gate corrective 0.1.54.
- Harmonisation : alignement de faces amélioré seulement ; P64-F02 reste prévu.
- Preuve : tests automatisés et reproduction locale ; fusion-validated: false,
  print-validated: false.

## Mise à jour P64-V2H02R — 2026-07-18

- C-SOLVEUR-DENSE : enveloppes multi-cavités bornées, placement beam traversant
  plusieurs EMS, points extrêmes aux frontières des réservations et validation
  de coupe localisée sont implémentés dans 0.1.53 et conservés dans 0.1.54.
- C-SOLVEUR-PORTFOLIO : Rapide, Normal et Approfondi explorent respectivement
  1, 2 et 4 priorités beam ; les méthodes restent distinctes même si leur meilleur
  résultat visible converge.
- C-RESULT-TRUTH : tous les résultats exposent `bgig.partition_capacity.v1` ; une
  marge positive est explicitement une borne nécessaire, pas un certificat de
  placement. Les épuisements heuristiques restent `no_solution_within_budget`.
- C-FUSION-UI : capacité théorique visible sur succès/échec et vue de dessus
  correctement occultée et correctement orientée autour de l'axe X ; P64-V2H02R est fusion-validated par la preuve 0.1.54 commit 42e8993.
- Limite : le projet de référence à 11 conteneurs et 34 contenus reste non
  certifié malgré environ 693,6 cm³ de marge théorique. Les variantes internes
  globales relèvent de P64-V2H03 à coordonner avec P45.
- Validation : `fusion-validated: true` pour la portée P64-V2H02R, `print-validated: false`. P44-V et P45
  restent bloquées pendant le chemin correctif P64-V2H03.

## Mise à jour P64-V2H03A — 2026-07-18

- C-GEOMETRY / C-ASSET : `contracted` pour une frontière locale de variantes
  immuables ; P45 garde les sémantiques, futures formes et certification locale.
- C-SOLVER / C-LAYOUT : `designed` pour une sélection globale paresseuse et
  bornée après la voie canonique, sans produit cartésien.
- C-QUALITY : identité par digest, déduplication, deux certificats, lanes
  préservées, monotonie des profils et fixtures de culs-de-sac deviennent des
  critères normatifs.
- C-USABILITY : aucun contrôle novice ajouté ; la traçabilité reste dans le
  diagnostic secondaire.
- Validation : documentaire seulement. Aucun runtime ou schéma projet ne change ;
  `fusion-validated: false` et `print-validated: false` pour P64-V2H03.
- Suite : P64-V2H03B est `ready` ; P64-V2H03C/V restent bloquées. P45 reste
  bloquée par P44-V.

## Mise à jour P64-V2H03B — 2026-07-18

- C-GEOMETRY / C-ASSET : `implemented-core` pour snapshots, producteurs et
  certificat local.
- C-QUALITY : `automated-validated` pour digests, provenance, déduplication,
  Pareto, fail-closed et corpus 11 × 34.
- C-SOLVER / C-LAYOUT : frontière disponible, sélection globale encore
  `designed` et non branchée jusqu'à H03C.
- C-USABILITY : aucune surface novice ne change.
- H03C devient `ready` ; H03V reste bloquée par C.

## Mise à jour P64-V2H03C — 2026-07-18

- C-SOLVER / C-LAYOUT : `implemented-core`, `automated-validated` pour la
  sélection conjointe variante-placement après échec du portefeuille canonique.
  Les affectations restent paresseuses et bornées, sans produit cartésien.
- C-GEOMETRY / C-ASSET : les cavités et jeux locaux proviennent exclusivement
  des variantes H03B certifiées ; la fermeture ne mute ni dimensions ni origines
  locales et les jeux externes restent globaux.
- C-QUALITY : certificats local, commun et global, digests de lanes, caps
  2/4/6, 32/384/3 072 états et 128/3 072/36 864 essais, stale et vérité
  `no_solution_within_budget` sont couverts automatiquement.
- C-USABILITY : aucune option novice ou experte n'est ajoutée ; la trace H03C
  reste dans le diagnostic secondaire des méthodes et efforts H08 existants.
- Preuve : `docs/P64_V2H03C_GLOBAL_SELECTION_EVIDENCE.md`, suite 566/566 OK.
- Limite : le mécanisme dense 11 × 34 reste non certifié jusqu'en Approfondi ;
  aucune impossibilité, preuve Fusion ou impression n'est revendiquée.
- Suite : P64-V2H03V `ready` ; P45 et P44-V restent bloquées pendant la gate.

## Mise à jour P64-V2H03V — 2026-07-18

- C-FUSION-UI / C-USABILITY : `implemented-fusion-unvalidated` pour le diagnostic
  H03C secondaire et replié ; le parcours normal ne gagne aucun contrôle.
- C-SOLVER / C-LAYOUT : aucune logique ne change ; la palette projette la trace
  H03C déjà certifiée et le contrôle canonique reste sur `stage_stack`.
- C-QUALITY : fixture synchronisée avec H03C, préflight pur, package 0.1.55,
  installateur borné, backups locaux et marqueur de commit.
- Limites : `fusion-validated: false`, `print-validated: false`, cas dense non
  certifié, aucune forme P45, valeur physique, tolérance ou scène automatique.
- Suite : observation humaine P64-V2H03V ; P44-V et P45 restent bloquées jusqu'au
  retour explicite.


## Mise à jour P64-A02 — 2026-07-21

- C-USABILITY / C-FUSION-UI : designed pour une boucle progressive où l'analyse
  locale reste discrète, le solve global est une action primaire et la
  finalisation une action séparée. Les résultats experts restent repliés.
- C-ASSET / C-GEOMETRY : contracted pour des variantes locales certifiées, un
  score explicable, des opportunités internes et des baies de boîte réservées.
  P45 conserve les sémantiques et formes ; P64 conserve la combinaison globale.
- C-SOLVER / C-LAYOUT : designed pour l'élargissement progressif de frontières,
  sans limite moteur top 3 et sans retrait des lanes historiques.
- C-QUALITY : contracted pour états explicites, digests par entité, invalidation
  minimale, réponses stale refusées, certificats local/global/finalisation et
  carte de capacité éphémère.
- C-RESULT-TRUTH : aucune zone, marge ou score ne prouve la faisabilité. Une
  insertion accélérée réutilise une pose, jamais un certificat ancien.
- Validation : documentaire uniquement. Aucun runtime, schéma ou comportement
  Fusion n'est implémenté ; P64-V2H03V reste ready-for-human-fusion-check.


## Mise à jour P64-V2H03V — 2026-07-21

- C-SOLVER / C-LAYOUT : fusion-validated pour la projection du fallback H03C,
  la sélection paresseuse de variantes et le certificat global visible.
- C-USABILITY / C-FUSION-UI : fusion-validated pour le diagnostic secondaire
  replié, le contrôle canonique et l'absence de scène automatique.
- C-QUALITY : la vérité no_solution_within_budget demeure intacte sur le corpus
  dense ; aucun budget heuristique ne devient une impossibilité.
- Limites : P45, valeurs physiques, tolérances et impression restent hors
  périmètre. print-validated: false.
- Suite : P64-V2H03 est clôturée ; P44-V doit être requalifiée avant P45.


## Mise a jour P44-V - preparation de requalification 0.1.55

- C-FUSION-UI / C-USABILITY : recette de requalification du runtime actuel, sans promotion avant retour Fusion.
- C-QUALITY : package, SHA installe, invariants DOM P44 et H03V controles.
- Suite : P44-V humaine, puis P45 seulement si OK explicite.


## Mise a jour P44-V - gate Fusion 0.1.55

- C-FUSION-UI / C-USABILITY : fondation UX fusion-validated pour la palette observee.
- C-QUALITY : reserve explicite, aucune preuve de charge a environ 50 conteneurs.
- Suite : P45-M001 peut etre cadre sans transfert du solveur global P64.


## Mise à jour P45-M001V — contrat accepté

- C-GEOMETRY / C-ASSET : `architecture-accepted` pour le composant commun
  `Pile` / `Basculer`, la pose verrouillée, les intentions et le certificat local.
- C-SOLVER / C-LAYOUT : inchangées ; P64 conserve budgets, placement et
  certificat global.
- C-USABILITY : même grammaire compacte pour cartes et autres assets ; le
  sleeving reste une spécialisation des cartes.
- C-QUALITY : quantité totale distincte du nombre par pile, compatibilité
  `auto` historique, fixtures d'axes et migration additive obligatoires.
- Suite : P64-L01 `ready` ; aucune capability runtime P45 promue.

## Mise à jour P64-L01 — état incrémental

- C-ASSET / C-GEOMETRY : `implemented-core` pour les identités source, pose,
  defaults hérités et invalidation locale ; aucune forme P45 ajoutée.
- C-SOLVER / C-LAYOUT : infrastructure de dépendances `implemented-core` ;
  méthodes, budgets, résultats et auto-solve public inchangés.
- C-PROJECT-CONTRACT : aucun champ ajouté ; cache et artefacts dérivés restent
  reconstructibles et hors `bgig.project.v1`.
- C-QUALITY : 16 fixtures L01, corpus cinquante conteneurs, parité de dérivation,
  stale fail-closed, cache borné et 587 tests complets.
- C-FUSION-UI : inchangée ; aucune scène ni matérialisation automatique.
- Suite : P64-L02 `ready`. `fusion-validated: false`,
  `print-validated: false`.

## Mise à jour P64-L02 — analyse locale contextuelle

- P64-L02 : implémenté et testé automatiquement.
- Capacités livrées : analyse contextuelle locale, compatibilités explicites, sous-scores séparés, Pareto déterministe, représentants UX progressifs et invalidation ciblée.
- Capacités non livrées : solve global, finalisation, remplissage, cales, matérialisation, validation Fusion et validation impression.
- P64-L03 est automated-validated ; P64-L03V est la dépendance suivante, sans ouvrir P46, P47-P50, P67-P69 ou P64-F02 hors dépendances.

## Mise à jour P64-L03 — cycle explicite

C-SOLVER / C-LAYOUT : orchestration staged implémentée sans changement des
méthodes, budgets ou résultats. C-PROJECT-CONTRACT : état et caches restent
dérivés hors schéma. C-FUSION-UI : action progressive Calculer / Finaliser /
Matérialiser, sans scène automatique. C-QUALITY : stale, provenance et clé
globale testés. La revue L03V est ensuite devenue `contextual-KO` sur la
séparation géométrique minimal/final ; ADR-0074 porte la correction.

## Mise à jour P64-L03R-A — contrat minimal et scène duale

- C-SOLVER / C-LAYOUT : `architecture-accepted` pour un `minimal_layout` sans
  surplus et un portfolio multi-graines borné par rareté, ancres, propagations,
  support local, symétrie et progressive widening.
- C-FUSION-UI : `contracted` pour matérialiser minimal ou finalisé, comparer les
  digests exacts et remplacer uniquement la scène possédée par BGIG.
- C-RESULT-TRUTH : le résiduel reste non attribué ; meilleure proposition
  certifiée dans le budget, jamais optimalité implicite.
- C-QUALITY : 18 fixtures contractuelles, monotonie, stale, scène et préservation
  des objets utilisateur.
- État : aucun runtime promu. P64-L03V contextual-KO ; P64-L03R-B ready.
  `fusion-validated: false`, `print-validated: false`.

## Mise à jour P64-L03R-B — solveur minimal certifié

- C-SOLVER / C-LAYOUT : `implemented-core`, `automated-validated` pour le
  portefeuille minimal multi-graines, les préfixes d'effort monotones, les
  couches locales supportées et la frontière Pareto globale non tronquée.
- C-RESULT-TRUTH : `minimal_layout` certifie les enveloppes minimales exactes et
  conserve le résiduel non attribué ; le résultat reste « meilleure proposition
  certifiée trouvée dans le budget ».
- C-QUALITY : variantes locales et digests L01/L02 consommés explicitement,
  fallback borné, symétrie canonique, réservation asymétrique, support, stale,
  échec borné et cas dense 11 × 34 couverts.
- C-FUSION-UI / C-CAD : inchangées dans B ; aucune scène, CAD IR ou
  matérialisation minimale n'est encore promue.
- Suite réalisée : P64-L03R-C `automated-validated` ; P64-L03R-V est désormais `ready-human-gate`.
  `fusion-validated: false`, `print-validated: false`.
## Mise à jour P64-L03R-C — matérialisation duale automatisée

- C-SOLVER / C-LAYOUT : l'orchestration staged consomme le `minimal_layout`
  certifié de L03R-B et rend stale tout changement de dépendance L01/L02 ; aucun
  solveur historique public ni budget n'est modifié.
- C-CAD : `implemented-core`, `automated-validated` pour une CAD IR minimale
  construite sans nouveau solve, sans résiduel distribué et avec digest de
  géométrie revalidé.
- C-FUSION-UI : `implemented-fusion-bridge`, `implemented-fusion-ui`,
  `automated-validated` pour la sélection minimal/finalisé, l'identité exacte,
  `Mettre à jour la scène` et le remplacement borné d'une seule racine BGIG.
- C-RESULT-TRUTH : la finalisation reste optionnelle et absente de C ; le plan
  minimal reste consultable et matérialisable après un échec de finition.
- C-QUALITY : fixtures 11 à 18, scène ambiguë fail-closed, ancien digest, stale,
  préservation d'objet utilisateur et altération CAD couvertes.
- Suite : P64-L03R-V `ready-human-gate` sur Fusion 0.1.57.
  `fusion-validated: false`, `print-validated: false`.


## Mise à jour P64-L04A — réutilisation locale certifiée

- C-ASSET / C-GEOMETRY : un asset ajouté ou modifié peut être dérivé dans le
  conteneur existant sans changer sa pose ni son enveloppe ; le producteur reste
  rectangulaire et ne crée aucune nouvelle intention P45.
- C-SOLVER / C-LAYOUT : `implemented-core`, `automated-validated` pour la
  recertification d’un plan monde fixe. La recherche globale n’est pas appelée ;
  un fallback de variante locale à enveloppe identique reste borné.
- C-PROJECT-CONTRACT : nouvel artefact, révision, digests, provenance, budget,
  compteurs et raisons d’arrêt ; le cache et le schéma projet ne deviennent pas
  sources d’autorité.
- C-FUSION-UI : `implemented-fusion-bridge`, `implemented-fusion-ui`,
  `automated-validated` pour le succès local, le recalcul global requis et les
  détails repliés. Une scène existante devient désynchronisée sans mutation.
- C-RESULT-TRUTH : aucun espace visible n’est promu en garantie ; le certificat
  local puis global décide. `unknown` n’est jamais promu.
- C-QUALITY : insertion dans une poche, invariance monde, déterminisme, caps,
  fallback même enveloppe, trop-grand fail-closed, nouvelle boîte/conteneur,
  certificat altéré, lifecycle, bridge et DOM couverts.
- Non livré : Deep anytime (L04B), attente UX (L04C), finalisation, capacité
  post-finalisation C01/C02, forme P45, valeur physique, preuve Fusion ou
  impression.
- Suite : P64-L04B `ready`, puis L04C et L04V.
  `fusion-validated: false`, `print-validated: false`.

## Mise à jour P64-L04B — Approfondi anytime

- C-SOLVER / C-LAYOUT : `implemented-core`, `automated-validated` pour le
  préfixe Normal incumbent et l’extension Deep bornée. Les caps par lane restent
  inchangés ; les trois lanes Deep partagent 30 000 ms.
- C-RESULT-TRUTH : une expiration conserve une solution Normal certifiée ; sans
  incumbent elle reste `no_solution_within_budget`. Une annulation stale reste
  fail-closed.
- C-PROJECT-CONTRACT : aucun champ projet ajouté. La provenance dérivée expose
  phases, budgets, temps, lanes, frontières, incumbent, sélection et arrêt.
- C-QUALITY : expiration avec/sans incumbent, monotonie, égalité conservatrice,
  completion Deep, certificat commun et intégrations staged/CAD/palette couverts ;
  639/639 tests complets.
- C-FUSION-UI : inchangée dans L04B. L’activité visuelle des opérations longues
  appartient à L04C ; le manifest reste 0.1.58.
- Livré ensuite par L04C : activité immédiate, identité, étape et temps écoulé.
- Non livré : finalisation, capacité post-finalisation, formes P45, valeurs
  physiques, preuve Fusion ou impression.
- Statut : `fusion-validated: false`, `print-validated: false`.

## Mise à jour P64-L04C — activité opérationnelle honnête

- C-USABILITY / C-FUSION-UI : implemented-fusion-ui et automated-validated
  pour l'activité immédiate, l'étape courante, le temps écoulé et l'identité
  exacte de chaque analyse, calcul, finalisation ou matérialisation.
- C-QUALITY : producteur pur déterministe, lifecycle terminal exact, verrou du
  même type dans la palette et le bridge, détails repliés, focus et autosave
  préservés ; 648/648 tests complets.
- C-PROJECT-CONTRACT : inchangé ; état dérivé non persisté, aucun pourcentage,
  aucune ETA et aucune annulation utilisateur décorative. stale_or_cancelled
  reste une invalidation de validité fail-closed.
- C-SOLVER / C-LAYOUT / C-GEOMETRY / C-CAD-IR : inchangées ; aucune opération
  métier n'est déclenchée par le suivi d'activité.
- Suite : P64-L04V est la prochaine gate Fusion distincte ; manifest 0.1.58,
  fusion-validated: false, print-validated: false.

## Mise a jour P64-L04V preparation de gate

- C-FUSION-UI / C-LAYOUT : preflight et fixture de gate automated-validated ; le prepareur ne lance aucun solve global, finaliseur ou remplacement de scene.
- Statut : ready-human-gate, fusion-validated: false, print-validated: false. La promotion depend seulement du retour humain L04V.
