# P60 - Correctif bootstrap et bouton Utilities

## Symptome

Au demarrage, la palette reste sur Chargement du projet puis expire. Tous les
boutons projet paraissent inactifs. Cliquer la commande Add-ins ouvre encore
l ancien formulaire technique.

## Cause

`palette.html` s execute pendant `palettes.add`, avant l attachement du handler
Python. Le premier `load_project` est perdu ; `project` reste nul et la garde
client annule les actions suivantes.

## Correctif 0.1.8

- handshake `bgig_palette_ready` retryable ;
- chargement projet declenche cote Python apres preuve du handler ;
- erreurs de bridge Promise visibles, aucun bouton silencieux ;
- bouton Utilities promu ouvrant seulement la palette ;
- ancien bouton Reglages experts retire ;
- icone maison BGIG SVG 16/32 px packagee.

## Gate

Recharger l add-in puis verifier chargement, boutons, palette toolbar,
materialisation et regeneration. `print-validated: false`.