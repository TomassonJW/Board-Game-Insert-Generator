# Status

Derniere mise a jour : 2026-07-04

## Etat global

Statut produit : **V0 fondateur experimental**.

Le depot contient deja un coeur Python minimal et testable hors Fusion 360. La
mission du 2026-07-03 a ajoute le systeme de pilotage projet : protocole Codex,
roadmap macro, backlog actionnable, prochaines actions, index ADR/logs et
templates GitHub.

La mission d'autonomie operatoire du 2026-07-03 ajoute une couche de controle
plus stricte : protocole d'autonomie, boucle d'execution, gates humaines, matrice
de validation, roles logiques, plan de sprint et runbook humain.

La mission `P0-M002` du 2026-07-03 ajoute une verification documentaire de base
dans la suite unitaire afin de detecter les fichiers de pilotage critiques
manquants et les sections minimales absentes.

La mission `P0-M005` du 2026-07-03 stabilise le format des ADR avec un template
dedie et un index de decisions plus prescriptif.

La mission `P1-M001` du 2026-07-03 consolide le contrat des dataclasses coeur :
les objets restent des value objects legers en millimetres, avec validation
agregee dans `validation.py`.

La mission `P1-M002` du 2026-07-03 durcit le loader JSON V0 : champs inconnus et
types invalides sont refuses avec des erreurs `ConfigError` actionnables.

La mission `P1-M003` du 2026-07-03 enrichit les rapports Markdown/JSON avec un
resume de diagnostic, les parametres de layout, les demandes de modules et les
valeurs de tolerance principales.

La mission `P1-M004` du 2026-07-03 ajoute la commande CLI `diagnose`, qui charge
une configuration, genere le layout et verifie la production des rapports
Markdown/JSON.

La mission `P2-M001` du 2026-07-03 formalise le contrat de layout rectangulaire
simple : `row_fill` est la seule strategie implementee, tandis que `grid` et
`columns` sont reserves mais encore refuses par la validation.

La mission `P2-M002` du 2026-07-03 ajoute la couverture unitaire des cas limites
`row_fill` : priorite, stabilite de l'ordre source, rotation, retour a la ligne
et depassement vertical.

La mission `P2-M003` du 2026-07-03 ajoute la strategie `grid` : cellules XY
regulieres, placement ligne/colonne deterministe, refus des grilles trop
profondes et exemple `examples/simple_grid.json`.

La mission `P2-M004` du 2026-07-03 ajoute un resume comparatif dans les rapports
Markdown/JSON : strategies, statut, empreinte, occupation XY, warnings et score
simple explicable.

La mission `P3-M001` du 2026-07-03 ajoute une classification explicite des faces
rectangulaires simples dans le coeur Python pur. Cette etape est preparatoire :
les valeurs de tolerance par defaut et les dimensions imprimables des exemples
existants ne changent pas.

La mission `P3-M002` du 2026-07-03 applique les regles de tolerance depuis les
roles de faces. Chaque face produit maintenant une application de tolerance avec
offset, source, regle et raison. Les valeurs de tolerance par defaut restent
inchangees et les dimensions imprimables des exemples existants restent
identiques.

La mission `P3-M003` du 2026-07-03 ajoute des profils d'impression explicites et
surchargeables dans le JSON V0. Le profil est resolu en `ToleranceProfile`, puis
les champs `tolerances` surchargent les valeurs champ par champ. Les profils sont
experimentaux et non valides physiquement.

La mission `P3-M004` du 2026-07-03 ajoute un protocole de calibration physique.
Ce protocole decrit coupons, mesures, contexte d'impression et criteres OK/KO,
sans realiser ni revendiquer d'impression reelle.

La mission `P4-M000` du 2026-07-03 prepare le rapport de gate Fusion 360. Le
rapport recommande de commencer par un contrat CAD-agnostic (`P4-M001`) avant
tout adaptateur Fusion executable. La gate humaine `Premiere integration Fusion
360` est maintenant atteinte.

