# Fusion Add-in Skeleton

## Statut

Ce dossier contient l'adaptateur Fusion 360 isole du projet BGIG.

Il est volontairement separe du coeur Python `src/board_game_insert_generator`.
Le coeur reste testable sans Fusion 360 et ne doit pas importer `adsk`.

Depuis `P4-M003`, l'add-in contient une premiere generation minimale de blocs
rectangulaires depuis une CAD IR JSON locale. Cette generation est codee, mais
reste en statut `manual validation required` tant qu'elle n'a pas ete lancee et
inspectee dans Fusion 360 par Thomas.

Ce que l'add-in cree maintenant :

- un composant de reference nomme comme non imprimable, avec une esquisse de
  l'empreinte de boite ;
- un composant par blank imprimable ;
- un corps rectangulaire extrude par blank ;
- des noms lisibles pour composants et bodies.

Ce que l'add-in ne cree pas :

- aucune cavite ;
- aucun couvercle ;
- aucune charniere ;
- aucun fillet/conge ;
- aucun export STL/3MF ;
- aucune validation physique.

## Structure

- `BoardGameInsertGenerator/BoardGameInsertGenerator.manifest` : manifeste
  d'add-in pour installation locale.
- `BoardGameInsertGenerator/BoardGameInsertGenerator.py` : point d'entree Fusion
  avec `run(context)` et `stop(context)`.
- `BoardGameInsertGenerator/fusion_skeleton.py` : logique testable hors Fusion
  pour l'etat document, la validation CAD IR, le plan d'operations et le plan de
  generation.
- `BoardGameInsertGenerator/cad_ir_input.json` : fixture CAD IR locale chargee
  par defaut par l'add-in.

## Installation locale

Depuis la racine du depot :

```powershell
$source = Resolve-Path .\fusion_addin\BoardGameInsertGenerator
$target = Join-Path $env:APPDATA "Autodesk\Autodesk Fusion 360\API\AddIns\BoardGameInsertGenerator"
New-Item -ItemType Directory -Force $target | Out-Null
Copy-Item -Path "$source\*" -Destination $target -Recurse -Force
```

Puis ouvrir Fusion 360, aller dans `Utilities > Add-ins`, selectionner
`Board Game Insert Generator` et lancer l'add-in.

## CAD IR locale

L'add-in charge le fichier suivant dans son propre dossier :

```text
BoardGameInsertGenerator/cad_ir_input.json
```

La fixture fournie contient :

- une reference de boite `285 x 285 x 70 mm` ;
- un blank `cards-main-01 rectangular blank` de `68.9 x 99.2 x 44.0 mm` ;
- un blank `dice-01 rectangular blank` de `59.7 x 59.2 x 29.0 mm`.

Les origines et dimensions sont celles de la CAD IR, deja calculees par le coeur
BGIG. Fusion ne recalcule ni layout, ni offsets, ni tolerances.

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
4. Verifier que `cad_ir_input.json` est present dans le dossier AddIns installe.
5. Lancer `Board Game Insert Generator` depuis `Utilities > Add-ins`.
6. Verifier le message final : il doit annoncer 1 reference outline et 2 blank
   bodies.
7. Dans le navigateur Fusion, verifier la presence de composants nommes :
   - `BGIG box reference - not printable` ;
   - `cards-main-01 - Main cards` ;
   - `dice-01 - Dice tray`.
8. Verifier les bodies :
   - `cards-main-01 rectangular blank` ;
   - `dice-01 rectangular blank`.
9. Avec `Inspect > Measure`, verifier les dimensions attendues des blanks :
   - `cards-main-01` : `68.9 x 99.2 x 44.0 mm` ;
   - `dice-01` : `59.7 x 59.2 x 29.0 mm`.
10. Noter tout ecart, message d'erreur ou comportement Zero Doc dans un futur log
    de validation.

Ce smoke test valide uniquement la creation CAD minimale dans Fusion. Il ne
valide pas l'impression, les jeux physiques ou les exports.

## Debug local hors Fusion

La partie testable est importable depuis Python standard :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -p test_fusion_skeleton.py
```

Les tests doivent rester independants de Fusion 360. Toute future logique qui ne
necessite pas l'API Fusion doit d'abord vivre dans `fusion_skeleton.py` ou un
module adjacent sans import `adsk`.

## Frontiere P4-M003

La conversion actuelle :

- charge et valide une CAD IR locale ;
- cree un plan de generation hors Fusion ;
- cree une esquisse de reference de boite ;
- cree des rectangles puis extrude des bodies simples pour les blanks ;
- marque la validation Fusion comme manuelle.

`P4-M004` ou toute mission suivante sur Fusion doit recevoir une nouvelle gate
humaine avant d'elargir le perimetre.