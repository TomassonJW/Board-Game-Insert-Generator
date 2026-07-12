# Fusion UI Strategy

Derniere mise a jour : 2026-07-07

## Objectif

P12-UI transforme l'add-in Fusion BGIG d'un flux developpeur vers une interface
utilisable et relancable depuis Fusion.

La strategie reste pragmatique : une commande Fusion classique enrichie est le
chemin principal tant qu'une palette persistante HTML n'apporte pas assez de
valeur pour justifier une architecture plus large.

## Strategie retenue P12-M001

Statut : `fusion-validated`, `print-validated: false`.

La premiere strategie officielle est `toolbar_button_reopens_command_without_addin_restart` :

- l'add-in cree une `CommandDefinition` nommee `Generate Board Game Insert` ;
- il ajoute un bouton dans `Design workspace > Utilities > Add-Ins` ;
- `run(context)` ouvre encore la commande immediatement pour le premier lancement ;
- si la boite de dialogue perd le focus ou se ferme, l'utilisateur peut cliquer
  le bouton toolbar pour rouvrir BGIG sans redemarrer l'add-in ;
- les handlers Fusion restent conserves au niveau module pour eviter le garbage
  collection ;
- `stop(context)` supprime le bouton, la definition de commande courante et
  l'ancien identifiant de commande ;
- `cad_ir_path.txt` et `exploded_view_mode.txt` restent des valeurs par
  defaut/fallback, pas le flux normal.

## Strategie retenue P12-M002+

Statut : `implemented-fusion`, validation Fusion manuelle requise,
`print-validated: false`.

La strategie P12-M002+ est `command_dialog_parametric_v0` :

- la meme commande `Generate Board Game Insert` expose une action `generate`,
  `regenerate` ou `clear_bgig_scene` ;
- l'utilisateur peut toujours fournir directement `CAD IR JSON path` ;
- l'utilisateur peut aussi fournir `BGIG config JSON path` et, si l'auto-detection
  echoue, `BGIG project root` ;
- l'add-in ajoute uniquement `<project root>/src` au `sys.path` cote add-in pour
  importer le coeur Python pur ;
- l'add-in applique les overrides de la commande a une config temporaire, genere
  une CAD IR temporaire, puis consomme cette CAD IR ;
- Fusion ne recalcule pas layout, solveur, clearances ou tolerances ;
- `Regenerate` nettoie les objets BGIG tagues puis regenere ;
- `Clear BGIG Scene` supprime uniquement les objets avec attributs BGIG crees par
  les generations P12-M002+.

Champs V0 exposes :

- `CAD IR JSON path` ;
- `BGIG config JSON path` ;
- `BGIG project root` ;
- `Generation mode` : `compact_only` ou `compact_and_exploded` ;
- dimensions de boite `box_inner_x_mm`, `box_inner_y_mm`, `box_inner_z_mm` ;
- grille `grid_units_x`, `grid_units_y`, `grid_units_z` ;
- `wall_thickness_mm`, `floor_thickness_mm` ;
- `peripheral_clearance_mm`, `module_gap_mm` ;
- `print_profile`.

Ces champs sont des overrides de configuration existante. Ils ne constituent pas
encore une UI complete de creation d'assets ou de modules.

## Palette persistante

Une palette persistante BGIG reste une option future, non implementee.

Elle doit etre arretee ou gatee si elle impose une architecture HTML/JS large,
fragile ou difficile a tester hors Fusion. Le chemin de repli reste une commande
Fusion classique plus robuste.

## Modes d'entree

### CAD IR input

Mode valide : l'utilisateur choisit un fichier CAD IR JSON deja genere. Fusion
consomme la CAD IR, sans recalculer layout, clearances, tolerances ou solveur.

### Config input

Mode code en P12-M002+ : l'utilisateur choisit une configuration BGIG JSON.
L'add-in genere une config temporaire avec overrides, puis une CAD IR temporaire.
Ce mode exige que Fusion puisse acceder au repo BGIG via auto-detection ou champ
`BGIG project root`.

## Regeneration V0

P12-M002+ ajoute une regeneration bornee : `regenerate` appelle d'abord
`Clear BGIG Scene`, puis relance la generation depuis la source choisie.

