# Roadmap

Cette roadmap decrit les phases macro jusqu'au produit cible. Le detail
operationnel vit dans `docs/BACKLOG.md`, l'etat courant dans `docs/STATUS.md`,
et la lecture par capabilities dans `docs/CAPABILITY_MAP.md`. La nomenclature
et le role de ces documents sont definis dans `docs/PILOTAGE_GLOSSARY.md`.

## Ordre canonique actif, amende par P67-V le 2026-07-14

Les phases historiques ci-dessous decrivent les briques construites, pas l'ordre
des prochaines missions. ADR-0047 et `docs/MVP_EXECUTION_PLAN.md` imposent :

1. P36-P42 puis P52-P60 : socle technique V0.1 observe ;
2. P60-R puis P61-P66 : convergence produit V0.1 revisee ;
3. P67 : atelier humain de priorisation post-MVP ; P68 : retours de vrais inserts ;
4. P44 : fondation UX ; P45 : formes et ergonomie geometrique ; P46 : gate V0.2 ;
5. P47-P50 : V0.3 couvercles et calibration ;
6. P69 : revue UI/UX exhaustive et cadrage humain des lots P70+.

Aucune mission P44+ ne peut devenir `ready` avant P66 puis P67. Aucune mission
P47+ ne peut devenir `ready` avant P46. P69 reste bloquee jusqu a P50.
Les explorations P33/P34 sont archivees et ne
valent pas acceptation de V0.2/V0.3.

La gate P67-V du 2026-07-14 accepte que P44 porte une
fondation UX bornee avant les geometries P45. Cette decision est documentee dans
ADR-0062 et le rapport P67. Seule P44-M001 devient `ready` ; les missions
suivantes gardent leurs dependances et P45/P46 restent bloques.

P43 est reouvert le 2026-07-12 : la scene Fusion historique reste observee,
mais le MVP produit n est pas accepte. P52 a P60 constituent le socle technique ;
P60-R a P66 ont ferme le chemin critique V0.1. P67-V rend P44-M001 ready ;
le reste de P44 suit ses dependances et P47 V0.3 reste bloque jusqu a P46.
ADR-0054 interdit les corps de remplissage
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
empreinte et aucun corps automatique n est cree.

## P64 implemente - 2026-07-13

Le package Fusion 0.1.15 implemente et durcit le solveur borne par etages de l ADR-0059 :
portefeuille XY deterministe, composition Z, rotations, appuis, ordre de retrait
et bilan de volume. `Auto`, `Cible` et `Fixe` sont des contrats par axe ; le
surplus est score selon la preference, sans revendication d optimalite globale.
Une proposition incomplete expose residuels et suggestion non mutante, puis est
bloquee avant materialisation Fusion. P63 ne coupe que les corps superieurs
intersectes. La validation Fusion du comportement P64 reste reportee a P66 ;
P65 devient ready.

Le durcissement runtime P64 ajoute des piles verticales hybrides bornees, une
revalidation des enveloppes consciente des rotations, la compensation de
profondeur utile des cavites sous les plateaux et des noms de corps Fusion
uniques. Les plans historiques gardent la priorite quand ils ferment deja le
volume ; aucune dependance externe ni corps automatique n est ajoute.

## P65 demarre - 2026-07-13

P65-M001 separe les jeux de placement X-Y et Z, avec heritage compatible pour
les projets existants. Le vide Z consomme la hauteur solvee et traverse la CAD IR.
La palette 0.1.16 rend la materialisation persistante a cote du recalcul, sans
autoriser une proposition partielle ou obsolete. Les travaux de lisibilite et d explication sont completes par P65-M003 et
P65-M004 ; P66-M000 devient la prochaine mission, avant P66-M001.

## P65-M002 implemente - 2026-07-13

P65-M002 rend independants le perimetre X-Y de boite, l ecart X-Y entre
conteneurs, l ecart Z entre etages et la marge Z superieure. La CAD IR 0.1.17
les expose sans creer de corps automatique. Les sketches de reference Fusion
sont conserves tagues/inspectables mais caches par defaut. La validation Fusion
et l impression reelle restent reportees a P66.

## P65-M003 implemente et automatise - 2026-07-13

Le contrat docs/P65_M003_FUNCTIONAL_CONTRACT.md definit la lecture canonique
des tailles dans Conteneurs : minimum derive, demande par axe Auto/Cible/Fixe,
taille calculee par le vrai plan, puis statut non calcule/a jour/perime/partiel/
impossible. Un CTA local Estimer les tailles reutilise solve_project, reste
dans Conteneurs et ne modifie ni sources, ni scene Fusion, ni CAD materialisee.

