# ADR-0008 - Isoler le squelette d'adaptateur Fusion 360

## Statut

Accepte

## Date

2026-07-03

## Carte liee

- `P4-M002 - Creer un squelette d'adaptateur Fusion 360`

## Contexte

`P4-M001` a defini une CAD IR agnostique. La mission suivante doit preparer
Fusion 360 sans deplacer la logique metier dans Fusion et sans rendre le coeur
Python dependant de l'API `adsk`.

La premiere integration doit aussi anticiper le mode Fusion "Zero Doc", ou
aucun document actif n'est ouvert.

## Options

1. Placer l'adaptateur dans `src/board_game_insert_generator`.
2. Placer l'adaptateur dans un dossier racine `fusion_addin/` separe du coeur.
3. Garder uniquement de la documentation et repousser tout squelette executable.

## Decision

Le squelette Fusion est place dans `fusion_addin/BoardGameInsertGenerator`.

Le fichier d'entree Fusion `BoardGameInsertGenerator.py` peut importer `adsk`,
mais aucun import `adsk` n'est autorise dans `src/board_game_insert_generator`.

La logique testable hors Fusion vit dans `fusion_skeleton.py` et reste sans
dependance Fusion. Elle valide une CAD IR serialisee, detecte l'etat de document
par duck typing et transforme les operations CAD IR en plan `planned_only`.

P4-M002 ne cree aucun composant, corps, sketch, extrusion ou export.

## Consequences

Effets positifs :

- le coeur Python reste importable et testable sans Fusion 360 ;
- la frontiere d'adaptateur est visible dans l'arborescence ;
- le cas Zero Doc est testable sans lancer Fusion ;
- la future generation Fusion pourra s'appuyer sur un plan d'operations sans
  recalculer layout ou tolerances.

Effets negatifs et risques :

- le manifeste devra etre verifie dans une vraie installation Fusion avant
  d'etre considere stable ;
- les tests ne prouvent pas encore la compatibilite runtime avec l'API Fusion ;
- la presence d'un squelette executable peut etre confondue avec une generation
  CAD fonctionnelle si le statut n'est pas maintenu explicitement.

## Alternatives refusees

L'adaptateur dans `src/board_game_insert_generator` est refuse pour eviter une
frontiere floue et des imports Fusion accidentels dans le coeur.

Un lot purement documentaire est refuse parce que la gate humaine a autorise un
squelette minimal, et que la detection Zero Doc peut deja etre testee utilement.

Une premiere generation de blanks est refusee dans cette ADR : elle appartient a
`P4-M003` et demande une nouvelle gate humaine.

## Suivi

- `rg -n "adsk" src/board_game_insert_generator` doit rester sans occurrence.
- `P4-M003` doit demander une nouvelle validation humaine avant toute creation
  reelle de geometrie Fusion.
- Les futures fonctions qui ne dependent pas directement de Fusion doivent
  rester testees hors Fusion.
