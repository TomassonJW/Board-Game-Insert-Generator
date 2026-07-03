# Fusion Add-in Skeleton

## Statut

Ce dossier contient le squelette `P4-M002` de l'adaptateur Fusion 360.

Il est volontairement separe du coeur Python `src/board_game_insert_generator`.
Le coeur reste testable sans Fusion 360 et ne doit pas importer `adsk`.

Ce squelette ne cree pas de geometrie Fusion :

- aucun composant reel ;
- aucun corps reel ;
- aucune esquisse ;
- aucune extrusion ;
- aucun export STL/3MF.

## Structure

- `BoardGameInsertGenerator/BoardGameInsertGenerator.manifest` : manifeste
  d'add-in pour installation locale.
- `BoardGameInsertGenerator/BoardGameInsertGenerator.py` : point d'entree Fusion
  avec `run(context)` et `stop(context)`.
- `BoardGameInsertGenerator/fusion_skeleton.py` : logique testable hors Fusion
  pour l'etat document, la validation CAD IR et le plan d'operations non
  executable.

## Installation locale

Copier le dossier `fusion_addin/BoardGameInsertGenerator` dans le dossier AddIns
local de Fusion 360.

Chemin Windows typique :

```text
%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\BoardGameInsertGenerator
```

Puis ouvrir Fusion 360, aller dans `Utilities > Add-ins`, selectionner
`Board Game Insert Generator` et lancer l'add-in.

## Cas Zero Doc

Fusion peut demarrer sans document actif. Le squelette detecte ce cas via
`activeDocument`.

Dans cet etat, l'add-in affiche un message demandant d'ouvrir ou creer un design
avant une generation future. Il ne tente pas de creer de document, de composant
ou de geometrie.

## Debug local hors Fusion

La partie testable est importable depuis Python standard :

```powershell
$env:PYTHONPATH = "src"
python -m unittest tests.test_fusion_skeleton
```

Les tests doivent rester independants de Fusion 360. Toute future logique qui ne
necessite pas l'API Fusion doit d'abord vivre dans `fusion_skeleton.py` ou un
module adjacent sans import `adsk`.

## Frontiere P4-M002

La conversion actuelle s'arrete a un plan d'operations :

- la CAD IR est chargee et validee ;
- les operations abstraites sont listees ;
- chaque operation est marquee `planned_only`.

`P4-M003` devra faire l'objet d'une nouvelle gate humaine avant toute creation
reelle de blanks rectangulaires dans Fusion.
