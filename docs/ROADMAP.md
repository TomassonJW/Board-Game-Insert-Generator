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

P44-M009H04V est remplacée par P44-M009H05V. P44-M007 reste bloquée jusqu’à cette preuve ; P44-V demeure la gate globale.
