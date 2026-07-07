# Fusion Add-in Skeleton

## Statut

Ce dossier contient l'adaptateur Fusion 360 isole du projet BGIG.

Il est volontairement separe du coeur Python `src/board_game_insert_generator`.
Le coeur reste testable sans Fusion 360 et ne doit pas importer `adsk`.

Depuis `P4-M003`, l'add-in contient une premiere generation minimale de blocs
rectangulaires depuis une CAD IR JSON locale. La fixture P4-M003 a ete lancee,
inspectee et mesuree dans Fusion 360. Depuis `P4-M004`, le chargement du fichier
CAD IR est stabilise : l'add-in peut consommer `cad_ir_input.json` dans son
dossier ou un chemin declare dans `cad_ir_path.txt`. Depuis `P6-M001`, l'add-in
code aussi les cavites rectangulaires simples depuis `subtract_rectangular_cavity`.
Depuis `P6-M002`, il code les encoches simples de paroi depuis
`describe_cavity_feature`, sous forme de coupes rectangulaires. Depuis
`P11-M001`, il code aussi la vue compacte de modules asset-first positionnes par
`metadata.executable_asset_plan`. Depuis la correction `P7-M001V`, il code aussi
une vue eclatee basique par occurrences liees : un composant Fusion unique par
module physique, une occurrence compacte et une occurrence eclatee. Depuis
`P11-M003`, l'add-in expose une commande UI minimale pour choisir le fichier CAD
IR et le mode de generation sans modifier manuellement les fichiers texte locaux. Depuis `P12-M002V3`, la commande expose aussi des champs parametriques V0, un flux config BGIG vers CAD IR temporaire, `generate` non cumulatif, `Regenerate` et `Clear BGIG Scene`.

Ce que l'add-in cree maintenant :

- une esquisse de reference de boite dans le composant racine, nommee comme non
  imprimable ;
- un composant Fusion par module physique BGIG ;
- une occurrence compacte par composant module ;
- une occurrence eclatee liee au meme composant quand le mode `compact_and_exploded` est actif ;
- un sketch d'empreinte et un corps rectangulaire extrude dans la definition du composant module ;
- une coupe rectangulaire verticale par operation `subtract_rectangular_cavity`, dans le composant source ;
- une coupe rectangulaire de paroi par encoche simple supportee, dans le composant source ;
- un module asset-first place par grille, si la CAD IR contient `metadata.executable_asset_plan.placements` ;
- des modules asset-first multi-layer, si les placements CAD IR resolus utilisent plusieurs hauteurs ou une origine Z non nulle ;
- des noms lisibles pour composants, occurrences, sketches, features et bodies.

Ce que l'add-in ne cree pas :

- aucune demi-lune courbe reelle ;
- aucun fond arrondi ;
- aucun couvercle ;
- aucune charniere ;
- aucun fillet/conge ;
- aucun export STL/3MF ;
- aucune validation physique.

## Structure

- `BoardGameInsertGenerator/BoardGameInsertGenerator.manifest` : manifeste
  d'add-in JSON pour installation locale.
- `BoardGameInsertGenerator/BoardGameInsertGenerator.py` : point d'entree Fusion
  avec `run(context)` et `stop(context)`.
- `BoardGameInsertGenerator/fusion_skeleton.py` : logique testable hors Fusion
  pour l'etat document, la validation CAD IR, le plan d'operations et le plan de
  generation.
- `BoardGameInsertGenerator/cad_ir_input.json` : fixture CAD IR locale chargee
  par defaut par l'add-in.
- `BoardGameInsertGenerator/cad_ir_path.txt` : fichier optionnel ignore par Git,
  conserve comme valeur par defaut heritee pour pointer vers une CAD IR JSON exportee ailleurs.
- `BoardGameInsertGenerator/exploded_view_mode.txt` : fichier optionnel ignore par
  Git, conserve comme valeur par defaut heritee pour choisir `compact_and_exploded` ou `compact_only`.
