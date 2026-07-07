# Status

Derniere mise a jour : 2026-07-07

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

La correction `P12-M002V7` stabilise l UI Fusion parametrique V0 apres KO P12-UI-M002V6 : modes `cad_ir_file` / `config_file` / `quick_parametric_box (disabled)`, project root auto-detecte ou memorise, settings local `bgig_ui_settings.json`, overrides actifs seulement en `config_file`, generation encapsulee sous une occurrence racine unique `BGIG Generated Scene` taguee `bgig:role = scene_root`, `generate` refuse toute scene ou objet BGIG tague deja present, `regenerate` valide puis supprime la racine par `deleteMe()` avant regeneration, et `clear_bgig_scene` ramene `BGIG objects remaining after clear` a `0` sans toucher aux objets non BGIG. Validation humaine P12-UI-M002V7 confirmee : `inspect_bgig_scene`, `generate`, anti-doublon, `regenerate`, `compact_only`, `compact_and_exploded`, `clear_bgig_scene` et preservation non-BGIG fonctionnent. Statut : `fusion-validated`, `print-validated: false`. Le reporting standard `inspect_bgig_scene` a ensuite ete simplifie pour dedupliquer les entites, compter une seule racine BGIG reelle et supprimer les faux positifs BGIG-looking.

## Phase active

Phase active : **P12-UI-M002V7 validee fonctionnellement / reporting inspect corrige a smoke-tester**.

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

Prochaine action recommandee : smoke test court du reporting `inspect_bgig_scene` corrige avant toute nouvelle extension UI, palette persistante, UI assets complete, solveur plus automatique ou nouvelle geometrie Fusion.

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
- UI Fusion parametrique P12-M002V7 : modes explicites, root auto-detecte/memorise, config JSON -> CAD IR temporaire, overrides config-only, scene racine taguee, `generate` refuse les doublons, occurrence racine unique taguee `bgig:role = scene_root`, suppression par `deleteMe()`, occurrence compacte initiale visible, occurrence eclatee liee via `addExistingComponent`, `regenerate` remplace sans doublons et `clear_bgig_scene` supprime la racine, `fusion-validated`, reporting inspect standard deduplique, `print-validated: false`.
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

Derniere verification pendant `P12-M002V7 - Registry BGIG et inspect read-only` :

- `python -m unittest discover -s tests` : OK, 169 tests passes.
- `python -m py_compile fusion_addin/BoardGameInsertGenerator/BoardGameInsertGenerator.py` : OK.
- `python -m py_compile fusion_addin/BoardGameInsertGenerator/fusion_skeleton.py` : OK.
- CLI Markdown/JSON : OK sur `simple_asset_product_scene.json`, `simple_asset_executable_plan.json`, `simple_multilayer_grid_scene.json`, `simple_tray.json` et `simple_finger_notch_tray.json`.
- Export CAD IR : OK sur `simple_asset_product_scene.json`, `simple_asset_executable_plan.json`, `simple_multilayer_grid_scene.json`, `simple_tray.json` et `simple_finger_notch_tray.json`.
- `git diff --check` : OK.
- `rg -n "adsk" src/board_game_insert_generator` : OK, aucune occurrence dans le coeur Python.
- Validation Fusion reelle : `P12-UI-M002V7` fonctionnelle confirmee. Reporting inspect deduplique code et teste hors Fusion ; smoke test court recommande. Impression 3D non validee.
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
