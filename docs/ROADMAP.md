# Roadmap

Cette roadmap decrit les phases macro jusqu'au produit cible. Le detail
operationnel vit dans `docs/BACKLOG.md`, l'etat courant dans `docs/STATUS.md`,
et la lecture par capabilities dans `docs/CAPABILITY_MAP.md`.

## Phase 0 - Gouvernance, autonomie, qualite

Objectif : rendre le depot autopilotable, gate-aware et maintenable.

Capabilities liees : pilotage projet, gates, validation, integration Git autonome.

Criteres de reussite : documents de controle presents, tests documentaires,
ADR/logs, autonomie direct-to-main, selection par capability.

## Phase 1 - Moteur Python pur

Objectif : stabiliser les value objects, le chargement JSON, la validation et les
rapports hors Fusion.

Capabilities liees : C-BOX, C-MODULE, base C-CAD-IR.

Criteres de reussite : une configuration locale valide produit un resultat
reproductible et teste hors Fusion.

## Phase 2 - Layout 2D simple

Objectif : placer des modules rectangulaires dans le plan XY avec strategies
simples et comparaison explicable.

Capabilities liees : C-LAYOUT-2D.

Criteres de reussite : `row_fill` et `grid` fonctionnent, les cas impossibles
sont refuses, les cellules theoriques restent distinctes des corps imprimables.

## Phase 3 - Tolerances, profils d'impression, clearances

Objectif : appliquer les jeux selon roles de faces, profils d'impression et types
de cavites.

Capabilities liees : C-MODULE, C-CAVITY, C-CALIBRATION.

Criteres de reussite : chaque offset et clearance expose sa source et ses limites
de validation.

## Phase 4 - CAD IR et pipeline Fusion minimal

Objectif : produire une CAD IR stable et generer des blanks rectangulaires
inspectables dans Fusion.

Capabilities liees : C-CAD-IR, C-FUSION-COMPACT.

Criteres de reussite : export CAD IR CLI, add-in isole, blanks mesures dans
Fusion, coeur Python sans `adsk`.

## Phase 5 - Cavites, receptacles et features ergonomiques

Objectif : decrire les cavites et aides ergonomiques cote moteur, rapports et CAD
IR, sans generation Fusion reelle.

Capabilities liees : C-CAVITY, C-FEATURE.

Criteres de reussite : cavites et features chargees, validees, reportees et
exportees comme intentions abstraites.

## Phase 6 - Generation Fusion reelle des cavites et features simples

Objectif : mapper progressivement `subtract_rectangular_cavity` puis certaines
features vers des operations Fusion reelles controlees.

Capabilities liees : C-FUSION-CAVITIES, C-FILLETS.

Criteres de reussite : smoke tests Fusion manuels, aucune logique metier dans
Fusion, aucune validation physique revendiquee.

Gate : obligatoire avant cuts, booleans, fillets, encoches ou fonds arrondis.

## Phase 7 - Vue compacte / vue eclatee

Objectif : produire dans Fusion une vue compacte dans la boite et une vue eclatee
ou repartie a plat pour inspection/export futur.

Capabilities liees : C-FUSION-COMPACT, C-FUSION-EXPLODED.

Criteres de reussite : positions de vue issues du moteur ou de la CAD IR, noms
stables, pas de changement dimensionnel.

## Phase 8 - Grille volumetrique 3D et etages

Objectif : raisonner en X/Y/Z, layers, volumes libres, support et empilement.

Capabilities liees : C-GRID-3D, C-LAYERS, C-STACKING.

Criteres de reussite : representation pure Python testee, collisions X/Y/Z
explicites, aucune promesse physique sans impression.

Statut P8-M001/P8-M002 : socle declaratif implemente pour grille X/Y/Z, layers,
placements explicites, zones reservees/interdites, ordre de retrait abstrait,
surfaces de support abstraites, rapports et metadata CAD IR. Aucun solveur
automatique ni generation Fusion volumetrique.

## Phase 9 - Assets, plateaux, boards, regles et reservations de couches

Objectif : passer d'un modele module-first a un modele asset-first avec
reservations non imprimables.

Capabilities liees : C-ASSET, C-RESERVATION.

Criteres de reussite : assets distincts des modules, dimensions approximatives
signalees, reservations verticales et XY documentees.

Statut P9-M001/P9-M002 : schema cible asset-first documente puis charge par le loader V0 comme donnees passives, sans derivation de modules.

## Phase 10 - Solveur semi-automatique et scoring

Objectif : proposer plusieurs variantes explicables et scorees.

Capabilities liees : C-SOLVER.

Criteres de reussite : scoring transparent, variantes refusees avec raison,
aucune dependance lourde sans ADR/gate.

## Phase 11 - Modules composites et formes soudees

Objectif : representer et generer des modules en L/T ou volumes soudes avec faces
internes sans jeu.

Capabilities liees : C-COMPOSITE.

Criteres de reussite : primitives soudees, roles internal/welded fiables,
generation CAD sous gate.