- `BoardGameInsertGenerator/bgig_ui_generated_config.json` : fichier temporaire
  genere par l'UI quand `BGIG config JSON path` est utilise.
- `BoardGameInsertGenerator/bgig_ui_generated_cad_ir.json` : CAD IR temporaire
  consommee par Fusion dans le flux config.

## Installation locale

La version courante de Fusion attend cette structure exacte :

```text
BoardGameInsertGenerator/
  BoardGameInsertGenerator.py
  BoardGameInsertGenerator.manifest
  cad_ir_input.json
  cad_ir_path.txt  # optionnel, local
  exploded_view_mode.txt  # optionnel, local
  fusion_skeleton.py
```

Le nom du dossier, du fichier Python principal et du fichier `.manifest` doit
etre identique. Le manifeste est un fichier texte en JSON, pas en XML.

Option recommandee pour une installation locale non-App-Store :

```powershell
$source = Resolve-Path .\fusion_addin\BoardGameInsertGenerator
$target = Join-Path $env:APPDATA "Autodesk\FusionAddins\BoardGameInsertGenerator"
New-Item -ItemType Directory -Force $target | Out-Null
Copy-Item -Path "$source\*" -Destination $target -Recurse -Force
```

Option alternative, egalement recherchee par Fusion sur Windows :

```powershell
$source = Resolve-Path .\fusion_addin\BoardGameInsertGenerator
$target = Join-Path $env:APPDATA "Autodesk\Autodesk Fusion 360\API\AddIns\BoardGameInsertGenerator"
New-Item -ItemType Directory -Force $target | Out-Null
Copy-Item -Path "$source\*" -Destination $target -Recurse -Force
```

Si l'add-in est ajoute manuellement avec le bouton `+`, selectionner le dossier
exact `BoardGameInsertGenerator`, pas son parent `fusion_addin` ni le dossier
`AddIns`.

Puis redemarrer Fusion 360 ou ouvrir `Utilities > Add-ins`, afficher `All scripts
and add-ins` ou filtrer `Add-ins`, selectionner `BoardGameInsertGenerator` et
lancer l'add-in.

## CAD IR locale

Par defaut, l'add-in charge le fichier suivant dans son propre dossier :

```text
BoardGameInsertGenerator/cad_ir_input.json
```

Il peut aussi charger un fichier exporte ailleurs si un fichier optionnel existe
au meme niveau :

```text
BoardGameInsertGenerator/cad_ir_path.txt
```

Dans `cad_ir_path.txt`, la premiere ligne non vide et non commentee doit etre un
chemin vers le JSON CAD IR. Le chemin peut etre absolu, ou relatif au dossier de
l'add-in. Exemple :

```text
C:\Users\janko\AppData\Local\Temp\bgig-cad-ir-input.json
```

La fixture fournie contient :

- une reference de boite `285 x 285 x 70 mm` ;
- un blank `cards-main-01 rectangular blank` de `68.9 x 99.2 x 44.0 mm` ;
- un blank `dice-01 rectangular blank` de `59.7 x 59.2 x 29.0 mm`.

Les origines et dimensions sont celles de la CAD IR, deja calculees par le coeur
BGIG. Fusion ne recalcule ni layout, ni offsets, ni tolerances.

Pour generer ce fichier depuis une configuration BGIG :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator export-cad-ir examples/simple_box.json --output fusion_addin/BoardGameInsertGenerator/cad_ir_input.json
```

Pour tester le flux produit asset-first P11-M003V4, generer une CAD IR sans blank legacy :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator export-cad-ir examples/simple_asset_product_scene.json --output $env:TEMP\bgig-simple-asset-product-scene.cad-ir.json
```

`examples/simple_asset_executable_plan.json` reste une fixture technique : elle contient volontairement un module manuel/legacy qui occupe une cellule pour tester les collisions et ne doit pas servir de smoke test produit principal.

