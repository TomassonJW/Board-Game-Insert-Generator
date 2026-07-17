# Status

Derniere mise a jour : 2026-07-18

## Etat global

Statut produit : **MVP V0.1 Fusion-only accepte ; validation d impression non acquise**.

Surface produit active : **add-in Fusion 360 uniquement** selon ADR-0055.
La palette embarquee est l editeur principal ; frontend, Vite et loopback sont historiques et hors runtime.
Phase active : P64-V2H03B est `implemented-core` et
`automated-validated`. La frontière locale et ses caps sont disponibles sans
routage public. P64-V2H03C devient la seule mission `ready`. P64-V2H02R reste
la dernière preuve Fusion ; P44-V et P45 restent bloquées.
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

La mission `P9-M002` charge maintenant `assets` depuis le JSON V0 comme donnees passives : validation stricte, rapports Markdown/JSON, metadata CAD IR `assets`, exemple `simple_assets.json`. Aucun module, cavity, layout ou operation Fusion n'est derive depuis ces assets.

La mission `P10-M001` definit les criteres de scoring de variantes dans `SOLVER_STRATEGY` : compacite, accessibilite, reservations, simplicite d'impression, setup et confiance de mesure. Aucun solveur, aucune variante automatique et aucune dependance lourde ne sont ajoutes.

La mission `P10-M002` ajoute `variant_comparison` dans les rapports Markdown/JSON : comparaison report-only des strategies deterministes `row_fill` et `grid`, sous-scores explicables et raisons. Aucun optimiseur global, aucune nouvelle strategie de placement, aucune dependance lourde et aucune generation Fusion ne sont ajoutes.

La mission `P10-M003` enrichit les variantes `rejected` avec `rejection_reasons` structurees : code, categorie, severite, message source, reference de contrainte et action corrective. Elle reste report-only et ne cree ni nouveau solveur ni nouveau placement.

La mission `P10-M004` produit `module_candidates` depuis les assets charges : candidats indicatifs, reservations seules ou blocages de dimensions. Ces candidats sont reportes et transportes en CAD IR metadata, sans modifier `modules`, sans layout automatique et sans Fusion.

La mission `P10-M005` expose une variante recommandee `asset-candidates:row_fill` depuis les candidats imprimables quand ils tiennent dans la boite. Cette variante reste report-only, transportee en metadata CAD IR, sans mutation de `modules` et sans geometrie Fusion.

La mission `P10-M006` groupe deterministiquement les assets compatibles par kind, intention et confiance de mesure. Les candidats groupes exposent plusieurs `source_asset_ids`, restent report-only et ne modifient pas la configuration source.

La mission `P10-M007` ajoute un exemple de variante asset-candidate rejetee par dimensions. Le rapport JSON/Markdown et la CAD IR metadata exposent `rejection_reasons`; aucune variante recommandee n'est produite pour ce cas.

La mission `P10-M008` produit maintenant un `executable_asset_plan` depuis la variante asset recommandee : modules generes abstraits, placement grille greedy X/Y/Z, dimensions couvertes en millimetres, score et refus actionnables. La sortie est exposee dans les rapports Markdown/JSON et dans `metadata.executable_asset_plan` CAD IR, sans modifier `modules` et sans generation Fusion.

La mission `P11-M001` code la premiere vue compacte Fusion depuis `metadata.executable_asset_plan` : les modules asset-first generes sont crees comme bodies rectangulaires dans le composant racine, positionnes par `origin_mm` / `size_mm` des placements grille X/Y/Z. Les garde-fous hors Fusion couvrent dimensions manquantes, span hors grille, sortie de boite et collision manifeste.

La validation humaine `P11-M001V` confirmee le 2026-07-06 documente le smoke test Fusion : add-in recopie dans le dossier Fusion AddIns, CAD IR `simple_asset_executable_plan` chargee, message conforme (`CAD IR module blanks planned: 1`, `Grid-positioned asset modules planned: 1`, `Blank bodies: 2`, `Grid-positioned module bodies: 1`, `Grid-positioned modules refused: 0`), module asset-first positionne par la grille, position `X 30.0 mm`, `Y 0.0 mm`, `Z 0.0 mm` conforme ou acceptable, taille `30.0 x 30.0 x 10.0 mm` conforme ou acceptable. Statut : `fusion-validated`, `print-validated: false`.

La mission `P7-M001` code une premiere vue eclatee Fusion basique. Le smoke test humain P7-M001V a valide la visibilite de la vue compacte/eclatee mais a refuse les copies independantes de bodies. Les corrections P7 creent maintenant un `Component` Fusion unique par module physique, une occurrence compacte et une occurrence eclatee liee du meme composant, detectent le contexte Part Design incompatible comme `assembly document required` et ne tentent plus de renommer directement `Occurrence.name`. La validation humaine `P7-M001V4` confirmee le 2026-07-06 valide dans un document Assembly-compatible le mode `compact_and_exploded`, les messages `Module components created: 2`, `Compact occurrences created: 2`, `Exploded occurrences created: 2`, `Linked exploded occurrences: yes`, `Occurrence direct rename attempted: no`, la presence des vues compacte/eclatee et le partage des composants sources par occurrences liees. Statut : `fusion-validated`, `print-validated: false`.

La mission `P11-M002` code une premiere scene Fusion multi-layer depuis les placements grille X/Y/Z deja resolus par `metadata.executable_asset_plan`. L'exemple `simple_multilayer_grid_scene` produit un module genere bas, un module genere plus haut sur deux unites Z et un placement explicite a `Z=1`; le plan hors Fusion expose les compteurs multi-layer et l'add-in conserve la strategie `Component` source + occurrences compactes/eclatees liees. La validation humaine `P11-M002V` du 2026-07-07 confirme le lancement de l'add-in, le chargement CAD IR, le message conforme et la generation multi-layer visible. Statut : `fusion-validated`, `print-validated: false`.

La mission `P11-M003` corrige l'ambiguite dimensionnelle observee apres P11-M002V : les modules asset-first generes distinguent maintenant span grille theorique, enveloppe asset-fit et taille imprimable. Le smoke test humain `P11-M003V` a ete KO partiel : la scene etait generee, mais les dimensions effectives n'etaient pas clairement verifiables dans le message Fusion. La correction `P11-M003V2` refuse les placements grille modernes sans `printable_body_size_mm`, garde `theoretical_grid_extent_mm` comme metadata d'occupation et ajoute un `Body sizing report`. La correction `P11-M003V3` cree une commande `Generate Board Game Insert` visible. Le smoke test humain P11-M003V3 a ensuite ete KO partiel cote produit parce que la fixture melangeait blank legacy et module asset-first ; la correction `P11-M003V4` ajoute `simple_asset_product_scene.json`, explicite `module_source` / `placement_source` et ajoute `Module source mapping` au message Fusion. La validation humaine `P11-M003V4` confirmee le 2026-07-07 apres le commit `134863c` valide l'add-in recopie, la commande UI, le chargement de `simple_asset_product_scene`, le mode `compact_and_exploded`, un seul module asset-first, zero blank legacy, les occurrences compactes/eclatees liees, le `Module source mapping`, le `Body sizing report`, `printable_body_size_mm` environ `25.6 x 25.6 x 9.8 mm`, bbox Fusion comparable et `size match yes`. Statut : `fusion-validated`, `print-validated: false`.

La mission `P12-M001` code un lancement UI Fusion relancable par bouton toolbar : les constantes de commande et d'emplacement sont centralisees dans le squelette testable, le message de generation expose la politique `toolbar_button_reopens_command_without_addin_restart`, et la documentation indique comment rouvrir BGIG sans redemarrer l'add-in. La validation humaine `P12-M001V` confirmee le 2026-07-07 apres le commit `a12ef42` valide la commande visible, le bouton dans `Design workspace > Utilities > Add-Ins`, la reouverture sans redemarrage, le chargement UI de `simple_asset_product_scene`, le mode `compact_and_exploded`, la generation Fusion, le `Body sizing report`, les occurrences liees et la ligne `UI reopen policy`. Statut : `fusion-validated`, `print-validated: false`.

La correction `P12-M002V6` a ete refusee en smoke test Fusion : les objets BGIG visibles n etaient pas retrouves par le tagging, `generate`/`regenerate` empilaient des doublons, `clear_bgig_scene` ne supprimait rien et le reporting pouvait lever `non_bgig_objects_preserved`.

La correction `P12-M002V7` stabilise l UI Fusion parametrique V0 apres KO P12-UI-M002V6 : modes `cad_ir_file` / `config_file` / `quick_parametric_box`, project root auto-detecte ou memorise, settings local `bgig_ui_settings.json`, overrides actifs en `config_file`, puis champs reutilises en `quick_parametric_box` depuis P12-M003, generation encapsulee sous une occurrence racine unique `BGIG Generated Scene` taguee `bgig:role = scene_root`, `generate` refuse toute scene ou objet BGIG tague deja present, `regenerate` valide puis supprime la racine par `deleteMe()` avant regeneration, et `clear_bgig_scene` ramene `BGIG objects remaining after clear` a `0` sans toucher aux objets non BGIG. Validation humaine P12-UI-M002V7 confirmee apres correction registry inspect : add-in recopie dans Fusion AddIns, document Assembly-compatible, inspect avant generation a zero racine/zero entite taguee/zero faux positif, generation `config_file` de `simple_asset_product_scene`, `BGIG scene roots created: 1`, `Registry validation: ok`, une occurrence BGIG visible attendue et reelle, `Legacy bodies created: 0`, `Body sizing report` avec `size match yes`, inspect apres generation avec `BGIG scene roots total: 1`, `BGIG scene root occurrences: 1`, entites taguees non redondantes, zero `BGIG-looking untagged`, `Inconsistencies: none`, regenerate sans doublon et clear ramenant les racines et objets BGIG a zero en preservant les objets non BGIG. Statut : `fusion-validated`, `print-validated: false`.

## Phase active

Phase active : **P12-M004V validee Fusion / prochaine extension produit sous gate**.
La mission `P12-M003` du 2026-07-07 rend le mode Fusion `quick_parametric_box` fonctionnel. La commande UI peut maintenant generer une CAD IR temporaire minimale depuis les champs de boite, grille, epaisseurs, clearances et profil, puis reutiliser le pipeline Fusion existant pour creer une scene V0. Le mode reste borne : une boite de reference, un module rectangulaire simple, aucune nouvelle geometrie avancee, aucune modification de tolerance par defaut et aucune validation d'impression revendiquee.

La validation humaine `P12-M003V` du 2026-07-08 confirme dans Fusion le mode `quick_parametric_box` en `compact_only` : CAD IR temporaire creee, scene racine BGIG creee, registry valide, zero objet BGIG non tague, une occurrence compacte visible, aucun legacy body, rapport de sizing conforme avec `printable_body_size_mm` `28.9 x 18.9 x 8.8 mm` et bbox Fusion reelle identique, `size match yes`. Statut : `fusion-validated`, `print-validated: false`.

La mission `P12-M004` du 2026-07-08 ameliore la persistance et la rehydratation de la commande Fusion classique. `bgig_ui_settings.json` conserve maintenant action, input mode, generation mode, chemins CAD IR/config/root et tous les champs parametriques P12 ; `commandCreated` les restaure, `quick_parametric_box` est pre-rempli avec les dernieres valeurs, `cad_ir_file` ignore les champs parametriques persistants au lieu de les refuser, et l action `regenerate` est preferee a l ouverture si une scene BGIG existe deja. Statut : `fusion-validated` apres `P12-M004V`, `print-validated: false`.

La mission d'automatisation locale du 2026-07-08 ajoute `scripts/fusion/` pour installer l'add-in courant, verifier l'installation, preparer des smoke tests CAD IR depuis config et precharger le smoke test `quick_parametric_box`. Codex doit desormais utiliser ces scripts pour preparer les gates Fusion et fournir a Thomas uniquement les actions restantes dans Fusion, sauf blocage d'ecriture AppData.

Le premier smoke test humain `P12-M004V` apres `c6cba19` etait KO : l'UI Fusion ne montrait pas les valeurs preparees. Cause identifiee : `bgig_ui_settings.json` etait ecrit par PowerShell en UTF-8 avec BOM, puis refuse silencieusement par `json.loads()` lu en `utf-8`. La correction `ab488dc` lit les settings en `utf-8-sig`, ecrit les settings sans BOM et ajoute un diagnostic visible `UI settings` dans la commande. Le smoke test humain apres `ab488dc` valide : bloc `UI settings`, pre-remplissage `quick_parametric_box`, reouverture avec valeurs conservees, modification `box_inner_x_mm = 160`, `regenerate`, reouverture avec `160`, `clear_bgig_scene` et preservation non-BGIG. Statut : `fusion-validated`, `print-validated: false`.

Etat : le pipeline P4 reste stable pour les blanks rectangulaires Fusion. La
vague P5 est terminee cote moteur Python pur, configuration, rapports et CAD IR.
P6-M001 est `fusion-validated` pour les cavites rectangulaires simples, avec
`print-validated: false`. P6-M002 est `fusion-validated` pour les encoches
simples de paroi top-open, avec `print-validated: false`. P6-M003 est termine
cote taxonomie abstraite CAD-agnostic. P8-M001 et P8-M002 sont termines cote grille
volumetrique declarative, layers, reservations, supports abstraits et metadata CAD IR.
P11-M001 est `fusion-validated` pour la vue compacte issue du plan asset-first,
avec l'ancienne attente dimensionnelle documentee. P7-M001 est
`fusion-validated` pour la vue eclatee basique par occurrences liees dans un
document Assembly-compatible, avec `print-validated: false`. P11-M002 est
`fusion-validated` pour une scene compacte/eclatee multi-layer depuis placements
X/Y/Z. P11-M003 est `fusion-validated` pour la commande UI minimale, le sizing asset-first explicite, la scene produit non ambigue, le mapping source et les occurrences compactes/eclatees liees. P11-M003V2 ajoute le rapport bbox planned/actual ; P11-M003V3 corrige l'affichage de la vraie commande UI ; P11-M003V4 valide le flux UI produit avec `simple_asset_product_scene`. La North
Star cible un generateur volumetrique asset-first, pilote par capabilities.

Prochaine action recommandee : stopper sur gate produit avant toute extension structurante : palette persistante, UI assets complete, solveur plus automatique, nouvelle geometrie Fusion, export imprimable ou validation d'impression. Aucune mission produit suivante n'est lancee dans ce run.

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
- Schema cible P9-M001 asset-first documente.
- Assets P9-M002 charges, valides, reportes et transportes en metadata CAD IR,
  sans generation de modules.
- Candidats de modules P10-M004 derives des assets comme metadata report-only,
  sans mutation de `modules` ni placement automatique.
- Variante recommandee P10-M005 depuis candidats assets, report-only et
  transportee en metadata CAD IR.
- Grouping P10-M006 borne des assets compatibles, expose par `source_asset_ids`.
- Exemple P10-M007 de variante asset rejetee avec `rejection_reasons` structurees.
- Plan executable P10-M008 depuis variante asset recommandee : modules generes abstraits, placement greedy grille et metadata CAD IR.
- Vue compacte Fusion P11-M001 depuis placements grille : `fusion-validated`,
  `print-validated: false`.
- Scene Fusion multi-layer P11-M002 depuis placements grille X/Y/Z :
  `fusion-validated`, `print-validated: false`.
- Sizing explicite P11-M003/P11-M003V2/P11-M003V4 des modules asset-first generes : span grille
  theorique, enveloppe asset-fit, taille de body imprimable, source de sizing,
  garde-fou anti-span-silencieux, source module/placement, assets contenus, clearances nommees et slack de grille visibles dans rapports/JSON/CAD IR ou plan Fusion.
- Commande UI Fusion minimale P11-M003/P11-M003V3 : champ `CAD IR JSON path`, mode
  `compact_only` / `compact_and_exploded`, command id Fusion valide, ouverture
  immediate du dialogue au lancement, bouton toolbar optionnel, fichiers texte
  locaux conserves comme fallback de compatibilite, `fusion-validated`, `print-validated: false`.

- Action UI `inspect_bgig_scene` read-only pour diagnostiquer occurrences root, components, bodies, sketches, entites taguees `bgig`, objets BGIG par nom non tagues et incoherences.
- Registry Fusion unique `BgigFusionRegistry` responsable de `scene_id`, tagging, recherche d attributs, inspection, clear et validation post-generation.
- Tagging immediat des roles `scene_root`, `scene_root_component`, `box_reference`, `compact_occurrence`, `exploded_occurrence`, `module_component`, `module_body`, sketches et cuts supportes.
- `generate` refuse les scenes existantes trouvees par tag ou nom BGIG ; `regenerate` clear puis revalide exactement une scene ; `clear_bgig_scene` preserve les objets non BGIG.
- UI Fusion parametrique P12-M002V7 : modes explicites, root auto-detecte/memorise, config JSON -> CAD IR temporaire, overrides config-only, scene racine taguee, `generate` refuse les doublons, occurrence racine unique taguee `bgig:role = scene_root`, suppression par `deleteMe()`, occurrence compacte initiale visible, occurrence eclatee liee via `addExistingComponent`, `regenerate` remplace sans doublons, `clear_bgig_scene` supprime la racine, reporting inspect standard deduplique et valide Fusion avant/apres generation/clear, `fusion-validated`, `print-validated: false`.
- UI Fusion `quick_parametric_box` P12-M003 : CAD IR temporaire minimale depuis champs Fusion, generation `compact_only` validee dans Fusion avec registry OK, occurrence compacte visible, bbox reelle conforme au body imprimable planifie et `print-validated: false`.
- Persistance UI Fusion P12-M004/P12-M004V : `bgig_ui_settings.json` sauvegarde action, input mode, generation mode, chemins et tous les champs parametriques P12 ; rehydratation au prochain `commandCreated`, champs parametriques ignores en `cad_ir_file`, action `regenerate` preferee quand une scene BGIG existe deja ; validation Fusion apres `ab488dc` confirmee, `print-validated: false`.
- Automatisation locale des smoke tests Fusion : scripts `scripts/fusion/` pour installer/verifier l'add-in, exporter une CAD IR de smoke test et precharger les settings quick parametric ; documentation `docs/FUSION_SMOKE_TEST_AUTOMATION.md`.
- Vue eclatee Fusion P7-M001 basique : composants physiques uniques avec
  occurrences compactes/eclatees liees, garde-fou `assembly document required`
  si le document actif est un Part Design incompatible, sans renommage direct de
  `Occurrence.name`, `fusion-validated`, `print-validated: false`.
- Criteres de scoring P10-M001 documentes, sans solveur executable.
- Comparaison P10-M002 report-only de variantes deterministes existantes dans les rapports.
- Raisons de rejet P10-M003 structurees et actionnables pour les variantes non generables.
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
  la fixture. Depuis P11-M003, le flux courant passe par une commande UI de
  selection CAD IR/mode ; les fichiers texte locaux restent un fallback. Toute
  nouvelle CAD IR exportee doit encore etre inspectee dans Fusion. Cela ne
  valide pas l'impression reelle.

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

## P13 - Asset input UI V0

La mission `P13-M001 - quick_asset_box UI V0` ajoute un premier flux asset-first directement depuis la commande Fusion classique. Le nouveau mode `quick_asset_box` reste distinct de `cad_ir_file`, `config_file` et `quick_parametric_box`.

Comportement implemente : champ texte editable `Assets (quick_asset_box)` au format `asset_id,type,count,x_mm,y_mm,z_mm,fit`, entrees separees par `;` ou saut de ligne, types V0 `tokens`, `dice`, `meeples`, `cards`, `sleeved_cards`, `generic`, persistance dans `bgig_ui_settings.json`, generation d'une config temporaire stricte, conversion par le pipeline existant `assets -> module_candidates -> recommended variant -> executable_asset_plan -> CAD IR -> Fusion`, puis reporting Fusion des assets lus/refuses, candidats, variante recommandee, modules generes/places/refuses, sizing report, statut explicite `asset_items_visualized: no`, `asset_cavities_generated: no`, `count_aware_storage_sizing: no` et `Print validation: false`.

Limites : pas de tableau assets avance, pas de palette HTML persistante, pas de solveur complexe, pas de cavites/logements assets, pas d'assets Fusion individuels, pas d'export STL/3MF, pas de validation d'impression. Le `count` est lu, persiste et reporte, mais P13-M001 V0 ne l'utilise pas encore pour multiplier footprint, hauteur, nombre de modules ou cavites : le sizing reste une enveloppe representative du plus grand asset du groupe plus clearances/murs/plancher. Un repere visuel minimal de volume boite est ajoute via outlines XY bas/haut non imprimables. Le profil UI `draft` est conserve dans les settings et mappe vers le profil moteur existant `fast_draft` seulement pour la config temporaire `quick_asset_box`.

Statut : `fusion-validated-v0` pour `P13-M001V` apres validation humaine Fusion du 2026-07-08 sur `bec0352`. Le mode `quick_asset_box` est valide comme UI asset-first V0 honnete : ouverture commande, champ assets persiste/prefilled, generate/regenerate/clear, module proxy asset-first, diagnostics de limites, registry OK et preservation des objets non-BGIG. Limites non validees et non implementees : assets individuels non visualises, cavites/logements non generes, sizing non count-aware, aucune garantie de capacite reelle, aucune impression 3D validee. Historique : premier essai P13-M001V KO a l ouverture par constante UI manquante `QUICK_ASSET_BOX_ASSETS_INPUT_ID`; deuxieme essai KO partiel apres `859bc7b` par reporting V0 trop trompeur; correction `bec0352` validee humainement.

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