La palette 0.1.18 expose la projection Python bgig.container_sizing_view.v1 :
elle montre les minimums, demandes, tailles calculees uniquement depuis le plan,
surplus et raisons de contrainte par axe. Estimer les tailles reutilise le
solveur borne existant, interdit les executions concurrentes et ne materialise
rien dans Fusion. Les tests automatises, la syntaxe de palette et le dry-run
d installation sont verts ; la reteste Fusion reste reservee a P66.

Le lot n ajoute aucun solveur, ne change ni score, tolerances, cavites,
reservations, etages, ni corps automatique.

## P65-M004 implemente et automatise - 2026-07-13

La palette 0.1.19 consomme bgig.preview_explanations.v1, projection Python
additive du plan P64. Score comparatif, appuis, ordre de retrait, residuels et
suggestions sont traduits sans formule JavaScript ni code solveur visible.
Exporter les imprimables devient primaire dans Apercu ; Recalculer et
Materialiser restent les actions persistantes uniques correspondantes.

Le lot ne change ni solveur, score, tolerance, reservation, cavite, CAD IR,
scene Fusion ou corps automatique. La validation Fusion et l impression reelle
restent reservees a P66.

## Route bornee de P65 a l acceptation MVP

1. **P65-M003 - tailles et estimation** (`implemented`, 0.1.18) : minimum,
   demande, calculee et leurs etats explicites dans Conteneurs.
2. **P65-M004 - explications d Apercu** (`implemented`, 0.1.19) : traduire
   sous-scores, appuis, retraits, residuels et suggestions ; clarifier les
   actions finales sans toucher aux formules ou au solveur.
3. **P66-M000 - quarantaine des complements** (`done`, 0.1.20) : masquer
   les actions normales Bac vide, Bloc plein / cale et Separateur, conserver la
   compatibilite historique et ne changer ni solveur ni geometrie.
4. **P66-M001 - preparation automatisee** : produire le projet canonique sans
   complement, les CAD IR, le package installe, les marqueurs et la checklist ;
   ne laisser a l humain que les observations dans Fusion.
5. **P66-V - gate humaine Fusion-only** : verifier le parcours complet, les
   plateaux encastres, orientations, multi-etages, edition/invalidation,
   estimation/recalcul, materialisation/regeneration, export, scene BGIG unique
   et preservation des objets non-BGIG.
6. **P66-Hxx si necessaire** : corriger uniquement les ecarts observes, retester
   automatiquement puis rejouer la gate.

Un P66 vert accepte le MVP fonctionnel V0.1 avec `print-validated: false`. La
publication ou le tag de release constitue ensuite une decision humaine separee.
P44 ne demarre pas automatiquement : P67 doit d abord prioriser humainement V0.2.

## Cadrage d execution P66 - 2026-07-13

`docs/P66_TERRA_EXECUTION_CONTRACT.md` rend P66 delegable sans ouvrir le scope
produit : P66-M000 met les complements experimentaux en quarantaine ; P66-M001
prepare fixtures, preuves, package et checklist ; P66-V reste une observation
humaine ; un KO ouvre seulement un P66-Hxx atomique ; P66-CLOSE aligne le
pilotage apres un OK explicite.

## Sequence post-MVP acceptee - 2026-07-13

- **P67** : atelier humain cible pour redefinir priorites, perimetre et preuves
  avant d activer P44 ; il conserve les identifiants P44-P50.
- **P68** : boucle parallele de premiers inserts reels et mesures locales ; elle
  nourrit les decisions sans changer silencieusement les valeurs par defaut.
- **P44-P46 / V0.2** : fondation UX P44, geometries/resistance P45, puis gate Fusion P46.
- **P47-P50 / V0.3** : couvercles et calibration physique, apres P46.
- **P69** : revue UI/UX humaine exhaustive, tres commentee, apres P44-P50 ; elle
  produit le backlog P70+ et ne corrige rien dans la mission de revue.

P44 a P50 restent des identifiants canoniques : les renumeroter casserait les
liens documentaires sans apporter de valeur Git. Leur priorite est decidee par
les dependances et statuts, pas par l ordre numerique.

## P67-M000 - Revue UX structurelle capturee - 2026-07-14

La revue post-MVP identifie un risque de sequence : ajouter les champs de formes
et couvercles avant de stabiliser focus, densite, architecture d information et
cycle document augmenterait la dette. Le rapport P67 propose quatre espaces
Boite, Conteneurs, Reglages et Apercu, une composition Conteneur parent ->
Elements enfants et une fondation UX en P44 avant la geometrie P45.