Le nettoyage est conservateur : seuls les objets tagues par BGIG sont supprimes.
Les anciennes geometries non taguees et les objets utilisateur ne sont pas
supprimes automatiquement.

## Limites

- Pas de palette HTML persistante codee.
- Pas d'UI assets complete.
- Pas de nouvelle geometrie Fusion.
- Pas de solveur ou recalcul metier dans Fusion.
- Pas d'export STL/3MF.
- Pas de validation d'impression 3D.
- Validation Fusion manuelle requise pour P12-M002+.
## Correction P12-M002V2 - UI utilisable

Statut : `implemented-fusion`, validation Fusion manuelle requise,
`print-validated: false`.

Le smoke test P12-M002V a refuse la premiere version parce que `regenerate`
pouvait accumuler des doublons, que `Clear BGIG Scene` n'etait pas assez lisible,
que le project root et la config etaient trop manuels, et que les champs
parametriques pouvaient sembler decoratifs.

La correction P12-M002V2 fixe la strategie :

- `Input mode` est explicite : `cad_ir_file`, `config_file`,
  `quick_parametric_box` ;
- `config_file` est le flux utilisateur par defaut quand le repo BGIG est detecte ;
- le project root est resolu via champ UI, `BGIG_PROJECT_ROOT`, auto-detection,
  puis `C:\Users\janko\Documents\BGIG` en dev mode ;
- les chemins valides sont memorises dans `bgig_ui_settings.json` local a l'add-in ;
- les champs parametriques sont des overrides `config_file` uniquement et sont
  rejetes en `cad_ir_file` ;
- `quick_parametric_box` etait visible comme cible produit mais non fonctionnel dans P12-M002V2 ; depuis P12-M003, il est actif via CAD IR temporaire minimale ;
- chaque generation cree une racine Fusion taguee `BGIG Generated Scene` ;
- `regenerate` planifie d'abord la generation, supprime l'ancienne scene BGIG
  taguee seulement si le plan est valide, puis regenere ;
- `clear_bgig_scene` supprime uniquement les objets BGIG tagues et preserve les
  objets utilisateur non BGIG.

La validation Fusion attendue devient `P12-UI-M002V2`.

## Correction P12-M002V3 - generate non cumulatif

Statut : `implemented-fusion`, validation Fusion manuelle requise,
`print-validated: false`.

Le smoke test P12-UI-M002V2 a refuse partiellement le comportement car l'action
`generate` permettait encore d'empiler silencieusement plusieurs scenes BGIG dans
le meme document. La correction P12-M002V3 rend la politique explicite :

- `generate` compte les racines BGIG taguees avant execution ;
- si aucune scene BGIG n'existe, `generate` cree une seule nouvelle scene ;
- si une scene BGIG existe deja, `generate` refuse sans creer de doublon et
  affiche `BGIG scene already exists. Use regenerate or clear first.` ;
- `regenerate` valide la nouvelle generation, nettoie uniquement les objets BGIG
  tagues, puis cree une scene de remplacement ;
- `clear_bgig_scene` reste le chemin explicite de suppression de la scene BGIG ;
- les messages Fusion affichent `BGIG scenes before`, `BGIG objects deleted`,
  `BGIG scenes after` et `Non-BGIG objects preserved`.

La validation Fusion attendue devient `P12-UI-M002V3`.

## Correction P12-M002V5 - occurrence compacte initiale visible

Statut : `implemented-fusion`, validation Fusion manuelle requise,
`print-validated: false`.

Le smoke test P12-UI-M002V4 a montre que la strategie source/helper cachee
cassait la visibilite des bodies. La correction P12-M002V5 utilise l'occurrence
initiale `addNewComponent` comme occurrence compacte visible officielle et cree
seulement l'occurrence eclatee via `addExistingComponent`. Aucune occurrence
source/helper n'est creee ou masquee.

La validation Fusion attendue devient `P12-UI-M002V5`.

### Correction P12-M002V6 - ownership par scene racine unique

P12-M002V6 corrige le modele d'ownership Fusion apres KO de P12-UI-M002V5.
Le chemin actif n'est plus un nettoyage par sous-objets disperses : chaque
generation BGIG cree une occurrence racine unique `BGIG Generated Scene`, taguee
`bgig:role = scene_root`, et tous les objets BGIG generes sont enfants du
`Component` de cette occurrence.