Pour tester la scene multi-layer P11-M002, generer une CAD IR asset-first avec
placements Z explicites :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator export-cad-ir examples/simple_multilayer_grid_scene.json --output $env:TEMP\bgig-simple-multilayer-grid-scene.cad-ir.json
```

Lancer ensuite l'add-in. Depuis P12-M001, Fusion doit ouvrir directement la commande `Generate Board Game Insert` et garder un bouton relancable dans `Design workspace > Utilities > Add-Ins`. Si la boite de dialogue perd le focus, est fermee ou devient difficile a retrouver, cliquer ce bouton pour rouvrir BGIG sans redemarrer l'add-in. Renseigner le chemin dans le champ `CAD IR JSON path` de la
commande BGIG. Par defaut, P7-M001 genere aussi la vue eclatee basique par
occurrences liees ; pour revenir au compact seul, choisir `compact_only` dans la
liste `Generation mode`. Les fichiers `cad_ir_path.txt` et
`exploded_view_mode.txt` restent supportes uniquement comme valeurs par defaut.

Pour tester les cavites rectangulaires P6-M001, generer plutot une CAD IR de
tray :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator export-cad-ir examples/simple_tray.json --output $env:TEMP\bgig-simple-tray-cad-ir.json
```

Pour une installation locale Fusion, utiliser maintenant la methode UI : garder le
fichier genere ou vous voulez, lancer l'add-in, verifier que la boite de dialogue `Generate Board Game Insert` s'ouvre, puis coller son chemin dans
`CAD IR JSON path`. Copier sous `cad_ir_input.json` ou renseigner
`cad_ir_path.txt` reste possible comme fallback de compatibilite, mais ce n'est
plus le flux utilisateur recommande.

## UI parametrique V0

Depuis P12-M002V3, le flux principal reste la commande Fusion
`Generate Board Game Insert`, avec des modes explicites :

- `Action` : `generate`, `regenerate` ou `clear_bgig_scene` ;
- `Input mode` : `cad_ir_file`, `config_file`, ou `quick_parametric_box (disabled)` ;
- `CAD IR JSON path (cad_ir_file)` pour charger une CAD IR existante ;
- `BGIG config JSON path (config_file)` pour generer une CAD IR temporaire depuis une config ;
- `BGIG project root (auto/memorized, optional)` ;
- `Generation mode` : `compact_only` ou `compact_and_exploded` ;
- champs V0 de boite, grille, epaisseurs, clearances et profil d'impression,
  marques comme overrides `config_file`.

Le mode config ajoute seulement `<BGIG project root>/src` au `sys.path` cote
add-in Fusion. Le coeur Python reste sans import `adsk`. Le project root est
resolu dans cet ordre : champ UI si renseigne, variable `BGIG_PROJECT_ROOT`,
auto-detection depuis la config ou l'add-in, puis dev root
`C:\Users\janko\Documents\BGIG` si present. Les derniers chemins valides sont
memorises dans `bgig_ui_settings.json` dans le dossier de l'add-in.

Les champs numeriques sont de vrais overrides de la config choisie. Ils sont
rejetes en mode `cad_ir_file` pour eviter une UI decorative. Le mode
`quick_parametric_box` reste visible comme cible produit, mais il est
explicitement desactive tant qu'un builder de config temporaire complet n'est pas
code.

Depuis P12-M002V3, chaque generation cree une occurrence racine taguee
`BGIG Generated Scene`. `generate` refuse maintenant de creer une nouvelle scene
si une scene BGIG taguee existe deja dans le document. `regenerate` planifie
d'abord la nouvelle generation, supprime cette scene BGIG taguee si le plan est
valide, puis regenere. `clear_bgig_scene` supprime uniquement les objets portant
les attributs BGIG, jamais les objets utilisateur non BGIG. Le message Fusion
affiche `BGIG scenes before`, `BGIG objects deleted`, `BGIG scenes after` et
`Non-BGIG objects preserved`.