## Phase 12 - Couvercles, mecanismes et empilement avance

Objectif : ajouter couvercles poses/coulissants, rainures, clips, charnieres et
interfaces fonctionnelles.

Capabilities liees : C-STACKING, futurs mecanismes.

Criteres de reussite : jeux fonctionnels dedies, gates impression, risques
explicites.

## Phase 13 - Esthetique, embossage, gravure, textures, decorations

Objectif : ajouter un langage visuel parametrable sans casser la fonction.

Capabilities liees : C-AESTHETIC.

Criteres de reussite : features esthetiques optionnelles, desactivables,
compatibles epaisseur/impression.

## Phase 14 - Calibration, impression reelle, packaging et beta utilisable

Objectif : transformer les preuves abstraites/CAD en usage reel imprime et
distribuable.

Capabilities liees : C-CALIBRATION et release.

Criteres de reussite : protocoles de mesure, profils ajustes, exemples reels,
versioning et packaging utilisateur.

## Regle de progression

Une phase peut etre exploree avant la precedente si elle reduit un risque majeur,
mais elle ne doit pas etre declaree terminee sans :

- capability liee mise a jour ;
- tests ou validation documentaire ;
- statut clair dans `docs/STATUS.md` ;
- backlog mis a jour ;
- gates explicites ;
- limites de validation visibles.

## Update 2026-07-08 - P13 Asset input UI V0

P13-M001 ajoute un premier mode Fusion `quick_asset_box` pour saisir des assets simples depuis la commande Fusion, generer une config temporaire et reutiliser le pipeline asset-first existant. Cette avancee sert M14 Usable beta, sans palette persistante, sans solveur complexe et sans validation d'impression. Gate active : `P13-M001V`.

## Update 2026-07-10 - P18 product rebase

La trajectoire produit est recadree par docs/VISION_GAP_ANALYSIS.md, docs/VOLUMETRIC_PRODUCT_MODEL.md et docs/BOX_FILL_SOLVER_ROADMAP.md. Le prochain increment recommande est le plan manuel de boite complete, avant palette persistante ou solveur global.

## P19 completion addendum

P19 est complet contre son contrat autorise : cellules libres AABB exactes (`exact_aabb_cells_v0`), conservation de volume, diagnostics structures, coverage par asset, CLI `validate-box-fill` / `report-box-fill` / `export-box-fill-plan`, fixtures valide et invalides, bridge explicite `derived_from_executable_asset_plan` et transport CAD IR metadata. Les cellules decrivent le residuel et ne constituent pas un placement automatique. P20 greedy reste bloque par gate humaine ; Fusion ne recalcule ni ne materialise ce plan.
## P20 completion - 2026-07-10

Statut : `done`, `implemented-core`, `implemented-cli`, `implemented-cad-ir-metadata`. Le moteur `box_fill_greedy_2d.v0` produit un nouveau BoxFillPlan sans muter la source, respecte locks, modules manuels, reservations et layers, supporte la rotation XY 90 degres et expose diagnostics, digest, metrics, rapports JSON/Markdown, preview SVG et metadata CAD IR. Aucun backtracking, solveur global, UI persistante, geometrie Fusion ou validation d impression n est ajoute. P21 reste gate et recommande les variantes/scoring.
## P21 completion - 2026-07-10

Statut : `done`, `implemented-core`, `implemented-cli`, `implemented-cad-ir-metadata`. `box_fill_variants.v0` compare un petit portefeuille de placements P20 deterministes, deduplique les geometries, expose sous-scores, front Pareto, preference et recommandation. Markdown, JSON, dashboard HTML statique et export de selection CAD IR sont disponibles. Aucun solveur global, UI persistante, Fusion ou validation d impression n est ajoute. La prochaine gate est ADR-0036 : choisir la premiere surface UX persistante.
## P22 UX surface gate - 2026-07-10

Statut : `done-docs`, gate ADR-0036 active. Le rapport `docs/P22_UX_SURFACE_GATE_REPORT.md` recommande une app locale de conception avec Fusion comme adaptateur CAD/export. La trajectoire et le scope P23 sont documentes, mais aucune UI persistante, dependance majeure ou materialisation Fusion de selection n est autorisee sans validation humaine explicite.
## P23 local composer - 2026-07-10

Statut : `done`, `implemented-local-ui`, `implemented-loopback-adapter`, `print-validated: false`. La validation humaine de l option D est materialisee par ADR-0040 : une app React/Vite locale pilote un adaptateur Python loopback qui convertit un draft versionne en contrats moteur P20/P21 et en CAD IR metadata-ready. Le parcours boite -> assets -> reservations -> variantes -> selection -> export est utilisable sans Fusion. Aucune logique de solveur n est dupliquee dans TypeScript, aucune persistence serveur, materialisation Fusion ou validation d impression n est ajoutee. Prochaine mission : P24-M001, qualite des editions locales et erreurs actionnables.