La mission `P4-M001` du 2026-07-03 definit une representation intermediaire CAD
abstraite et serialisable. La CAD IR V0 represente boite de reference,
composants, corps rectangulaires, dimensions theoriques/imprimables,
classifications de faces, tolerances appliquees, operations abstraites et
metadata, sans import Fusion 360.

La mission `P4-M002` du 2026-07-03 cree un squelette d'adaptateur Fusion 360
isole dans `fusion_addin/BoardGameInsertGenerator`. Il contient un manifeste, un
point d'entree `run(context)` / `stop(context)`, une detection Zero Doc et une
planification CAD IR `planned_only`, sans creation de geometrie Fusion reelle.

La mission `P4-M003` du 2026-07-03 code la premiere generation Fusion minimale
depuis une CAD IR JSON locale. L'add-in cree une esquisse de reference de boite
et des blanks rectangulaires par esquisse + extrusion dans le composant racine.
Le manifeste d'add-in a ete corrige au format JSON attendu par Fusion et le
chemin Part Design a ete adapte au composant racine. Le smoke test manuel a
confirme que l'add-in apparait, que le message final est OK, que les modules
sont visibles et que les dimensions mesurees correspondent a la CAD IR.

La mission `Export CAD IR CLI` du 2026-07-03 ajoute la commande
`export-cad-ir`, capable de transformer une configuration BGIG en CAD IR JSON V0
lisible et compatible avec le squelette Fusion existant. Cette commande ne
modifie pas les dimensions, les tolerances ou la geometrie Fusion ; elle rend la
fixture `cad_ir_input.json` regenerable depuis le moteur.
La mission `P4-M006` du 2026-07-03 stabilise le pipeline CAD IR vers Fusion,
autorise par gate humaine sous le libelle `P4-M004`. L'add-in resout maintenant
l'entree CAD IR depuis `cad_ir_input.json` ou `cad_ir_path.txt`, valide le
contrat minimal avant generation, affiche des erreurs Fusion actionnables et
garde la geometrie limitee aux blanks rectangulaires deja autorises.

La decision de gouvernance `Autonomous Git Integration Policy` du 2026-07-03
autorise Codex a gerer automatiquement les operations Git normales apres une
mission reussie. La decision corrective `Direct-to-main autonomous integration`
du 2026-07-03 rend le push direct de `main` vers `origin/main` obligatoire comme
chemin standard quand les tests passent, que `git diff --check` passe, que le
workspace est propre et qu'aucune vraie gate humaine n'est atteinte. Les pull
requests ne sont plus la voie normale ; elles restent un repli pour protection de
branche, review imposee, conflit, divergence non triviale, risque structurant,
probleme d'authentification ou refus GitHub.
La gate humaine du 2026-07-04 autorise la vague P5 limitee aux cavites simples
cote moteur Python pur, configuration, rapports et CAD IR. La mission `P5-M001`
ajoute des cavites rectangulaires simples abstraites : elles sont chargees depuis
`modules[].cavities`, validees contre les dimensions externes du module, les
parois X/Y et le fond, exposees dans les rapports Markdown/JSON et transportees
dans la CAD IR par l'operation abstraite `subtract_rectangular_cavity`. Fusion ne
les coupe pas encore.

La mission `P5-M002` du 2026-07-04 specialise les logements de cartes et cartes
sleevees : les cavites `cards` et `sleeved_cards` peuvent omettre `clearance_mm`,
qui est alors resolu depuis `card_clearance_mm` ou `sleeved_card_clearance_mm` du
profil actif. Une valeur explicite inferieure au profil actif est refusee et la
source de clearance est exposee dans les rapports et la CAD IR.

La mission `P5-M003` du 2026-07-04 specialise les receptacles ouverts pour
`tokens`, `dice` et `meeples`. Les cavites `tokens` et `dice` peuvent utiliser
`token_clearance_mm`, les cavites `meeples` utilisent `meeple_clearance_mm`, et
les sources sont exposees via `clearance_source`. Aucune valeur dediee aux des
n'est ajoutee tant qu'elle n'est pas calibree physiquement.