Regles actives :

- `generate` refuse si une racine BGIG ou un objet BGIG tague existe deja ;
- `regenerate` valide la nouvelle generation, supprime les racines BGIG via
  `Occurrence.deleteMe()`, verifie que zero objet BGIG tague reste, puis regenere ;
- `clear_bgig_scene` supprime les occurrences racines taguees, puis nettoie
  seulement les objets legacy explicitement tagues BGIG ;
- les objets utilisateur non BGIG ne sont jamais cibles ;
- aucun sketch, gabarit, body ou feature BGIG ne doit etre cree hors du
  `Component` de la racine `BGIG Generated Scene`.

Le message Fusion doit afficher `BGIG scene roots before`, `BGIG scene roots
created`, `BGIG scene roots deleted`, `BGIG scene roots after`, `BGIG objects
remaining after clear` et `Non-BGIG objects preserved: yes`.

## Correction P12-M002V7 - registry BGIG et inspect read-only

Statut : code hors Fusion implemente, validation Fusion manuelle requise.

Le smoke test P12-M002V6 a ete refuse : Fusion creait des objets visibles, mais
BGIG ne les retrouvait pas ensuite. P12-M002V7 ajoute un registry interne unique
et une action `inspect_bgig_scene` dans le menu Action.

Action `inspect_bgig_scene` :

- ne genere rien ;
- ne supprime rien ;
- liste les occurrences root, components, bodies et sketches ;
- liste les entites avec attribut group `bgig` ;
- affiche `role`, `scene_id`, `module_id`, parent/context et visibilite quand
  disponibles ;
- signale les objets dont le nom ressemble a BGIG mais sans attribut BGIG.

Smoke test P12-UI-M002V7 :

1. Copier l'add-in a jour depuis le repo vers le dossier Fusion AddIns.
2. Ouvrir un document Fusion Assembly-compatible propre.
3. Creer un petit objet utilisateur non BGIG pour verifier la preservation.
4. Lancer `BoardGameInsertGenerator`.
5. Choisir Action = `inspect_bgig_scene`, puis Run.
   - Attendu : `BGIG scene roots total: 0`.
   - Attendu : l'objet utilisateur peut etre visible dans les compteurs globaux,
     mais il ne doit pas apparaitre comme entite taguee BGIG.
6. Choisir Action = `generate`, Input mode = `config_file`, config
   `examples/simple_asset_product_scene.json`, mode `compact_only`, puis Run.
   - Attendu : pas d'erreur Python.
   - Attendu : `BGIG scene roots created: 1`.
   - Attendu : `Registry validation: ok` ou diagnostic actionnable.
   - Attendu : un module visible.
7. Relancer Action = `inspect_bgig_scene`.
   - Attendu : `BGIG scene roots total: 1`.
   - Attendu : occurrence racine `scene_root`, occurrence compacte
     `compact_occurrence`, component `module_component`, body `module_body` et
     box reference tagues avec `scene_id`.
   - Attendu : aucune incoherence critique.
8. Relancer Action = `generate` sans clear.
   - Attendu : refus propre, aucun doublon cree.
9. Lancer Action = `regenerate` deux fois.
   - Attendu : toujours exactement une scene BGIG, aucun doublon visuel.
10. Lancer Action = `clear_bgig_scene`.
    - Attendu : `BGIG scene roots deleted: 1`.
    - Attendu : `BGIG objects remaining after clear: 0`.
    - Attendu : objet utilisateur non BGIG preserve.
11. Relancer Action = `inspect_bgig_scene`.
    - Attendu : `BGIG scene roots total: 0`.
    - Attendu : objet utilisateur non BGIG toujours present.
12. Refaire generate/regenerate/clear avec `compact_and_exploded`.
    - Attendu : une occurrence compacte et une occurrence eclatee liees, toujours
      sous une seule scene BGIG.

Si `inspect_bgig_scene` voit un objet BGIG par nom mais sans attribut, copier le
rapport complet : c'est maintenant le diagnostic primaire pour corriger le niveau
exact de creation/tagging Fusion.

## P12-M002V7R - reporting inspect BGIG deduplique

