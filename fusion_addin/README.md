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
`describe_cavity_feature`, sous forme de coupes rectangulaires. Cette generation
d'encoches reste a inspecter manuellement dans Fusion avant d'etre consideree
validee.

Ce que l'add-in cree maintenant :

- une esquisse de reference de boite dans le composant racine, nommee comme non
  imprimable ;
- un sketch d'empreinte par blank dans le composant racine ;
- un corps rectangulaire extrude par blank ;
- une coupe rectangulaire verticale par operation `subtract_rectangular_cavity` ;
- une coupe rectangulaire de paroi par encoche simple supportee ;
- des noms lisibles pour sketches, features et bodies.

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

## Installation locale

La version courante de Fusion attend cette structure exacte :

```text
BoardGameInsertGenerator/
  BoardGameInsertGenerator.py
  BoardGameInsertGenerator.manifest
  cad_ir_input.json
  cad_ir_path.txt  # optionnel, local
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
      `Simple finger notch features planned: 1`, `Simple finger notch sketches: 1`
      et `Simple finger notch cuts: 1` ;
    - body cible : `finger-notch-tray-01 rectangular blank` ;
    - feature attendue : `front-half-moon-notch`, executee comme coupe
      rectangulaire de bounding box dans la paroi frontale, pas comme demi-lune
      courbe ;
    - verifier qu'il ne s'agit pas seulement d'un sketch visible dans le fond de
      la cavite : une coupe volumique doit etre visible dans la paroi du tray ;
    - position de coupe attendue : X `26.8 mm`, Y `0.8 mm`, Z `9.2 mm` ;
    - taille de coupe attendue : `18.0 x 4.0 x 10.0 mm` ;
    - cavite conservee : `62.0 x 52.0 x 20.0 mm`.
12. Noter tout ecart, message d'erreur ou comportement Zero Doc dans un futur log
    de validation.

Ce smoke test valide uniquement la creation CAD minimale dans Fusion. Il utilise
volontairement le composant racine pour rester compatible avec les documents
Fusion Part Design qui refusent plusieurs composants enfants. Il ne valide pas
l'impression, les jeux physiques ou les exports.

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
- cree des rectangles dans le composant racine puis extrude des bodies simples
  pour les blanks ;
- cree des coupes rectangulaires verticales simples pour `subtract_rectangular_cavity` ;
- cree des coupes rectangulaires de paroi simples pour les encoches supportees ;
- marque la validation Fusion comme manuelle.

Toute mission suivante qui elargit le perimetre Fusion, notamment vers demi-lunes
courbes, fonds arrondis, fillets ou exports, doit recevoir une nouvelle gate
humaine avant implementation.