Cette trajectoire est acceptee par la gate humaine P67-V.
ADR-0062 est `accepted`; seule P44-M001 est `ready`. P69 reste apres P50
comme audit
UI/UX exhaustif du produit enrichi. Les complements restent en quarantaine et
aucune capability, geometrie, valeur de tolerance ou validation physique ne
change.

## P67-V accepte - Fondation UX avant geometrie - 2026-07-14

Thomas accepte D67-01 a D67-11 et ADR-0062. P44 porte desormais la fondation
UX bornee ; P45 garde les formes et P46 la gate V0.2. Les complements restent
en quarantaine et P69 reste apres P50.

P44-M001 devient la seule mission `ready`. Les jeux herites puis surchargeables
X/Y/Z par plateau, livret, asset et conteneur sont une intention acceptee, mais
leurs roles physiques restent distincts. P44-M008 doit cadrer formules, defaults
et migration avant P44-M009. Aucun default, solveur, schema ou runtime ne change
pendant P67-V.

## P66-M001 gate-prepared - 2026-07-14

P66-M001 fige une fixture complete sans complement et une fixture impossible,
leurs preuves deterministes, le preflight CAD/Fusion, l installation du package
0.1.20 et la checklist humaine de 21 etapes. Le runtime, le solveur, les jeux et
la geometrie restent inchanges. P66-V est la prochaine et unique action : elle
reste humaine, `fusion-validated: false`, `print-validated: false`. P67 et P44
ne demarrent pas avant le retour P66 OK explicite.

## P66-CLOSE - MVP V0.1 accepte - 2026-07-14

Thomas a retourne `P66 Fusion OK 0.1.20 - commit 6e351bb`. Le MVP Fusion-only
V0.1 est donc `mvp-accepted`, `fusion-validated`, `print-validated: false`.
P67 devient `ready` comme atelier humain de priorisation ; P68 reste
`planned-after-p66`. P44-P50 conservent leurs identifiants et restent bloques
jusqu aux decisions P67 et aux dependances V0.2/V0.3. Aucun tag ou release ne
resulte de cette acceptance.

## P44-M002V2 - Correction avant poursuite de la fondation UX - 2026-07-14

Le package 0.1.22 reste trace comme implementation automatisee mais recoit un KO
UX humain sur la compacite. La trajectoire P44 est donc interrompue avant
P44-M003 pour une correction bornee hybride A+B dans le package 0.1.23.

P44-M003 ne redevient disponible qu apres la gate humaine P44-M002V. Aucun
schema, solveur, tolerance, geometrie, complement ou scene Fusion ne change dans
cette correction. Cette requalification protege la sequence UX avant geometrie.

## P44-M002V acceptée et orthotypographie française - 2026-07-14

Le package 0.1.23 reçoit la validation humaine de densité. P44-M003 redevient la
prochaine mission `ready` de la fondation UX.

À partir de P44-M003, tout nouveau texte utilisateur respecte le français
accentué. P44-M006 garde la responsabilité de l’audit exhaustif des textes
historiques, avec preuves UTF-8, anti-mojibake et validation Fusion. Cette
exigence reste une qualité de surface et ne modifie aucune sémantique métier.


## P44-M003 implémentée - Navigation UX 0.1.24 - 2026-07-14

P44-M003 livre quatre onglets primaires, retire Précédent/Suivant et réunit
Boîte/plateaux/livrets ainsi que Conteneurs/éléments sans changer les
collections source. L’interversion X/Y est locale : dimensions source pour
boîte, élément et plat, contrat complet de taille pour conteneur ; elle ne
déplace jamais une origine. La rotation historique est conservée hors du
parcours normal. Les changements restent UI-only et la gate P44-M003V est
requise avant P44-M004.


## P44-M003V acceptée et P44-M004 — 2026-07-14

La preuve humaine P44-M003V Fusion OK 0.1.24 - commit 7b71d01 ferme la gate de
navigation. P44-M004 réalise ensuite, dans le package 0.1.25, la projection UI
conteneur parent / contenus enfants et les modes de taille compatibles, sans
changer le modèle ni les capacités géométriques. P44-M004V devient la seule
prochaine preuve ; P44-M005 et les missions suivantes gardent leurs
dépendances. P45 reste après P44-V et print-validated: false.

## P44-M004V2 — correction de densité avant P44-M005

La revue 0.1.25 n’accepte pas la densité réelle, sans invalider le modèle de
composition. L’option humaine hybride C devient une correction bornée :
1180 px utiles, chrome compact, barre unique, grilles techniques horizontales,
actions secondaires en menus et calculs repliés. Le package cible est 0.1.26.

