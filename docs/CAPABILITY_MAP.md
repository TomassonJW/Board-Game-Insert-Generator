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
| C-ASSET | Asset model | Asset-first design | `fusion-validated-v0` | M6 Asset-first project model | Assets charges/reportes P9-M002; module_candidates metadata P10-M004/P10-M005; grouping borne P10-M006; plan executable borne P10-M008; P13-M001/P13-M001V valide Fusion une saisie `quick_asset_box` V0 honnete avec module proxy asset-first, assets lus depuis l UI, generate/regenerate/clear et limites explicites; P13-ASSET-M002/P13-ASSET-M002V valide Fusion le sizing count-aware V0 pour assets simples, diagnostics de piles/capacite, debug visual asset-fit, regenerate sans doublon et preservation non-BGIG; P13-ASSET-M003/P13-ASSET-M003V valide Fusion une cavite rectangulaire globale asset-fit V0 via `single_asset_fit_rectangular_cavity_v0`; P13-ASSET-M004/P13-ASSET-M004V valide Fusion `per_source_asset_rectangular_compartments_v0` avec compartiments rectangulaires par asset source; dette UX `quick_asset_box` documentee; assets individuels, cavites par pile/item, capacite physique garantie, solveur global, UI avancee et impression restent gates |
| C-MODULE | Module model | Modular printable bodies | `implemented-core` | M1 Engine foundation | Aucune active |
| C-CAVITY | Cavity model | Cavities and ergonomic features | `implemented-cad-ir` | M4 Abstract cavities | Gate Fusion cuts |
| C-FEATURE | Ergonomic feature model | Cavities and ergonomic features | `implemented-cad-ir` | M4 Abstract cavities / M8 Ergonomic planner | Taxonomie P6-M003 implementee ; gate Fusion pour nouvelles geometries |
| C-LAYOUT-2D | 2D layout | Volumetric layout | `implemented-core` | M2 Simple layout | Aucune active |
| C-GRID-3D | 3D volumetric grid | Volumetric layout | `implemented-cad-ir` | M7 Volumetric planner | P8-M001 implemente le socle declaratif; P10-M008 utilise un placement greedy abstrait; P11-M001 est `fusion-validated` pour la consommation compacte des placements; P11-M002 est validee Fusion pour la scene multi-layer; P11-M003 corrige le sizing explicite grille / asset-fit / printable; P11-M003V2 ajoute le rapport bbox planned/actual; P11-M003V3 corrige la vraie commande UI visible; P11-M003V4 valide Fusion la scene produit non ambigue et le mapping source; print-validated: false |
| C-LAYERS | Layer / stage model | Volumetric layout | `implemented-cad-ir` | M7 Volumetric planner | Layers declaratifs P8-M001; gate impression avant support physique |
| C-RESERVATION | Board / tray / lid reservation | Asset-first design | `implemented-cad-ir` | M6 Asset-first project model | Reservations abstraites P8-M002; gate si impact dimensions publiques ou generation Fusion |
| C-ACCESS | Accessibility and removal order | Human validation gates | `implemented-cad-ir` | M8 Ergonomic planner | Removal order abstrait P8-M002; validation ergonomique humaine avant confort revendique |
| C-STACKING | Support / stacking rules | Volumetric layout | `implemented-cad-ir` | M7 Volumetric planner | Support surfaces abstraites P8-M002; gate impression reelle |
| C-COMPOSITE | Composite modules | Modular printable bodies | `planned` | M9 Composite modules | Gate modules composites |
| C-CAD-IR | CAD IR | CAD generation pipeline | `implemented-cad-ir` | M3 CAD pipeline | Gate si contrat incompatible |
| C-FUSION-COMPACT | Fusion compact view | CAD generation pipeline | `fusion-validated` | M3 CAD pipeline / M7 Volumetric planner | Blanks rectangulaires valides; vue compacte grille P11-M001 validee manuellement dans Fusion; P11-M002 validee Fusion pour multi-layer; P11-M003 change les bodies asset-first vers `printable_body_size_mm`; P11-M003V2 refuse les tailles ambigues et affiche la bbox reelle; P11-M003V3 corrige la commande UI visible; P11-M003V4 valide Fusion la scene produit non ambigue et le mapping source; print-validated: false |
| C-FUSION-EXPLODED | Fusion exploded view | CAD generation pipeline | `fusion-validated` | M5 CAD inspection views | P7-M001V4 valide la vue eclatee basique par composants uniques et occurrences compactes/eclatees liees en document Assembly-compatible; Part Design est detecte comme incompatible; le renommage direct de `Occurrence.name` est evite; P11-M002 valide une scene eclatee multi-layer; P11-M003 conserve les occurrences liees via commande UI; P11-M003V2 ajoute le rapport dimensionnel; P11-M003V3 corrige la commande UI visible; P11-M003V4 valide Fusion la scene produit non ambigue et le mapping source; print-validated: false |
| C-FUSION-UI | Fusion command UI | CAD generation pipeline | `fusion-validated` | M14 Usable beta | P11-M003 ajoute une commande Fusion minimale avec chemin CAD IR et mode compact/exploded; P11-M003V4 valide l'usage UI avec scene produit non ambigue; P12-M001 valide Fusion le bouton toolbar relancable; P12-M002V7 corrige la commande parametrique V0 avec modes `cad_ir_file`/`config_file`, action `inspect_bgig_scene`, registry BGIG, root auto-detecte/memorise, scene racine `BGIG Generated Scene`, `generate` refuse les doublons, occurrence racine unique taguee `bgig:role = scene_root`, attributs `scene_id`/`role`/`module_id`, suppression par `deleteMe()`, occurrence compacte initiale visible, occurrence eclatee liee via `addExistingComponent`, `regenerate` remplace sans doublons attendu et `clear_bgig_scene` supprime la racine; P12-UI-M002V7 validee Fusion avec inspect/generate/regenerate/clear, registry et ownership racine BGIG; reporting inspect deduplique; P12-M003V valide Fusion `quick_parametric_box` en `compact_only` avec CAD IR temporaire, registry OK, occurrence compacte visible et bbox conforme; P12-M004/P12-M004V valide Fusion la persistance complete des champs UI, la rehydratation au prochain `commandCreated`, le diagnostic `UI settings`, `generate`, `regenerate`, reouverture avec derniere valeur conservee et `clear_bgig_scene` preservant les objets non-BGIG; KO initial par settings PowerShell UTF-8 BOM documente et corrige; P13-M001/P13-M001V valide Fusion `quick_asset_box` comme premier input asset-first depuis la commande Fusion classique, avec champ texte assets persiste, config temporaire, reuse du pipeline assets existant, reporting V0 honnete, outlines bas/haut du volume boite, generate/regenerate/clear sans doublon et preservation des objets non-BGIG; P13-ASSET-M002/P13-ASSET-M002V valide Fusion le sizing count-aware V0, `storage_sizing`, diagnostics `capacity_per_stack`/`pile_count`/`declared_capacity`, sketch debug asset-fit non imprimable, regenerate count-aware et clear final; P13-ASSET-M003/P13-ASSET-M003V valide Fusion une cavite asset-fit globale dans le flux `quick_asset_box`; P13-ASSET-M004/P13-ASSET-M004V valide Fusion des compartiments asset-specific V0, reporting associe, debug outlines, generate/regenerate/clear; dette UX `quick_asset_box` documentee; limites non validees : assets individuels, cavites par pile/logements detailles, capacite physique garantie, solveur global, optimisation avancee, UI avancee et impression; print-validated: false |
| C-FUSION-CAVITIES | Fusion cavities | CAD generation pipeline | `fusion-validated` | M5 CAD cavities | Cavites rectangulaires CAD IR validees Fusion; P13-ASSET-M003/P13-ASSET-M003V valide Fusion une cavite asset-fit globale V0; P13-ASSET-M004/P13-ASSET-M004V valide Fusion plusieurs cavites top-open par asset source via `per_source_asset_rectangular_compartments_v0`; print-validated: false |
| C-FILLETS | Fillets and finger notches | CAD generation pipeline | `fusion-validated` | M5 CAD ergonomic features | Encoche rectangulaire top-open validee Fusion, print-validated: false ; courbes/fillets bloques |
| C-SOLVER | Solver and scoring | Volumetric layout | `implemented-core` | M10 Semi-automatic solver | Variant comparison P10-M002 report-only; raisons de rejet structurees P10-M003; module_candidates P10-M004; variante recommandee P10-M005; grouping borne P10-M006; plan concret greedy P10-M008; P13-M001 reutilise ce pipeline sans backtracking ni optimisation globale; P13-ASSET-M002/P13-ASSET-M002V valide une heuristique count-aware bornee pour piles/footprint/refus explicite sans solveur global; gate architecture si optimiseur majeur |
| C-CALIBRATION | Calibration and print validation | Human validation gates | `designed` | M11 Physical validation | Impression reelle |
| C-AESTHETIC | Aesthetic layer | Design language and aesthetics | `planned` | M12 Design language | Gate esthetique structurante |

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
- Gate active : `P13-ASSET-M005-GATE`; aucune validation d'impression.