Procedure P12-M002V3 recommandee :

1. Copier l'add-in a jour dans le dossier Fusion AddIns.
2. Ouvrir un document Fusion Assembly-compatible.
3. Creer un objet utilisateur simple non BGIG dans la scene, par exemple un petit
   sketch ou body de test.
4. Lancer `Board Game Insert Generator`.
5. Verifier que la commande `Generate Board Game Insert` s'ouvre avec `Action`,
   `Input mode`, `CAD IR JSON path`, `BGIG config JSON path` et `Clear BGIG
   Scene` visible via `Action = clear_bgig_scene`.
6. Choisir `Input mode = config_file` et verifier que `BGIG config JSON path` est
   pre-rempli avec `examples/simple_asset_product_scene.json` ou le dernier
   chemin memorise.
7. Verifier que `BGIG project root` est pre-rempli ou laisser vide si
   auto-detecte. Ne le retaper que si le message d'erreur le demande.
8. Choisir `Action = generate` et `Generation mode = compact_and_exploded`.
9. Laisser les overrides vides ou modifier un override simple, par exemple
   `peripheral_clearance_mm`, puis cliquer `Run`.
10. Verifier le message final : `Input mode used`, `Project root`, `Config path`,
    `Input CAD IR`, `BGIG scenes before: 0`, `BGIG scene roots created: 1`,
    `BGIG scenes after: 1`, `Module source mapping`, `Body sizing report`,
    `Print validation: false`.
11. Relancer la commande avec `Action = generate`. L'add-in doit refuser sans
    creer de doublon et afficher `BGIG scene already exists. Use regenerate or
    clear first.` avec `BGIG scenes before` et `BGIG scenes after` inchanges.
12. Relancer la commande depuis le bouton toolbar, choisir `Action = regenerate`
    deux fois et verifier qu'il n'y a pas de doublons : une seule scene BGIG
    compacte et une seule zone eclatee doivent rester apres chaque regeneration.
    Le message doit afficher les scenes detectees avant, les objets BGIG
    supprimes, les objets non BGIG preserves et les scenes apres generation.
13. Relancer la commande, choisir `Action = clear_bgig_scene`, cliquer `Run`, puis
    verifier que la scene BGIG disparait, que `BGIG scenes after: 0` est affiche
    et que l'objet utilisateur non BGIG est preserve.
14. Tester `Input mode = cad_ir_file` avec un fichier CAD IR existant. Laisser
    les overrides vides ; si un override est renseigne, l'add-in doit refuser
    clairement au lieu de l'ignorer.

Validation attendue : correction codee, validation Fusion manuelle P12-M002V3
requise, `print-validated: false`.
## Cas Zero Doc

Fusion peut demarrer sans document actif. Le squelette detecte ce cas via
`activeDocument`.

Dans cet etat, l'add-in affiche un message demandant d'ouvrir ou creer un design
avant generation. Il ne tente pas de creer de document automatiquement.

## Smoke test manuel Fusion 360

Statut attendu avant execution : `manual validation required`.

Procedure :

1. Installer l'add-in avec la commande PowerShell ci-dessus.
2. Ouvrir Fusion 360.
3. Creer un nouveau design vide ou ouvrir un design de test.
4. Exporter ou localiser le fichier CAD IR JSON a tester.
5. Lancer `Board Game Insert Generator` depuis `Utilities > Add-ins`.
6. Verifier qu'une boite de dialogue `Generate Board Game Insert` s'ouvre et qu'un bouton du meme nom est disponible dans `Design workspace > Utilities > Add-Ins`.
7. Fermer ou defocaliser la boite de dialogue, puis cliquer le bouton toolbar `Generate Board Game Insert` pour verifier que BGIG se rouvre sans redemarrer l'add-in.
8. Dans cette commande, verifier la presence du champ `CAD IR JSON path` et du choix `Generation mode` (`compact_only` / `compact_and_exploded`).
9. Renseigner `CAD IR JSON path`, choisir `compact_only` ou `compact_and_exploded`, puis valider.
10. Verifier le message final : il doit annoncer le fichier CAD IR charge, le mode de generation, les composants modules, occurrences, cuts, refus et `UI reopen policy: toolbar_button_reopens_command_without_addin_restart`.
11. Dans le navigateur Fusion, verifier dans le composant racine la presence de
   sketches nommes :
   - `BGIG box reference - not printable outline` ;
   - `cards-main-01 - Main cards footprint` ;
   - `dice-01 - Dice tray footprint`.