La gate P44-M004V2 remplace la preuve de densité attendue avant P44-M005.
Aucune étape géométrique, de tolérance, de CAD ou d’impression n’est avancée.

## P44-M004V2H01 — ajustements de gate 0.1.27

Le retour 0.1.26 accepte la direction hybride C. Un hotfix 0.1.27 rend les deux
barres de création collantes sous les onglets et transforme les messages globaux
en toasts temporisés. P44-M005 reste bloquée jusqu’à la nouvelle observation
Fusion.

## P44-M004V2 acceptée — 2026-07-15

La preuve humaine "P44-M004V2 Fusion OK 0.1.27 - commit 80c1a6c" ferme la gate UX de la densité hybride C dans le
package 0.1.27. La validation est limitée aux cartes compactes parent / enfants,
aux contrôles collants et aux notifications temporisées ; elle ne fait avancer
ni géométrie, ni tolérance, ni CAD, ni impression.

P44-M005 devient la prochaine mission ready-for-explicit-go. Elle reste
strictement non commencée tant que Thomas ne donne pas le GO.

## P44-M005 — création pilotée 0.1.28

P44-M005 compacte la création sans modifier le modèle : preset unique,
destination explicite, ajout local et gestion locale des presets personnels.
Les compléments restent hors parcours. La gate P44-M005V doit observer cette UX
dans Fusion avant P44-M006 ; aucune capability géométrique ou physique n’avance.

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


## P44-M006 acceptée — gate Fusion 0.1.30

Preuve humaine : P44-M006 Fusion OK 0.1.30 - commit d82def6. Le cycle document,
la récupération locale, les réglages visibles et le diagnostic replié sont
fusion-validated. P44-M008 devient la prochaine mission ready-for-explicit-go ;
P44-M007 reste bloquée par P44-M009. print-validated: false.

## P44-M008 - Proposition du contrat de jeux herites - 2026-07-15

P44-M008 formalise sans code trois roles : asset-cavite, plat-encastrement et
conteneur externe. Heritage par axe, zero explicite, sources effectives et max
pour la paire de conteneurs sont proposes. La gate humaine formules/defaults/
migration est ouverte. P44-M009 et P44-M007 restent bloques.

## P44-M009 - Tolerances par role implementees (2026-07-16)

P44-M009 implemente l option B dans le package 0.1.31 : trois roles, heritage
par axe, zero explicite, provenance et deux vecteurs externes. Compatibilite
historique preservee et paires resolues par maximum, jamais somme. La mission
ne qualifie ni Fusion ni impression : fusion-validated: false,
print-validated: false. P44-M007 est la prochaine mission sur GO explicite.

## P44-M009H01 - Correction UI avant calcul adaptatif (2026-07-16)

Le retour humain sur la 0.1.31 demande une correction bornée avant P44-M007 :
les jeux unitaires quittent les lignes principales, rejoignent des volets
repliés et utilisent un seul champ X/Y plus un champ Z distinct. Le package
cible est 0.1.32. Le modèle X/Y/Z reste intact pour la rétrocompatibilité ;
aucune valeur ni formule n’est recalibrée.

Observation Fusion acceptée le 2026-07-16 : P44-M009H01 Fusion OK 0.1.32 -
commit 8fc5157. P44-M007 redevient ready-for-explicit-go. Le premier détail
borné de cette mission rendra « Hauteur de conception » visiblement grisée dans
Réglages, sans modifier son statut dérivé ni les calculs. P44-V reste la gate
globale de fondation UX.

## P44-M009H02 - Correction fonctionnelle des jeux (2026-07-16)

Le retour Fusion postérieur à P44-M009H01 révoque sa validation fonctionnelle :
les champs globaux modifiaient les scalaires historiques sans synchroniser les
defaults par rôle, et la palette pouvait afficher des valeurs effectives
périmées. Le package 0.1.33 synchronise ces deux représentations, lit le dernier
résultat dérivé et prouve l’isolation sur deux assets et trois conteneurs.

Les formules de l’ADR-0063 ne changent pas. P44-M007 reste bloquée jusqu’à la
gate P44-M009H02V ; P44-V reste la gate globale.

## P44-M009H03 - Simplification globale des jeux de conteneurs (2026-07-16)

La revue produit remplace la correction H02 par une simplification de contrat : les jeux entre conteneurs et conteneur-boîte sont des réglages globaux du projet, jamais des propriétés éditables d’un bac. ADR-0064 remplace cette partie de l’ADR-0063 sans supprimer les données historiques.