La validation humaine `P12-UI-M002V7` confirme le fonctionnement Fusion de
`inspect_bgig_scene`, `generate`, l'anti-doublon, `regenerate`, `compact_only`,
`compact_and_exploded`, `clear_bgig_scene` et la preservation des objets non
BGIG. L'impression 3D reste non validee.

La correction courante ne change pas la generation ni la geometrie. Elle corrige
le rapport standard `inspect_bgig_scene` :

- les attributs BGIG trouves sont distingues des entites BGIG uniques ;
- une meme entite portant plusieurs attributs n'est plus repetee ;
- `scene_root_component`, `box_reference`, `module_component`, bodies, sketches
  et features ne sont plus comptes comme scene roots ;
- `BGIG scene roots total` compte uniquement les occurrences racines BGIG ;
- les entites deja taguees sont exclues de `BGIG-looking untagged entities` ;
- le rapport standard est court, avec un echantillon limite et des compteurs par
  type d'entite.

Validation Fusion P12-UI-M002V7 apres correction registry inspect :

- inspect avant generation : `BGIG scene roots total: 0`, `Tagged BGIG unique entities: 0`, `BGIG-looking untagged entities: 0`, `Inconsistencies: none` ;
- generate `config_file` sur `simple_asset_product_scene` : `BGIG scene roots created: 1`, `Registry validation: ok`, `Visible BGIG occurrences actual: 1`, `Legacy bodies created: 0`, `Body sizing report`, `size match yes` ;
- inspect apres generation : `BGIG scene roots total: 1`, `BGIG scene root occurrences: 1`, entites taguees non redondantes, zero faux positif, `Inconsistencies: none` ;
- regenerate : ancienne racine supprimee, nouvelle scene creee proprement, pas de doublon/stacking, objets non BGIG preserves ;
- clear : racine supprimee, `BGIG objects remaining after clear: 0`, objets non BGIG preserves.
## P12-M003 - quick_parametric_box fonctionnel

`quick_parametric_box` est code comme un flux UI borne et CAD-agnostic : Fusion lit les champs de commande, construit une CAD IR temporaire minimale, puis reutilise le pipeline existant de generation CAD IR. Le mode genere une scene V0 simple avec une boite de reference et un module rectangulaire imprimable derive d'une cellule de grille.

Ce mode ne lance pas de solveur assets, ne change pas les tolerances par defaut et ne genere aucune nouvelle geometrie avancee. Il expose dans le message Fusion les valeurs saisies, la taille theorique de cellule, la taille imprimable planifiee, le `Body sizing report` et `Print validation: false`.

Statut : `fusion-validated`, `print-validated: false`.

Validation Fusion `P12-M003V` du 2026-07-08 :

- input mode utilise : `quick_parametric_box` ;
- action : `generate` ;
- mode : `compact_only` ;
- CAD IR temporaire creee dans le dossier local de l'add-in ;
- boite `120.0 x 80.0 x 30.0 mm`, grille `4 x 4 x 3`, unite `30.0 x 20.0 x 10.0 mm` ;
- body imprimable planifie `28.9 x 18.9 x 8.8 mm` ;
- scene racine BGIG creee, registry `ok`, zero objet BGIG non tague ;
- une occurrence compacte visible, aucun legacy body ;
- bbox Fusion reelle `28.9 x 18.9 x 8.8 mm`, `size match yes` ;
- aucune validation d'impression 3D.

## P12-M004 - Persistance UI et regeneration confortable

Statut : `implemented-fusion`, validation Fusion manuelle `P12-M004V` requise,
`print-validated: false`.

P12-M004 conserve la strategie de commande Fusion classique. Aucune palette HTML
persistante n'est implementee. La commande sauvegarde maintenant dans
`bgig_ui_settings.json` : action, input mode, generation mode, chemins CAD IR,
config JSON et project root, ainsi que tous les champs parametriques P12.

A la prochaine ouverture de `Generate Board Game Insert`, `commandCreated`
rehydrate ces valeurs. Le mode `quick_parametric_box` retrouve donc les dernieres
dimensions de boite, unites de grille, epaisseurs, clearances et profil. Les
modes `config_file` et `cad_ir_file` retrouvent leurs derniers chemins utiles.