La mission `P5-M004` du 2026-07-04 ajoute des features ergonomiques abstraites
associees aux cavites : `finger_notch`, `side_notch`, `center_notch`,
`half_moon_notch`, `rounded_floor` et `grip_aid`. Elles sont chargees depuis la
configuration, validees contre les dimensions locales de cavite, exposees dans
les rapports Markdown/JSON et transportees dans la CAD IR par
`describe_cavity_feature`. Fusion ne les genere pas encore.

La mission strategique `P0-M009` du 2026-07-04 realigne la North Star, la spec
produit, la roadmap, l'architecture, l'autonomie et le backlog autour d'une
cible asset-first et volumetrique. Elle ajoute une capability map, des strategies
cibles pour assets, layers, solveur, accessibilite et vues eclatees, ainsi qu'une
ADR de pilotage par capabilities. Aucun comportement moteur, aucune tolerance et
aucune geometrie Fusion ne changent.

La mission `P6-M001` du 2026-07-04 code la premiere generation Fusion reelle de
cavites rectangulaires simples. L'add-in transforme les operations CAD IR
`subtract_rectangular_cavity` en coupes rectangulaires verticales depuis le dessus
du blank, limitees au body cible via `participantBodies`. Les features
ergonomiques, fonds arrondis, fillets, booleans complexes et exports restent hors
perimetre.

La validation humaine `P6-M001V` confirmee le 2026-07-06 documente le smoke test
Fusion : add-in lance, CAD IR `simple_tray` chargee, blank genere, cavite
rectangulaire generee, message conforme (`Blank bodies: 1`, `Rectangular cavity
cuts: 1`) et dimensions mesurees conformes. Les cavites rectangulaires simples
passent a `fusion-validated`. `print-validated: false` reste explicite : aucune
impression 3D n'a ete faite.

La mission `P6-M002` du 2026-07-06 code la generation Fusion d'encoches de
doigts simples depuis les operations CAD IR `describe_cavity_feature`. Les
features supportees sont transformees en coupes rectangulaires de bounding box
limitees au body cible. Les demi-lunes restent une intention abstraite : aucune
geometrie courbe, fond arrondi, fillet, export ou validation d'impression n'est
revendiquee.

Le premier smoke test humain `P6-M002V` a ete KO partiel : la feature etait lue,
mais Fusion montrait seulement un sketch/profil mal place, sans vraie coupe
volumique dans la paroi. Le correctif du 2026-07-06 convertit les points modele
vers l'espace sketch via `modelToSketchSpace`, transporte explicitement paroi,
plan et direction de cut.

Le second smoke test humain `P6-M002V` apres `3760abe` a confirme une coupe
volumique, mais sous forme de fenetre rectangulaire fermee dans la paroi. Le
correctif courant interprete `size_mm.z` comme `notch_depth_from_top_mm`, place le
bas du profil a `body_top_z - notch_depth_from_top_mm` et fait depasser le haut
du profil au-dessus du body pour produire une morsure top-open. Le smoke test
humain apres `b27c2e7` confirme le blank, la cavite, le message, la coupe
top-open dans la paroi frontale et l'absence de fenetre fermee. Cette version
est `fusion-validated` comme `top-open rectangular wall notch`.

`print-validated: false` reste explicite : aucune impression 3D n'a ete faite.

La mission `P6-M003` formalise une taxonomie CAD-agnostic des aides de prise :
`top_open_rectangular_notch`, `top_open_half_moon_notch`, `through_wall_window`,
`blind_internal_thumb_scoop`, `side_relief_notch`, `dual_side_card_access` et
`rounded_floor_intent`. Les rapports et la CAD IR exposent cette taxonomie sans
ajouter de nouvelle geometrie Fusion reelle.

La mission `P8-M001` implemente le socle de grille volumetrique 3D dans le coeur
Python pur : config `volumetric_grid`, unites X/Y/Z, layers, placements de
modules, zones reservees/interdites, validation de couverture utile, cellules
libres et metadata CAD IR. Aucun solveur automatique et aucune generation Fusion
volumetrique ne sont ajoutes.

