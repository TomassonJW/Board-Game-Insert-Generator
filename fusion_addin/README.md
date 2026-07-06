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
module physique, une occurrence compacte et une occurrence eclatee, a tester
manuellement dans Fusion avant validation.

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
  permettant de pointer vers une CAD IR JSON exportee ailleurs.
- `BoardGameInsertGenerator/exploded_view_mode.txt` : fichier optionnel ignore par
  Git, permettant de choisir `compact_and_exploded` ou `compact_only`.

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

Pour tester les placements grille P11-M001, generer une CAD IR asset-first :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator export-cad-ir examples/simple_asset_executable_plan.json --output $env:TEMP\bgig-simple-asset-executable-plan.cad-ir.json
```

Pointer ensuite `cad_ir_path.txt` vers ce fichier. Par defaut, P7-M001 genere
aussi la vue eclatee basique par occurrences liees ; pour revenir au compact
seul, creer `exploded_view_mode.txt` avec `compact_only`.

Pour tester les cavites rectangulaires P6-M001, generer plutot une CAD IR de
tray :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator export-cad-ir examples/simple_tray.json --output $env:TEMP\bgig-simple-tray-cad-ir.json
```

Pour une installation locale Fusion, utiliser l'une des deux methodes :

1. Copier ensuite le fichier genere dans le dossier `BoardGameInsertGenerator`
   installe sous le nom `cad_ir_input.json`.
2. Laisser le fichier genere ailleurs et ecrire son chemin dans
   `cad_ir_path.txt`, place dans le dossier `BoardGameInsertGenerator` installe.

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
4. Verifier que `cad_ir_input.json` est present dans le dossier AddIns installe,
   ou que `cad_ir_path.txt` pointe vers un JSON CAD IR exporte et existant.
5. Lancer `Board Game Insert Generator` depuis `Utilities > Add-ins`.
6. Verifier le message final : il doit annoncer le nombre de reference outlines,
   blank bodies et rectangular cavity cuts crees dans le composant racine.
7. Dans le navigateur Fusion, verifier dans le composant racine la presence de
   sketches nommes :
   - `BGIG box reference - not printable outline` ;
   - `cards-main-01 - Main cards footprint` ;
   - `dice-01 - Dice tray footprint`.
8. Verifier les bodies nommes :
   - `cards-main-01 rectangular blank` ;
   - `dice-01 rectangular blank`.
9. Avec `Inspect > Measure`, verifier les dimensions attendues des blanks P4 :
   - `cards-main-01` : `68.9 x 99.2 x 44.0 mm` ;
   - `dice-01` : `59.7 x 59.2 x 29.0 mm`.
10. Pour le smoke test P6-M001, pointer `cad_ir_path.txt` vers la CAD IR generee
    depuis `examples/simple_tray.json`, relancer l'add-in et verifier :
    - message final : `Blank bodies: 1` et `Rectangular cavity cuts: 1` ;
    - body cible : `token-tray-01 rectangular blank` ;
    - footprint de cavite attendue : `62.0 x 52.0 mm` ;
    - profondeur de coupe attendue : `20.0 mm` ;
    - plancher conserve attendu : `3.0 mm`.
11. Pour le smoke test P6-M002, generer une CAD IR depuis
    `examples/simple_finger_notch_tray.json`, pointer `cad_ir_path.txt` vers ce
    fichier, relancer l'add-in et verifier :
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

13. Pour le smoke test compact P11-M001 avec le code courant, generer une CAD IR
    depuis `examples/simple_asset_executable_plan.json`, pointer `cad_ir_path.txt`
    vers ce fichier, mettre `exploded_view_mode.txt` a `compact_only`, relancer
    l'add-in et verifier :
    - message final : `CAD IR module blanks planned: 1`,
      `Grid-positioned asset modules planned: 1`, `Module components planned: 2`,
      `Compact occurrences planned: 2`, `Exploded occurrences planned: 0`,
      `Module components created: 2`, `Compact occurrences created: 2`,
      `Exploded occurrences created: 0`, `Linked exploded occurrences: yes` ;
    - composant manuel existant : `manual-reference-bin-01 - Manual reference bin` ;
    - composant asset-first attendu : `Grid placed Grouped candidate for tokens` ;
    - occurrence compacte asset-first attendue a l'origine `X 30.0 mm`,
      `Y 0.0 mm`, `Z 0.0 mm` ;
    - dimensions attendues du module asset-first : `30.0 x 30.0 x 10.0 mm` ;
    - verifier que les occurrences compactes restent presentes et aux dimensions attendues.
14. Pour le smoke test P7-M001V3, garder la meme CAD IR
    `examples/simple_asset_executable_plan.json`, laisser le mode par defaut
    `compact_and_exploded`, relancer l'add-in et verifier :
    - utiliser un design Fusion compatible avec plusieurs composants/occurrences ;
    - si Fusion affiche `assembly document required`, le document actif est un
      Part Design incompatible : creer/ouvrir un document Assembly-compatible ou
      utiliser le workflow Fusion `add this Part to an Assembly`, puis relancer ;
    - message final attendu dans le bon contexte : `Generation mode: compact_and_exploded`,
      `Module components planned: 2`, `Compact occurrences planned: 2`,
      `Exploded occurrences planned: 2`, `Module components created: 2`,
      `Compact occurrences created: 2`, `Exploded occurrences created: 2` et
      `Linked exploded occurrences: yes` ;
    - deux composants modules sources attendus, nommes lisiblement, dont
      `manual-reference-bin-01 - Manual reference bin` et
      `Grid placed Grouped candidate for tokens` ;
    - occurrence compacte manuelle :
      `manual-reference-bin-01 rectangular blank compact occurrence` ;
    - occurrence compacte asset-first :
      `generated - asset-group-candidate - tokens - store - exact grid positioned rectangular blank compact occurrence` ;
    - occurrences eclatees attendues :
      - `manual-reference-bin-01 rectangular blank exploded occurrence` ;
      - `generated - asset-group-candidate - tokens - store - exact grid positioned rectangular blank exploded occurrence` ;
    - origine attendue de l'occurrence eclatee manuelle : `X 140.0 mm`,
      `Y 0.0 mm`, `Z 0.0 mm` ;
    - origine attendue de l'occurrence eclatee asset-first : `X 179.2 mm`,
      `Y 0.0 mm`, `Z 0.0 mm` ;
    - dimensions attendues du module asset-first : `30.0 x 30.0 x 10.0 mm` ;
    - verifier dans le browser Fusion que l'occurrence compacte et l'occurrence
      eclatee d'un meme module referencent le meme composant source ;
    - modifier visuellement ou renommer un element dans la definition du composant
      source de test, puis verifier que les deux occurrences representent la meme
      definition ;
    - verifier que Fusion n'a pas cree de fillet, fond arrondi, module composite
      ou export STL/3MF.
15. Noter tout ecart, message d'erreur ou comportement Zero Doc dans un futur log
    de validation.

Ce smoke test valide uniquement la creation CAD minimale dans Fusion. Depuis la
correction P7, la vue eclatee exige des composants/occurrences Fusion lies. Un
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
- marque la validation Fusion comme manuelle.

Toute mission suivante qui elargit le perimetre Fusion, notamment vers demi-lunes
courbes, fonds arrondis, fillets ou exports, doit recevoir une nouvelle gate
humaine avant implementation.