Les champs parametriques restent actifs uniquement en `config_file` et
`quick_parametric_box`. En `cad_ir_file`, ils sont affiches comme valeurs
persistantes mais ignores, afin qu'une saisie quick precedente ne casse pas le
chargement direct d'une CAD IR. Si une scene BGIG est deja presente dans le
document, l'ouverture de la commande prefere `Action = regenerate` pour guider
l'utilisateur vers le remplacement sans doublon.

Smoke test P12-M004V attendu : ouvrir BGIG, choisir `quick_parametric_box`, saisir
`120 x 80 x 30`, grille `4 x 4 x 3`, epaisseurs, clearances et profil, generer,
rouvrir, verifier la rehydratation, changer `box_inner_x_mm` a `160`, lancer
`regenerate`, verifier le remplacement sans doublon, rouvrir et verifier `160`,
puis lancer `clear_bgig_scene` en confirmant la preservation des objets non BGIG.
## Automatisation locale des smoke tests Fusion

Depuis la mission de preparation P12-M004V, Codex doit utiliser
`scripts/fusion/` pour preparer les validations Fusion :

- `install_addin.ps1` copie l'add-in courant dans le dossier Fusion AddIns ;
- `prepare_smoke_test.ps1` exporte une CAD IR depuis une config et pre-remplit
  les settings UI ;
- `prepare_quick_parametric_test.ps1` pre-remplit le workflow
  `quick_parametric_box` ;
- `check_installed_addin.ps1` verifie les marqueurs de l'add-in installe.

La procedure humaine commence donc dans Fusion, pas dans PowerShell, sauf si
l'ecriture AppData est bloquee. La reference operationnelle est
`docs/FUSION_SMOKE_TEST_AUTOMATION.md`.
### Correction P12-M004V - settings PowerShell UTF-8 BOM

Le premier smoke test P12-M004V apres automatisation a ete KO : l'UI ne montrait
pas les valeurs preparees. La cause racine etait l'encodage du fichier
`bgig_ui_settings.json` ecrit par PowerShell avec BOM UTF-8, alors que le loader
Python le lisait en `utf-8` avant `json.loads()`.

Correction : le loader lit maintenant les settings avec `utf-8-sig`, les scripts
PowerShell ecrivent en UTF-8 sans BOM, et la commande Fusion affiche un bloc
`UI settings` indiquant le chemin lu, `UI settings loaded`, le mode, l'action, le
mode de generation et les valeurs quick box chargees.

P12-M004V doit verifier ce bloc avant de lancer `generate` ou `regenerate`.

## P13-M001 - quick_asset_box UI V0

`quick_asset_box` est un mode de commande Fusion classique, pas une palette persistante. Le champ `Assets (quick_asset_box)` accepte une saisie compacte :

`asset_id,type,count,x_mm,y_mm,z_mm,fit`

Les entrees sont separees par `;` ou par saut de ligne. Les types UI V0 sont `tokens`, `dice`, `meeples`, `cards`, `sleeved_cards`, `generic`; `generic` est mappe vers le kind coeur `other`. Le champ `fit` accepte `exact`, `loose` ou `approximate`; `loose` est transporte comme `dimension_confidence = approximate`.

La commande genere une config temporaire BGIG stricte depuis les champs boite/grille/parois/clearances/profil et `assets[]`, puis reutilise le pipeline existant : assets charges, `module_candidates`, variante recommandee, `executable_asset_plan`, CAD IR et generation Fusion. Les assets invalides sont refuses dans le rapport sans bloquer si au moins un asset valide reste.

Limites : pas de tableau avance, pas de palette HTML, pas de solveur complexe, pas de nouvelle geometrie Fusion, pas de validation d'impression.

## P13-ASSET-M002 - Reporting et debug visuel count-aware

`quick_asset_box` reste une commande Fusion classique. Le rapport affiche maintenant `count_aware_storage_sizing: yes|partial|no`, `asset_debug_visualization: yes/no`, les capacites par pile, nombres de piles, enveloppe `asset_fit`, taille module et garantie de capacite.

Le debug visuel Fusion est minimal et non imprimable : un sketch `asset-fit debug outline` est cree sur le haut du module asset candidate pour montrer l'enveloppe XY retenue. Les assets individuels ne sont pas dessines et `asset_cavities_generated` reste `no`.

## P13-ASSET-M003 - Smoke quick_asset_box avec cavite