Le package 0.1.34 retire le volet de jeu externe des cartes, conserve les overrides asset et plateau/livret, et réorganise Réglages en tableau dense X/Y–Z. P44-M007 reste bloquée jusqu’à la gate P44-M009H03V ; P44-V reste la gate globale de fondation UX.

## P44-M009H04 - Consolidation de densité UI (2026-07-16)

Le package 0.1.35 ferme les écarts visuels observés sur 0.1.34 sans rouvrir le contrat de tolérance : largeur utile bornée dans Réglages, composition gauche compacte et dimensions de conteneur intégrées dans l’en-tête en Cible/Fixe.

P44-M009H03V est remplacée par P44-M009H04V. P44-M007 reste bloquée jusqu’à cette preuve ; P44-V demeure la gate globale.

## P44-M009H05 - Distribution finale des contrôles conteneur (2026-07-16)

Le package 0.1.36 sépare visuellement l’identité à gauche des contrôles à droite et intègre le mode global dans la ligne Conteneurs. Son état devient fidèle aux cartes et son application couvre les trois axes de chaque conteneur.

Preuve humaine acceptée le 2026-07-16 : P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0. P44-M007 devient ready-for-explicit-go ; P44-V demeure la gate globale et print-validated: false.

## P44-M007 - Calcul adaptatif et Aperçu priorisé (2026-07-16)

Le package 0.1.37 orchestre la palette en deux temps : dérivations à 350 ms puis proposition complète à 1 500 ms de stabilité. Les réponses dépassées ne peuvent plus remplacer l’état courant, même entre deux requêtes du même type et de la même révision. `Recalculer maintenant` reste le fallback explicite.

L’Aperçu présente désormais son statut et ses projections réelles avant les alertes et détails. `Matérialiser dans Fusion` reste unique, persistant et strictement manuel ; `Hauteur de conception` reste dérivée, grisée et non éditable. Aucun schéma, solveur, budget, valeur physique, tolérance, géométrie ou contrat CAD ne change.

Statut : implemented, automated-validated, human-fusion-check-required par P44-M007V, fusion-validated: false, print-validated: false. P45/P46 et les lots ultérieurs restent verrouillés jusqu’aux gates P44 prévues.

## P44-M007H01 - Correction de saisie et clarification cartes/conteneurs (2026-07-16)

Le package 0.1.37 a échoué la vérification humaine de saisie rapide : chaque
réponse d’autosave, validation ou solve reconstruisait le DOM et pouvait retirer
focus ou sélection. Le package 0.1.38 sépare désormais les mises à jour de fond
du rendu structurel, diffère la peinture dérivée pendant une édition et conserve
les doubles gardes de réponses obsolètes.

Le même lot borné clarifie la méthode de mesure des cartes, rend les deltas
sleeves X/Y et Z explicites sans migration des anciens projets, et transforme
les conteneurs en sections repliables à en-tête permanent.

Statut : implemented, automated-validated, human-fusion-check-required par
P44-M007H01V, désormais supersédée par P44-M007H02V, fusion-validated: false,
print-validated: false. Aucun lot P45/P46, P47-P50, P67, P68 ou P69 n’est ouvert.

## P44-M007H02 - Mesure cartes et sleeves cohérents (2026-07-16)

Le package 0.1.39 finalise le correctif P44-M007 avant sa gate Fusion. Le preset
`Cartes` devient non sleevé par défaut, la méthode de mesure rejoint la droite
de la ligne principale et seuls les champs actifs restent visibles.

Les sleeves proposent 3 mm au total sur X/Y et 0,19 mm par carte sur Z dans les
deux méthodes. En épaisseur paquet, une estimation grisée utilise 0,31 mm par
carte et le Z résolu ajoute le delta par carte sans jamais cumuler la surcharge
au roundtrip.

Statut : implemented, automated-validated, human-fusion-check-required par
P44-M007H02V, fusion-validated: false, print-validated: false. La gate H01 est
supersédée. Les dispositions d’assets non-cartes restent dans P45 après P44-V ;
aucun solveur de placement, tolérance, géométrie ou comportement de scène n’est
modifié ici.

## P44-M007H03 - Résolution cartes et repli global cohérents (2026-07-16)

Le package 0.1.40 corrige le KO contextuel observé sur 0.1.39 : les cartes
manuelles appliquent réellement le delta sleeve X/Y sans cumul, `Nb cartes`
reste dérivé du Z déclaré et les faits anciens sont remplacés par
`À recalculer` pendant le cycle adaptatif. Les contrôles cartes sont resserrés,
les modes de densité obsolètes disparaissent et les conteneurs gagnent un repli
global en plus du repli individuel.