La mission `P8-M002` enrichit ce modele volumetrique avec reservations typees, ordre de retrait abstrait, directions d'acces et surfaces de support abstraites. Les rapports Markdown/JSON et `metadata.volumetric_grid` CAD IR exposent `support_surfaces` et `removal_sequence`, sans solveur automatique, sans nouvelle operation Fusion et sans validation physique de portance.

La mission `P9-M001` specifie le schema cible asset-first : assets distincts des modules, quantites, dimensions exactes/approximatives, intentions de rangement et liens optionnels vers reservations volumetriques. Le loader V0 refuse encore `assets` ; aucune generation de module ou modification de layout n'est ajoutee.

## Phase active

Phase active : **P8 volumetric planner abstrait / gate avant generation Fusion volumetrique**.

Etat : le pipeline P4 reste stable pour les blanks rectangulaires Fusion. La
vague P5 est terminee cote moteur Python pur, configuration, rapports et CAD IR.
P6-M001 est `fusion-validated` pour les cavites rectangulaires simples, avec
`print-validated: false`. P6-M002 est `fusion-validated` pour les encoches
simples de paroi top-open, avec `print-validated: false`. P6-M003 est termine
cote taxonomie abstraite CAD-agnostic. P8-M001 et P8-M002 sont termines cote grille
volumetrique declarative, layers, reservations, supports abstraits et metadata CAD IR.
La North Star cible un
generateur volumetrique asset-first, pilote par capabilities.

Prochaine action recommandee : `P9-M002` pour charger des assets JSON stricts sans generation de modules, si l'activation reste additive et CAD-agnostic. Une nouvelle gate humaine est requise avant toute generation Fusion
reelle liee a la grille 3D, aux layers, aux vues eclatees ou aux features
avancees.

## Implemente

- Chargement de configurations JSON locales.
- Modeles Python par dataclasses.
- Validation de dimensions et contraintes de base.
- Layout rectangulaire `row_fill` deterministe.
- Application de tolerances simples par face.
- Rapports Markdown et JSON.
- Exemples JSON.
- Tests unitaires hors Fusion 360.
- ADR initiales sur moteur pur, cellules theoriques et JSON.
- Gouvernance projet et backlog Codex.
- Protocole d'autonomie operatoire.
- Politique d'integration Git autonome apres mission reussie.
- Gates humaines obligatoires.
- Matrice de validation.
- Roles logiques d'agents.
- Plan de sprint 2 a 4 semaines.
- Runbook humain de supervision.
- Dry run de selection autonome `P0-M004`.
- Verification documentaire de base `P0-M002`.
- Template ADR stabilise `P0-M005`.
- Contrat des dataclasses coeur documente et teste `P1-M001`.
- Chargement JSON strict sur champs inconnus et types invalides `P1-M002`.
- Rapports Markdown/JSON enrichis et erreurs CLI categorisees `P1-M003`.
- Commande CLI de diagnostic `P1-M004`.
- Contrat de strategies layout formalise `P2-M001`.
- Cas limites `row_fill` couverts par tests `P2-M002`.
- Strategie de layout `grid` implementee et documentee `P2-M003`.
- Resume comparatif de layout dans les rapports `P2-M004`.
- Classification explicite des faces rectangulaires simples `P3-M001`.
- Regles de tolerance appliquees par role de face `P3-M002`.
- Profils d'impression explicites et surchargeables `P3-M003`.
- Protocole de calibration physique `P3-M004`.
- Rapport de gate Fusion 360 `P4-M000`.
- Representation intermediaire CAD-agnostic `P4-M001`.
- Squelette d'adaptateur Fusion 360 isole et non generateur `P4-M002`.
- Chargement CAD IR et plan de generation Fusion minimale testes hors Fusion P4-M003.
- Manifeste Fusion JSON verifie par test hors Fusion.
- Chemin Fusion P4-M003 compatible documents Part Design via composant racine.
- Commande CLI `export-cad-ir` pour generer une CAD IR JSON V0 depuis une configuration BGIG.
- Pipeline CAD IR vers Fusion stabilise : entree par `cad_ir_input.json` ou
  `cad_ir_path.txt`, validation minimale du contrat et messages d'erreur
  actionnables dans Fusion.