`quick_asset_box` reste la commande Fusion classique. Le smoke test M003 prepare le meme cas count-aware que M002 (`130 x 50 x 60`, grille `4 x 4 x 3`, assets tokens `40` et `23`) mais attend maintenant une coupe reelle : `asset_cavities_generated: yes`, `asset_cavity_policy: single_asset_fit_rectangular_cavity_v0`, une cavite asset-fit planifiee/generee, dimensions de cavite, fond restant et murs attendus.

Le rapport doit encore afficher `asset_items_visualized: no`, l'absence de cavites individuelles par item/pile et `Print validation: false`.

## P13-ASSET-M004 - Smoke quick_asset_box avec compartiments

Le smoke quick_asset_box utilise le cas `130 x 50 x 60`, grille `4 x 4 x 3`, assets `coin-tokens,tokens,40,18,16,2,loose; status-tokens,tokens,23,10,35,2,loose`. Il doit montrer deux compartiments rectangulaires top-open par asset source, `asset_cavity_policy: per_source_asset_rectangular_compartments_v0`, `asset_compartment_cavities_planned: 2`, `asset_compartment_cavities_generated: 2`, debug outlines et `Print validation: false`.

## P13-ASSET-M005 - Smoke quick_asset_box avec encoches d'acces

Le meme smoke prepare maintenant les encoches d'acces V0. Le rapport attendu ajoute `asset_access_features_generated`, `asset_access_policy: per_compartment_top_open_rectangular_notch_v0`, `asset_access_notches_planned`, `asset_access_notches_generated` et `asset_access_notches_refused`.

Validation humaine attendue : verifier dans Fusion que chaque compartiment supporte possede une vraie coupe rectangulaire top-open sur le mur avant, que la paroi interne et le fond restent presents, puis verifier `regenerate` sans doublon et `clear_bgig_scene` avec preservation des objets non-BGIG.

## P14-USABLE-ASSET-TRAY-M001 - UX attendue du layout multi-assets

`quick_asset_box` peut maintenant produire un module asset-first avec plusieurs compartiments asset-specific dans des scenarios 3+ assets, quand le layout row/column/shelf tient dans la boite. L'UI Fusion classique reste une commande, pas une palette persistante. La validation humaine P14 devra verifier que les rapports exposent clairement la strategie de layout et les refus eventuels, sans pretendre a une validation d'impression.

## P14-USABLE-ASSET-TRAY-M002 - Printability dans le message quick_asset_box

Le rapport Fusion `quick_asset_box` affiche maintenant `printability_checked: yes`, `printability_validated_by_print: no`, un resume `printability_report_v0` par module et les `printability_warning`. Cette UI reste une commande Fusion classique et le rapport ne remplace pas une impression de test.

## P14-USABLE-ASSET-TRAY-M003 - Aide inline quick_asset_box

La commande Fusion classique affiche maintenant une aide courte avant le champ `Assets (quick_asset_box)` : format, exemple, unites, role de `count`, semantique `x/y/z`, cas cards/sleeved_cards et valeurs `fit`. Les champs boite/grille/murs/fond/clearances ont des labels plus explicites. Aucune palette HTML n'est introduite.

## P14-USABLE-ASSET-TRAY-M004 - Presets quick_asset_box

Le script `scripts/fusion/prepare_quick_asset_test.ps1` accepte maintenant `-Preset p14_complete`, `-Preset tokens`, `-Preset dice_meeples_generic` et `-Preset cards_tokens`. Les presets sont stockes dans `scripts/fusion/quick_asset_presets.json`, ecrivent les dimensions de boite/grille et le champ `Assets (quick_asset_box)` dans `bgig_ui_settings.json`, et gardent `-AssetsText` comme override manuel. Pour la gate P14, le preset par defaut est `p14_complete` afin de charger 5 assets et de tester un layout multi-assets plus representatif. Cette mission prepare les smoke tests ; elle n'ajoute pas de tableau avance ni de palette persistante.

## P15-M003 - Champ max stack height et reporting stack policy

La commande Fusion classique `quick_asset_box` affiche maintenant un champ optionnel `Max stack height mm (quick_asset_box, optional)`. Vide, les defaults moteur `flat_tray` par type restent actifs. Renseigne, le champ est sauvegarde dans `bgig_ui_settings.json`, rehydrate a la reouverture et applique a la config temporaire sous `assets[].max_stack_height_mm` pour tokens/dice/meeples/generic.