Statut : implemented, automated-validated, fusion-validated: true,
print-validated: false. Preuve Fusion reçue le 2026-07-16 :
`P44-M007H03 Fusion OK 0.1.40 - commit 92f07c8`. Aucun solveur de placement,
valeur physique, tolérance, géométrie, CAD IR ou comportement de scène n’est
modifié. P0-M010 devient la prochaine mission documentaire ; P45 reste bloqué.

## P0-M010 - Pilotage de reprise compact (2026-07-16)

La maintenance documentaire isole un point de reprise court, synchronisé et auditable. Elle ne réécrit pas l’historique : elle distingue le résumé actif, les sources canoniques de détail et les preuves archivées. Le prochain lot est P44-VP, préparation documentaire de la gate globale P44 ; P45 demeure bloqué jusqu’à P44-V. Aucun comportement produit ou physique ne change.

## P44-VP - Préparation de la gate globale P44 (2026-07-16)

Le package 0.1.40 de référence `92f07c8` reçoit un dossier et une préparation Fusion reproductible. La prochaine étape est P44-V ; P45 reste bloqué. Aucun comportement produit ou physique ne change.


## P44-VH01 - Cohérence Z et reprise multi-étages (2026-07-16)

Le KO contextuel P44-V a révélé une divergence de données dans la palette : Z et la hauteur affichée changeaient sans mettre à jour box.usable_height_mm. Le package 0.1.41 synchronise cette hauteur dérivée avant calcul et persistance, sans modifier le solveur volumétrique. Le cas initial est observé comme calculable ; P44-VH01V est supersédée par P64-H01V sans revendication fusion-validated.

Après P64-H01V, P44-VH02 traite uniquement la suppression directe, la confirmation de suppression d’un conteneur non vide et les noms incrémentaux. P44-V reste ouverte et P45 demeure bloqué. print-validated: false.


## P64-H01 - Durcissement dense et équilibre X/Y/Z (2026-07-17)

Le retour sur le projet réel confirme P44-VH01 mais révèle que les partitions
contiguës de P64 peuvent encore produire un faux impossible à forte densité et
que balanced attend trop longtemps avant d'utiliser Z. Le package 0.1.42 ajoute
une recherche adaptative bornée et fait de l'expansion X/Y/Z avec charge
d'étages un critère explicite. Les étages progressent avec la densité sans
modifier le mode compact, les contraintes physiques ou le schéma.

P64-H01 est fusion-validated par `P64-H01 Fusion OK 0.1.42 - commit 5865645`.
P44-VH02 devient le seul lot de code suivant ; P45 demeure bloqué.
print-validated: false.


## P44-VH02 - Suppression directe et noms incrementiels (2026-07-17)

Le package 0.1.43 ajoute la suppression visible des elements, la confirmation atomique des conteneurs non vides et le suffixage des noms dupliques. P44-VH02V est la seule gate humaine suivante ; P44-V reste ouverte et P45 reste bloque. print-validated: false.
## P64-H02 — Reprise diversifiée après validation (2026-07-17)

Le package 0.1.44 conserve les quatre ordres canoniques et toute la logique
P64-H01. Seulement après un cul-de-sac, il peut essayer jusqu’à six ordres
hash-diversifiés, un par portefeuille, puis réapplique sans relâchement les mêmes
contrats d’enveloppe, cavité, support et réservation. Le cas exact de 8 conteneurs
et deux réservations supérieures construit désormais deux niveaux. La correction
P44-VH02H01 réunit également `...` et la croix dans la même cellule d’action.

P64-H02V reçoit ensuite un KO contextuel sur un nouveau faux impossible. Aucune
preuve Fusion OK n'est revendiquée ; P64-A01 puis P64-H04 remplacent cette
trajectoire. P44-V et P45 restent bloqués. `fusion-validated: false`,
`print-validated: false`.

## P64-A01 — Portefeuille multi-solveurs et finitions (2026-07-17)

Le solveur par étages reste le chemin rapide, mais les KO contextuels P64-H02 et
P64-H03 interdisent de continuer par simple ajout de seeds. H03R conserve toutefois
les gains déjà observés ; ADR-0068 introduit un contrat commun, un greedy 3D
EP/EMS, un beam robuste et un portefeuille Auto.
ADR-0069 reporte la finition continue et modulaire après la faisabilité.

