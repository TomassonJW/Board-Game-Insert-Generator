# 2026-07-03 - Stabilisation du pipeline CAD IR vers Fusion

## Mission

Stabiliser la chaine configuration BGIG -> export CAD IR -> fichier JSON ->
add-in Fusion -> blanks rectangulaires minimaux.

La gate humaine a ete validee sous le libelle `P4-M004`. Pour ne pas reecrire
l'historique du backlog, la carte de suivi est enregistree comme `P4-M006`.

## Changements

- L'add-in Fusion resout l'entree CAD IR depuis `cad_ir_input.json` par defaut ou
  depuis un chemin configure dans `cad_ir_path.txt`.
- `cad_ir_path.txt` accepte la premiere ligne non vide et non commentee, en chemin
  absolu ou relatif au dossier de l'add-in.
- Les erreurs de fichier absent, override vide, JSON invalide, schema invalide ou
  unites invalides affichent un message Fusion plus actionnable.
- Les tests hors Fusion couvrent le chargement, les overrides et la validation
  minimale du contrat CAD IR.
- Aucune nouvelle geometrie Fusion n'est ajoutee.

## Limites

- La generation reste limitee a la reference de boite et aux blanks
  rectangulaires deja autorises.
- Aucune cavite, aucun fillet/conge, aucun couvercle et aucun export STL/3MF ne
  sont ajoutes.
- Toute nouvelle CAD IR exportee doit encore etre inspectee dans Fusion ; cela ne
  vaut pas validation d'impression reelle.

## Suite

Nouvelle gate humaine requise avant tout elargissement Fusion ou export
imprimable.