12. Verifier les bodies nommes :
   - `cards-main-01 rectangular blank` ;
   - `dice-01 rectangular blank`.
13. Avec `Inspect > Measure`, verifier les dimensions attendues des blanks P4 :
   - `cards-main-01` : `68.9 x 99.2 x 44.0 mm` ;
   - `dice-01` : `59.7 x 59.2 x 29.0 mm`.
14. Pour le smoke test P6-M001, generer une CAD IR depuis
    `examples/simple_tray.json`, lancer l'add-in, renseigner son chemin dans
    `CAD IR JSON path`, choisir le mode voulu et verifier :
    - message final : `Blank bodies: 1` et `Rectangular cavity cuts: 1` ;
    - body cible : `token-tray-01 rectangular blank` ;
    - footprint de cavite attendue : `62.0 x 52.0 mm` ;
    - profondeur de coupe attendue : `20.0 mm` ;
    - plancher conserve attendu : `3.0 mm`.
15. Pour le smoke test P6-M002, generer une CAD IR depuis
    `examples/simple_finger_notch_tray.json`, lancer l'add-in, renseigner son
    chemin dans `CAD IR JSON path`, choisir le mode voulu et verifier :
    - message final : `Blank bodies: 1`, `Rectangular cavity cuts: 1`,
      `Simple finger notch features planned: 1`, `Simple finger notch sketches: 1`,
      `Simple top-open finger notch cuts: 1` et `Finger notch topology: top-open rectangular wall cut` ;
    - body cible : `finger-notch-tray-01 rectangular blank` ;
    - feature attendue : `front-half-moon-notch`, executee comme coupe
      rectangulaire de bounding box dans la paroi frontale, pas comme demi-lune
      courbe ;
    - verifier qu'il ne s'agit pas d'une fenetre fermee dans la paroi : la coupe
      doit rejoindre le bord superieur du tray et former une morsure ouverte ;
    - position XY de coupe attendue : X `26.8 mm`, Y `0.8 mm` ;
    - profondeur verticale depuis le haut : `10.0 mm` ;
    - profil top-open attendu : bas `Z 13.0 mm`, haut au-dessus du body `Z 24.0 mm` ;
    - taille de coupe CAD IR : `18.0 x 4.0 x 10.0 mm` ;
    - cavite conservee : `62.0 x 52.0 x 20.0 mm`.

16. Pour le smoke test compact produit P11-M003V4 avec le code courant, generer une CAD IR
    depuis `examples/simple_asset_product_scene.json`, lancer l'add-in,
    renseigner son chemin dans `CAD IR JSON path`, choisir `compact_only` et
    verifier :
    - message final : `CAD IR module blanks planned: 0`,
      `Grid-positioned asset modules planned: 1`, `Module components planned: 1`,
      `Compact occurrences planned: 1`, `Exploded occurrences planned: 0`,
      `Module components created: 1`, `Compact occurrences created: 1`,
      `Exploded occurrences created: 0`, `Linked exploded occurrences: yes`,
      puis les blocs `Module source mapping` et `Body sizing report` ;
    - dans le bloc `Body sizing report`, verifier pour le module asset-first : `source printable_body_size_mm`, `grid span 30.0 x 30.0 x 10.0 mm`, `printable body planned 25.6 x 25.6 x 9.8 mm`, `actual Fusion body bbox 25.6 x 25.6 x 9.8 mm` ou tolerance mesure comparable, et `size match yes` ;
    - verifier qu'aucun composant manuel ou legacy blank n'est genere pour cette scene produit ;
    - composant asset-first attendu : `Grid placed Grouped candidate for tokens` ;
    - occurrence compacte asset-first attendue a l'origine `X 0.0 mm`,
      `Y 0.0 mm`, `Z 0.0 mm` ;
    - dimensions attendues du module asset-first : `25.6 x 25.6 x 9.8 mm` ;
    - verifier que les occurrences compactes restent presentes et aux dimensions attendues.
