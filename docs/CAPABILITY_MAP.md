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
| C-ASSET | Asset model | Asset-first design | `implemented-cad-ir` | M6 Asset-first project model | Assets charges/reportes P9-M002; module_candidates metadata P10-M004/P10-M005; grouping borne P10-M006; plan executable borne P10-M008; gate si schema incompatible, solveur complexe ou Fusion |
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
| C-FUSION-UI | Fusion command UI | CAD generation pipeline | `implemented-fusion` | M14 Usable beta | P11-M003 ajoute une commande Fusion minimale avec chemin CAD IR et mode compact/exploded; P11-M003V4 valide l'usage UI avec scene produit non ambigue; P12-M001 valide Fusion le bouton toolbar relancable; P12-M002V3 corrige la commande parametrique V0 avec modes `cad_ir_file`/`config_file`, root auto-detecte/memorise, scene racine `BGIG Generated Scene`, `generate` refuse les doublons, `regenerate` remplace sans doublons attendu et `clear_bgig_scene` tagged-only; validation Fusion P12-M002V3 requise; print-validated: false |
| C-FUSION-CAVITIES | Fusion cavities | CAD generation pipeline | `fusion-validated` | M5 CAD cavities | Cavites rectangulaires validees Fusion, print-validated: false |
| C-FILLETS | Fillets and finger notches | CAD generation pipeline | `fusion-validated` | M5 CAD ergonomic features | Encoche rectangulaire top-open validee Fusion, print-validated: false ; courbes/fillets bloques |
| C-SOLVER | Solver and scoring | Volumetric layout | `implemented-core` | M10 Semi-automatic solver | Variant comparison P10-M002 report-only; raisons de rejet structurees P10-M003; module_candidates P10-M004; variante recommandee P10-M005; grouping borne P10-M006; plan concret greedy P10-M008; gate architecture si optimiseur majeur |
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