Chemin critique avant reprise de P44-V : P64-H04/H05/H06 intégrés (vérité,
observabilité, contrat/baseline et greedy 3D EP/EMS), P64-H07 beam/portfolio intégré dans 0.1.50,
P64-H08 intégré dans 0.1.51 ; P64-V2 0.1.51 est ensuite un KO contextuel.
P64-V2H01 0.1.52 devient la gate corrective. P45/P46 reprennent seulement
après P64-V2H01 et une P44-V positive.

Le sous-ensemble de fermeture P64-F01 nécessaire au certificat est avancé
dans P64-V2H01. Le reste de P64-F01 et P64-F02 est planifié après P46 afin
de ne pas gonfler le chemin critique V0.2 ; elles précèdent les finitions plus physiques. P64-F03 attend des retours
d'impression pertinents. P64-X01 exact reste après benchmark, ADR de dépendance
et GO distinct. Le contrat exécutable est
`docs/P64_MULTI_SOLVER_PORTFOLIO_PROGRAM.md`.
### Avancement P64-H07 — package 0.1.50

Le beam 3D, les efforts monotones, la reconstruction certifiée et le
portefeuille Auto interne sont intégrés. P64-H08 rend ces contrôles visibles
dans Fusion 0.1.51 ; P64-V2H01 remplace la gate après le KO contextuel 0.1.51.

### Avancement P64-H08 — package 0.1.51

Méthode, effort et critères mesurés sont exposés comme préférences locales dans
la palette Fusion. Le diagnostic secondaire rend méthode/effort/famille/temps
observables, sans changer les dimensions ni matérialiser automatiquement. P64-V2 0.1.51 a ensuite reçu un KO contextuel ; la gate corrective est
P64-V2H01. P44-V, P45 et P46 restent verrouillés.

### Avancement P64-V2H01 — package 0.1.52

Le KO réel révèle que le beam gonflait les enveloppes pendant la faisabilité et
que le résiduel était rejeté avant une fermeture. La correction place d'abord
les minima, traite plateau/livret comme contraintes conditionnelles, puis ferme
les axes Auto/Cible avant le certificat commun.

Le cas anonymisé réel distingue maintenant les méthodes : Étages et piles reste
sans solution dans son budget ; Placement 3D libre et Auto certifient 9 corps
sur plusieurs niveaux. L'alignement de faces progresse, mais l'harmonisation
modulaire P64-F02 reste future. La seule étape ouverte est la gate Fusion
P64-V2H01 0.1.52.

### Avancement P64-V2H02R — package 0.1.54

Le cas réel étendu invalide la gate P64-V2H01 0.1.52 sans supprimer ses gains.
P64-V2H02 corrige les faux blocages d'enveloppes multi-cavités, d'EMS, de points
extrêmes et de réservations localisées. Il rend les budgets d'effort réellement
croissants, publie une borne de capacité sur chaque résultat et corrige
l'occlusion de la vue de dessus. La preuve Fusion `P64-V2H02R Fusion OK 0.1.54 - commit 42e8993` confirme aussi le repère Y retourné autour de l'axe X.

La marge volumique positive du projet dense ne suffit pas à prouver une
configuration orthogonale. Le package reste honnêtement non certifié sur ce cas
et prépare deux trajectoires distinctes : P64-V2H03 pour des variantes internes
bornées coordonnées avec P45, et P64-X01 pour un éventuel mode exact sous ADR et
benchmark. P64-U01 portera ultérieurement une progression non modale et annulable.

P64-V2H02R est clôturée. L'arbitrage P64-V2H03A / P45 est maintenant accepté ;
P44-V, P45 et P46 restent verrouillées ; aucun défaut, tolérance, schéma ou comportement de matérialisation
n'est modifié. `print-validated: false`.

## P64-V2H03A — Frontière P45/P64 acceptée (2026-07-18)

ADR-0070 fixe la coordination des variantes internes. P45 reste propriétaire
des modes de disposition, formes et certificats locaux. P64 consomme une petite
frontière de variantes certifiées, choisit variante et placement sous des lanes
bornées, puis réapplique le certificat global.

La séquence corrective devient : P64-V2H03B pour types, certificats, fixtures et
caps ; P64-V2H03C pour sélection globale et télémétrie ; P64-V2H03V seulement si
une observation Fusion est requise. P44-V et P45 restent bloquées pendant ce
chemin. Aucune valeur physique, tolérance, default, scène ou preuve d'impression
ne change.

## P64-V2H03B — Frontière locale implémentée (2026-07-18)

La frontière locale ADR-0070 est exécutable dans le cœur Python : canonique,
relayout rectangulaire, digest, certificat fail-closed, provenance, Pareto et
caps monotones. Les fixtures 1 à 8 incluent le mécanisme anonymisé 11 × 34.