17. Pour le smoke test P7/P11 en vue eclatee produit, garder la meme CAD IR
    `examples/simple_asset_product_scene.json`, laisser le mode par defaut
    `compact_and_exploded`, relancer l'add-in et verifier :
    - utiliser un design Fusion compatible avec plusieurs composants/occurrences ;
    - si Fusion affiche `assembly document required`, le document actif est un
      Part Design incompatible : creer/ouvrir un document Assembly-compatible ou
      utiliser le workflow Fusion `add this Part to an Assembly`, puis relancer ;
    - message final attendu dans le bon contexte : `Generation mode: compact_and_exploded`,
      `Module components planned: 1`, `Compact occurrences planned: 1`,
      `Exploded occurrences planned: 1`, `Module components created: 1`,
      `Compact occurrences created: 1`, `Exploded occurrences created: 1`,
      `Linked exploded occurrences: yes`, `Occurrence direct rename attempted: no`
      et `Occurrence naming policy: component_source_name_with_plan_role_mapping` ;
    - un seul composant module source attendu, nomme lisiblement :
      `Grid placed Grouped candidate for tokens` ;
    - les noms exacts des occurrences dans le Browser Fusion ne sont pas un
      critere : certains contextes Fusion exposent `Occurrence.name` en lecture
      seule ;
    - verifier plutot que le composant source est nomme lisiblement et
      que le message indique la politique de mapping compact/exploded ;
    - verifier que l'add-in n'a pas echoue avec
      `property '_get_name' of 'Occurrence' object has no setter` ;
    - origine attendue de l'occurrence eclatee asset-first : `X 140.0 mm`,
      `Y 0.0 mm`, `Z 0.0 mm` ;
    - dimensions attendues du module asset-first : `25.6 x 25.6 x 9.8 mm` ;
    - verifier dans le browser Fusion que l'occurrence compacte et l'occurrence
      eclatee d'un meme module referencent le meme composant source ;
    - modifier visuellement ou renommer un element dans la definition du composant
      source de test, puis verifier que les deux occurrences representent la meme
      definition ;
    - verifier que Fusion n'a pas cree de fillet, fond arrondi, module composite
      ou export STL/3MF.
