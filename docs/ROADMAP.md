# Roadmap

Cette roadmap decrit les phases macro jusqu'au produit cible. Le detail
operationnel vit dans `docs/BACKLOG.md`, l'etat courant dans `docs/STATUS.md`,
et la lecture par capabilities dans `docs/CAPABILITY_MAP.md`.

## Ordre canonique actif depuis le 2026-07-12

Les phases historiques ci-dessous decrivent les briques construites, pas l'ordre
des prochaines missions. ADR-0047 et `docs/MVP_EXECUTION_PLAN.md` imposent :

1. P36-P42 puis P52-P60 : socle technique V0.1 observe ;
2. P60-R puis P61-P66 : convergence produit V0.1 revisee ;
3. P44-P46 : V0.2 formes et ergonomie ;
4. P47-P50 : V0.3 couvercles et calibration.

Aucune mission P44+ ne peut devenir `ready` avant P66. Aucune mission P47+ ne
peut devenir `ready` avant P46. Les explorations P33/P34 sont archivees et ne
valent pas acceptation de V0.2/V0.3.

P43 est reouvert le 2026-07-12 : la scene Fusion historique reste observee,
mais le MVP produit n est pas accepte. P52 a P60 constituent le socle technique ;
P60-R a P66 portent desormais le chemin critique V0.1. P44 V0.2 et P47 V0.3
restent bloques jusqu a P66. ADR-0054 interdit les corps de remplissage
automatiques et impose l expansion des bacs demandes.

ADR-0055 impose aussi la surface produit : add-in Fusion et palette embarquee uniquement.
Les references Studio web des phases historiques sont supersedees.

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
## P24 project quality - 2026-07-10

Statut : `done`, `implemented-local-ui`, `implemented-validation`, `print-validated: false`. L app locale permet une allocation explicite de plusieurs assets par module et intercepte les erreurs de draft avant l appel moteur. L import est structurellement filtre, le moteur reste autoritaire et le schema V0 reste compatible. P25 doit rendre le demarrage plus guide avec des templates locaux, sans cloud ni nouveau solveur.
## P25 guided starters - 2026-07-10

Statut : `done`, `implemented-local-ui`, `implemented-loopback-adapter`, `print-validated: false`. Le Studio presente trois drafts V0 locaux et verifies pour demarrer un jeu de cartes, une boite mixte ou une boite avec plateau. Chaque modele traverse l adaptateur Python et P21 ; aucun catalogue distant, compte, stockage serveur, IA ou nouveau solveur n est ajoute. P26 doit rendre les mesures et limites visibles avant generation.

## P26 generation readiness - 2026-07-10

Statut : `done`, `implemented-local-ui`, `implemented-validation`, `print-validated: false`. Le Studio derive un resume novice de la saisie locale : assets, allocations, candidats, reservations, layers et corrections. Il ne recalcule pas P21 et ne promet aucune validation physique. P27 doit rendre les compromis des sorties P21 encore plus lisibles sans modifier leur calcul.

## P27 proposal explanations - 2026-07-10

Statut : `done`, `implemented-local-ui`, `print-validated: false`. Les sorties P21 sont traduites en intention, cas de choix, compromis et sous-scores lisibles, avec trace moteur progressive. Aucun calcul P21 ne change. Le prochain jalon est P28, gate humaine obligatoire avant materialisation Fusion d une selection explicite.

## P28 Fusion selection bridge - 2026-07-11

Statut : `implemented-cad-ir-selection-bridge`, `technical-path-observed`, `product-ux-rejected`, `print-validated: false`. La selection locale P21 devient une liste de composants CAD IR `rectangular_blank` que l add-in Fusion existant sait deja lire. Les dimensions et positions sont copiees depuis le plan resolu ; aucun score, placement, tolerance, cavite ou paroi n est invente. Le retour humain P28 rejette ce resultat comme experience produit ; P31 doit le remplacer par de vrais bacs avant toute nouvelle preuve Fusion.
## P29 product recovery - 2026-07-11

Statut historique : superseded-for-mvp par ADR-0055. Cette tranche avait retenu Studio local principal / palette secondaire ; elle ne pilote plus le produit.
## P30 living Studio - 2026-07-11

Statut : `implemented-local-ui`, `browser-inspection-pending`, `print-validated: false`. La direction `Atelier de rangement` est implementee : parcours progressif, boite centrale mise a jour en direct, propositions explicables, controles experts replis et etat de fabrication lisible. Le moteur, le schema V0 et la frontiere Fusion ne changent pas. P31 reste une gate : choisir la strategie de vrais bacs avant de remplacer les blanks P28.
## P31 functional tray gate - 2026-07-11

Statut : `implemented-cad-ir-open-top-trays`, `fusion-validated`, `print-validated: false`. Le premier bac recommande conserve exactement l enveloppe P21 et retire une cavite unique ouverte par le haut avec parois et fond issus des defaults existants. Ce scope ne change ni score, ni placement, ni tolerance ; il reporte compartiments, encoches, formes et mecanismes. La prochaine action est le smoke Fusion P31.
## P31 open-top trays - 2026-07-11

Statut : `implemented-cad-ir-open-top-trays`, `fusion-validated`, `print-validated: false`. Les selections Studio/P21 exportent maintenant de vrais bacs ouverts avec parois, fond et cavite unique. Les compromis P21, defaults, Fusion comme adaptateur et limites de fabrication restent explicites. Le smoke Fusion P31 est accepte ; P32 peut construire la palette Fusion secondaire.
## P32 Fusion palette - 2026-07-11