H03C devient `ready`. Aucun résultat public, schéma, UI, default, jeu
externe, valeur physique ou état Fusion n'est modifié.
`print-validated: false`.

## P64-V2H03C — Sélection globale implémentée (2026-07-18)

La frontière locale H03B est consommée après le portefeuille canonique complet.
Le beam développe variante et placement dans un même état borné, les lanes
Quick/Normal/Deep restent préfixées et le certificat produit commun est complété
par un certificat global de sélection. Le diagnostic secondaire porte budgets,
compteurs, digests, rejets et arrêt sans ajouter de contrôle à la palette.

Le cul-de-sac multi-cavités minimal et la réservation localisée sont résolus ;
les succès canoniques restent sur leur fast path. Le mécanisme dense 11 × 34
reste `no_solution_within_budget` jusque dans la lane Deep : H03C augmente la
capacité de recherche sans promettre qu'un volume positif implique une
disposition.

P64-V2H03V devient `ready` car le résultat visible peut changer. Cette gate ne
calibre aucune valeur et ne vaut pas impression. Les futures formes restent la
propriété de P45 ; un éventuel solveur exact reste P64-X01 sous ADR et benchmark
distincts.

## P64-V2H03V — Gate Fusion préparée (2026-07-18)

Le package 0.1.55 projette la trace H03C dans un diagnostic secondaire replié et
fournit une fixture variantes plus un contrôle canonique. Le préflight confirme
la solution du cul-de-sac minimal, deux variantes non canoniques certifiées et
la non-régression `stage_stack`, sans scène automatique.

La trajectoire attend maintenant l'observation humaine H03V. Elle ne valide ni
le cas dense, ni une valeur physique, ni P45, ni l'impression. Aucune mission
runtime suivante n'est ouverte avant le retour explicite.


## P64-A02 — Trajectoire de calcul étagé et capacité réutilisable (2026-07-21)

P64-A02 ajoute une trajectoire contractuelle sans court-circuiter la gate H03V.
Le produit cible ne relance plus silencieusement tout le solveur après chaque
frappe. Il maintient des analyses locales cachables, lance l'agencement global
sur action explicite, puis finalise séparément le volume restant avant
matérialisation.

### Macro-phase L — calcul incrémental et solve explicite

- L01 introduit les états, digests, dépendances et caches sans modifier encore
  l'UX publique ;
- L02 produit les frontières locales, scores décomposés, compatibilité
  sous-plateau et shortlist repliée ;
- L03 rend le solve global explicite et introduit le plan finalisable ;
- L03V observe dans Fusion la stabilité, les invalidations et l'absence de scène
  automatique.

### Macro-phase F — finalisation choisie

- F01 distribue simplement le résiduel autour des enveloppes, avec fallback exact ;
- F02 ajoute équilibrage absolu et proportion relative, puis l'harmonisation
  modulaire si P45/P46 l'autorisent ;
- F03 propose des cales explicites seulement après données physiques suffisantes.

### Macro-phase C — capacité post-solve réutilisable

- C01 détecte et affiche en lecture seule les opportunités internes et baies
  réservées ;
- C02 permet une insertion locale d'asset lorsque l'enveloppe monde ne change
  pas, puis recertifie tout le plan ;
- C03 permet un nouveau conteneur seulement dans une baie de boîte réservée ;
- CV vérifie les parcours Fusion, le fallback vers solve global et l'absence de
  création automatique.

Séquence : H03V et sa clôture, P44-V, P45-M001, L01, L02, L03/L03V, P45/P46,
F01, F02, C01/C02, F03, C03/CV. Cette séquence peut être replanifiée par une ADR
ultérieure, mais aucune carte runtime n'est ouverte par P64-A02.


## P64-V2H03V — Gate Fusion validée (2026-07-21)

Le retour `P64-V2H03V Fusion OK 0.1.55` clôt la trajectoire corrective H03.
La coordination P45/P64, la frontière locale, la sélection globale paresseuse et
leur diagnostic Fusion sont validés pour ce périmètre. La suite ne traite pas le
cas dense comme résolu : il reste no_solution_within_budget.

Le chemin critique revient à P44-V, qui doit être requalifiée avant l'ouverture
de P45. Les programmes P64-A02 restent une architecture future, pas un
changement runtime déjà validé. print-validated: false.


## P44-V - Preparation de requalification 0.1.55 (2026-07-21)

La gate globale P44 est preparee sur 0.1.55 apres P64-V2H03V. Cinq observations Fusion couvrent saisie, repli, import dense, scene preservee et materialisation explicite. P45 reste bloque.