Le message de generation expose la politique de rangement : `storage_orientation`, `stack_height_policy`, `max_stack_height_mm`, `stack_height_used_mm`, `xy_expansion_used` et `z_expansion_used` par asset et par candidat module. Cela prepare la validation P15 sans ajouter de palette HTML ni de tableau assets avance.

## P15-M004 - Semantique grid dans le rapport Fusion

Le rapport `quick_asset_box` affiche maintenant `grid_semantics: placement_reservation_lattice_v0`, `body_snap_to_grid: no`, `grid_span_is_reserved_space: yes` et `body_size_may_be_smaller_than_grid_span: yes`. Le `Module source mapping` et le `Body sizing report` repetent cette distinction : le span grille reserve des cellules, tandis que le body Fusion est dimensionne par `printable_body_size_mm`.

Cette mission ne change pas la geometrie et n'ajoute pas de visualisation de cellules. Elle rend seulement le comportement lisible pour la gate P15.

## P15-M005 - Preset smoke P15

`prepare_quick_asset_test.ps1` utilise maintenant `p15_tray_semantics` par defaut. Ce preset prepare une box `220 x 160 x 60`, une grille `8 x 5 x 3`, `max_stack_height_mm = 18` et cinq assets mixtes. L'objectif UX de gate est de verifier dans Fusion que les champs sont pre-remplis, que `max_stack_height_mm` est persiste, et que le rapport explique `flat_tray`, `stack_height_policy` et la semantique grid.

## P16-M001 - Reporting attendu du packing 2D

La commande Fusion classique `quick_asset_box` doit rester le support de P16. La future implementation doit rendre visibles dans le rapport :

- `tray_packing_policy: flat_tray_2d_v0` ;
- `pile_grid_columns` et `pile_grid_rows` ;
- `target_aspect_ratio` ;
- `max_module_length_mm` ;
- `linear_layout_avoided: yes/no` ;
- warnings si un module reste long parce que le packing 2D ne tient pas.

Aucune palette HTML, aucun tableau asset avance et aucune nouvelle geometrie complexe ne sont introduits par cette strategie.

## P16-M003 - Diagnostics de cavites et notches lies au packing 2D

Le rapport metadata `quick_asset_box` transporte maintenant la politique de packing 2D jusque dans les diagnostics de cavites et d'encoches. Cela permet de verifier que chaque compartiment et chaque notch provient bien de l'enveloppe `flat_tray_2d_v0` retenue, sans visualiser les items individuels ni generer de cavites par pile.

## P16-M004 - UI et resume du packing 2D

La commande Fusion classique `quick_asset_box` expose maintenant deux champs optionnels supplementaires : `Target aspect ratio (quick_asset_box, optional)` et `Max module length mm (quick_asset_box, optional)`. Ils sont sauvegardes dans `bgig_ui_settings.json`, rehydrates a la reouverture, puis appliques aux assets itemises simples de la config temporaire.