Statut : `implemented-fusion-palette`, `fusion-smoke-required`, `print-validated: false`. La palette locale `Atelier de rangement` devient l ouverture normale de l add-in. Elle garde Fusion dans son role secondaire : lire le design deja prepare, inspecter la scene, appliquer une mise a jour explicite et exporter. Le dialogue CommandInputs demeure disponible uniquement sous `Reglages experts`. Les tests hors Fusion sont passes ; la validation P32 attend une observation humaine de la palette et de son bridge.

## P32 Fusion palette smoke - 2026-07-11

Statut : `done`, `fusion-validated`, `print-validated: false`. Retour humain `P32 Fusion OK`. La palette concise est acceptee comme surface Fusion secondaire pour previsualiser, mettre a jour et exporter une scene deja resolue. Le dialogue CommandInputs reste un recours expert. P33 peut maintenant implementer les premiers reglages de forme et d esthetique dans le Studio, sans transformer Fusion en outil de conception.

## P33 forme et apparence - 2026-07-11

Statut : `implemented-studio-preview`, `browser-inspection-pending`, `print-validated: false`. Le projet transporte maintenant une apparence versionnee V0 : theme, labels, typographie, coins, biseau et prise symbolique. Le Studio la rend vivante sans modifier le solveur ni la geometrie de fabrication. Les finitions Fusion restent explicitement non materialisees. P34 doit passer une gate humaine avant de representer un couvercle, une rainure ou un clip.

## P34 sliding lid coupon - 2026-07-11

Statut : implemented-cad-ir-coupon, implemented-fusion-adapter, fusion-smoke-required, print-validated: false. Apres le choix humain C, P34-M001 livre le contrat et P34-M002 ajoute un coupon hors boite : bac ouvert + capot unique avec deux glissieres jointes. Le solveur, les tolerances globales et les bacs ranges restent inchanges. Le smoke Fusion doit observer les deux joins avant P35 impression/mesures.

## Rebase P54-R - Vrai MVP Fusion-only

Statut : accepted-product-direction.

ADR-0055 supersede le chemin Studio web principal. L add-in Fusion est le produit
unique et sa palette embarquee devient l editeur complet. Le coeur Python reste
CAD-agnostic ; la palette appelle ce coeur et l adaptateur adsk materialise.

Le frontend React/Vite, le serveur loopback et P23-P30 restent des prototypes
historiques non packages. P56-P60 suivent maintenant : editeur palette, solveur
pur, resultat palette, scene fidele, acceptance Fusion end-to-end.
## P59 implemente - 2026-07-12

La materialisation Fusion-only derive maintenant la CAD IR du plan P57 reel,
avec correspondance exacte des corps demandes, cavites P55 fixes, zero filler
automatique et synchronisation de scene possedee. P60 devient l unique gate de
sortie V0.1 ; les V0.2 et V0.3 restent bloquees jusqu a son acceptation.

## P60 UX 0.1.9 et suite structurelle

La finition V0.1 rend les presets, les corps pleins et les dimensions finales de
bac accessibles dans la palette Fusion. Apres acceptation P60, P61 introduira
par ADR un empilement vertical explicite avant les formes ergonomiques P44-P46.
Les couvercles P47-P50 restent bloques jusqu a P46.

## Rebase P60-R - Convergence produit V0.1 revisee

La revue humaine du 2026-07-12 classe P60 `product-review-ko` tout en conservant
ses preuves techniques. Le simple ajout d un nombre de bacs en hauteur est
refuse : le solveur P57 reste XY, place tout a Z = 0 et reduit tous les
conteneurs sous une pile globale de plateaux.

Le nouveau chemin critique est strictement sequentiel :

1. P60-R : contrats, alternatives, ADR et pilotage ;
2. P61 : etat reactif, diagnostics discrets et architecture de palette ;
3. P62 : catalogue local, sleeves et orientations de rangement ;
4. P63 : reservations superieures encastrees pour plateaux/livrets ;
5. P64 : solveur volumetrique borne par etages ;
6. P65 : Conteneurs, Reglages et Apercu integres ;
7. P66 : acceptance humaine du vrai MVP revise dans Fusion.

P61-P65 ne deviennent pas `ready` avant acceptation des ADR structurelles qui
les concernent. Aucune dependance de solveur externe, valeur de tolerance ou
forme ergonomique V0.2 n est ajoutee par ce rebase.

## P61 implemente - 2026-07-12

Le package Fusion 0.1.10 implemente les etats source/derive/solve/materialise,
l invalidation explicable, l ancien Apercu grise, les diagnostics techniques
replies, le parcours renomme et les densites Compact/Detaille. Il ne modifie ni
le solveur P57, ni les reservations P40, ni les tolerances. P62 devient ready.

## P62 implemente - 2026-07-13

Le package Fusion 0.1.12 implemente le catalogue local de cartes, sleeves,
epaisseur mesuree ou comptee, orientations a plat/debout/auto, dimensions
physiques et resolues ainsi que les presets personnels locaux exportables.
Le solveur global reste P57 : P62 corrige ses entrees de cavite mais ne revendique
ni reservations superieures P63 ni empilement multi-etages P64. P63 devient ready.


## P63 implemente - 2026-07-13

Le package Fusion 0.1.13 implemente les reservations superieures localisees :
empreintes descendantes, composition des plats qui se chevauchent, ordre de
retrait, appui, prise rectangulaire, non-percement, vues et operations CAD
IR/Fusion distinctes. Les corps demandes conservent leur hauteur complete hors
empreinte et aucun corps automatique n est cree. La validation Fusion reste
reportee a P66 ; P64 devient ready.