Derniere verification pendant `P13-M001 - quick_asset_box UI V0 / correction P13-M001V KO partiel` :

- `python -m unittest discover -s tests` : OK, 180 tests passes apres correction P13-M001V KO partiel.
- `python -m py_compile fusion_addin/BoardGameInsertGenerator/BoardGameInsertGenerator.py fusion_addin/BoardGameInsertGenerator/fusion_skeleton.py` : OK.
- CLI Markdown/JSON : OK sur `simple_asset_product_scene.json`, `simple_asset_executable_plan.json`, `simple_multilayer_grid_scene.json`, `simple_tray.json` et `simple_finger_notch_tray.json`.
- Export CAD IR : OK sur `simple_asset_product_scene.json`, `simple_asset_executable_plan.json`, `simple_multilayer_grid_scene.json`, `simple_tray.json` et `simple_finger_notch_tray.json`.
- `scripts/fusion/prepare_quick_asset_test.ps1 -DryRun` : OK, actions Fusion mises a jour avec diagnostics V0 honnetes.
- `scripts/fusion/prepare_quick_asset_test.ps1` : OK, add-in corrige reinstalle et settings `quick_asset_box` ecrits.
- `scripts/fusion/check_installed_addin.ps1` : OK avec marqueurs P13 renforces, incluant diagnostics non count-aware.
- `git diff --check` : OK.
- `rg -n "adsk" src/board_game_insert_generator` : OK, aucune occurrence dans le coeur Python.
- Validation Fusion reelle : `P13-M001V` OK le 2026-07-08 apres correction `bec0352`, comme V0 honnete avec limites explicites. Impression 3D non validee.

Derniere verification pendant `P12-M002V7 - Registry BGIG et inspect read-only` :

- `python -m unittest discover -s tests` : OK, 169 tests passes.
- `python -m py_compile fusion_addin/BoardGameInsertGenerator/BoardGameInsertGenerator.py` : OK.
- `python -m py_compile fusion_addin/BoardGameInsertGenerator/fusion_skeleton.py` : OK.
- CLI Markdown/JSON : OK sur `simple_asset_product_scene.json`, `simple_asset_executable_plan.json`, `simple_multilayer_grid_scene.json`, `simple_tray.json` et `simple_finger_notch_tray.json`.
- Export CAD IR : OK sur `simple_asset_product_scene.json`, `simple_asset_executable_plan.json`, `simple_multilayer_grid_scene.json`, `simple_tray.json` et `simple_finger_notch_tray.json`.
- `git diff --check` : OK.
- `rg -n "adsk" src/board_game_insert_generator` : OK, aucune occurrence dans le coeur Python.
- Validation Fusion reelle : `P12-UI-M002V7` confirmee apres correction registry inspect. `inspect_bgig_scene`, `generate`, anti-doublon, `regenerate`, `compact_only`, `compact_and_exploded`, `clear_bgig_scene`, ownership racine BGIG, reporting deduplique et preservation non-BGIG valides dans Fusion. Impression 3D non validee.
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

## P13-ASSET-M002 - Count-aware storage sizing implemente

P13-ASSET-M002 ajoute un sizing count-aware V0 pour `tokens`, `dice`, `meeples` et `generic`. Le moteur utilise `count` pour calculer capacite par pile, nombre de piles XY, enveloppe asset-fit, taille module finale, et refuse proprement les cas qui ne tiennent pas dans la boite/grille. Les cartes et cartes sleevees gardent `z_mm` comme hauteur totale de paquet, avec `count` reporte mais non multiplie.

Cote Fusion, `quick_asset_box` reporte `count_aware_storage_sizing: yes|partial|no`, diagnostics `asset_sizing` et `module_candidate_sizing`, `declared_capacity_guarantee = heuristic_envelope_only_not_physical_cavity`, et cree un sketch debug non imprimable `asset-fit debug outline` sur les modules asset candidates. `asset_items_visualized: no`, `asset_cavities_generated: no` et `Print validation: false` restent vrais.

Statut : `fusion-validated-v0` apres validation humaine Fusion du 2026-07-09 sur `357bfc1`. P13-ASSET-M002V confirme `generate`, `regenerate`, `clear_bgig_scene`, registry OK, preservation des objets non-BGIG, module count-aware qui change de taille quand `count` change, diagnostics `capacity_per_stack`, `pile_count`, `declared_capacity`, `asset_fit`, `module_size`, metadata/report `storage_sizing`, warnings cavites non generees et capacite heuristique non print-validee. Aucune validation d'impression 3D.

## P13-ASSET-M002V - Validation Fusion count-aware

Validation humaine Fusion confirmee le 2026-07-09 sur `357bfc1`.

Resultats observes : add-in reinstalle par scripts Codex, document Fusion Assembly-compatible, `quick_asset_box` charge avec assets pre-remplis, `generate` OK, `count_aware_storage_sizing: yes`, `sizing_scope: count_aware_stacked_rectangular_piles_v0`, `asset_debug_visualization: yes`, diagnostics de piles/capacite/taille presents, `Body sizing report`, `Registry validation: ok`, `Print validation: false`.

Test count-aware valide : avec `coin-tokens,tokens,40,18,16,2,loose` et `status-tokens,tokens,23,10,35,2,loose`, module `50.0 x 39.0 x 48.0`; apres modification de `coin-tokens` a `80`, `regenerate` produit `68.0 x 39.0 x 56.0`. La taille, les piles, la capacite declaree et le grid span changent avec `count`.

Limites maintenues : assets individuels non visualises, cavites/logements non generes, pas de solveur global, pas d'optimisation avancee, capacite heuristique non garantie physiquement, aucune impression 3D validee.

## P13-ASSET-M003 - Asset-fit cavity V0 implemente

P13-ASSET-M003 ajoute la premiere cavite asset-first reelle pour `quick_asset_box`. Le moteur attache aux modules `executable_asset_plan` une metadata `asset_fit_cavity` planifiee ou refusee. L'adaptateur Fusion consomme cette metadata pour creer une coupe rectangulaire top-open globale via le mecanisme existant `subtract_rectangular_cavity`.

Strategie retenue : `single_asset_fit_rectangular_cavity_v0`, origine locale alignee sur `wall_thickness_mm`, fond conserve `floor_thickness_mm`, taille de cavite egale a `asset_fit_size_mm`. Les types supportes sont `tokens`, `dice`, `meeples`, `generic`; les cartes restent refusees pour cette cavite V0.

Pour le smoke M003 prepare, le cas `coin-tokens,tokens,40,18,16,2,loose` + `status-tokens,tokens,23,10,35,2,loose` produit un module `50.0 x 39.0 x 48.0` et une cavite `47.6 x 36.6 x 46.8 mm`, avec fond `1.2 mm` et murs attendus `1.2 mm`.

Limites maintenues : assets individuels non visualises, pas de cavites par pile, pas de solveur global, pas d'optimisation avancee, capacite heuristique non garantie physiquement, aucune impression 3D validee.

Verifications realisees pendant P13-ASSET-M003 : suite unitaire complete OK (`185 tests`), `py_compile` add-in OK, CLI Markdown/JSON/export CAD IR OK sur les exemples P12/P13 pertinents, `prepare_quick_asset_test.ps1 -DryRun` OK, `prepare_quick_asset_test.ps1` OK avec add-in installe, `check_installed_addin.ps1` OK, `git diff --check` OK, `rg -n "adsk" src/board_game_insert_generator` sans occurrence.

Statut : `fusion-validated-v0` apres validation humaine Fusion `P13-ASSET-M003V` confirmee le 2026-07-09 sur `04dfdb6`, `print-validated: false`.


## P13-ASSET-M003V - Validation Fusion asset-fit cavity V0

Validation humaine Fusion confirmee le 2026-07-09 sur `04dfdb6`.

Resultats observes : add-in reinstalle par scripts Codex, document Fusion Assembly-compatible, `quick_asset_box` charge avec champ assets pre-rempli, `generate` OK, module exterieur count-aware genere, vraie cavite rectangulaire top-open coupee dans le body et non limitee a un sketch.

Le rapport valide `count_aware_storage_sizing: yes`, `asset_cavities_generated: yes`, `asset_cavity_policy: single_asset_fit_rectangular_cavity_v0`, `asset_fit_cavities_planned: 1`, `Asset-fit cavities generated: 1`, `Rectangular cavity cuts: 1`, module environ `50.0 x 39.0 x 48.0 mm`, cavite environ `47.6 x 36.6 x 46.8 mm`, fond restant `1.2 mm`, murs attendus `1.2 mm`, `asset_items_visualized: no`, `Body sizing report`, `Registry validation: ok` et `Print validation: false`.

Regenerate valide : modification d'un count ou d'une dimension, module + cavite recalcules sans doublon. Clear final valide : `clear_bgig_scene` fonctionne et preserve les objets non-BGIG.

Limites maintenues : assets individuels non visualises, cavites par pile/item non generees, pas de solveur global, pas d'optimisation avancee, capacite encore heuristique, aucune impression 3D validee.


## P13-ASSET-M004 - Asset-specific compartments V0 implemente

P13-ASSET-M004 remplace, pour les assets count-aware supportes, la cavite globale M003 par des compartiments rectangulaires top-open par asset source dans le meme module exterieur. La policy active est `per_source_asset_rectangular_compartments_v0`.

Comportement implemente : le moteur conserve le sizing count-aware, calcule un compartiment par asset source, choisit deterministiquement une orientation simple ligne X ou colonne Y selon le fit, puis l'adaptateur Fusion cree une coupe `subtract_rectangular_cavity` par compartiment. Les coupes conservent un fond commun `floor_thickness_mm`; le mur interne minimal est `wall_thickness_mm`. Le debug sketch asset-fit affiche aussi les outlines de compartiments non imprimables.

Reporting ajoute : `asset_compartments_generated`, `asset_compartment_cavities_planned`, `asset_compartment_cavities_refused`, `asset_compartment_debug_outlines`, diagnostics par asset (`asset_id`, `count_read`, dimensions, `capacity_per_stack`, `pile_count`, `declared_capacity`, origine locale, taille cavite, fond et murs attendus). `asset_fit_cavities_planned/generated` reste un compteur compatible des coupes asset-first, incluant les compartiments.

Smoke prepare : avec `coin-tokens,tokens,40,18,16,2,loose` et `status-tokens,tokens,23,10,35,2,loose`, le module attendu est environ `52.8 x 39.0 x 48.0 mm`, avec deux cavites environ `37.6 x 17.6 x 46.8 mm` et `11.6 x 36.6 x 46.8 mm`, fond `1.2 mm`, mur interne `1.2 mm`, `Registry validation: ok` attendu et `Print validation: false`.

Limites maintenues : assets individuels non visualises, cavites par pile/item non generees, pas de solveur global, pas d'optimisation avancee, pas de fillets/conges, pas d'export STL/3MF, aucune impression 3D validee.

Statut : `fusion-validated-v0` apres validation humaine Fusion `P13-ASSET-M004V` confirmee le 2026-07-09 sur `9e050ba`, `print-validated: false`.


## P13-ASSET-M004V - Validation Fusion compartiments asset-specific V0

Validation humaine Fusion confirmee le 2026-07-09 sur `9e050ba`.

Resultats observes : add-in reinstalle par scripts Codex, document Fusion Assembly-compatible, `UI settings loaded: yes`, `quick_asset_box` charge avec champ assets pre-rempli, `generate` OK, module exterieur count-aware genere.

Le rapport valide `asset_cavity_policy: per_source_asset_rectangular_compartments_v0`, `asset_compartments_generated: yes`, `asset_compartment_cavities_planned: 2`, `asset_compartment_cavities_generated: 2`, `Rectangular cavity cuts: 2`, `Body sizing report`, `Registry validation: ok` et `Print validation: false`.

Observation Fusion validee : deux vraies cavites rectangulaires top-open sont coupees dans le body, correspondent aux assets sources `coin-tokens` et `status-tokens`, sont separees par une paroi interne et ne sont pas seulement des sketches. Les debug outlines de compartiments sont visibles. Dimensions observees coherentes : module environ `52.8 x 39.0 x 48.0 mm`, cavite `coin-tokens` environ `37.6 x 17.6 x 46.8 mm`, cavite `status-tokens` environ `11.6 x 36.6 x 46.8 mm`, fond restant `1.2 mm`.

Regenerate valide : modification d'un asset ou d'une dimension, module + compartiments recalcules sans doublon. Clear final valide : `clear_bgig_scene` fonctionne et preserve les objets non-BGIG.

Limites explicitement non validees : UX encore peu claire, champs assets difficiles a comprendre, pas d'onglets/sections/presets ergonomiques, assets individuels non visualises, cavites par pile/item non generees, pas de solveur global, pas d'optimisation avancee, pas de fillets/conges, pas d'export STL/3MF, capacite encore heuristique, aucune impression 3D validee.

Dette UX enregistree : l'interface `quick_asset_box` fonctionne mais reste peu comprehensible pour un humain. Une future mission UI/UX devra clarifier les champs, formats, unites, effets de `count`, dimensions, grille, murs, fond et clearances. Cette dette n'est pas traitee dans P13-ASSET-M004V.

## P13-ASSET-M005 - Per-compartment access notches V0 implemente

P13-ASSET-M005 ajoute une premiere aide de prise par compartiment asset-specific. La policy active est `per_compartment_top_open_rectangular_notch_v0`.

Comportement implemente : chaque compartiment `per_source_asset_rectangular_compartments_v0` peut porter un `asset_access_notch`. La regle V0 place une encoche rectangulaire top-open sur le mur avant du module (`-Y`), centree sur la largeur utile du compartiment. La largeur cible est `18.0 mm`, avec refus sous `6.0 mm` disponible apres marges laterales ; la profondeur cible depuis le haut est `10.0 mm`, avec refus sous `4.0 mm`. Les compartiments non adjacents au mur avant externe sont refuses pour eviter de couper a travers un autre compartiment ou une paroi interne.

Cote Fusion, les notches planifiees sont converties en `FusionFingerNotchCutPlan` avec `source_feature_kind = asset_access_notch` et reutilisent la coupe rectangulaire top-open existante. Le rapport ajoute `asset_access_features_generated`, `asset_access_policy`, `asset_access_notches_planned`, `asset_access_notches_generated`, `asset_access_notches_refused` et les diagnostics par asset/compartiment.

Smoke prepare : avec `coin-tokens,tokens,40,18,16,2,loose` et `status-tokens,tokens,23,10,35,2,loose`, le module attendu reste environ `52.8 x 39.0 x 48.0 mm`, avec deux compartiments et deux encoches d'acces planifiees sur le mur avant. Les notches attendues sont des coupes rectangulaires top-open reelles, pas seulement des sketches.

Limites maintenues : assets individuels non visualises, cavites par pile/item non generees, pas de solveur global, pas d'optimisation avancee, pas de courbes/demi-lunes/scoops, pas de fillets/conges, pas d'export STL/3MF, aucune impression 3D validee.

Statut : `fusion-validated-v0` apres validation humaine Fusion `P13-ASSET-M005V` confirmee le 2026-07-09 sur `baa7cf9`, `print-validated: false`.

## P13-ASSET-M005V - Validation Fusion access notches par compartiment

Validation humaine Fusion confirmee le 2026-07-09 sur `baa7cf9`.

Resultats observes : add-in reinstalle par scripts Codex, document Fusion Assembly-compatible, `quick_asset_box` charge avec champ assets pre-rempli, `generate` OK, module exterieur count-aware genere et compartiments asset-specific generes.

Le rapport valide `asset_cavity_policy: per_source_asset_rectangular_compartments_v0`, deux vraies cavites rectangulaires top-open, paroi interne presente, fond conserve, `asset_access_policy: per_compartment_top_open_rectangular_notch_v0`, `asset_access_features_generated`, `asset_access_notches_planned`, `asset_access_notches_generated`, `Registry validation: ok` et `Print validation: false`.

Observation Fusion validee : deux encoches top-open frontales reelles sont coupees dans le body, ne sont pas seulement des sketches, ne detruisent ni la paroi interne ni le fond. Regenerate valide : modification d'un count ou d'une dimension, module + compartiments + encoches recalcules sans doublon. Clear final valide : `clear_bgig_scene` fonctionne et preserve les objets non-BGIG.

Limites explicitement non validees : UX encore peu claire, assets individuels non visualises, cavites par pile/item non generees, pas de demi-lunes, pas de courbes/scoops, pas de fillets/conges, pas d'export STL/3MF, capacite encore heuristique, aucune impression 3D validee.

Dette UX enregistree : l'interface `quick_asset_box` reste difficile a comprendre. Une future mission UI/UX devra clarifier champs, unites, effets de `count`, grille, walls, floor, clearances, modes et politiques.

## P14-USABLE-ASSET-TRAY-M001 - Layout multi-assets quick_asset_box

Statut : `implemented-core`, validation Fusion sprint P14 requise, `print-validated: false`.

P14-USABLE-ASSET-TRAY-M001 ajoute un layout deterministe plus robuste pour les compartiments asset-specific issus de `quick_asset_box`. Le moteur essaye maintenant les strategies `deterministic_single_row_by_source_asset_v0`, `deterministic_single_column_by_source_asset_v0`, puis `deterministic_shelf_by_source_asset_v0`. La strategie shelf permet de supporter proprement des cas 3 et 4 assets compatibles dans un module count-aware unique, avec compartiments separes, parois internes reportees et encoches frontales planifiees pour les compartiments touches par le mur avant.

Si aucun layout de compartiments ne tient dans l'enveloppe XY utile, le moteur retourne `ASSET_COMPARTMENTS_DO_NOT_FIT` et conserve les tentatives de layout dans `layout_attempts`. Le fallback vers une grande cavite asset-fit unique est supprime quand un layout de compartiments requis est refuse, pour eviter un resultat Fusion trompeur.

Limites : pas de solveur global, pas de backtracking, pas d'optimisation avancee, pas de cavites par pile/item, pas de visualisation d'items individuels, aucune validation Fusion P14 ni impression 3D encore realisee.

## P14-USABLE-ASSET-TRAY-M002 - Printability safety report V0

Statut : `implemented-core`, validation Fusion sprint P14 requise, `print-validated: false`.

P14-M002 ajoute `printability_report_v0` aux modules asset-first generes et aux placements CAD IR. Le rapport verifie les dimensions deja resolues par le moteur : murs externes minimum, paroi interne minimum, fond conserve, profondeur maximale de cavite, profondeur maximale d'encoche et hauteur de module. Il expose `printability_checked: yes` et `printability_validated_by_print: no`.

Le rapport reste volontairement heuristique et report-only : il ne change aucune tolerance par defaut, ne valide aucune impression physique et ne remplace pas une calibration reelle. Le message `quick_asset_box` affiche maintenant les lignes printability et les warnings associes.

## P14-USABLE-ASSET-TRAY-M003 - UX quick_asset_box V0 plus lisible

Statut : `implemented-fusion-ui`, validation Fusion sprint P14 requise, `print-validated: false`.

P14-M003 ameliore la commande Fusion classique sans palette HTML : ajout d'un bloc visible `Quick asset format and units`, exemple inline `coin-tokens,tokens,30,20,20,2,loose`, rappel du format `asset_id,type,count,x_mm,y_mm,z_mm,fit`, explication de `count`, des dimensions en mm, de la semantique cartes/decks et des valeurs `fit`. Les champs parametriques affichent maintenant des labels contextualises pour boite, grille, murs, fond, clearances et profil d'impression. La persistance existante reste inchangee.

## P14-USABLE-ASSET-TRAY-M004 - Presets et scenarios quick asset

Statut : `implemented-smoke-prep`, tests automatises OK, validation Fusion sprint P14 requise, `print-validated: false`.

P14-M004 ajoute un catalogue local `scripts/fusion/quick_asset_presets.json` et un parametre `-Preset` a `scripts/fusion/prepare_quick_asset_test.ps1`. Les presets disponibles sont `p14_complete`, `tokens`, `dice_meeples_generic` et `cards_tokens`. Depuis la correction de gate P14, le preset par defaut est `p14_complete` afin de valider un scenario riche 5 assets ; `-AssetsText` reste un override manuel, et aucun comportement de geometrie produit n'est modifie.
## P14-USABLE-ASSET-TRAY-M005 - Preparation gate Fusion sprint P14

Statut : `gate-prepared-corrected`, preparation gate corrigee pour utiliser le preset riche `p14_complete`, validation humaine Fusion `P14-USABLE-ASSET-TRAY-SPRINT-V` requise, `print-validated: false`.

La premiere preparation utilisait `tokens`, trop proche de P13-ASSET-M005 pour valider le sprint P14. La correction de gate prepare maintenant `p14_complete` : box `220 x 160 x 96`, grid `8 x 5 x 4`, assets `coin-tokens`, `status-tokens`, `damage-tokens`, `dice-set` et `wood-meeples`. Le smoke Fusion doit verifier le sprint P14 complet : layout multi-assets 3 sources tokens avec shelf layout, presets, printability report V0, aide inline quick_asset_box, regeneration sans doublon, clear preserve non-BGIG, et absence de validation impression 3D.
## P15-TRAY-SEMANTICS-ALIGNMENT-SPRINT

