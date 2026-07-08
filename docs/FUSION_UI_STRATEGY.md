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
