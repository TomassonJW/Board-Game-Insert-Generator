# Log - Export CAD IR depuis la CLI

Date : 2026-07-03

## Mission

Ajouter une commande CLI permettant de produire une CAD IR JSON V0 depuis une
configuration BGIG, afin que l'add-in Fusion ne depende plus uniquement d'une
fixture manuelle.

## Resultat

- Commande ajoutee : `python -m board_game_insert_generator export-cad-ir <config> --output <cad_ir_input.json>`.
- Le JSON exporte reutilise `build_blank_cad_scene` et conserve le contrat
  `cad_ir.v0`.
- Le test CLI recharge le fichier exporte via le squelette Fusion hors Fusion et
  construit un plan de generation.
- Aucune geometrie Fusion, valeur de tolerance, cavite, fillet ou export STL/3MF
  n'a ete ajoute.

## Validation attendue

Validation automatisee pour le flux CLI et la compatibilite hors Fusion. Toute
nouvelle CAD IR utilisee dans Fusion doit encore etre inspectee dans Fusion et ne
constitue pas une validation d'impression reelle.