- Cavites rectangulaires simples abstraites dans la configuration, la validation,
  les rapports Markdown/JSON et la CAD IR `subtract_rectangular_cavity`.
- Clearances de logements `cards`, `sleeved_cards`, `tokens`, `dice` et
  `meeples` resolues depuis le profil actif et tracables via `clearance_source`.
- Features ergonomiques abstraites de cavites P5-M004 chargees, validees,
  reportees et exportees dans la CAD IR par `describe_cavity_feature`.
- Taxonomie P6-M003 des aides de prise, exposee dans les rapports et la CAD IR,
  avec validation des couples `kind` / `taxonomy`.
- Socle P8-M001 de grille volumetrique 3D declarative : config, validation,
  cellules libres/occupees/reservees/interdites, rapports et metadata CAD IR.
- Enrichissement P8-M002 des reservations typees, ordre de retrait, directions
  d'acces, surfaces de support abstraites, rapports et metadata CAD IR.
- Schema cible P9-M001 asset-first documente, avec assets distincts des modules
  et loader V0 encore inchange.
- Generation Fusion de cavites rectangulaires simples P6-M001 depuis
  `subtract_rectangular_cavity`, avec coupe verticale limitee au body cible,
  `fusion-validated` et `print-validated: false`.
- Generation Fusion d'encoches de doigts simples P6-M002 depuis
  `describe_cavity_feature`, comme coupes rectangulaires de paroi top-open
  limitees au body cible, avec correctifs `modelToSketchSpace` et profil depasse
  au-dessus du body, `fusion-validated` comme `top-open rectangular wall notch` et
  `print-validated: false`.
- Pilotage produit par North Star, Product Pillars, Capability Map, milestones,
  epics, missions, gates et validations.
- Roadmap 0-14 alignee avec la cible volumetrique asset-first.
- Smoke test CAD manuel P4-M003 valide dans Fusion : add-in visible, message OK,
  modules visibles et dimensions conformes a la fixture.

## Experimental

- Le layout `row_fill` est formalise mais n'est pas un optimiseur.
- La strategie `grid` est deterministe mais n'est pas un optimiseur.
- La strategie `columns` est reservee mais non executable.
- Les roles `internal` et `welded` ont des regles de tolerance sans jeu, mais ne
  sont pas encore detectes automatiquement par des modules composites.
- Les `PrimitiveVolume`, `CompositeModule` et `Feature` existent comme concepts
  mais ne pilotent pas encore une generation complete.
- Les features ergonomiques P5-M004 restent abstraites dans le coeur ; seules les
  encoches simples de paroi sont mappees par P6-M002 en coupe rectangulaire
  Fusion. Les fonds arrondis, demi-lunes courbes reelles et fillets ne sont pas
  generes.
- Les cavites rectangulaires P6-M001 sont `fusion-validated`, mais non
  `print-validated`.
- Les encoches de doigts simples P6-M002 sont `fusion-validated` comme coupes
  rectangulaires de paroi top-open, mais non `print-validated`.
- Les tolerances par defaut et les profils d'impression sont prudents mais non
  calibres sur impression.
- Les dataclasses restent volontairement legeres ; les erreurs metier sont
  agregees par `validation.py`.
- Le squelette Fusion P4-M002 est testable hors Fusion.
- La generation Fusion P4-M003 est validee manuellement dans Fusion pour le
  chargement, le message final, l'apparition des modules et les dimensions de
  la fixture. Depuis P4-M004/P4-M006, toute nouvelle CAD IR exportee peut etre
  pointee par `cad_ir_path.txt`, mais doit encore etre inspectee dans Fusion.
  Cela ne valide pas l'impression reelle.

## Prevu

- Strategie de layout `columns`.
- Generation Fusion reelle de fonds arrondis, fillets, conges, booleans complexes
  ou geometrie courbe, sous nouvelle gate humaine.
- Modules composites en L/T.
- Couvercles, rainures et mecanismes.
- Surcouche esthetique.
- Assistant de conception.
- Modele asset-first.
- Solveur volumetrique 3D et reservations derivees d'assets.
- Modele asset-first reliant assets plats, boards, regles et reservations P8.
- Vue Fusion eclatee.
- Solveur semi-automatique et scoring.
- Packaging produit et exemples reels.