Le rapport `quick_asset_box` affiche les valeurs globales et repete `tray_packing_policy`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm` et `linear_layout_avoided` dans les lignes `asset_sizing`, `asset_cavity`, `asset_access_notch` et `module_candidate_sizing`. L'UI reste une commande Fusion classique, pas une palette persistante.

## P16-M005 - Preset smoke P16

`prepare_quick_asset_test.ps1` utilise maintenant `p16_ergonomic_tray_packing` par defaut. Le preset charge cinq assets, une box `240 x 170 x 60`, une grille `8 x 5 x 3`, `max_stack_height_mm = 18`, `target_aspect_ratio = 1.4` et `max_module_length_mm = 70`. L'objectif est de valider visuellement et textuellement le passage de `flat_tray_linear_v0` a `flat_tray_2d_v0` sans nouvelle geometrie produit.


## P17-M001 - Workflow UI export/preprint V0

P17 garde la commande Fusion classique. La future action `export_printables` doit etre presentee comme une action separee de `generate`, `regenerate`, `inspect_bgig_scene` et `clear_bgig_scene`. Elle doit exporter la scene BGIG courante seulement si des modules imprimables sont detectes, puis afficher le dossier, les fichiers, les modules refuses et `print_validated: false`.

Cette action ne doit pas fermer la dette UX generale : pas de palette HTML, pas de tableau assets avance, pas de promesse `ready to print`. Le message doit rester honnete : export technique prepare pour preprint, validation physique toujours requise.


## P17-M002 - Action UI export_printables

L'action `export_printables` est ajoutee a la liste Action de la commande Fusion classique. Elle ne depend pas du mode d'entree selectionne et ne requiert pas de chemin CAD IR/config, car elle agit sur la scene BGIG deja generee dans le document Fusion courant.

Le message utilisateur affiche le dossier export, le format STL, les modules detectes/exportes/refuses, les chemins de fichiers et `print_validated: false`. Les manifestes complets restent une mission separee P17-M003.


## P17-M003 - Rapport manifestes export

Le message `export_printables` affiche maintenant les chemins `manifest_json` et `manifest_markdown`. Ces fichiers sont crees automatiquement dans le dossier export. L'utilisateur ne doit pas les interpreter comme validation d'impression : ils documentent seulement ce qui a ete exporte, refuse et averti.


## P17-M004 - Printability blockers dans UI

Le resume `quick_asset_box` affiche maintenant `printability_status` et `printability_export_allowed` en plus des warnings historiques. Cela rend visible si un export technique est autorise par les checks heuristiques V0, sans transformer ce statut en validation d'impression.

## P17-M006 - Gate export/preprint preparee

Le workflow UI reste une commande Fusion classique, pas une palette persistante. La preparation P17 ecrit les settings `quick_asset_box` avec le preset `p17_printable_export` et laisse l'action initiale sur `generate`. Apres generation, l'utilisateur rouvre BGIG, choisit `export_printables`, puis valide les STL, manifestes, refus non-printables et `print_validated: false`.
## P32 - Palette produit secondaire

Statut : `implemented-fusion-palette`, smoke humain P32 requis, `print-validated: false`.

La restriction historique sur la palette est levee par ADR-0042 et la direction produit acceptee : au lancement, l add-in ouvre une petite palette HTML locale `BGIG - Atelier de rangement` au lieu du formulaire CommandInputs. Elle ne contient pas de chemin CAD ni de policy brute. Elle montre le design recu, l etat de scene et le statut fabrication, puis propose `Previsualiser`, `Mettre a jour la scene`, `Exporter les bacs` et `Reglages experts`.

Le pont reste borne : HTML envoie une action Fusion, l add-in relit le registre ou reutilise les actions existantes, puis renvoie un resume JSON. Aucun calcul de layout, clearance, tolerance ou geometrie metier ne passe dans la palette. La commande historique est conservee comme recours expert et pour les diagnostics. La palette reste `fusion-smoke-required` tant qu elle n est pas observee dans une session Fusion reelle.

## P32 smoke Fusion accepte

Statut : `fusion-validated`, `print-validated: false`.

Le retour humain `P32 Fusion OK` du 2026-07-11 accepte la premiere palette secondaire. La palette est donc le point d entree normal de l add-in; le dialogue CommandInputs demeure le mode expert/secours. Cette validation couvre la surface et son bridge d actions, pas la fabrication physique.

## Decision active depuis ADR-0055

La palette persistante n est plus une option future : elle est la surface produit
principale du MVP Fusion-only.

Elle est embarquee dans fusion_addin/BoardGameInsertGenerator et ne depend
d aucun serveur web. Son bridge appelle le coeur Python pur ; JavaScript ne
calcule ni layout, ni cavite, ni tolerance, ni CAD.

La commande classique reste le mode expert, diagnostic et secours. Les sections
historiques qui disent palette future ou Studio principal sont supersedees par
ADR-0055 et docs/FUSION_ONLY_MVP_CONTRACT.md.

## P58 - Resultat moteur dans la palette principale

La vue Resultat utilise bgig.partition_result_view.v1 et non une illustration.
Elle montre la vue dessus, la coupe centrale, les corps et cavites, les noms de
contenus, le surplus, la pile, les supports, le digest et l invariant zero corps
automatique. Impossible n affiche aucun SVG de solution. Modifier invalide le
plan ; sauvegarder sans modification le conserve. L action de materialisation
reste desactivee jusqu a P59.