Statut : sprint lance apres refus de validation usable P14. P14 est techniquement fonctionnel, mais le sizing par defaut cree des modules trop hauts pour les assets itemises. Objectif P15 : clarifier et corriger les semantiques `z_mm`, `count`, `grid`, groupement et mode de rangement sans solveur global ni nouvelle geometrie complexe.

## P15-M001 - Audit semantique z/grid/grouping

Statut : `done-docs`, ADR acceptee `docs/DECISIONS/ADR-0033-tray-semantics-v0.md`, pas de changement moteur.

Decision : `tokens`, `dice`, `meeples` et `generic` gardent `z_mm` comme dimension unitaire, mais le defaut produit devient `storage_orientation = flat_tray` avec `max_stack_height_mm`. `vertical_stack` conserve l'ancien comportement uniquement en mode explicite. La grille est documentee comme `placement_reservation_lattice_v0`, pas comme taille physique de body.
## P15-M002 - storage_orientation flat_tray V0

Statut : `implemented-core`, tests assets cibles OK, validation Fusion non encore realisee, `print-validated: false`.

P15-M002 introduit les champs additifs `assets[].storage_orientation` (`auto`, `flat_tray`, `vertical_stack`) et `assets[].max_stack_height_mm`. Pour `tokens`, `dice`, `meeples` et `generic`, `auto` se resout maintenant en `flat_tray` : le moteur garde `z_mm` comme epaisseur unitaire, mais limite la hauteur de pile par un plafond produit avant de creer plus de piles XY. Defaults moteur : tokens `12.0 mm`, dice `20.0 mm`, meeples `24.0 mm`, generic `16.0 mm`.

`vertical_stack` conserve explicitement l'ancien comportement qui utilise la hauteur disponible de la boite/grille. Les fixtures historiques a tokens epais `simple_asset_grouping.json` et `simple_asset_executable_plan.json` le declarent maintenant explicitement pour rester des tests legacy, tandis que les nouveaux tests P15 prouvent le defaut `flat_tray`.

Exemple teste : 30 tokens `10 x 10 x 2 mm` passent de `33.6 x 13.6 x 21.8 mm` en `vertical_stack` a `63.6 x 13.6 x 11.8 mm` en `flat_tray`. Avec `max_stack_height_mm = 6`, le meme cas devient `93.6 x 23.6 x 5.8 mm`.

Metadata/reporting moteur : `storage_sizing` transporte `storage_orientation`, `stack_height_policy`, `available_asset_fit_height_mm`, `max_stack_height_mm`, `stack_height_used_mm`, `xy_expansion_used` et `z_expansion_used`.

## P15-M003 - max_stack_height_mm et reporting stack policy

Statut : `implemented-fusion-ui`, tests Fusion skeleton cibles OK, validation Fusion P15 non encore realisee, `print-validated: false`.

P15-M003 expose dans la commande Fusion classique un champ global optionnel `Max stack height mm (quick_asset_box, optional)`. Vide, le moteur garde les defaults `flat_tray` par type. Renseigne, ce champ est sauvegarde dans `bgig_ui_settings.json` sous `quick_asset_box_max_stack_height_mm`, rehydrate a la reouverture, puis applique `assets[].max_stack_height_mm` aux assets temporaires `quick_asset_box` hors cards/sleeved_cards.

Le rapport `quick_asset_box` affiche maintenant `max_stack_height_mm`, `storage_orientation`, `stack_height_policy`, `max_stack_height_mm`, `stack_height_used_mm`, `xy_expansion_used` et `z_expansion_used` par asset et par candidat module. Exemple teste : le scenario deux tokens avec override `6 mm` produit un module `112.0 x 100.0 x 6.0 mm`, `capacity_per_stack 2`, `pile_count 15` pour `coin-tokens`, au lieu d'utiliser la pile par defaut `12 mm`.

## P15-M004 - Grid semantics report V0

Statut : `implemented-reporting`, tests assets et Fusion skeleton cibles OK, validation Fusion P15 non encore realisee, `print-validated: false`.

P15-M004 clarifie que la grille `quick_asset_box` reste une lattice de placement/reservation. Les placements asset-first et le plan Fusion reportent maintenant `grid_semantics: placement_reservation_lattice_v0`, `body_snap_to_grid: no`, `grid_span_is_reserved_space: yes` et `body_size_may_be_smaller_than_grid_span: yes`.

Le body Fusion continue d'utiliser `printable_body_size_mm` ; `theoretical_grid_extent_mm` est un span de reservation/occupation, pas une taille de body a extruder. Le resume `quick_asset_box`, `Module source mapping` et `Body sizing report` exposent cette difference pour eviter une interpretation trompeuse de la grille.

## P15-M005 - Preset smoke P15 realiste

Statut : `gate-prepared`, validation humaine Fusion `P15-TRAY-SEMANTICS-ALIGNMENT-SPRINT-V` requise, `print-validated: false`.

P15-M005 ajoute le preset `p15_tray_semantics` et le met par defaut dans `scripts/fusion/prepare_quick_asset_test.ps1`. Le scenario prepare : box `220 x 160 x 60`, grid `8 x 5 x 3`, `max_stack_height_mm = 18`, assets `coin-tokens`, `status-tokens`, `dice-set`, `wood-meeples` et `cubes`.

Validation automatique locale : le preset lit 5 assets, genere 4 candidats/modules places, planifie 5 compartiments et 5 encoches, et produit des modules bas : tokens `132.8 x 22.0 x 18.0 mm`, dice `132.0 x 20.0 x 18.0 mm`, meeples `112.8 x 16.8 x 18.4 mm`, cubes `98.4 x 10.4 x 17.2 mm`. Le rapport attendu expose `flat_tray`, `stack_height_policy`, `max_stack_height_mm`, `grid_semantics: placement_reservation_lattice_v0`, `body_snap_to_grid: no`, printability report et `Print validation: false`.

Gate humaine active : ouvrir Fusion, verifier les settings precharges, generer, verifier que les modules ne deviennent pas des tours hautes, modifier `count` ou `max_stack_height_mm`, lancer `regenerate` sans doublon, puis `clear_bgig_scene` avec preservation non-BGIG.

## P15-TRAY-SEMANTICS-ALIGNMENT-SPRINT-V - Validation Fusion

Validation humaine Fusion confirmee le 2026-07-09 sur le commit `648eba9`.

Resultats observes : add-in reinstalle par scripts Codex, document Fusion Assembly-compatible, settings UI charges, mode `quick_asset_box`, preset `p15_tray_semantics`, box `220 x 160 x 60`, grid `8 x 5 x 3` et `Max stack height mm = 18` rehydrates correctement. `generate`, `regenerate` et `clear_bgig_scene` fonctionnent ; regenerate remplace sans doublon ; les objets non-BGIG sont preserves.

P15 est valide comme realignement semantique asset-first : `z_mm` et `count` sont clarifies, `flat_tray` devient le defaut pour les assets simples, `max_stack_height_mm` est expose et pris en compte, l'expansion XY precede l'expansion Z, et la grille est reportee comme `placement_reservation_lattice_v0` avec `body_snap_to_grid: no`. Les modules ne deviennent plus automatiquement des tours hautes et restent autour de 17-18 mm dans le smoke P15.

Limites maintenues : `print-validated: false`, pas de packing 2D ergonomique, pas d'optimisation avancee, encoches primitives, UX encore perfectible, pas d'export STL/3MF, pas de fillets/conges, pas de visualisation individuelle des items.

Dette produit ouverte pour P16 : le layout `flat_tray` V0 etale encore les piles principalement en ligne X, ce qui produit des modules longs peu ergonomiques. Le sprint suivant doit introduire un packing 2D de piles/compartiments avec ratio cible, longueur maximale, lignes/colonnes et reporting explicite.

## P16-ERGONOMIC-2D-TRAY-PACKING-SPRINT

Statut : sprint lance apres validation humaine P15. Objectif : remplacer le comportement `flat_tray` lineaire par une heuristique deterministe `flat_tray_2d_v0` pour les assets simples (`tokens`, `dice`, `meeples`, `generic`), sans solveur global, backtracking ni nouvelle geometrie complexe.

Cible produit : organiser les piles en colonnes/rangees, limiter les longues barres X, conserver des modules bas, maintenir compartiments/encoches V0, expliciter `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm` et les warnings si un layout 2D raisonnable ne tient pas.

Gate attendue : validation Fusion `P16-ERGONOMIC-2D-TRAY-PACKING-SPRINT-V` apres preparation d'un preset `p16_ergonomic_tray_packing`. `Print validation: false` reste obligatoire.

## P16-M001 - Strategie flat_tray_2d documentee

Statut : `done-docs`, ADR acceptee `docs/DECISIONS/ADR-0034-flat-tray-2d-packing-v0.md`, pas de changement moteur.

Decision : `flat_tray_linear_v0` nomme l'ancien comportement P15 qui etale les piles surtout sur une ligne X. `flat_tray_2d_v0` devient la cible par defaut pour `tokens`, `dice`, `meeples` et `generic` : calcul de `items_per_pile`, `pile_count`, puis repartition en `pile_grid_columns` x `pile_grid_rows` selon un ratio cible et une longueur maximale souple, sans solveur global ni backtracking.

La grille globale reste une lattice de reservation (`placement_reservation_lattice_v0`) et le body ne snap pas physiquement a la grille (`body_snap_to_grid: no`). `vertical_stack` reste un mode explicite/legacy, pas le defaut.

## P16-M002 - Packing 2D V0 des piles implemente

Statut : `implemented-core`, tests assets et suite complete OK, validation Fusion P16 non encore realisee, `print-validated: false`.

P16-M002 remplace le packing interne `flat_tray_linear_v0` par `flat_tray_2d_v0` pour les assets simples en `flat_tray`. Le moteur calcule toujours `capacity_per_stack`, `pile_count` et `items_per_pile`, puis choisit une grille locale `pile_grid_columns x pile_grid_rows` selon un ratio cible `1.6` et une longueur maximale heuristique. `vertical_stack` conserve le packing lineaire legacy.

Exemples testes : 30 tokens `10 x 10 x 2` avec stack max par defaut passent de l'ancien module P15 `63.6 x 13.6 x 11.8` a `33.6 x 23.6 x 11.8` en `3 x 2` piles ; avec `max_stack_height_mm = 6`, le module passe de `93.6 x 23.6 x 5.8` a `53.6 x 33.6 x 5.8` en `5 x 3` piles. 8 des de 16 mm sont testes en `4 x 2`, et 12 piles de cubes en `4 x 3`.

Metadata ajoutee : `tray_packing_policy`, `target_aspect_ratio`, `max_module_length_mm`, `pile_grid_columns`, `pile_grid_rows`, `linear_layout_avoided` sur `storage_sizing`, diagnostics par asset et compartiments. Compartiments, cavites et notches utilisent deja les nouvelles enveloppes, sans cavite par item.

## P16-M003 - Diagnostics cavites/notches alignes sur packing 2D

Statut : `implemented-reporting`, tests Fusion skeleton cibles OK, validation Fusion P16 non encore realisee, `print-validated: false`.

Les compartiments, cavites rectangulaires top-open et access notches suivent deja les enveloppes `flat_tray_2d_v0` produites par P16-M002. P16-M003 rend ce lien explicite dans les diagnostics Fusion : `asset_sizing_diagnostics`, `asset_cavity_diagnostics`, `asset_access_diagnostics` et `module_candidate_sizing_diagnostics` transportent maintenant `tray_packing_policy`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm` et `linear_layout_avoided` quand disponibles.

Aucune cavite par item ou par pile n'est ajoutee. Les notches restent rectangulaires top-open et non destructives selon les regles P13/P14 existantes.

## P16-M004 - UI et reporting P16 clarifies

Statut : `implemented-fusion-ui`, tests automatises OK, validation Fusion P16 non encore realisee, `print-validated: false`.

P16-M004 rend le packing 2D exploitable depuis la commande Fusion classique `quick_asset_box`. Deux champs optionnels sont ajoutes et persistes dans `bgig_ui_settings.json` : `Target aspect ratio (quick_asset_box, optional)` et `Max module length mm (quick_asset_box, optional)`. Ils alimentent la config temporaire sous `assets[].target_aspect_ratio` et `assets[].max_module_length_mm` pour les assets itemises simples, sans toucher aux cards/sleeved_cards.

Le resume Fusion affiche maintenant explicitement `target_aspect_ratio`, `max_module_length_mm`, `tray_packing_policy`, `pile_grid_columns`, `pile_grid_rows` et `linear_layout_avoided` dans les diagnostics asset, module, cavite et access notch. Le schema JSON public accepte les deux champs additifs optionnels sur `assets[]`; les valeurs non positives sont refusees par validation.

Limites maintenues : pas de solveur global, pas de backtracking, pas de nouvelle geometrie, pas de cavites par pile/item, pas de visualisation individuelle des assets et aucune validation d'impression.

## P16-M005 - Preset smoke P16 ergonomique

Statut : `implemented-smoke-prep`, tests automatises OK, validation Fusion P16 non encore realisee, `print-validated: false`.

Le script `scripts/fusion/prepare_quick_asset_test.ps1` utilise maintenant `p16_ergonomic_tray_packing` par defaut. Ce preset prepare une box `240 x 170 x 60`, une grille `8 x 5 x 3`, `max_stack_height_mm = 18`, `target_aspect_ratio = 1.4`, `max_module_length_mm = 70` et cinq assets : `coin-tokens`, `status-tokens`, `damage-tokens`, `dice-set`, `wood-meeples`.

Assets exacts : `coin-tokens,tokens,48,10,10,2,loose; status-tokens,tokens,36,10,10,2,loose; damage-tokens,tokens,24,14,12,2,loose; dice-set,dice,8,16,16,16,loose; wood-meeples,meeples,18,12,12,8,loose`.

Objectif de gate : verifier dans Fusion que le rapport expose `flat_tray_2d_v0`, des `pile_grid_columns` / `pile_grid_rows` multi-ranges, `linear_layout_avoided`, les champs P16 rehydrates, les compartiments/encoches existants, `printability_checked: yes`, `Registry validation: ok` et `Print validation: false`.

## P16-M006 - Preparation gate Fusion P16

Statut : `gate-prepared`, validation humaine Fusion `P16-ERGONOMIC-2D-TRAY-PACKING-SPRINT-V` requise, `print-validated: false`.

La gate P16 doit utiliser le preset `p16_ergonomic_tray_packing`, mode `quick_asset_box`, action `generate` ou `regenerate` si une scene BGIG existe deja, generation `compact_only`, box `240 x 170 x 60`, grid `8 x 5 x 3`, `max_stack_height_mm = 18`, `target_aspect_ratio = 1.4`, `max_module_length_mm = 70`.

Validation attendue : `tray_packing_policy: flat_tray_2d_v0`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm`, `linear_layout_avoided`, compartiments et encoches V0 conserves, regenerate sans doublon, clear preserve non-BGIG, `Registry validation: ok`, `Print validation: false`.


## P16-ERGONOMIC-2D-TRAY-PACKING-SPRINT-V - Validation Fusion

Statut : `fusion-validated-v0` apres validation humaine Fusion du 2026-07-09 sur `a75688e`, `print-validated: false`.

Resultats valides : add-in reinstalle par les scripts Codex, document Fusion Assembly-compatible, settings UI charges, mode `quick_asset_box`, preset `p16_ergonomic_tray_packing`, box `240 x 170 x 60`, grid `8 x 5 x 3`, `Max stack height mm = 18`, `Target aspect ratio = 1.4`, `Max module length mm = 70` et assets pre-remplis.