18. Pour le smoke test P11-M003V3 multi-layer, generer une CAD IR depuis
    `examples/simple_multilayer_grid_scene.json`, lancer l'add-in dans un
    document Assembly-compatible, renseigner son chemin dans `CAD IR JSON path`,
    choisir `compact_and_exploded` et verifier :
    - message final attendu : `Grid-positioned asset modules planned: 2`,
      `Multi-layer grid modules planned: 1`, `Grid modules with Z placement: 1`,
      `Grid module height variants: 2`, `Module components planned: 3`,
      `Compact occurrences planned: 3`, `Exploded occurrences planned: 3`,
      `Module components created: 3`, `Compact occurrences created: 3`,
      `Exploded occurrences created: 3`, `Linked exploded occurrences: yes`,
      `Occurrence direct rename attempted: no`, puis un bloc `Body sizing report` ;
    - composant manuel attendu : `manual-reference-bin-01 - Manual reference bin` ;
    - composants asset-first attendus : `Grid placed Candidate module for Flat token field`
      et `Grid placed Candidate module for Tall dice column` ;
    - module bas attendu : origine `X 30.0 mm`, `Y 0.0 mm`, `Z 0.0 mm`,
      dimensions imprimables `61.6 x 61.6 x 7.8 mm` ;
    - span grille theorique du module bas : `90.0 x 90.0 x 10.0 mm` ;
    - ligne `Body sizing report` du module bas : source `printable_body_size_mm`, `printable body planned 61.6 x 61.6 x 7.8 mm`, `actual Fusion body bbox` comparable et `size match yes` ;
    - module haut attendu : origine `X 0.0 mm`, `Y 0.0 mm`, `Z 10.0 mm`,
      dimensions imprimables `37.6 x 37.6 x 17.8 mm` ;
    - span grille theorique du module haut : `60.0 x 60.0 x 20.0 mm` ;
    - ligne `Body sizing report` du module haut : source `printable_body_size_mm`, `printable body planned 37.6 x 37.6 x 17.8 mm`, `actual Fusion body bbox` comparable et `size match yes` ;
    - occurrences compactes et eclatees visibles, liees aux memes composants
      sources ;
    - aucun solveur, module composite, fillet, geometrie courbe ou export STL/3MF.
19. Noter tout ecart, message d'erreur ou comportement Zero Doc dans un futur log
    de validation.

Ce smoke test valide uniquement la creation CAD minimale dans Fusion. Depuis
P11-M003V4, verifier aussi que le flux produit normal passe par `simple_asset_product_scene.json`, la boite de dialogue
`Generate Board Game Insert`, sans modifier `cad_ir_path.txt` ni
`exploded_view_mode.txt`, et que les modules asset-first generes utilisent les
tailles imprimables et non les spans grille bruts en lisant le bloc
`Body sizing report` : `printable body planned` doit correspondre a
`actual Fusion body bbox`, et `grid span` doit rester une metadata d'occupation.
Depuis la correction P7, la vue
eclatee exige des composants/occurrences Fusion lies. Les
noms lisibles sont portes par les composants sources et par le message de
mapping ; l'add-in ne tente plus de renommer directement les occurrences. Un
document Part Design est non compatible avec cette vue liee : l'add-in doit
afficher `assembly document required` et ne doit pas revenir aux copies
independantes de bodies. Creer ou ouvrir un document Assembly-compatible, ou
ajouter le Part a une Assembly avec le workflow Fusion, puis relancer l'add-in.
Il ne valide pas l'impression, les jeux physiques ou les exports.

## Debug local hors Fusion

La partie testable est importable depuis Python standard :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -p test_fusion_skeleton.py
```

Les tests doivent rester independants de Fusion 360. Toute future logique qui ne
necessite pas l'API Fusion doit d'abord vivre dans `fusion_skeleton.py` ou un
module adjacent sans import `adsk`.

## Frontiere P6

La conversion actuelle stabilisee :

- charge et valide une CAD IR locale depuis `cad_ir_input.json` ou depuis un
  chemin declare dans `cad_ir_path.txt` ;
- cree un plan de generation hors Fusion ;
- cree une esquisse de reference de boite dans le composant racine ;
- cree un composant Fusion par module physique et y extrude le body rectangulaire source ;
- cree des coupes rectangulaires verticales simples pour `subtract_rectangular_cavity` ;
- cree des coupes rectangulaires de paroi simples pour les encoches supportees ;
- cree des occurrences compactes pour les modules deja places par la CAD IR ;
- cree des occurrences eclatees liees aux memes composants sources quand le mode le demande ;
- peut generer une CAD IR temporaire depuis une config BGIG si le repo est accessible ;
- tague les objets BGIG crees pour permettre `Clear BGIG Scene` et `Regenerate` ;
- marque la validation Fusion comme manuelle.

Toute mission suivante qui elargit le perimetre Fusion, notamment vers demi-lunes
courbes, fonds arrondis, fillets ou exports, doit recevoir une nouvelle gate
humaine avant implementation.