## A valider par impression reelle

- Jeux peripheriques.
- Jeux inter-modules.
- Jeux pour cartes sleevees.
- Jeux de couvercles coulissants.
- Charnieres, clips et mecanismes.
- Epaisseurs minimales, rayons, chanfreins et patterns.

## Tests et verifications connus

Commande de test principale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

Commande d'exemple :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/simple_box.json --format markdown
```

Derniere verification pendant `P9-M001 - Schema cible asset-first` :

- `python -m unittest discover -s tests` : OK, 120 tests passes.
- `python -m py_compile src\board_game_insert_generator\models.py src\board_game_insert_generator\config_loader.py src\board_game_insert_generator\validation.py src\board_game_insert_generator\volumetric.py src\board_game_insert_generator\report.py src\board_game_insert_generator\cad_ir.py` : OK.
- `python -m board_game_insert_generator examples\simple_box.json --format markdown` : OK.
- `python -m board_game_insert_generator examples\simple_box.json --format json` : OK.
- `python -m board_game_insert_generator export-cad-ir examples\simple_box.json` : OK, schema `cad_ir.v0`, 4 composants.
- `python -m board_game_insert_generator examples\simple_tray.json --format markdown` : OK.
- `python -m board_game_insert_generator examples\simple_tray.json --format json` : OK.
- `python -m board_game_insert_generator export-cad-ir examples\simple_tray.json` : OK, schema `cad_ir.v0`, 1 composant.
- `python -m board_game_insert_generator examples\simple_finger_notch_tray.json --format markdown` : OK.
- `python -m board_game_insert_generator examples\simple_finger_notch_tray.json --format json` : OK.
- `python -m board_game_insert_generator export-cad-ir examples\simple_finger_notch_tray.json` : OK, schema `cad_ir.v0`, 1 composant.
- `python -m board_game_insert_generator examples\simple_3d_grid.json --format markdown` : OK, section `Volumetric grid` exposee.
- `python -m board_game_insert_generator examples\simple_3d_grid.json --format json` : OK, `volumetric_grid.free_cell_count = 18`.
- `python -m board_game_insert_generator export-cad-ir examples\simple_3d_grid.json` : OK, schema `cad_ir.v0`, metadata `volumetric_grid`, 2 composants.
- `python -m board_game_insert_generator examples\simple_3d_reservations.json --format markdown` : OK, sections `Support surfaces` et `Removal sequence` exposees.
- `python -m board_game_insert_generator examples\simple_3d_reservations.json --format json` : OK, `support_surfaces` et `removal_sequence` presents.
- `python -m board_game_insert_generator export-cad-ir examples\simple_3d_reservations.json` : OK, schema `cad_ir.v0`, metadata `volumetric_grid.support_surfaces`, 2 composants.
- `git diff --check` : OK.
- `rg -n "adsk" src/board_game_insert_generator` : OK, aucune occurrence dans le coeur Python.

## Risques actifs

- Le moteur a deja des concepts futurs dans `models.py`; il faut eviter de les
  presenter comme fonctionnels tant qu'ils ne sont pas generes et testes.
- L'integration Fusion 360 peut facilement aspirer de la logique metier ; les ADR
  et `AGENTS.md` interdisent ce couplage.
- Les tolerances seront credibles seulement apres une boucle d'impression reelle.
- Le backlog est volontairement large ; chaque mission doit rester petite et
  testable.
- L'autonomie Git ne doit pas masquer les vraies gates produit : toute extension
  Fusion, export imprimable ou validation physique reste bloquee tant que la gate
  correspondante n'est pas explicitement validee.
- Les cartes avec dependances non terminees doivent rester `todo` et ne pas etre
  selectionnees comme `ready`.

## Regle de mise a jour

Mettre a jour ce fichier apres toute mission significative, notamment si :

- une carte change de statut ;
- un comportement est implemente ou retire ;
- une verification passe ou echoue ;
- une hypothese devient une decision ;
- une limite est decouverte.