Le smoke Fusion valide `generate`, `tray_packing_policy: flat_tray_2d_v0`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm`, `linear_layout_avoided: yes`, modules non reduits a des barres 1D quand un packing 2D raisonnable est possible, module tokens compact et compartimente, des en `4 x 2`, meeples en `3 x 3`, modules generes/places, compartiments asset-specific, encoches top-open quand possible, registry OK, regenerate sans doublon et clear preserve non-BGIG.

Reporting valide : `grid_semantics: placement_reservation_lattice_v0`, `body_snap_to_grid: no`, grid span de reservation distinct de la taille physique du body, `printability_report_v0`, `printability_checked: yes`, `printability_validated_by_print: no`, warnings printability lisibles et `Print validation: false`.

Limites maintenues : packing encore heuristique, pas de solveur global, pas d'optimisation avancee, encoches primitives, UX perfectible, pas de palette HTML, pas de tableau assets avance, pas d'export STL/3MF valide, pas de fillets/conges, pas de courbes/demi-lunes/scoops, pas de visualisation individuelle des items, aucune impression 3D validee.

## P17-PRINTABLE-EXPORT-AND-PREPRINT-SPRINT

Statut : sprint lance apres validation humaine P16. Objectif : definir puis implementer une premiere chaine V0 de pre-impression : export de modules imprimables, manifeste export, dossier de sortie propre, rapport printability plus actionnable et preparation d'un pack imprimable sans pretendre a une validation physique.

Garde-fous : export depuis Fusion uniquement si l'API est fiable, pas d'export des objets non-BGIG, references, debug sketches/outlines ou helpers/source occurrences, `print-validated: false` obligatoire, aucune promesse `ready to print` absolue. P17-M001 a ouvert le sprint ; P17-M006 prepare maintenant la gate humaine export/preprint.


### P17-M001 - ADR export/preprint V0

Statut : `done-docs`. `ADR-0035-printable-export-preprint-v0.md` fixe le contrat V0 : export Fusion-only, cible STL par module, 3MF reporte sauf API simple, exclusion stricte des objets non-BGIG/references/debug/helpers/source/exploded par defaut, noms deterministes, manifeste JSON/Markdown et `print_validated: false` obligatoire.

Suite realisee : P17-M002 a implemente `export_printables` sans simuler de succes si l'API Fusion refuse l'export.


### P17-M002 - Action Fusion export_printables

Statut : `implemented-fusion-unvalidated`. La commande Fusion classique accepte maintenant l'action `export_printables`. Elle inspecte la scene BGIG courante, exige exactement une racine BGIG, collecte seulement les bodies tagues `bgig:role = module_body`, exporte chacun en STL via `design.exportManager.createSTLExportOptions(...)/execute(...)`, puis affiche un rapport avec compteurs, fichiers exportes, refus, `manifest_json`, `manifest_markdown` et `print_validated: false`.

Exclusions V0 : scene roots, scene root components, occurrences compactes/eclatees, references/outlines, sketches debug, features/cuts et objets non-BGIG ne sont pas exportes directement. Ils sont soit ignores, soit listes comme refuses avec raison. Si `design.exportManager` est indisponible ou si Fusion refuse l'export STL, le rapport passe en `technical_gate`/`partial_or_failed` au lieu de simuler une reussite.

Suite realisee : P17-M003 a ajoute les manifestes export.


### P17-M003 - Export manifest V0

Statut : `implemented-fusion-unvalidated`. L'action `export_printables` ecrit maintenant `bgig_export_manifest.json` et `bgig_export_manifest.md` dans le dossier export. Le JSON expose `schema_version: bgig.export_manifest.v0`, politique export, format, timestamp, statut, settings UI, source CAD IR si disponible, assets, modules, fichiers exportes, refus, warnings et `print_validated: false`.

Limite : le manifeste est un artefact d'audit preprint. Il ne prouve pas la printability physique, ne remplace pas la gate Fusion et ne valide aucune impression. Suite realisee : P17-M004 a ajoute les blockers printability.


### P17-M004 - Printability blockers V0

Statut : `implemented-core-fusion-reporting`. `printability_report_v0` expose maintenant `printability_status`, `printability_export_allowed`, `issue_counts` et `issues[]` avec severites `warning`/`blocker`. Les anciens `warnings[]` restent presents pour compatibilite.

Regle V0 : les murs/fonds sous minimum et une cavite supprimant toute la hauteur deviennent des blockers et desactivent `printability_export_allowed`; la profondeur d'encoche importante, les modules hauts, cavites non planifiees et l'absence de validation physique restent des warnings. Le resume Fusion `quick_asset_box` affiche `printability_status` et `printability_export_allowed`. Suite realisee : P17-M005 a ajoute le protocole preprint.


### P17-M005 - Calibration coupon / preprint check V0

Statut : `protocol-ready`. Le sprint P17 ne cree pas encore de geometrie coupon Fusion ; P17-M005 ajoute plutot `docs/PREPRINT_CHECK_PROTOCOL.md` et `examples/preprint_check_v0.json` pour cadrer une future session preprint a partir du dossier export, des STL et des manifestes.

Le protocole conserve `print_validated: false` et distingue `not_printed`, `printed_unmeasured`, `measured_local_ok`, `measured_local_ko` et `retest_required`. Suite realisee : P17-M006 prepare la gate Fusion P17 export complet.


### P17-M006 - Gate Fusion P17 export complet

Statut : `done`, `fusion-validated-v0`, `print-validated: false`. Le preset `p17_printable_export` prepare le scenario riche 5 assets valide en P16 puis ajoute le focus export : action `export_printables`, STL V0 par body `module_body`, manifestes `bgig_export_manifest.json` / `bgig_export_manifest.md`, refus des entites non imprimables et `print_validated: false`.

Preparation locale : add-in installe dans AppData via `scripts/fusion/prepare_quick_asset_test.ps1 -Preset p17_printable_export`, settings UI ecrits en `quick_asset_box`, action initiale `generate`.

## P17-PRINTABLE-EXPORT-AND-PREPRINT-SPRINT-V - Validation Fusion

Statut : `fusion-validated-v0` apres validation humaine Fusion du 2026-07-10 sur le commit `5d99d36`, `print-validated: false`.

Le smoke test confirme dans un document Fusion Assembly-compatible que les settings du preset `p17_printable_export` sont charges, que `quick_asset_box` genere les modules, compartiments et encoches V0, puis que l'action `export_printables` ecrit un STL par module BGIG imprimable et les manifestes `bgig_export_manifest.json` / `bgig_export_manifest.md` dans un dossier d'export dedie.

Le filtre export est valide fonctionnellement : objets non-BGIG, racines, references/outlines, sketches de debug, helpers, sources et vues eclatees ne sont pas exportes. Les manifestes tracent scene, assets, modules, dimensions, warnings et statut print. `clear_bgig_scene` reste fonctionnel apres export et preserve les objets non-BGIG.

P17 valide une chaine technique export/preprint V0, pas le produit cible ni une promesse d'impression. Aucune impression 3D physique, validation slicer, validation materiau, validation dimensionnelle reelle ou garantie `ready to print` n'est revendiquee.

## P18-M001 - Audit vision versus etat reel

Statut : `done-docs`. `docs/VISION_GAP_ANALYSIS.md` confirme que la North Star reste valide : BGIG dispose d'une fondation asset-first/Fusion/preprint solide, mais le produit actuel reste un atelier de generation de bacs et non un concepteur de rangement complet.

Dette prioritaire : `quick_asset_box` est une commande de test/developpement, la grille est une lattice de reservation et le placement greedy n'est pas un solveur de remplissage. P18 recadre donc les prochains travaux comme architecture produit : plan de boite, intentions, modules, reservations, variantes et UX de composition. Aucun moteur, schema public ou comportement Fusion n'est modifie.

## P18-M002 - UX produit cible

Statut : done-docs. UX_PRODUCT_VISION.md definit six ecrans de la boite a l'export et confirme que la commande Fusion classique reste un outil de smoke/dev, non l'UX finale.

## P18-M003 - Modele produit volumetrique cible

Statut : done-docs. VOLUMETRIC_PRODUCT_MODEL.md separe explicitement la boite, assets, intentions, reservations, layers, modules, compartiments, variantes, volumes libres et export. Fusion reste une projection.

## P18-M004 - Roadmap solver/box fill

Statut : done-docs. BOX_FILL_SOLVER_ROADMAP.md separe six niveaux, recommande ox_fill_v0_manual_modules et interdit de sauter directement au solveur global.

## P18-M005 - ADR architecture UX

Statut : done-docs, ADR-0036 Propose. CommandInputs Fusion reste dev/smoke; toute palette persistante ou app locale/web exige une gate humaine avant implementation.

## P18-M006 - Recommandation P19

Statut : `done-docs`. P19 recommande est `P19-BOX-FILL-MANUAL-MODULES-SPRINT`: premier `BoxFillPlan` manuel, valide par collisions, reservations, couverture et volume libre. P19 est bloque par gate humaine avant toute extension de modele executable.

## P18-VISION-UX-VOLUMETRIC-REBASE-SPRINT - Validation strategique

Statut : `accepted` le 2026-07-10. Les livrables P18 sont acceptes : audit d'ecart, UX cible, modele volumetrique, roadmap solver, ADR-0036 et recommandation P19. La North Star reste le rangement complet dans le volume X/Y/Z de la boite; la commande Fusion classique reste une surface de dev, smoke, compatibilite et actions CAD/export, jamais l'UX finale.

ADR-0036 est acceptee comme direction de roadmap, sans autoriser de palette, d'app ni de dependance UI lourde. L'extension additive, versionnee, CAD-agnostic et retrocompatible de `BoxFillPlan` est autorisee pour P19. La premiere surface persistante reste une gate humaine distincte.

## P19-BOX-FILL-MANUAL-MODULES-SPRINT

Statut : `authorized`. Le sprint doit produire dans le moteur Python pur un plan de boite manuel, verifiable et explicable. Il n'autorise ni solveur automatique, ni palette/app, ni nouvelle geometrie Fusion, ni changement de tolerance.
## P19-M001 - Contrat BoxFillPlan V0

Statut : `done`. ADR-0037 accepte `box_fill_plan.v0` comme extension optionnelle et CAD-agnostic. Le contrat verrouille les allocations explicites, reservations, layers, modules manuels, coverage et FreeVolume aggregate; Fusion reste une projection future. Suite autorisee : P19-M002, modeles et loader purs.
## P19-M002 - Modeles et chargement additif

Statut : `implemented-core`. Le coeur Python charge maintenant le bloc optionnel `box_fill_plan.v0` dans des dataclasses pures : BoxFillBox derive de la boite existante, modules manuels, reservations, layers, allocations explicites et references vers `Cavity`/`Feature` existants. Les JSON historiques restent inchanges lorsque le bloc est absent. La fixture `examples/box_fill_manual_v0.json` et les tests couvrent chargement, schema et retrocompatibilite.

Limite : ce lot ne valide pas encore limites, collisions, references, coverage ni FreeVolume; ces analyses sont le prochain lot P19-M003.
## P19-M003 - Validation, coverage et FreeVolume aggregate

Statut : `implemented-core`. `validate_config` raccorde `BoxFillPlan` a une analyse pure : limites du volume utile, dimensions, IDs, layers, collisions modules/reservations, exception d'overlap mutuelle explicite, references, allocations et coverage. Les assets non couverts et sur-alloues sont des erreurs actionnables. `FreeVolume` calcule le volume total libre par soustraction des modules et reservations declares, avec qualification `aggregate_only` et sans pretendre connaitre les regions libres utilisables.

Limites : aucun solveur, regions libres exactes, score de variantes, support physique ou projection Fusion n'est ajoute.
## P19-M004 - Rapports et transport CAD IR BoxFillPlan

Statut : `implemented-core`, `implemented-cad-ir-metadata`. Les rapports Markdown/JSON exposent `box_fill_plan` avec box derivee, assets, layers, reservations, modules manuels, allocations, compartiments/features references, coverage, validation et FreeVolume aggregate. La CAD IR transporte le meme contrat en `metadata.box_fill_plan`, sans creer de composant, operation, cut ou visualisation Fusion.

Limites : la CAD IR est un transport inspectable; Fusion ne consomme pas encore ce plan. Aucun solveur, variante automatique, region libre exacte, palette ou nouvelle geometrie n'est ajoute.
## P19-BOX-FILL-MANUAL-MODULES-SPRINT - Cloture

Statut : `done`, `implemented-core`, `implemented-cad-ir-metadata`. P19 fournit la premiere source de verite executable d'une boite complete : `box_fill_plan.v0`, BoxFillBox derivee, assets existants, layers, reservations non imprimables, modules manuels, allocations explicites, references Cavity/Feature, coverage, validation 3D et FreeVolume aggregate. Les rapports et la CAD IR exposent ce plan sans le recalculer ni le materialiser dans Fusion.

Preuves : 223 tests automatises, fixture `examples/box_fill_manual_v0.json`, sorties CLI Markdown/JSON/CAD IR et metadata inspectable. P19 n'est ni une validation Fusion de BoxFillPlan, ni une impression physique, ni un solveur, ni une UI persistante.

Prochaine gate : acceptation humaine de `P20-BOX-FILL-GREEDY-2D-SPRINT` decrit dans `docs/P20_RECOMMENDATION.md`. La gate palette/app ADR-0036 reste distincte.
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
## P21 - Portefeuille de variantes deterministes

Statut : `done`, `implemented-core`, `implemented-cli`, `implemented-cad-ir-metadata`, `print-validated: false`.

P21 livre `box_fill_variants.v0` : un portefeuille borne de policies P20 deterministes, deduplique par geometrie, avec sous-scores exposes, front Pareto, profils de preference transparents et recommandation uniquement parmi les variantes `solved`. Les sorties sont lisibles en Markdown/JSON, comparables dans un tableau HTML statique autonome, et exportables sous forme de selection explicite avec metadata CAD IR. La fixture `examples/p21/portfolio.json` prouve plusieurs layouts reproductibles.

Limites : aucun backtracking, solveur global, recherche exhaustive, UI persistante, materialisation Fusion, validation ergonomique ou impression reelle. La prochaine etape produit reste la gate ADR-0036 de choix de surface persistante.
## P22 - Gate de surface UX persistante

Statut : `done-docs`, gate humaine active.

Le rapport `docs/P22_UX_SURFACE_GATE_REPORT.md` compare commande Fusion, palette Fusion, app locale et trajectoire hybride. Il recommande une app locale de conception comme surface principale et Fusion comme adaptateur CAD/export, mais n autorise aucune implementation : le choix de surface et de stack reste une decision humaine explicite selon ADR-0036.
## P23 - Local Composer

Statut : `done`, `implemented-local-ui`, `implemented-loopback-adapter`, `print-validated: false`.

La validation humaine D du 2026-07-10 est appliquee par ADR-0040. `frontend/` apporte une interface React/TypeScript/Vite claire et progressive : dimensions utiles de la boite, inventaire des assets, reservations non imprimables, modules candidats, preference, comparaison P21, selection, verrouillage local et telechargement de la decision. L interface ne recalcule pas le placement : elle appelle `local_composer.py`, qui reconstruit les contrats moteurs existants, execute P21 et produit une CAD IR `cad_ir.v0` avec selection explicite.

Securite et frontieres : l API est standard-library, liee a `127.0.0.1`/`localhost`, limite les requetes JSON et n autorise CORS que depuis les deux origines Vite locales. Les projets sont importes et exportes par le navigateur ; aucune ecriture arbitraire de fichier, persistence distante, cloud, authentification ou materialisation Fusion n est introduite.

Preuves locales : tests `test_local_composer.py` (draft deterministe, export, erreurs de schema, HTTP/CORS), build React/Vite et recette loopback `starter -> portefeuille -> selection -> CAD IR` passes. La recette visuelle automatisee par navigateur n a pas pu etre executee car le runtime navigateur local a ete bloque par le sandbox Windows avant ouverture ; cela ne remet pas en cause les preuves HTTP/build mais reste une verification visuelle a refaire dans un environnement navigateur disponible.

Limites : les scores restent des proxies P21, une impression/ergonomie physique n est pas validee, Fusion ne consomme pas encore la selection P23 et le draft V0 ne propose pas encore une edition UX complete des allocations multi-assets. Prochaine mission ready : `P24-M001 - Qualite du projet local`.
## P24 - Qualite du projet local

Statut : `done`, `implemented-local-ui`, `implemented-validation`, `print-validated: false`.

Le Studio local accepte maintenant une selection explicite de plusieurs assets par module candidat. Une allocation deja choisie dans un autre module est lisible et bloquee dans l interface. Avant chaque generation, une prevalidation pure TypeScript affiche les erreurs actionnables : dimensions, quantites, layers, IDs, enums, allocations absentes, inconnues ou dupliquees. L import refuse les fichiers qui ne respectent pas la structure V0 avant de les afficher, puis liste les corrections metier restantes.

Le moteur reste la source de verite : la prevalidation est une aide ergonomique qui ne recalcule ni score ni placement. Le contrat `bgig.local_composer.v0` est inchange. Preuves : build Vite, verification comportementale du module TypeScript et regression Python qui confirme les allocations multi-assets dans le plan P21 resolu.

Limites : l inspection navigateur reste a rejouer dans un runtime non bloque par le sandbox Windows ; les templates de demarrage, la persistence avancee, Fusion et les validations physiques restent hors P24. Prochaine mission ready : `P25-M001 - Demarrage guide par modele de jeu`.
## P25 - Demarrage guide par modele de jeu

Statut : `done`, `implemented-local-ui`, `implemented-loopback-adapter`, `print-validated: false`.

Le Studio propose trois points de depart locaux : boite mixte, jeu de cartes et boite avec plateau. Chaque carte explique le cas vise et charge un draft V0 independant en memoire ; le projet courant reste exportable par le navigateur et aucun catalogue distant n est consulte. L endpoint loopback `/api/starters` reste borne a localhost et expose le meme contrat de draft que l edition manuelle.

Preuves : les trois drafts passent par P21 avec une recommandation, les tests Python couvrent le catalogue et l endpoint, la recette HTTP verifie catalogue, CORS, UI servie et generation. Le runtime navigateur de recette est bloque par le sandbox Windows avant ouverture, donc l inspection visuelle reste a rejouer ailleurs.

Limites : ces modeles sont des hypotheses locales a mesurer et ajuster ; aucune bibliotheque partagee, sauvegarde serveur, Fusion, impression ou ergonomie physique n est validee. Prochaine mission ready : `P26-M001 - Resume de preparation avant generation`.

## P26 - Resume de preparation avant generation

Statut : `done`, `implemented-local-ui`, `implemented-validation`, `print-validated: false`.

Avant de lancer P21, le Studio affiche maintenant un resume derive du draft : nombre d assets, allocations candidates, modules, reservations, layers et corrections restantes. Un etat pret ou a completer est explicite et la section rappelle que cette lecture ne remplace ni le moteur, ni une mesure reelle, ni une validation d impression, d ergonomie ou Fusion.

Preuves : build Vite et verification comportementale TypeScript pour un draft pret puis une allocation manquante. Le resume utilise `validateDraft` et ne cree aucun score ou placement nouveau. Inspection navigateur toujours a rejouer hors sandbox Windows. Prochaine mission ready : `P27-M001 - Explication des compromis de proposition`.

## P27 - Explication des compromis de proposition

Statut : `done`, `implemented-local-ui`, `print-validated: false`.

Les cartes P21 presentent desormais une intention lisible, le cas dans lequel choisir la variante, le compromis a surveiller et une explication courte de chaque sous-score. Les raisons techniques brutes restent accessibles par divulgation progressive pour les utilisateurs experts et dans les exports, mais ne sont plus le premier message pour un debutant. Les policies, scores, recommendation et solveur restent strictement inchanges.

Preuves : build Vite et verification TypeScript des cinq policies bornees, des explications de scores et du fallback. Inspection navigateur toujours a rejouer hors sandbox Windows. La prochaine etape n est pas autonome : `P28-GATE`, materialisation Fusion d une selection, exige une validation humaine et un smoke Fusion reel.

## P28 - Pont Fusion de selection locale

Statut : `implemented-cad-ir-selection-bridge`, `technical-path-observed`, `product-ux-rejected`, `print-validated: false`.

La gate de scope P28 est approuvee le 2026-07-11. L export local convertit a present la variante P21 selectionnee en composants CAD IR `rectangular_blank` explicites, un par module imprimable, en recopiant strictement ses origines et dimensions resolues. Fusion consomme ce contrat existant sans connaitre P21, sans recalcul de placement ni modification de tolerance.

Preuves hors Fusion : les tests Local Composer et CLI chargent la scene dans `generation_plan_from_cad_ir`; l export reel `mixed-box` produit trois composants et un plan de trois blanks. Le retour utilisateur observe le chemin mais rejette le message et les blocs comme experience produit. P28 ne recoit donc pas `fusion-validated` et P31 doit apporter parois, fond et logements avant une nouvelle validation Fusion ; aucune ergonomie, slicer ou impression n est validee.
## P29 - Redressement produit et UX premium

Statut : `done-docs`, `accepted-product-direction`, `print-validated: false`.

Le retour humain de P28 confirme que le raccord CAD IR genere bien un artefact technique mais echoue comme experience produit : dialogue Fusion technique en anglais, telemetrie brute et simples enveloppes sans bacs fonctionnels. P28 est donc requalifie `KO produit/UX`, sans annuler ses preuves de raccord.

L objectif actif accepte ADR-0042 : Studio principal, palette Fusion secondaire, vrais bacs avant esthetique, parametres vivants et mecanismes prepares sous gates physiques. `docs/PREMIUM_PRODUCT_EXECUTION_PLAN.md` decoupe la trajectoire P29 a P35. La direction P30 est maintenant implementee ; la prochaine gate est P31, strategie de vrais bacs.
## P30 - Studio vivant et parcours novice

Statut : `implemented-local-ui`, `browser-inspection-pending`, `print-validated: false`.

La direction visuelle `Atelier de rangement` approuvee le 2026-07-11 est maintenant materialisee dans le Studio local. La boite est l element central : ses dimensions, sa capacite indicative, ses reservations et les positions connues se mettent a jour immediatement. Le parcours est reduit a cinq etapes simples (boite, contenu, organisation, idees, suite) ; les reservations, candidats et le telechargement technique restent explicitement en mode expert. Les statuts `A explorer`, `A verifier dans Fusion` et `A imprimer et mesurer` ne sont plus caches dans une telemetrie brute.

Preuves : build TypeScript/Vite, test de contrat frontend P30, suite Python complete (248 tests), API loopback et UI locale repondent en HTTP 200. La connexion de recette navigateur a echoue avant ouverture a cause du sandbox Windows (`apply deny-read ACLs`) ; l inspection visuelle automatisee reste donc a rejouer dans un environnement navigateur disponible.

Limites : l apercu est une carte de rangement, pas une geometrie de bac. Il ne valide ni parois, ni fond, ni logement, ni Fusion, ni slicer, ni impression. Prochaine gate : P31, strategie de projection vers de vrais bacs.
## P31 - Gate bacs fonctionnels

Statut : `implemented-cad-ir-open-top-trays`, `fusion-validated`, `print-validated: false`.

Le rapport P31 reutilise les contrats deja existants : P21 fournit l enveloppe resolue, CAD IR connait les cavites, et l adaptateur Fusion sait planifier des coupes rectangulaires top-open. La recommandation est volontairement petite : un bac ouvert par module selectionne, sans compartiment asset-specific, encoche, changement de tolerance ou calcul Fusion. P31 est approuve et le code est livre ; la validation Fusion reste obligatoire avant toute qualification Fusion.
## P31-M001 - Bacs ouverts depuis une selection P21

La selection locale transforme chaque module imprimable en bac ouvert : enveloppe P21 conservee, parois de 1.2 mm, fond de 1.2 mm et cavite `free` top-open. La CAD IR porte une operation `subtract_rectangular_cavity`, une trace des assets associes et un statut `planned_for_fusion_smoke`. Les modules trop petits sont refuses avec `P31_TRAY_CAVITY_NOT_FEASIBLE`.

Preuves : tests de projection et de refus, plan Fusion hors API avec trois cavites pour `mixed-box`, CLI P31, suite complete de 249 tests et build Studio. Limites : aucune scene Fusion n a encore ete observee, aucune capacite asset-specific, encoche, forme ou impression n est validee. Prochaine gate : smoke Fusion P31.
## P31 Fusion smoke - Validation humaine

Retour humain : `P31 Fusion OK`. Les trois bacs ouverts `mixed-box` sont observes dans Fusion avec parois, fond et cavite ouverte. Cette validation couvre le chemin selection P21 -> CAD IR -> coupes Fusion pour le smoke P31 uniquement. L ajustement des assets, les compartiments, le slicer et l impression restent non valides.
## P32 - Palette Fusion secondaire

Statut : `implemented-fusion-palette`, `fusion-smoke-required`, `print-validated: false`.

L ouverture normale de l add-in montre maintenant `BGIG - Atelier de rangement`, une petite palette locale en francais. Elle resume trois choses utiles : le design recu, la scene Fusion et le statut de fabrication. Elle propose seulement `Previsualiser`, `Mettre a jour la scene`, `Exporter les bacs` et un acces volontaire aux reglages experts. Les chemins CAD, diagnostics bruts et le formulaire CommandInputs ne sont plus la premiere experience.

Le bridge ne recalcule rien : il relit l inspection de scene et reutilise les actions existantes de generation/regeneration/export. La palette affiche explicitement que la geometrie a ete observee dans Fusion mais que l impression ne reste pas validee. Preuves hors Fusion : 87 tests Fusion hors API, `python -m py_compile` et `git diff --check` OK. Prochaine action : P32-GATE, smoke humain de la palette dans Fusion.

## P32 Fusion smoke - Validation humaine

Retour humain : `P32 Fusion OK`.

La palette secondaire `BGIG - Atelier de rangement` est acceptee dans Fusion. Elle remplace bien le formulaire technique comme ouverture normale et conserve le formulaire historique comme recours expert. Le smoke couvre la lecture simple du design et de la scene, les actions de previsualisation/mise a jour/export et la lisibilite du statut de fabrication. P32 est donc `fusion-validated`.

Limites maintenues : aucune promesse de fit asset-specific, de slicer ou d impression. Prochaine mission autonome : P33, forme et esthetique parametriques dans le Studio.

## P33 - Forme et apparence parametriques V0

Statut : `implemented-studio-preview`, `browser-inspection-pending`, `print-validated: false`.

Le Studio propose maintenant une carte `Finition vivante` dans l etape finale : coins arrondis/droits/biseautes, rayon et biseau d apercu, prise symbolique, ambiance, labels et typographie. Chaque changement est immediat dans la vue de boite, persiste avec le projet et voyage dans la selection puis les metadata CAD IR sous `bgig.appearance.v0`.

Le contrat est volontairement non destructif : P21 garde exactement le meme digest, les dimensions, placements, tolerances, murs, fond et cavites ne changent pas, et la CAD IR porte `stored_for_preview_only_not_materialized`. Le navigateur automatise ne peut pas se connecter dans ce sandbox Windows ; build Vite et tests de contrat sont OK. Prochaine vraie gate : P34, choix du premier mecanisme et validation physique cible avant toute geometrie de couvercle ou clip.

## P34 - Coupon coulissant a deux pieces

Statut : `accepted-gate`, `experimental-contract`, `implemented-cad-ir-coupon`, `implemented-fusion-adapter`, `fusion-smoke-required`, `print-validated: false`.

Le choix humain C du 2026-07-11 retient le couvercle coulissant. P34-M001 ajoute le contrat `bgig.mechanism.v0`, ses bornes locales, les refus de modules trop petits, le transport Local Composer/CAD IR et un panneau Studio clair. Le plan P21, son digest, les dimensions de bac ouvert et les tolerances globales ne changent pas.

P34-M002 ajoute un seul coupon place a cote de la boite pour le premier module compatible : un bac ouvert et un capot. Le capot est une piece unique, composee d une plaque et de deux glissieres laterales jointes par `join_rectangular_prism`. L adaptateur Fusion consomme cette primitive additive avec des bornes XY et un recouvrement Z obligatoire. Aucun statut physique n est revendique.

Le smoke Fusion est prepare par `P34_SLIDING_LID_FUSION_SMOKE.md`. Il doit confirmer deux glissieres jointes au capot et `Joined cap rails: 2`. Seulement apres ce retour, P35 pourra demander l impression et les mesures de glisse.
## Rebase produit canonique - 2026-07-12

Statut : `P36 canonical product rebase` termine et verifie.

Thomas clarifie et accepte l'ordre V0.1 fonctionnelle, V0.2 formes/ergonomie,
puis V0.3 couvercles. L'audit confirme que P33/P34 ont ete engages trop tot : le
Studio et le moteur ne couvrent pas encore le regroupement simple par bac, la
pile plateaux/livrets, le dimensionnement global des bacs ni l'affectation de
tout le volume.

P33 reste un prototype de preview. P34 reste une exploration CAD non conforme au
coulissant canonique et son smoke Fusion n'est plus demande. Aucun statut de code
ou test existant n'est efface, mais ces lots sont `superseded-for-product`.

La vision, ADR-0047, l'audit et le plan P36-P50 sont alignes. La prochaine mission codee est P37, contrat projet V0.1 et migration compatible.

## P37 - Contrat projet V0.1 et migration

Statut : `done`, `implemented-core`, `implemented-loopback-adapter`,
`print-validated: false`.

`bgig.project.v1` est maintenant le contrat de projet user-first : boite,
reglages de jeu/parois, lignes de pieces avec `container_group_id`, groupes de
bacs, elements plats quantifies et remplissages. Le normaliseur migre les drafts
`bgig.local_composer.v0` sans les muter, conserve les donnees techniques dans un
snapshot et reporte apparence/couvercle comme options inactives. Les routes
`/api/project-v1/starter` et `/api/project-v1/normalize` sont disponibles pour
P38.

Preuves : tests du contrat, migration P23, API loopback et cardinalite 72/50/25
passent ; build TypeScript/Vite passe. Le portfolio P21 et l export restent
volontairement sur P23 tant que P39 ne derive pas les bacs V1.

Prochaine mission : P38, reconstruction du Studio autour du contrat V1.

## P38 - Studio de saisie V0.1

Statut : `done`, `implemented-local-ui`, `implemented-client-validation`,
`print-validated: false`.

Le Studio est maintenant organise autour du langage utilisateur : boite, pieces
a ranger, plateaux/livrets, bacs demandes, volumes de remplissage et reglages de
fabrication. Chaque ligne de piece choisit une forme, des mesures, une quantite
et le bac cible. Les imports V0/V1 et la sauvegarde JSON restent disponibles
sans exposer candidats, layers, apparence ou couvercles dans le parcours V0.1.

Preuves : 275 tests Python passent, le build TypeScript/Vite passe et le Studio
local repond en HTTP 200, tout comme `/api/project-v1/starter` qui retourne le
contrat `bgig.project.v1`. L inspection navigateur automatisee reste indisponible
dans le sandbox Windows ; elle ne constitue pas une gate humaine et aucun statut
Fusion ou impression n est revendique.

Prochaine mission : P39, derivation expliquable des bacs et logements depuis les
pieces et leur bac cible.

## P39 - Derivation des bacs et logements

Statut : `done`, `implemented-core`, `implemented-loopback-adapter`,
`implemented-local-ui`, `print-validated: false`.

Le moteur pur derive maintenant un bac minimal par groupe cible. Il compte les
piles des pieces, preserve l epaisseur totale des paquets de cartes, ajoute les
jeux, parois et fonds, puis explique toute dimension qui depasse la boite. Le
Studio affiche ce resultat apres `Construire mes bacs` sans pretendre que les
bacs sont deja places, generes dans Fusion ou imprimables.

Preuves : 284 tests Python passent, le build TypeScript/Vite passe et la recette
locale reelle retourne un plan P39 `ready_for_p40` pour 72 jetons : un bac de
40.2 x 58.8 x 49.8 mm avec 6 piles. Aucun statut Fusion ou impression n est
revendique.

P40 reste responsable de la pile des plateaux et livrets. P41 reste responsable
du placement global, du jeu entre bacs et du remplissage de volume.

Prochaine mission : P40, pile superieure de plateaux et livrets.

## P40 - Pile superieure plateaux et livrets

Statut : `done`, `implemented-core`, `implemented-loopback-adapter`,
`implemented-local-ui`, `print-validated: false`.

La pile des plateaux/livrets est maintenant une reservation non imprimable : son
ordre, son empreinte, son epaisseur totale et la hauteur restante sont calcules.
Les bacs sont recalcules sous cette hauteur. Le resultat annonce un support a
completer ou une aire candidate suffisante a confirmer ; il ne promet pas de
support continu avant P41.

Preuves : 293 tests Python passent, le build TypeScript/Vite passe et la recette
locale reelle reserve 191.2 x 141.2 x 5.6 mm pour un plateau et un livret, laisse
50.4 mm aux bacs et retourne `support_extension_required` de facon explicable.
Aucun statut Fusion ou impression n est revendique.

Prochaine mission : P41, placement global, support continu et fermeture du
volume.

## P41 - Fermeture de volume

Statut : done, plan global place, regions classees, collisions et conservation verifiees. Preuves : 300 tests et recette locale OK. Prochaine mission : P42 CAD IR/Fusion.
## P42 - Geometrie fonctionnelle V0.1

Statut : `done`, `implemented-core`, `implemented-loopback-adapter`,
`implemented-local-ui`, `implemented-cad-ir`, `fusion-smoke-required`,
`print-validated: false`.

Le bouton `Construire mon insert` construit maintenant le plan P41 et transforme
ce plan en bacs ouverts, logements par famille, supports et remplissages. Un bac
vide exact qui ne conserve pas ses parois ou son fond est refuse clairement. Une
petite region automatique qui ne peut pas garder ces epaisseurs reste du jeu
technique explique, jamais une piece fragilisee en silence.

Preuves : tests CAD IR, route locale, commande d export reproductible, lecture
par l adaptateur Fusion hors API, test compact 50 bacs / 72 familles / 25
elements plats et build TypeScript/Vite. Aucun statut Fusion ou impression n est
revendique.

Prochaine mission : P43, preparation puis observation humaine Fusion du jeu
temoin uniquement.
## P42a - Regroupement des remplissages automatiques

Le preflight P43 a montre que la decomposition exacte P41 pouvait produire trop
de petits bacs automatiques dans Fusion. P42 fusionne maintenant uniquement les
cellules libres compatibles et contigues, conserve leur provenance et ne fusionne
jamais une forme en L. Le jeu temoin passe de 111 a 20 pieces CAD. L export
`export-project-v1-cad` accepte les JSON UTF-8 avec BOM Windows.

Preuves : test anti-fragmentation, scene P43 relue par l adaptateur compact,
validation des tests P42 et de l export BOM. La geometrie P43 a ensuite ete observee ; son acceptance produit est reouverte.

## P43 - Correction de l acceptance MVP V0.1

Statut : `reopened`, `fusion-validated-geometry-only`,
`product-mvp-rejected`, `print-validated: false`.

Le retour `Fusion P43 OK` du 2026-07-12 reste une preuve que le jeu temoin
preparation peut etre observe dans Fusion. Il ne prouve pas le MVP produit : la
palette affiche `Chargement...` sans solution de secours, la saisie Studio n a
pas de preuve visuelle/runtime suffisante et les 15 complements automatiques
restants ne sont pas justifies comme bacs utiles.

Le depot conserve P37 a P42 comme fondations testees : contrat, derivation,
reservation, controle de volume, CAD IR et adapter Fusion. Elles ne sont plus
qualifiees comme parcours V0.1 accepte. P52 documente la reprise et P53 a P60
ferment successivement semantique, editeur, cavites, partition, resultat,
CAD/Fusion et acceptance. V0.2 et V0.3 restent bloques.

## P53 - Clarification cavites fixes / enveloppes extensibles

Statut : `done-docs`, `accepted-product-semantics`, `implementation-required`.

La clarification humaine du 2026-07-12 rejette tout remplissage automatique du
volume par de petits corps. Les assets et leurs quantites calibrent les cavites.
Apres reservation des plateaux/livrets, les enveloppes exterieures des bacs
demandes s agrandissent pour occuper le volume imprimable ; le surplus devient
de la matiere dans les parois et les fonds.

P39 reste reutilisable pour les cavites et minima. P40 reste reutilisable pour la
pile superieure. La strategie P41/P42 `free region -> automatic filler` est
`superseded-for-product`. ADR-0054, le contrat V0.1 et P54-P60 portent la reprise.
Aucun code fonctionnel n est modifie par P53.

## P54 - Architecture UX de l editeur premium

Statut : `done-docs`, `implemented-reference`, `visual-runtime-pending`,
`print-validated: false`.

P54 fournit une specification complete et un prototype HTML haute fidelite : rail
projet, travail central, apercu permanent, tableaux assets et plateaux/livrets,
cartes de bacs, fabrication, etats de chargement/erreur/calcul/resultat, mode
simple/avance, responsive et accessibilite. La reference explique clairement que
les cavites restent calibrees et que BGIG ne cree aucun corps automatique.

Preuves : test P54 sur sections obligatoires, invariants ADR-0054, structure HTML,
breakpoints et absence de sequences d encodage connues. Le prototype repond en
HTTP 200. L inspection graphique automatisee reste indisponible car les deux
runtimes de controle Windows echouent avant connexion ; P56 ne pourra pas etre
qualifie produit sans preuve visuelle du frontend reel.

Prochaine mission : P55, contrat executable cavite/minimum/final.

## P55 - Contrat executable cavites fixes / enveloppes extensibles

Statut : done, implemented-core, implemented-loopback-adapter,
print-validated: false.

Le schema bgig.project.v1 accepte desormais, par groupe de bac, les axes
extensibles, les dimensions exterieures verrouillees et la preference de surplus.
Ces champs sont additifs : les projets P37 et les migrations P23 recoivent des
valeurs par defaut compatibles.

Le module pur expandable_envelope produit le contrat
bgig.expandable_envelope_contract.v1. Il fige les dimensions et origines locales
des cavites P39 dans le repere de l enveloppe minimale, distingue enveloppe
minimale et finale, trace le surplus X/Y autour du repere et le surplus Z sous ce
repere, puis refuse minimum depasse, axe interdit, verrou incoherent ou limite de
boite depassee. Aucun corps automatique, placement global, CAD ou calcul Fusion
n est produit. La route locale POST /api/project-v1/derive-envelopes expose ce
rapport.

Preuves : 321 tests Python passent, dont formes rond/carre/rectangle/cartes/
cube/pion/custom, quantites, plusieurs cavites par groupe, migration additive,
immutabilite du cavity_layout, contraintes, erreurs et API HTTP. P56 est la
prochaine mission ready ; P57 reste responsable de la partition conjointe.

## P54-R - Realignement integral Fusion-only

Statut : done-docs, accepted-product-direction, implementation-required.

La decision humaine Fusion uniquement supersede ADR-0040 et ADR-0042 pour le
MVP. BGIG est un add-in Fusion 360 ; la palette HTML embarquee est la surface
principale. Aucun navigateur externe, serveur loopback, Vite ou application web
n appartient au runtime ou au packaging utilisateur.

Le coeur src/board_game_insert_generator reste pur et sans adsk. La palette edite
bgig.project.v1, transmet des messages JSON versionnes au bridge, affiche le plan
moteur et declenche l adaptateur CAD. CommandInputs reste expert/secours.

La branche codex/p56-premium-editor au commit f669b82 n a jamais ete integree a
main et est classee prototype web abandonne. P55 reste valide pour son contrat
pur ; la route derive-envelopes loopback est historique.

P56-P60 sont redefinis : editeur Fusion, partition pure, resultat dans la
palette, materialisation fidele, puis acceptance end-to-end Fusion. Aucune
validation d impression n est revendiquee.
## P56 - Editeur complet embarque dans Fusion

Statut : implemented, automated-validated, fusion-smoke-prepared,
fusion-validated: false, print-validated: false.

La palette P32 est devenue l editeur principal a six vues : Boite, Pieces,
Plateaux, Bacs, Fabrication et Resultat. Les tables Pieces et Plateaux sont
sans limite arbitraire, les groupes de bacs sont stables, et le mode avance
expose jeux, parois, fonds, axes extensibles, dimensions verrouillees et
preferences de surplus.

Le JavaScript ne calcule aucune regle metier. Il transmet des requetes
bgig.palette.request.v1 ; palette_project.py normalise bgig.project.v1, appelle
les contrats purs P40/P55, renvoie bgig.palette.response.v1 et persiste le projet
atomiquement dans Documents/BGIG/projects, hors du dossier remplace lors des
mises a jour de l add-in. Import, export et reprise locale sont couverts.

L installateur embarque les modules Python purs dans lib/board_game_insert_generator.
L add-in installe est donc autonome vis-a-vis du depot, de Vite, de localhost et
d un navigateur. Le preparateur P56 a installe et verifie les marqueurs dans
AppData. Le controle visuel Fusion n a pas pu etre automatise : le runtime de
controle Windows echoue avec apply deny-read ACLs. Ce statut ne vaut donc pas
fusion-validated.

Preuves ciblees : 6 tests bridge, 5 tests DOM, 87 tests Fusion historiques et
validation syntaxique JavaScript. P57 est la prochaine mission ready ; la gate
humaine produit reste P60.
## P57 - Solveur de partition et expansion conjointe

Statut : implemented, automated-validated, fusion-validated: false,
print-validated: false.

Le module pur partition_solver.py produit bgig.partition_plan.v1. Il reserve la
pile P40, reprend les cavites et minima P55, explore une famille bornee de
partitions en rangees, rotations et ordres deterministes, puis distribue le
surplus uniquement aux axes extensibles des bacs demandes. Chaque enveloppe
finale est revalidee par P55 avant acceptation.

Une solution construite remplit tout le volume imprimable sous la pile hors jeux
techniques. Les jeux contre la boite et entre corps restent des vides. Le nombre
de corps final est exactement groupes constructibles + complements exacts
explicitement demandes ; automatic_body_count reste zero. Le mode de complement
historique auto est refuse avec correction, et un complement exact qui ne couvre
pas la hauteur de rangement recoit un diagnostic specifique.

La palette expose Calculer la partition et les diagnostics P57 via le bridge
versionne. Elle permet aussi de saisir les complements exacts. Les boutons de
materialisation/export du CAD historique ont ete retires du parcours normal en
attendant P59.

Preuves ciblees : 9 tests solveur, 7 tests bridge, 5 tests DOM et 87 tests Fusion
historiques. Le solveur est borne et explicable, mais ne revendique pas
l optimalite mathematique globale. P58 est ready.

## P58 - Resultat reel dans la palette Fusion

Statut : implemented, automated-validated, fusion-validated: false,
print-validated: false.

Le module pur partition_result_view.py transforme une partition P57 construite
en bgig.partition_result_view.v1 sans modifier le plan. Il fournit une vue dessus
orthographique, une coupe X/Z declaree au centre Y, les corps, cavites, pile
plate, supports et details utilisateur. Les rotations 0/90 transforment les
cavites depuis leur repere P55 vers le monde de facon testee.

La palette affiche exclusivement ce modele : SVG au viewBox millimetrique,
noms des bacs et contenus, positions, dimensions monde, minimum/final, surplus,
rotation, complements, pile, couverture de support, digest et zero corps
automatique. Une partition impossible n affiche aucun dessin. Une modification
invalide le resultat ; sauvegarde et export sans modification le conservent.
Materialiser dans Fusion reste explicitement desactive jusqu a P59.

Preuves ciblees : 5 tests de projection, 4 contrats palette resultat, 7 tests
bridge, 5 tests DOM et 87 tests Fusion historiques. La syntaxe JavaScript passe.
Le controle visuel Fusion n est pas revendique ; la gate complete reste P60.
P59 est ready.
## P59 - Materialisation CAD et synchronisation de scene

Statut : `implemented`, `automated-validated`, `fusion-validated: false`,
`print-validated: false`.

`partition_cad.py` transforme exclusivement `bgig.partition_plan.v1` en
`cad_ir.v0`. Une partition obsolete ou modifiee est refusee. Chaque placement
P57 devient exactement un composant CAD ; les enveloppes finales sont les
blanks imprimables et les cavites P55 restent top-open, fixes et exprimees dans
le repere local du corps apres rotation. Les complements creux, pleins et
separateurs ne sont crees que s ils sont explicitement demandes. Aucun volume
libre, filler P41/P42 ou corps automatique n est materialise.

La palette expose maintenant `materialize_project` et `regenerate_project` via
le bridge versionne. L entrypoint ecrit la CAD IR atomiquement, utilise le mode
`compact_only`, puis appelle l adaptateur Fusion existant. Generate refuse une
scene BGIG preexistante ; regenerate remplace uniquement la scene possedee par
le registry. Inspect, clear et export sont accessibles dans la palette et
preservent les objets non-BGIG. Une erreur de bridge renvoie toujours une
reponse versionnee au lieu de laisser expirer l interface.

Preuves ciblees : 8 tests du constructeur CAD, 8 tests du bridge projet, 4
tests de synchronisation entrypoint, 5 tests resultat palette, 5 tests DOM et
87 tests de l adaptateur Fusion historique. Syntaxes Python et JavaScript
valides. Le packaging exige `partition_cad.py` et le manifeste passe en 0.1.6.

Limite : aucune observation de cette scene P59 dans Fusion n est encore
revendiquee. P60 est desormais la seule gate active avant acceptation V0.1.
## P60 - Preparation de la gate Fusion-only

Statut : `prepared-in-repository`, `automated-evidence-green`,
`human-fusion-observation-required`, `print-validated: false`.

Le fixture `p60_mvp_project.json` couvre deux bacs, trois cavites de hauteurs
differentes, un livret et zero complement. Sa preparation a detecte puis corrige
un defaut P59 : le surplus Z etait place sous l enveloppe par P57, mais une
cavite courte gardait son ancien fond et devenait fermee. P59 recale maintenant
chaque cavite sur la face superieure finale sans changer ses dimensions ; un
test multi-hauteurs verrouille cet invariant.

Le script `prepare_p60_mvp_acceptance.ps1` installe l add-in du commit courant,
verifie le runtime Fusion-only, ecrit le fixture comme projet courant et marque
le commit installe. Les preuves hors Fusion confirment 2 corps, 3 cavites, zero
automatique et 2 occurrences compactes. L observation Fusion et l export reel
restent la gate humaine active.
## P60 - Correctif bridge palette QT 0.1.7

Statut : `implemented`, `automated-validated`, `fusion-retest-required`,
`print-validated: false`.

Le premier retour humain P60 valide la qualite visuelle de la palette mais
observe que les actions projet expirent apres 8 secondes et que Fusion affiche
`Action inconnue`. La cause est le retour asynchrone `response` emis par le
navigateur QT apres chaque `sendInfoToHTML`. Le handler le traitait comme une
nouvelle action utilisateur et renvoyait une notification, creant une boucle de
transport.

Le patch ignore desormais uniquement l action technique `response`, acquitte
les vraies actions HTML avec `returnData = OK` et conserve tous les routages
produit. La palette utilise aussi une taille initiale/minimale 1120 x 760, sans
reduire une taille utilisateur plus grande. Trois tests de transport verrouillent
le rebond QT, l ordre du garde-fou et les dimensions. Une nouvelle observation
Fusion reste requise avant d accepter P60.
## P60 - Correctif bootstrap et lanceur Utilities 0.1.8

Statut : `implemented`, `automated-validated`, `fusion-retest-required`,
`print-validated: false`.

Le second retour humain confirme que le projet ne se charge jamais au demarrage.
La cause est une course distincte du rebond QT : le HTML envoyait `load_project`
pendant `palettes.add`, avant que `incomingFromHTML.add(handler)` soit termine.
L evenement etait perdu, `project` restait nul et la garde JavaScript annulait
ensuite silencieusement tous les boutons projet.

Le bootstrap 0.1.8 utilise maintenant un handshake `bgig_palette_ready` repete.
La reception de ce signal prouve que le handler Python est attache ; Python
charge alors directement le projet et renvoie une reponse versionnee. Les
boutons affichent un etat explicite tant que le bootstrap n est pas termine.

La commande promue de la barre Utilities ouvre desormais exclusivement la
palette `BGIG - Atelier de rangement`. L ancien dialogue technique n est plus
relie au bouton ni expose dans la palette. Le package contient une icone maison
BGIG SVG en 16 et 32 px et le controle est `isPromotedByDefault`.

Preuves hors Fusion : handshake, ordre des routes, retry, absence de bootstrap
historique, lanceur palette, promotion toolbar, ressources SVG valides et
packaging testes. Une nouvelle observation Fusion reste obligatoire.

## P60 - Finition UX Fusion-only 0.1.9

Statut : implemented, automated-validated, partial-fusion-observation,
fusion-retest-required, print-validated: false.

Le retour humain du package 0.1.8 confirme maintenant le chargement, les actions
projet, le calcul P57, le resultat P58 et la materialisation P59 dans Fusion.
Les anciens KO transport/bootstrap sont donc resolus sur ce parcours. P60 reste
ouverte tant que regeneration sans doublon, inspection et export ne sont pas
observes sur le package courant.

Le package 0.1.9 porte la palette initiale/minimale a 1280 x 1100. Le coeur pur
fournit des presets editables Jetons, Cartes sleevees, Des et Pions, chacun
verifie comme entree produisant une partition a un corps. Fabrication expose
maintenant Bac vide, Bloc plein / cale sans cavite et Separateur. La vue Bacs
montre les dimensions finales X/Y/Z en mode simple ; vide signifie automatique,
une valeur renseignee reste soumise aux minima et limites de boite P55/P57.

Preuves : suite complete 387 tests, dont chaque preset jusqu a une partition
construite, tests bridge/DOM/transport, syntaxe JavaScript Node, py_compile,
parsing PowerShell, git diff --check, dry-run P60 et absence de adsk dans le
coeur.

La gate 0.1.9 est maintenant renforcee par une fixture unique : Bac jetons X
local verrouille a 80 mm, Bac cartes et Cale pleine avant solid de 20 x 238,8 x
63,4 mm. Les preuves hors Fusion confirment 3 corps, 1 complement explicite, 3
cavites, 0 automatique et 3 occurrences compactes. Le preparateur sauvegarde
tout projet courant different avant d installer cette fixture. L observation
Fusion reste requise.

## P60-R - Revue produit et realignement documentaire

Statut : `done-docs`, `product-review-ko`, `technical-baseline-useful`,
`implementation-not-authorized`, `print-validated: false`.

Le retour humain confirme que le parcours atteint la materialisation Fusion et
que l Apercu apporte une vraie valeur. Il refuse cependant P60 comme acceptance
produit : rapport d inspection brut au demarrage, etat non reactif, vocabulaire
et densite a reprendre, pile globale de plateaux contraire a l usage attendu,
et solveur P57 incapable de plusieurs etages Z.

Le rapport `docs/P60_PRODUCT_FEEDBACK_REALIGNMENT.md` explique les causes dans
le code et definit le parcours cible Boite -> Plateaux et livrets -> Elements du
jeu -> Conteneurs -> Reglages -> Apercu. Les ADR-0056 a ADR-0060 sont proposees,
non acceptees. Aucun runtime, schema, solveur, adaptateur ou tolerance n est
modifie dans P60-R.

La prochaine action est une revue humaine des cinq ADR. Apres acceptation, P61
ouvre le plus petit lot d implementation : etat reactif, diagnostics discrets
et architecture de palette. La sortie V0.1 est transferee a P66.

## P61 - Etat reactif et architecture de palette Fusion

Statut : `implemented`, `automated-validated`, `fusion-retest-required`,
`print-validated: false`.

Le GO humain accepte ADR-0056 a ADR-0060. Le package 0.1.10 supprime le mode
avance global, ordonne le parcours Boite -> Plateaux et livrets -> Elements du
jeu -> Conteneurs -> Reglages -> Apercu et installe une barre d actions en trois
zones. Les listes Elements et Conteneurs offrent les densites Compact/Detaille.

Le bridge Python retourne un digest source stable et les etats source, derive,
solve et materialise. Apres edition, la palette recalcule les minima apres 350
ms, conserve l ancien Apercu grise, marque la proposition a recalculer et refuse
Materialiser/Regenerer tant que le plan est obsolete. Aucune scene Fusion n est
modifiee automatiquement.

L inspection saine du demarrage reste silencieuse : le rapport complet est
place dans Details techniques et n alimente plus le message global. Les codes
P57, digests et statuts moteur ont quitte le premier niveau de l Apercu.

Preuves initiales : 33 tests palette/bridge, controle syntaxique Node et suite
complete 389 tests OK.

### Hotfix P61 - synchronisation de scene Fusion

Le retour humain du 2026-07-13 a revele que `Materialiser dans Fusion`
continuait d appeler la creation stricte meme lorsqu une scene BGIG saine
existait deja. Le package 0.1.11 choisit maintenant creation pour un document
sans scene et regeneration pour l unique scene BGIG correctement identifiee.
Une scene multiple, non taguee ou ambigue reste bloquee sans suppression.

Le statut `synchronized` exige desormais une inspection apres execution : une
chaine de succes ne suffit plus si la scene ne peut pas etre retrouvee avec
exactement le nombre de corps calcules. Le
rapport retourne par Fusion est place dans `Details techniques` en cas de
blocage. 392 tests automatises passent ; validation Fusion encore requise.

## P62 - Catalogue d elements et orientations

Statut : `implemented`, `automated-validated`, `fusion-retest-required`,
`print-validated: false`.

Le package 0.1.12 ajoute un catalogue local versionne de cinq formats de cartes,
les dimensions non sleevees/sleevees, une surcharge manuelle prioritaire et les
orientations `flat`, `upright_long_edge`, `upright_short_edge` et `auto`. Le
coeur conserve les dimensions physiques de depart et expose separement les
dimensions XYZ resolues consommees par les cavites.

L epaisseur d un paquet peut etre mesuree directement ou calculee depuis le
nombre de cartes, l epaisseur unitaire et les sleeves. Les projets historiques
sans champs P62 migrent additivement en dimensions explicites, a plat, sans
changer leurs cavites.

Les presets personnels sont stockes atomiquement hors du package Fusion, sans
compte ni cloud. Ils sont enregistrables depuis un element, reutilisables,
supprimables, importables et exportables. Les dimensions resolues restent
visibles dans les cartes compactes et detaillees de la palette.

Preuves : 401 tests automatises, syntaxe Python/JavaScript et packaging pur
verifies. Aucune validation Fusion ou impression n est revendiquee.


## P63 - Reservations superieures encastrees

Statut : `implemented`, `automated-validated`, `fusion-retest-required`,
`print-validated: false`.

Le package 0.1.13 remplace le rabotage global sous plateaux/livrets par le
contrat `bgig.top_inset_reservations.v1`. Les corps demandes montent au plan
superieur de conception hors empreinte. Les elements plats qui se chevauchent
se composent en Z ; les elements cote a cote ne consomment pas une pile globale.

Chaque reservation porte son ordre de retrait, son plan d appui et une prise
rectangulaire simple. Une coupe est refusee si elle perce le fond minimal du
corps ou descend sous le fond d une cavite intersectee. Les prises courbes et
autres ergonomies V0.2 restent hors scope.

La CAD IR distingue les coupes superieures des cavites de contenu. L adaptateur
Fusion verifie leur ouverture sur la face superieure, leur profondeur retenue et
leurs bornes locales. L Apercu expose les empreintes en vue de dessus et en coupe
X/Z. Aucun corps automatique n est cree.

Preuves : 408 tests automatises passent, package Fusion 0.1.13 prepare et coeur
Python sans `adsk`. Aucune observation Fusion ni impression n est revendiquee.

## P64 - Solveur volumetrique multi-etages et durcissement runtime

Statut : implemented, automated-validated, runtime-hardened,
fusion-retest-required, print-validated: false.

Le package 0.1.15 conserve bgig.volumetric_stage_solver.v1, son portefeuille
borne et deterministe et ses plans historiques par etages complets. Il ajoute un
repli par piles verticales independantes : un corps haut peut traverser plusieurs
intervalles Z a cote de piles de corps plus courts. Les plans historiques gardent
la priorite quand ils sont valides ; le repli hybride n est choisi que lorsqu il
resout un cas que les tranches globales ne ferment pas.

La revalidation des enveloppes finales respecte maintenant la rotation XY : une
dimension locale Y d un corps tourne est comparee a la largeur monde X
correspondante. Les cas reels 4, 5 puis 6 bacs de cartes avec un bac haut restent
ainsi monotones ; le sixieme bac declenche un second niveau sans retirer le bac
haut voisin.

Conformement a ADR-0057, une cavite de contenu intersectee par un plateau conserve
sa profondeur utile sous l encastrement. Sa profondeur CAD finale vaut profondeur
de base plus profondeur cumulee des reservations superieures qui la recouvrent.
Le fond minimal reste une contrainte dure et bloque la proposition si cette
compensation ne tient pas. Le plan distingue la cavite de base fixe de la
compensation appliquee.

Le pont Fusion attribue des noms techniques uniques aux corps meme lorsque
plusieurs conteneurs portent le meme nom utilisateur. La vue resultat reprend le
vrai sous-score du solveur et dessine les cavites ouvertes sur le sommet final,
comme la CAD IR.

Preuves : 428 tests automatises passent. La matrice cartes/jetons 4-5-6 est
construite, le cas hybride contient des origines Z non nulles et des corps qui
traversent plusieurs intervalles, et un plan CAD IR de sept corps nommes
identiquement passe generation_plan_from_cad_ir avec sept noms uniques.
Compilation Python et git diff --check passent. Aucune observation Fusion de
ce correctif ni impression n est encore revendiquee. P65 reste ready.


## P65-M001 - Jeux X-Y/Z et materialisation persistante

Le premier increment P65 separe le jeu X-Y entre conteneurs du jeu Z. Les
anciens projets sans champ Z heritent du jeu X-Y ; le solveur reserve le vide Z
dans son budget de hauteur, le valide, l expose dans son plan et le transporte
dans la CAD IR. Aucune cale ni aucun corps automatique n est cree.

La palette 0.1.16 renomme le champ historique, ajoute le reglage Z et place
Materialiser dans Fusion juste apres Recalculer dans la barre basse. Le bouton
reste desactive sans solution complete et a jour. L ancien bouton local de l Apercu
est retire pour eviter le doublon.

Preuves automatisees : 430 tests passent. Les tests projet, solveur volumique,
partition, CAD et palette couvrent l heritage X-Y vers Z, un cas anisotrope 0,6/1,2 mm, les origines Z, le
parametre CAD et l unicite de l action. Validation Fusion et impression reelle non
revendiquees ; P65-M001 est integree dans le P65 termine.
## P65-M002 - Separation des frontieres de jeu

P65-M002 separe quatre roles non ambigus : jeu X-Y total entre conteneurs,
jeu X-Y par cote entre conteneur et boite, jeu Z total entre conteneurs et
marge Z superieure de boite. Les projets V1 historiques sans le nouveau champ
X-Y de boite heritent de leur jeu X-Y historique, sans changer leurs placements.
Le fond reste ancre a Z=0 ; aucune cale, aucun support ni corps imprimable
automatique n est cree.

La palette Fusion 0.1.17 affiche chaque role une seule fois. La CAD IR les
transporte explicitement. Les deux sketches de reference de boite restent
tagues et inspectables, mais sont masques par defaut a la creation comme a la
regeneration. Preuves automatisees : 434 tests executes verts en trois lots,
compilation Python, git diff --check et exemple CLI verts. Validation Fusion
et impression reelle restent a realiser ; fusion-retest-required,
print-validated: false.

## P65-M003 - Tailles de conteneurs et estimation non mutante

Statut : implemented, automated-validated, fusion-retest-required,
print-validated: false.

Le package Fusion 0.1.18 ajoute la projection Python
bgig.container_sizing_view.v1. Chaque conteneur est relie par son identifiant
stable a son minimum derive, sa demande Auto/Cible/Fixe, sa taille calculee,
son surplus, son etage et son appui. La palette n infere aucune dimension
physique ou proposition elle-meme.

Dans Conteneurs, la vue compacte affiche minimum, reglage, taille calculee et
statut. La vue detaillee explique chaque axe, le surplus et l etage. Estimer
les tailles appelle le solve_project existant, reste dans l onglet, ne
sauvegarde pas et ne materialise pas Fusion. Les etats non calcule, a jour,
perime, partiel et impossible restent distinguables. Une estimation concurrente
est refusee.

Aucun changement de solveur, score, tolerance, cavite, reservation, geometrie,
CAD IR ou corps automatique ne fait partie de ce lot. Materialiser dans Fusion
reste l action persistante unique et demeure bloquee sans proposition complete
et a jour.

Preuves : 440 tests automatises, syntaxe JavaScript, compilation Python,
git diff --check et dry-run d installation Fusion verts. Validation Fusion et
impression reelle restent a realiser en P66. P65-M003 est integree et
P65-M004 est implementee dans le package 0.1.19.

## P65-M004 - Explications et actions finales de l Apercu

Statut : implemented, automated-validated, fusion-retest-required,
print-validated: false.

Le package Fusion 0.1.19 ajoute bgig.preview_explanations.v1 au resultat de
partition. Cette projection Python pure traduit le score comparatif, les appuis
d etages, l appui des plateaux/livrets, l ordre de retrait, les residuels et les
suggestions. Elle ne modifie pas le plan, le score, les placements ni la
materialisabilite.

Apercu ne montre plus les enums de support ou les raisons internes au premier
niveau. Les sous-criteres du score sont nommes et l aide precise que le score ne
remplace pas une validation physique. Les residuels restent non materialises et
les suggestions exigent une decision humaine explicite. Exporter les imprimables
est primaire localement ; Recalculer et Materialiser dans Fusion restent uniques
dans la barre persistante.

Preuves : 445 tests automatises, syntaxe JavaScript et compilation Python verts.
Le package Fusion 0.1.19 est installe localement depuis 23aaa70 et ses marqueurs
sont verifies. La gate humaine Fusion et l impression restent a realiser.

## P66 - Quarantaine, preuve et fermeture du MVP V0.1

Statut : `P66-M000 done`, `P66-M001 done`, `P66-V accepted`, `P66-CLOSE done`,
`mvp-accepted`, `fusion-validated`, `print-validated: false`.

Le contrat `docs/P66_TERRA_EXECUTION_CONTRACT.md` borne la suite. P66-M000 retire
le parcours normal de creation de Bac vide, Bloc plein / cale et Separateur, et
ne fournit plus de presets de complements. Les projets historiques gardent leur
schema, loader, coeur, bridge et materialisation : un `fill_elements` explicite
reste importable, lisible, sauvegardable et regenerable, sans migration
destructive ni corps automatique.

Le package Fusion est 0.1.20. Aucun solveur, tolerance, geometrie, nombre de
corps automatique ou semantique future des complements ne change. Preuves : 446
tests automatises, syntaxe JavaScript, compilation Python et `git diff --check`
verts ; aucune validation Fusion ni impression reelle n est revendiquee.

P66-M001 prepare ensuite un projet canonique sans complement, un projet
impossible, les preuves, le package installe et la checklist. P66-V reste une
observation humaine Fusion. Un KO ouvre uniquement un hotfix P66-Hxx borne ; un
OK clot le MVP fonctionnel Fusion-only avec `print-validated: false`.
## Sequence post-MVP cadree

P44-P50 gardent leurs identifiants canoniques. P67 est l atelier humain qui
priorise leur perimetre avant P44. P68 recueille les premiers retours de vrais
inserts sans changer les defaults. P44-P46 portent la V0.2 formes/ergonomie,
P47-P50 la V0.3 couvercles/calibration, puis P69 realise la revue UI/UX exhaustive
et prepare humainement les lots P70+.

## P66-M001 - Preparation automatisee de la gate Fusion

Statut : `done`, `automated-validated`, `gate-prepared`,
`human-fusion-gate-required`, `fusion-validated: false`,
`print-validated: false`.

P66-M001 ajoute les deux fixtures sans complement, le preflight pur Python, les
preuves bridge/CAD/Fusion et le preparateur unique. La fixture complete fixe 8
corps demandes, 2 etages, 2 reservations superieures, 7 coupes et un plan CAD
compact deterministe ; la fixture impossible expose `CONTAINER_MINIMUM_BLOCKED`
sans plan CAD ni materialisation. Le package Fusion reste 0.1.20 et le runtime
produit n est pas modifie.

Le preparateur reutilise l installateur existant, verifie le runtime palette,
les marqueurs et la version, preserve un projet utilisateur different une seule
fois, installe atomiquement la fixture puis ecrit le commit et un rapport de
preflight. La suite complete, compileall, diff-check, controle adsk, dry-run et
installation reelle sont les preuves requises avant P66-V. Aucune validation
Fusion ou impression n est declaree.

## P66-CLOSE - MVP V0.1 accepte dans Fusion

Statut : `done`, `mvp-accepted`, `fusion-validated`,
`print-validated: false`.

Retour humain recu le 2026-07-14 : `P66 Fusion OK 0.1.20 - commit 6e351bb`.
Le package 0.1.20 et le commit `6e351bbd652ebdf496e7e53060d0d18dda7c6b57`
ont ete prepares et observes pour le parcours P66. Le MVP V0.1 Fusion-only est
accepte : palette, projet, calcul, invalidation, materialisation, regeneration,
export et preservation non-BGIG ont passe la gate humaine.

Cette acceptance ne deduit aucune validation d impression, de tolerance
physique, de resistance, d ergonomie V0.2 ou de couvercle V0.3. Aucun tag ou
release n est publie. P67 est ouvert pour arbitrer humainement P44-P50 ; P68
reste `planned-after-p66` et P44-M001 reste bloque jusqu a cette decision.

## P67-M000 - Revue UX structurelle capturee

Statut : `done-docs` apres integration, `p67-in-review`,
`human-review-required`, `no-runtime-change`, `print-validated: false`.

La revue humaine du 2026-07-14 confirme que le MVP est utilisable comme version
de developpement, mais identifie avant les geometries V0.2 une dette de densite,
de stabilite pendant la saisie, d architecture d information, de vocabulaire et
de cycle de document. L audit relie notamment la fermeture de Placement et
ordre a la reconstruction complete des cartes HTML apres chaque changement.

Le rapport `docs/P67_POST_MVP_PRIORITIZATION_REPORT.md` explique les champs
Retrait calcule, encastrement/prise, hauteur utilisable, preference solveur,
sleeves, Verifier/Recalculer, Sauvegarder et Inspecter. Il propose quatre onglets,
des conteneurs parents avec elements enfants, une barre de creation, un vrai
cycle de document local et un calcul adaptatif sans scene Fusion automatique.

Au terme de P67-M000, ADR-0062 propose de placer cette fondation UX dans P44 avant les geometries P45,
puis de conserver P46 comme gate V0.2. Cette reorientation n est pas acceptee :
P67-V reste humain, P44-M001 reste `blocked-by-p67-v`, les complements restent
en quarantaine et aucun runtime, schema, solveur, tolerance, CAD ou statut de
capability n est modifie.

## P67-V - Fondation UX acceptee

Thomas accepte explicitement D67-01 a D67-11, l option C et ADR-0062 le
2026-07-14. P67 passe a `done-human-gate`. P44 porte la fondation UX, P45
conserve les geometries ergonomiques et P46 la gate V0.2 complete. P69 reste
apres P50.

La decision confirme quatre onglets, la composition Conteneur parent ->
Elements enfants, la toolbar sans complements, le bouton X/Y, le calcul hybride
adaptatif sans scene automatique, le cycle de document, la separation gabarit
asset/profil de cavite et les accents semantiques fixes. Les complements restent
en quarantaine pour maintenant.

La revue ajoute deux intentions :

- plateaux, livrets, assets et conteneurs heritent d un jeu pertinent puis
  peuvent le surcharger X/Y/Z par objet ;
- les cartes Conteneurs proposent un mode global discret, un mode unique par
  conteneur, `Solidite` permanente et les calculs secondaires replies.

Ces intentions ne changent encore ni schema ni formule. Asset/cavite,
plateau/encastrement et jeux externes des conteneurs restent distincts. Aucun
default n est modifie. La valeur 0,2 / 0,2 / 0 mm n est pas declaree universelle.
P44-M008 doit produire un contrat/ADR de tolerance et obtenir une gate humaine
avant P44-M009.

P44-M001 devient la seule mission `ready`, avec le contrat
`docs/P44_M001_UI_STATE_STABILITY_CONTRACT.md` et le package cible 0.1.21.
Aucun runtime n est modifie par P67-V. La suite complete de 451 tests passe,
sans constituer une preuve de la future implementation. `print-validated: false`.

## P44-M001 - Stabilite de saisie et d etat de la palette

Statut : `done`, `implemented`, `automated-validated`,
`fusion-retest-required`, `print-validated: false`.

Le package Fusion 0.1.21 stabilise les rendus de palette sans modifier le
schema, le coeur, le solveur, les jeux, les tolerances, les reservations, la
geometrie ou la scene Fusion. Avant toute reconstruction de liste, la palette
capture le focus, la selection/caret, les details ouverts, la carte active et le
scroll. Les champs et cartes sont ensuite retrouves par identifiant metier
stable, jamais par leur seul index de liste.

Chaque edition incremente une revision source. Les reponses derivees de
validation ou de calcul qui correspondent a une revision obsolete sont ignorees;
les reponses pertinentes restaurent le contexte d interaction. Import, chargement
et bootstrap effectuent un reset explicite. Les listes de cinquante conteneurs
sont couvertes dans le bridge et aucun appel de scene Fusion n est ajoute.

Preuves automatisees : 453 tests passes, dont DOM, bridge et transport de
palette ; syntaxe JavaScript, exemple CLI, `compileall`, controle de frontiere
`adsk` et `git diff --check` passes. Une observation Fusion reste requise avant
toute promotion au-dela de `implemented`. P44-M002 ne devient possible qu apres
l integration de ce lot dans `main`.

## P44-M002 - Densite compacte et hierarchie de carte

Statut : `done`, `implemented`, `automated-validated`,
`fusion-retest-required`, `print-validated: false`.

Le package Fusion 0.1.22 compacte les cartes de listes sans masquer leurs
reglages essentiels : le mode Compact garde les champs editables, les grilles
s adaptent aux valeurs X/Y/Z et les actions de carte font au moins 40 px. Les
titres sont renforces, sans nouvelle navigation ni changement de vocabulaire
metier.

Dans les cartes Conteneurs, `Solidite`, paroi minimale et fond minimal restent
visibles. Taille calculee, etage, appui, surplus et raisons par axe rejoignent
`Details calcules`, replie par defaut. Cette presentation ne modifie ni projet,
ni schema, ni calcul, ni scene Fusion ; les garanties de focus/scroll P44-M001
restent actives.

Preuves automatisees : 454 tests, DOM/bridge/transport, syntaxe JavaScript,
exemple CLI, `compileall`, controle de frontiere `adsk` et `git diff --check`.
Une observation Fusion reste requise avant toute promotion au-dela de
`implemented`. P44-M003 ne devient possible qu apres integration de ce lot dans
`main`.

## P44-M002V2 - Correction de densite technique hybride A+B

Statut : `implemented`, `automated-validated`, `fusion-validation-required`,
`human-ux-rework`, `print-validated: false`.

La validation humaine du package 0.1.22 a conclu a un KO de compacite reelle :
les preuves DOM etaient trop faibles pour qualifier la densite visuelle. Ce KO
ne remet pas en cause les garanties de focus, de bridge ou de coeur.

Le package 0.1.23 remplace l empilement de champs etires par des bandes
semantiques et une grille technique dense : identite, dimensions, options,
placement et solidite. Les champs numeriques sont bornes sur palette large,
restent groupes en 2 x 2 sous 560 px et les cibles interactives conservent
40 px. Prise/tolerances, Placement/ordre et Solidite restent visibles ; seules
les explications et valeurs calculees secondaires sont repliees.

Aucun schema, loader, bridge metier, solveur, tolerance, geometrie, CAD IR ou
scene Fusion n est modifie. Preuves : 455 tests, syntaxe JavaScript, exemple
CLI, compileall, frontiere `adsk` et diff-check passes. P44-M003 reste bloque
jusqu au retour humain exact
`P44-M002V Fusion OK 0.1.23 - commit <sha>`.

## P44-M002V accepté et exigence de français accentué

Thomas a confirmé :
`P44-M002V Fusion OK 0.1.23 - commit 2f78a99`.

La correction hybride A+B est donc `fusion-validated` pour la densité et la
lisibilité des cartes. Cette preuve ne qualifie ni impression, ni géométrie.

Le pilotage ajoute un invariant UX : les textes visibles par l’utilisateur
emploient les accents et caractères français corrects. La palette est déjà
déclarée UTF-8 ; les identifiants techniques restent ASCII. La règle s’applique
aux nouveaux textes dès P44-M003 et la normalisation exhaustive de l’historique
est planifiée dans P44-M006. P44-M003 devient `ready-after-p44-m002v`.


## P44-M003 - Quatre onglets, sections fusionnées et X/Y

Statut : `done`, `implemented`, `automated-validated`,
`human-fusion-gate-required`, `no-business-change`, `print-validated: false`.

Le package Fusion 0.1.24 ramène la navigation à quatre onglets : Boîte et
plateaux, Conteneurs et éléments, Réglages, Aperçu. Précédent et
Suivant disparaissent. Les collections restent plates : la composition
conteneur-parent / éléments-enfants est toujours P44-M004.

Le bouton X/Y échange localement les deux dimensions de boîte, d’élément et
de plateau/livret. Pour un conteneur, il échange le contrat complet X/Y : mode,
cible, fixe et expansion. Il ne modifie ni origine, ni Z, ni valeur résolue. Un
élément Cartes devient une mesure explicite comme lors d’une édition directe.
`rotation_deg_z` reste compatible et uniquement exposée dans un détail historique.

`Retrait calculé` devient `Ordre de retrait`. La phrase de plateau/livret
explique position, taille du logement encastré et côté de la zone de prise.
Les textes modifiés sont en UTF-8 accentué ; le roundtrip du nom
`Éléments d’été — boîte à dés` est couvert.

Preuves automatisées : DOM, bridge conservé, roundtrip, Qt transport,
acceptance P66 de non-régression et alignement Fusion-only. La suite complète,
compileall, frontière `adsk`, diff-check et installation Fusion restent requis
avant P44-M003V. Aucune validation Fusion ni impression n’est revendiquée.


## P44-M003V acceptée puis P44-M004 — Composition conteneur / contenu

Thomas a confirmé P44-M003V Fusion OK 0.1.24 - commit 7b71d01 : les quatre
onglets et l’interversion X/Y de P44-M003 sont fusion-validated. La preuve
reste limitée à cette UX ; print-validated: false.

P44-M004 livre le package 0.1.25. La palette projette maintenant les contenus
sous leur conteneur via container_group_id, sans migration ni arbre récursif.
Le titre est le nom éditable, le changement de parent devient Déplacer vers…,
et les dimensions ont un mode unifié par conteneur. Les anciens projets aux
axes divergents restent éditables via Personnalisé et leur détail historique.
Le mode global est confirmé et n’invente aucune dimension cible ou fixe.

Statut : implemented, automated-validated, human-fusion-gate-required,
fusion-validated: false pour P44-M004, print-validated: false. Aucun schéma,
bridge, solveur, tolérance, géométrie, CAD IR ou scène Fusion n’est modifié.
La prochaine preuve est P44-M004V dans Fusion.

## P44-M004V — retour de densité non accepté et correction P44-M004V2

La revue humaine du package 0.1.25 confirme des comportements de composition,
mais refuse la densité UX : largeur utile sous-exploitée, titres et aides
redondants, premier conteneur trop bas et comparaison de plusieurs relations
parent/enfants insuffisante. P44-M004 ne devient donc pas fusion-validated.

P44-M004V2 livre l’hybride C dans le package 0.1.26. La palette utilise jusqu’à
1180 px, réunit état et cycle de vie, conserve une seule barre de création et de
densité, puis affiche boîte, plats, conteneurs et contenus en rangées techniques.
Les réglages primaires restent visibles ; actions et calculs secondaires sont
repliés. Les cibles principales restent à 40 px et trois seuils responsifs
préservent l’usage étroit.

Statut : implemented, automated-validated, human-fusion-gate-required,
fusion-validated: false, print-validated: false. Aucun schéma, bridge, solveur,
tolérance, géométrie, CAD IR, scène Fusion ou complément n’est modifié. La
prochaine preuve est P44-M004V2 dans Fusion sur le package 0.1.26.

## P44-M004V2H01 — contrôles collants et notifications temporisées

La revue Fusion de 0.1.26 accepte la compacité hybride C et demande deux
ajustements avant fermeture de gate. Le package 0.1.27 garde la barre Créer et la
ligne Plateaux et livrets collées sous les onglets avec un offset dérivé de la
hauteur réelle de l’en-tête. Les confirmations sont remontées et disparaissent
après 3 secondes ; avertissements et erreurs après 6 secondes.

Statut : implemented, automated-validation-required,
human-fusion-gate-required, fusion-validated: false,
print-validated: false. Aucun schéma, bridge, solveur, tolérance, géométrie,
CAD IR ou scène Fusion n’est modifié.

## P44-M004V2 acceptée — gate Fusion 0.1.27

Thomas a confirmé "P44-M004V2 Fusion OK 0.1.27 - commit 80c1a6c".

Statut : done-human-gate, fusion-validated pour la surface UX P44-M004V2 ;
print-validated: false.

La validation humaine couvre la densité hybride C, l’affichage compact de la
composition conteneur / éléments, les contrôles Créer et Plateaux et livrets
collants, et les toasts temporisés. Elle ne promeut aucune capability de
schéma, bridge, solveur, tolérance, géométrie, CAD IR, scène Fusion automatique
ou impression physique.

P44-M005 est ready-for-explicit-go et reste non commencée.

## P44-M005 — création pilotée et presets

Le package 0.1.28 remplace les boutons de presets dispersés par une création
explicite : un preset, une destination Nouveau conteneur lié ou existante, puis
Ajouter. Le raccourci + local réutilise le preset sélectionné dans le conteneur
courant. Les presets personnels apparaissent dans la même liste ; import,
export et suppression locale sont conservés.

Statut : implemented, automated-validation-required,
human-fusion-gate-required, fusion-validated: false,
print-validated: false. Aucun schéma, bridge, solveur, tolérance, géométrie,
CAD IR ou scène Fusion n’est modifié. Les compléments restent en quarantaine.
La prochaine preuve est P44-M005V dans Fusion.

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


## P44-M006 — réglages, cycle document et diagnostic

Statut : done-human-gate, package 0.1.30, fusion-validated: true,
print-validated: false.

Preuve humaine : P44-M006 Fusion OK 0.1.30 - commit d82def6. Le KO 0.1.29 est
fermé : l’état Fusion de démarrage et Inspecter reste lisible, et Nouveau,
Ouvrir ou récent confirme uniquement l’abandon d’une édition non enregistrée.

Le bridge sans adsk gère maintenant un document nommé, des récents bornés et une
récupération locale atomique. La palette utilise le FileDialog Fusion pour
Ouvrir et Enregistrer sous ; Nouveau ne peut pas écraser le dernier fichier
nommé. Les réglages sont visibles, documentés et la hauteur de conception est
dérivée de Z moins le jeu sous le couvercle. Les outils de scène sont repliés
dans Diagnostic et scène Fusion, avec confirmation pour Effacer.

Aucun schéma, solveur, tolérance, géométrie, CAD IR, complément ou
matérialisation automatique ne change. Les 467 tests, la compilation et les contrôles de frontière sont verts. La gate P44-M006V est validée ; print-validated: false.

## P44-M008 - Contrat de jeux herites et overrides par objet

Statut : proposition documentaire integree, gate humaine ouverte,
print-validated: false.

Le contrat et ADR-0063 proposent trois roles physiques distincts, une cascade
par axe avec zero explicite et la preservation P65 : asset-cavite et plat X/Y
par cote, jeu plat Z sous l element, boite X/Y par cote, voisinage conteneur
X/Y/Z total. La proposition de paire conteneur est max. Aucun code, schema
execute, solveur, CAD IR, materialisation ou valeur numerique n a change.

P44-M009 reste bloquee jusqu a validation humaine explicite des formules,
defaults projetes et migration.

## P44-M009 - Jeux par objet implementes (2026-07-16)

Statut : done, implemented, automated-validated, package 0.1.31,
fusion-validated: false, print-validated: false.

La gate P44-M008 accepte l option B. Le schema additif resout les overrides
X/Y/Z, preserve null comme heritage et 0 comme valeur explicite. Les projets
historiques gardent leurs scalaires et resultats. Les conteneurs exposent
between_mm et box_per_side_xy_mm ; toute paire applique max, jamais une somme,
y compris en Z. Coeur, palette, rapports et CAD IR exposent la provenance.
Aucune scene automatique, complement, recalibration ou impression reelle.

P44-M007 devient ready-for-explicit-go ; P44-V reste la gate humaine globale.

## P44-M009H01 - Correction de densité des jeux (2026-07-16)

Statut : implemented, automated-validated, package 0.1.32, présentation UI
observée mais validation fonctionnelle révoquée, fusion-validated: false,
print-validated: false.

Les jeux unitaires des assets, plateaux/livrets et conteneurs sont déplacés
dans des volets repliés par défaut. Le parcours normal expose un seul champ
X/Y et un champ Z séparé lorsque le rôle le prévoit. Une saisie X/Y met à jour
les deux axes.

Le schéma, le loader, le cœur, les rapports, le solveur et la CAD IR restent
compatibles X/Y/Z. Les valeurs anisotropes importées sont préservées et
signalées jusqu’à une saisie X/Y commune. Aucun défaut, calcul, jeu physique,
géométrie ou comportement de scène ne change.

Preuve humaine initiale : P44-M009H01 Fusion OK 0.1.32 - commit 8fc5157.
Cette preuve est ensuite révoquée pour le comportement fonctionnel ; elle ne
conserve qu’une observation visuelle historique. P44-M007 est rebloquée par
P44-M009H02V.

## P44-M009H02 - Isolation corrective des jeux (2026-07-16)

Statut : implemented, automated-validated, package 0.1.33,
human-fusion-check-required, fusion-validated: false, print-validated: false.

La palette synchronise désormais les champs globaux historiques avec les
vecteurs `clearance_defaults_v1` réellement consommés par le moteur et marque
leurs sources `project_default`. Les cartes lisent les dernières valeurs
effectives du recalcul silencieux au lieu de conserver une projection périmée.

Les tests prouvent qu’un override d’asset inférieur remplace le default sans
modifier l’autre asset et qu’avec trois conteneurs un jeu de 2 mm ne concerne
que les interfaces adjacentes ; la paire restante conserve 0,2 mm. La règle
pairwise max de l’ADR-0063 ne change pas. Le champ « Hauteur de conception » est
visiblement grisé, toujours dérivé et non éditable.

Validation : 476 tests, syntaxe JavaScript et tests DOM ciblés passés. P44-M007
reste bloquée par P44-M009H02V.

## P44-M009H03 - Jeux de conteneurs globaux et Réglages dense (2026-07-16)

Statut : implemented, automated-validated, package 0.1.34, human-fusion-check-required, fusion-validated: false, print-validated: false.

La décision produit ADR-0064 retire toute édition et tout effet runtime des jeux externes par bac. Tous les conteneurs utilisent `container_between_mm` et `container_box_per_side_xy_mm` au niveau projet. Les anciens `clearance_overrides_v1` restent validés et sérialisés sans migration destructive, mais sont inactifs.

Les overrides asset, plateau et livret restent inchangés. Réglages sépare désormais les épaisseurs minimales et un tableau global X/Y–Z : jeu entre conteneurs, jeu conteneur-boîte et jeu élément-cavité par défaut. Le Z conteneur-boîte correspond à la marge sous couvercle. « Hauteur de conception » reste dérivée, grisée et non éditable.

Validation : 474 tests, syntaxe JavaScript et tests DOM passent. Compileall, frontière adsk et `git diff --check` passent également. P44-M009H02V est annulée ; P44-M007 reste bloquée par P44-M009H03V.

## P44-M009H04 - Densité finale de Réglages et des conteneurs (2026-07-16)

Statut : implemented, automated-validated, package 0.1.35, human-fusion-check-required, fusion-validated: false, print-validated: false.

La revue Fusion 0.1.34 accepte la direction fonctionnelle H03 mais refuse encore deux étirements UI. H04 borne le bloc Réglages à 760 px et son tableau à 590 px, avec toutes les grilles alignées à gauche.

Dans les cartes conteneur, le nombre d’éléments passe sous le nom, le minimum et le mode sont bornés, les libellés deviennent « Épaisseur paroi » et « Épaisseur fond ». En Cible/Fixe, X, interversion, Y et Z sont placés directement dans l’en-tête ; en Auto ils sont absents. La rangée de dimensions séparée est supprimée.

Aucun schéma, bridge, solveur, tolérance, géométrie ou comportement de scène ne change. Validation : 474 tests, syntaxe JavaScript, tests DOM et transport Qt, `compileall` et frontière `adsk` passent. P44-M007 reste bloquée par P44-M009H04V.

## P44-M009H05 - En-tête conteneur distribué et mode global fiable (2026-07-16)

Statut : done, implemented, automated-validated, fusion-validated, package 0.1.36, commit 7c76ba0, print-validated: false.

La revue Fusion 0.1.35 confirme la densité générale et demande une dernière distribution horizontale : identité et minimum à gauche, contrôles du mode jusqu’à la suppression justifiés à droite. Le mode global quitte sa bande dédiée et rejoint la ligne Conteneurs.

Le sélecteur global ne prétend plus être Auto lorsque les cartes diffèrent : il affiche Mixte, ou le mode uniforme réel. Appliquer Auto, Cible ou Fixe configure les trois axes de chaque conteneur ; Cible et Fixe peuvent repartir des dimensions explicites existantes ou des minima calculés.

Aucun schéma, bridge, solveur, tolérance, géométrie ou comportement de scène ne change. Validation automatisée : 475 tests, syntaxe JavaScript, DOM, transport Qt, compileall et frontière adsk passent. Preuve humaine : P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0. P44-M007 est ready-for-explicit-go ; aucune validation d’impression n’est acquise.

## P44-M007 - Calcul adaptatif et Aperçu priorisé (2026-07-16)

Statut : implemented, automated-validated, package 0.1.37, human-fusion-check-required par P44-M007V, fusion-validated: false, print-validated: false.

La palette valide les dérivations après 350 ms sans nouvelle édition puis demande la proposition complète à 1 500 ms de stabilité. Une nouvelle édition annule le solve planifié. Une réponse dérivée ne peut mettre l’UI à jour que si sa révision source est courante et si son identité est la dernière requête du même type. `Recalculer maintenant` reste le fallback manuel ; l’action `Vérifier` disparaît du parcours normal.

Dans Aperçu, le statut compact et les vues dessus/X-Z précèdent désormais les alertes et les détails. `Matérialiser dans Fusion` reste l’unique action de matérialisation et n’est jamais appelée automatiquement. `Hauteur de conception` reste calculée depuis Z moins le jeu sous couvercle, `readonly`, hors tabulation et visiblement grisée.

Aucun schéma, bridge Python, solveur, budget, valeur physique, tolérance, géométrie, CAD IR ou comportement de scène ne change. Validation : 477 tests, syntaxe JavaScript, tests ciblés DOM/Aperçu/transport Qt/squelette, parse PowerShell, suite complète, `compileall`, exemple CLI, frontière `adsk` et préparation dry-run de la gate passent. P44-M007V est la seule action suivante ; aucune validation d’impression n’est acquise.

## P44-M007H01 - Focus stable, cartes explicites et conteneurs repliables (2026-07-16)

Statut : implemented, automated-validated, package 0.1.38,
human-fusion-check-required par P44-M007H01V, fusion-validated: false,
print-validated: false.

Le retour humain sur le package 0.1.37 a confirmé une perte de focus et de
sélection lors des éditions rapides. La cause était la reconstruction complète
du DOM éditable à chacune des réponses silencieuses d’autosave, validation et
solve. La palette 0.1.38 met désormais à jour les statuts, l’Aperçu et les faits
calculés sans remplacer les champs. La peinture des dimensions dérivées est
différée tant qu’un champ éditable reste actif ; un rendu complet n’est conservé
que pour une mutation réellement structurelle.

Les cartes placent `Méthode de mesure` entre Forme et X. `Épaisseur paquet`
affiche Z et masque Qté/Épaisseur carte ; `Épaisseur carte × nb` fait
l’inverse. Les sleeves exposent un delta commun X/Y et un delta Z par carte en
mode compté. Les champs projet correspondants sont optionnels : leur absence
conserve le catalogue historique, leur activation dans la nouvelle UI propose
2,0 mm et 0,08 mm. Ces valeurs restent non validées physiquement.

Chaque conteneur devient une section repliable indépendante : son en-tête
complet reste visible et seuls ses assets sont masqués. Le solveur, ses budgets,
les tolérances, la géométrie, la CAD IR et la matérialisation automatique ne
changent pas.

Validation automatisée : 481 tests, syntaxe JavaScript, tests ciblés
catalogue/projet/presets/DOM/transport, parse PowerShell, dry-run de gate,
`compileall`, exemple CLI, frontière `adsk` et `git diff --check`.
P44-M007H01V a été supersédée avant observation par P44-M007H02V. Aucune
validation d’impression n’est acquise.

## P44-M007H02 - Mesure cartes et estimation sleeves sans cumul (2026-07-16)

Statut : implemented, automated-validated, package 0.1.39,
human-fusion-check-required par P44-M007H02V, fusion-validated: false,
print-validated: false. P44-M007H01V est supersédée avant observation.

Le preset intégré s’appelle désormais `Cartes` et reste non sleevé par défaut.
La méthode de mesure est le dernier contrôle avant le menu : après Z en
`Épaisseur paquet`, après Épaisseur carte en `Épaisseur carte × nb`.
Les champs inactifs disparaissent au lieu de rester éditables.

Activer les sleeves initialise des deltas éditables de 3 mm au total sur X/Y et
0,19 mm par carte sur Z. Le delta Z est disponible dans les deux méthodes. En
épaisseur paquet, le nombre de cartes est estimé par Z / 0,31, arrondi à
l’entier le plus proche et affiché dans un champ grisé. Le Z résolu ajoute
l’estimation multipliée par le delta Z. Un Z déclaré additif séparé empêche
toute accumulation lors d’un autosave, d’une validation ou d’un roundtrip ;
désactiver les sleeves restitue le Z saisi.

La compatibilité reste conservatrice : un ancien projet sans deltas garde le
comportement catalogue historique. Le solveur de placement, ses budgets, les
tolérances, la géométrie, la CAD IR et la scène ne changent pas. Les modes de
disposition des assets non-cartes sont reportés à P45, où ils pourront avoir un
effet géométrique réel.

Validation automatisée : 483 tests passent, syntaxe JavaScript, tests ciblés
catalogue/projet/presets/DOM/transport, parse PowerShell, dry-run de gate,
`compileall`, exemple CLI, frontière `adsk` et diff-check. P44-M007H02V est
la seule action suivante. Les valeurs 3, 0,19 et 0,31 mm ne sont pas calibrées
physiquement et aucune validation d’impression n’est acquise.

## P44-M007H03 - Repli global et résolution sleeves fiable (2026-07-16)

Statut : implemented, automated-validated, package 0.1.40,
gate P44-M007H03V, fusion-validated: true,
print-validated: false. Preuve reçue le 2026-07-16 :
`P44-M007H03 Fusion OK 0.1.40 - commit 92f07c8`.

Le retour Fusion sur 0.1.39 a confirmé deux défauts : le delta sleeve X/Y
n’était pas appliqué aux cartes en dimensions manuelles et un fait `Résolu`
ancien pouvait rester visible pendant autosave, validation et solve. Le cœur
conserve désormais `card_declared_xy_mm` séparément des dimensions résolues,
comme il le faisait déjà pour le Z déclaré. Le cas signalé 66 × 88 × 27 mm avec
deltas 3 mm et 0,19 mm/carte estime 87 cartes et résout 69 × 91 × 43,53 mm ;
désactiver les sleeves restitue 66 × 88 × 27 mm et le roundtrip ne cumule rien.

La palette marque immédiatement les faits cartes `À recalculer` après une
édition et ne repeint le résultat courant qu’après acceptation de la dérivation
correspondante. Les champs secondaires ont été compactés, `Nb cartes` remplace
le libellé long, les modes obsolètes `Compact`/`Détaillé` ont été supprimés,
les placeholders d’épaisseur indiquent `Défaut` et un contrôle global replie ou
déplie tous les conteneurs sans mutation du projet.

Validation automatisée : 484 tests passent, syntaxe JavaScript, parse
PowerShell, dry-run de gate, `compileall`, exemple CLI, frontière `adsk` et
diff-check. Le solveur de placement, ses budgets, les tolérances, la géométrie,
la CAD IR et la scène restent inchangés. Les valeurs 3, 0,19 et 0,31 mm ne sont
pas calibrées physiquement. P44-M007H03V est validée dans Fusion ;
P0-M010 devient la prochaine mission documentaire.

## P0-M010 - Pilotage de reprise compact (2026-07-16)

Statut : done, documentation-validated, sans changement runtime ni validation produit supplémentaire.

`docs/PILOTAGE_CURRENT.md` devient le point d’entrée court : état actif, une seule prochaine mission, éléments bloqués et liens vers les sources canoniques. `RESUME_STATE.md` conserve explicitement le snapshot P22 comme archive historique. Les instructions de reprise utilisent une lecture progressive : index, action/gate/contrat actifs, puis sources de détail si nécessaire.

P44-VP devient la seule mission `ready` : elle prépare P44-V sans ouvrir P45 ni modifier le runtime. `print-validated: false` reste inchangé.

## P44-VP - Préparation de la gate globale P44 (2026-07-16)

Statut : done, gate-prepared, documentation-validated. Le dossier et le script installent et contrôlent le package 0.1.40 de référence `92f07c8`, puis ne laissent à Thomas que la revue Fusion globale. P44-V devient la seule action humaine suivante. Aucun runtime, solveur, schéma, tolérance, géométrie, scène automatique ou valeur physique ne change ; `print-validated: false`.


## P44-VH01 - Correction du plafond Z réellement transmis

Le retour P44-V a confirmé tous les autres points observés, mais a produit un KO contextuel sur un projet dense : environ 23 conteneurs, plusieurs éléments plats et impossibilité persistante malgré un Z de boîte porté à 5 000 mm.

Le solveur multi-étages n’était pas la cause primaire. La palette affichait Hauteur de conception = Z moins jeu sous couvercle, tandis que le payload conservait une ancienne box.usable_height_mm. Le cœur continuait donc à chercher dans l’ancienne hauteur et rejetait correctement les cavités qui ne pouvaient pas gagner les 10 mm de réservation supérieure.

P44-VH01 synchronise la hauteur cachée avec la valeur dérivée lors des deux éditions concernées et avant tout envoi moteur ou document. Une régression de 24 conteneurs avec plateau et 5 000 mm réellement disponibles construit plusieurs étages sans collision. Le solveur, ses budgets et ses heuristiques ne changent pas.

Package : 0.1.41. Statut : implemented, automated-validated ; cas initial observé comme calculable, gate P44-VH01V supersédée par P64-H01V, fusion-validated: false, print-validated: false. P44-V reste ouverte. P44-VH02 est le lot UX suivant après P64-H01V ; P45 reste bloqué.


## P64-H01 - Recherche dense et répartition 3D équilibrée (2026-07-17)

Le projet réel de 30 conteneurs et 77 éléments utilise environ 40 % du volume
minimal disponible. Après ajout d'un asset 10 × 10 × 5 mm dans le bac le plus
dense, les groupes contigus historiques ne produisaient pourtant plus aucun
candidat à 183 mm de hauteur. Un prototype non contigu réparti en deux groupes
d'empreintes comparables démontre une solution complète.

Le solveur évalue désormais des partitions adaptatives LPT de tailles variables
avant les familles historiques, avec huit nombres d'étages au maximum par ordre
et une borne Z optimiste. Le mode `balanced` choisit aussi ses rangées XY en
fonction de la hauteur d'étage, compare l'expansion moyenne X/Y/Z et équilibre
les empreintes minimales entre niveaux. Le mode `compact` conserve sa priorité
aux compositions simples.

Les régressions donnent 1, 2 puis 3 étages pour 2, 8 puis 32 conteneurs
homogènes, contre un étage pour 8 en mode compact. La fixture dense anonymisée
trouve deux étages complets ; le projet réel augmenté trouve une solution en
environ 1,8 seconde. Aucun schéma, défaut, tolérance, valeur physique, cavité,
géométrie ou comportement de scène ne change.

Validation automatisée : 488 tests, `compileall`, exemple CLI, dry-run de la
gate Fusion, frontière `adsk` et `git diff --check`.

Package : 0.1.42. Statut : implemented, automated-validated,
fusion-validated: true par la preuve `P64-H01 Fusion OK 0.1.42 - commit
5865645`, print-validated: false. P44-VH02 est désormais la seule mission de
code suivante ; P45 reste bloqué.


## P44-VH02 - Suppression directe et noms de conteneurs non ambigus (2026-07-17)

La palette expose une croix de suppression directement a cote du menu de chaque element. La suppression d'un conteneur non vide demande une confirmation : l'annulation conserve tout, la confirmation retire atomiquement le conteneur et tous ses elements. Toute creation de conteneur applique un suffixe numerique deterministe au premier nom deja present.

Aucun schema, bridge, solveur, valeur physique, tolerance, geometrie, CAD IR ou scene automatique ne change.

Package : 0.1.43. Statut : implemented, automated-validated, human-fusion-check-required par P44-VH02V, fusion-validated: false, print-validated: false. P44-V reste ouverte ; P45 reste bloque.
## P64-H02 — Reprise diversifiée après cul-de-sac (2026-07-17)

Le nouveau cas Fusion sauvegardé n’est pas un manque de volume : la boîte mesure
250 × 180 × 70 mm et contient 8 conteneurs, 11 éléments et deux réservations
supérieures. Le portefeuille canonique trouve 8 candidats complets en volume,
mais tous placent une cavité trop haute sous le plateau ou le livret. Un ordre
différent des mêmes corps construit une solution complète en deux niveaux.

Le solveur conserve son chemin canonique. Seulement après
`NO_STAGE_COMPOSITION_FITS` ou `NO_VALIDATED_STAGE_PROPOSAL`, il essaie au plus
six ordres diversifiés, déterministes et stables. L’état exact laissé dans Fusion
construit 8 conteneurs sur 2 niveaux après 3 portefeuilles au total. Les compteurs
agrégés restent exposés. La croix de suppression et le menu `...` partagent aussi
désormais la même cellule de la ligne principale.

Package : 0.1.47. Statut : implemented, automated-validated ; P64-H03R conserve la recherche dirigée au-dessus de H04.
Un cas dense demeure un KO contextuel ; `fusion-validated: false`, `print-validated: false`. Aucun schéma,
default, dimension physique, tolérance, cavité, réservation, géométrie, CAD IR
ou comportement de scène ne change. P64-A01/H04 supersèdent la trajectoire ;
P44-V reste ouverte et P45 reste bloqué.

## P64-A01 — Architecture portefeuille multi-solveurs (2026-07-17)

Statut : `done`, `documentation-validated`, sans modification runtime.

Le retour P64-H02V confirme les corrections UX mais révèle un nouveau faux
impossible. P64-H03R conserve davantage d'ordres et de structures car ils
résolvent des cas supplémentaires ; un cas réel l'épuise encore. Le package
reste sans preuve `fusion-validated`.

ADR-0068 conserve le solveur par étages comme baseline rapide et planifie un
greedy 3D EP/EMS, un beam robuste, un portefeuille Auto et un mode exact futur.
ADR-0069 sépare faisabilité et finition : fermeture continue puis harmonisation
modulaire, avec fallback obligatoire vers la solution certifiée.

Le programme P64-H05 à H08 constituait le chemin critique avant P64-V2 et reprise
de P44-V. P64-H05/H06/H07/H08 sont intégrés ; P64-V2 0.1.51 a ensuite reçu
un KO contextuel et P64-V2H01 porte la gate corrective. P45/P46 et les lots ultérieurs ne
sont pas ouverts. Aucun schéma, default, dimension physique, tolérance, cavité,
géométrie, CAD IR ou scène ne change ; `print-validated: false`.


## P64-H05 — Contrat commun et baseline `Étages et piles` (2026-07-17)

Package : 0.1.48. Statut : `implemented`, `automated-validated`.

La baseline H03R reste le chemin `stage_stack`. Elle est maintenant enveloppée par des candidats, budgets et certificats immuables. Le validateur commun est utilisé durant la sélection et avant exposition d'une solution complète ; il couvre boîte, jeux, collisions, enveloppes, cavités/parois/fonds, réservations, appuis, retrait, conservation et absence de corps automatiques.

Les références H04 simple, dense et réservations restent identiques bit-à-bit ; les ordres, piles, budgets, score, digest et télémétrie H04 ne changent pas. Un cas dense contextuel reste sans solution dans le budget, donc P64-H06 reste nécessaire. Aucune preuve Fusion ni impression nouvelle : dernière preuve solveur P64-H01 0.1.42 ; `print-validated: false`.

## P64-H06 — Placement 3D libre greedy EP/EMS (2026-07-17)

Package : 0.1.49. Statut : `implemented`, `automated-validated`.

La famille interne `free_3d_greedy` place une enveloppe canonique par conteneur
avec des espaces maximaux vides, des points extrêmes issus des faces, le choix
du participant courant le plus contraint, les rotations XY 0/90 et une seule
trajectoire greedy déterministe. Les limites sur états, essais, EMS et points
sont explicites et obligatoires ; aucun profil produit par défaut n'est créé.

Le corpus H04 simple, dense H01 et réservations H02 est placé. Les tests couvrent
aussi un franchissement de plan Z local, un appui supérieur sur deux corps, la
non-collision, la déduplication, le déterminisme, les bornes nécessaires et
l'épuisement honnête du budget. Le moteur réutilise le validateur géométrique
commun ; la certification produit complète est livrée ensuite par P64-H07 avant
toute exposition comme matérialisable.

Le chemin public `solve_partition_plan` et la baseline `stage_stack` ne changent
pas. Beam, portefeuille Auto, profils d'effort, UI, finition, cales, variantes
P45 et solveur exact restent hors scope. Aucune nouvelle preuve Fusion ni
impression : dernière preuve solveur P64-H01 0.1.42 ; `print-validated: false`.
## P64-H07 — Beam robuste et portefeuille Auto (2026-07-17)

Package : 0.1.50. Statut : `implemented`, `automated-validated`.

La famille interne `free_3d_beam` conserve plusieurs états EP/EMS, explore les
rotations XY et les enveloppes finales autorisées, et s'arrête sous des limites
dures d'états, essais, largeur, temps et candidats. Une fermeture libre ne
reclasse aucun résiduel : plus aucun EMS imprimable ne doit rester.

L'adaptateur libre restaure enveloppes, cavités, parois, fonds, réservations,
appuis, retrait et conservation avant le certificat commun. Celui-ci vérifie
désormais aussi l'identité exacte entre snapshot candidat et placements du
plan. `portfolio_auto` conserve le fast path simple, applique trois profils
monotones, refuse les admissions seulement géométriques, déduplique entre
familles et classe seulement des plans certifiés.

Le corpus H04 simple/dense/réservations conserve une solution Auto certifiée ;
un cas multi-niveaux distinct obtient un plan beam complet certifié. Le chemin
public `solve_partition_plan`, le schéma, l'UI, les dimensions physiques, les
jeux, la CAD IR et la scène restent inchangés. P64-H07 se termine ; P64-H08 est alors préparée, sans
preuve Fusion ou impression nouvelle. `print-validated: false`.

## P64-H08 — Réglages Fusion, critères honnêtes et diagnostic secondaire (2026-07-17)

Package : 0.1.51. Statut : `implemented`, `automated-validated`.

La palette expose `Auto intelligent` (défaut), `Étages et piles` et
`Placement 3D libre`, avec les efforts Rapide/Normal/Approfondi. Les réglages
sont conservés dans l'état local du document, pas dans `bgig.project.v1` : aucun
projet existant n'est migré ou auto-enregistré par ce choix.

Le chemin Auto classe seulement les plans complets certifiés ; le mode baseline
reste préservé et le mode 3D libre exclut la baseline. Les propositions
résiduelles héritées restent visibles, non matérialisables et diagnostiquées.
La réponse silencieuse des préférences ne reconstruit pas le DOM éditable ; elle
relance un aperçu adaptatif borné en conservant focus et sélection.

P64-V2 a été préparée par `scripts/fusion/prepare_p64_v2_solver_portfolio_test.ps1`
puis a reçu un KO contextuel sur le cas dense réel ; aucune preuve Fusion ou
impression nouvelle n'est revendiquée.
`print-validated: false`.

## P64-V2H01 — Fermeture continue corrective avant certificat (2026-07-17)

Le cas Fusion réel de P64-V2 a été reproduit sur la sauvegarde locale : boîte
250 x 180 x 70 mm, 9 conteneurs, 26 éléments et deux réservations supérieures.
Dans la 0.1.51, Étages et piles ne trouvait aucun arrangement ; le greedy
produisait une géométrie non certifiée avec résiduel ; le beam élaguait avant
placement complet. Les familles étaient distinctes dans le code, mais aucune
ne produisait le résultat utilisateur attendu.

Le package 0.1.52 sépare désormais placement des minima et fermeture continue.
Le beam conserve plusieurs états compacts, les zones plateau/livret sont
conditionnelles, puis seuls les axes Auto/Cible absorbent le résiduel avant
certificat. Aucun corps n'est créé et aucun axe Fixe, asset, cavité, paroi,
fond, jeu ou défaut physique n'est recalibré.

La fixture anonymisée du cas réel établit que :

- Étages et piles reste honnêtement sans solution dans son budget ;
- Placement 3D libre et Auto trouvent 9 corps certifiés sur plusieurs niveaux ;
- le résiduel imprimable final est nul ;
- les coupes supérieures, cavités, supports et retraits passent le validateur
  commun ;
- la fermeture expose statut, itérations, candidats et faces alignées.

Statut : implemented, automated-validated, package 0.1.52,
ready-for-human-fusion-check. Préparation :
scripts/fusion/prepare_p64_v2h01_continuous_closure_test.ps1.

La régularité visuelle progresse par alignement de faces, mais la modularité
adaptative reste P64-F02. fusion-validated: false ; print-validated: false.

## P64-V2H02R — Repère de vue de dessus (2026-07-18)

P64-V2H02R est fusion-validated par la preuve `P64-V2H02R Fusion OK 0.1.54 - commit 42e8993`. La vue de dessus est confirmée depuis le dessus, avec l'occlusion, les calculs et la coupe X/Z inchangés.

Le projet réel étendu à 11 conteneurs et 34 contenus révèle quatre faux blocages
internes : dérivation multi-cavités en rangée unique, élagage beam exigeant un
seul EMS, points initiaux ignorant les frontières de réservations et préfiltre de
profondeur non localisé. Le lot 0.1.53 corrige ces quatre mécanismes sans changer
les cavités, les valeurs physiques, le schéma ou la matérialisation explicite.

Le beam exécute d'abord la variante EMS historique à une priorité, puis la
variante multi-EMS avec le plafond du profil. La fixture P64-V2H01 conserve ainsi
sa solution certifiée au lieu d'être évincée par le sur-ensemble de candidats.

Les profils d'effort explorent maintenant 1, 2 et 4 priorités de participants,
avec des largeurs beam 8, 24 et 64. Un même résultat entre profils reste possible,
mais les domaines explorés et les métriques sont désormais réellement distincts.

`bgig.partition_capacity.v1` est attaché à tous les résultats. Sur la sauvegarde
de référence, le volume utilisable par le solveur est 3 105 083,712 mm³, la
somme des enveloppes minimales 2 411 449,9376 mm³ et la marge théorique
693 633,7744 mm³, soit environ 693,6 cm³ et 22,34 %. Cette marge est une borne
nécessaire et non une preuve d'empilabilité.

Après correction des faux blocages, le projet complet reste
`no_solution_within_budget`. Une relaxation exacte de diagnostic hors produit,
sans dépendance ajoutée, conclut à l'infaisabilité de la combinaison canonique
sous les origines explicites et réservations actuelles. Le produit ne revendique
pas cette preuve : il reste honnêtement non certifié et prépare P64-V2H03 pour
les variantes internes bornées, à coordonner avec P45.

La palette affiche la capacité sur succès et échec, retire les mesures trompeuses
des diagnostics de budget et peint la vue de dessus du bas vers le haut avec les
cavités composées avec leur corps parent. Un corps supérieur masque donc les
cavités inférieures.

Package : 0.1.54. Statut : fusion-validated,
done-human-gate par P64-V2H02R ; `fusion-validated: true`,
`print-validated: false`. P44-V et P45 restent bloqués. P64-U01 conserve la future
progression de calcul non modale et annulable ; aucun écran bloquant n'est ajouté.

## P64-V2H03A — Arbitrage des variantes internes (2026-07-18)

Statut : `done-documentation`, architecture acceptée, runtime non commencé.

ADR-0070 et
`docs/P64_V2H03_INTERNAL_VARIANT_COORDINATION_CONTRACT.md` séparent désormais
la conception locale du placement global. P45 possède les intentions
fonctionnelles, futures formes et certificat local. P64 reçoit seulement des
variantes immuables certifiées, choisit paresseusement variante et placement,
puis applique son certificat global.

Le premier runtime restera un fallback correctif après le portefeuille canonique
complet. Les lanes Rapide/Normal/Approfondi devront être préfixes et monotones,
sans produit cartésien ni éviction d'une solution historique. Les caps
numériques seront mesurés et verrouillés dans P64-V2H03B, pas inventés par ce
lot documentaire.

Aucun code, schéma `bgig.project.v1`, default, jeu, tolérance, valeur physique,
cavité, scène Fusion ou comportement de matérialisation n'est modifié.
P64-V2H03B devient la seule mission `ready` ; P64-V2H03C et P64-V2H03V restent
bloquées. P44-V et P45 restent bloquées. `fusion-validated: false` et
`print-validated: false` pour P64-V2H03.

## P64-V2H03B — Frontière locale certifiée (2026-07-18)

Statut : `implemented-core`, `automated-validated`.

`container_internal_variants.py` conserve `canonical_v1`, génère des
relayouts rectangulaires bornés, certifie les invariants locaux, déduplique et
élague par Pareto. Les profils verrouillent 24/48/96 variantes générées,
4/8/12 retenues et 2/4/6 options futures par expansion.

Le corpus 11 × 34 observe 231 layouts bruts sur le cœur dense. Les sorties
publiques restent bit-à-bit identiques. Preuve :
`docs/P64_V2H03B_LOCAL_VARIANT_EVIDENCE.md`.

Suite complète : 556/556 OK (166,087 s). Aucun schéma, solveur public, UI, valeur
physique, scène ou corps automatique n'est modifié. H03C devient `ready`.
`fusion-validated: false` et `print-validated: false`.
