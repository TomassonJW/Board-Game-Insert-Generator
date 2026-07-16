# P44-VH01 — Hauteur de conception cohérente avec le solveur

Statut : implemented, automated-validated ; gate P44-VH01V supersédée par P64-H01V après observation contextuelle positive du cas initial. fusion-validated: false, print-validated: false.

## Déclencheur

La gate P44-V a produit un KO contextuel avec environ 23 conteneurs et des réservations supérieures. Modifier fortement Z dans la palette ne changeait pas les diagnostics de fond sous plateau et le calcul restait impossible.

## Diagnostic prouvé

La palette modifiait box.inner_dimensions_mm.z et affichait Z - box.lid_clearance_mm, mais laissait box.usable_height_mm à son ancienne valeur. Le cœur utilise cette hauteur utilisable pour le plafond du solveur. La valeur visible, la valeur persistée et la valeur réellement calculée pouvaient donc diverger.

Le solveur volumétrique fonctionne aussi en Z : une fixture avec 24 conteneurs demandés, un plateau de 10 mm et 5 000 mm réellement utilisables construit plusieurs étages sans collision et applique la réservation supérieure.

## Correction bornée

- une fonction unique calcule la hauteur de conception visible ;
- box.usable_height_mm est synchronisé avec Z - jeu Z conteneur-boîte lors de l’édition de Z ou du jeu sous couvercle ;
- la synchronisation est répétée avant validation, solve, autosave et sauvegarde nommée afin qu’un projet historique ne conserve jamais une valeur cachée divergente dans la palette ;
- la valeur reste dérivée, grisée et non éditable ;
- aucun budget, ordre, score ou heuristique du solveur n’est modifié ;
- aucune tolérance, géométrie, valeur physique ou scène Fusion n’est recalibrée automatiquement.

Cette correction applique la sémantique déjà acceptée par ADR-0064 : le jeu Z conteneur-boîte est la marge retirée de la hauteur intérieure.

## Validation automatisée

- test DOM de la synchronisation Z/jeu sous couvercle et des payloads moteur/document ;
- régression solveur avec 24 conteneurs, réservation supérieure et plusieurs étages ;
- tests ciblés palette et solveur ;
- suite complète, syntaxe JavaScript, compileall, frontière adsk et git diff --check avant intégration.

## Gate Fusion 0.1.41

Après installation par scripts/fusion/prepare_p44_vh01_design_height_test.ps1, vérifier le projet contextuel :

1. Z modifié entraîne immédiatement une Hauteur de conception égale à Z moins le jeu Z conteneur-boîte ;
2. une très grande hauteur volontaire produit des étages au lieu de réutiliser les anciens diagnostics de fond ;
3. une hauteur réaliste peut encore refuser un empilement réellement trop bas ;
4. aucune scène n’est créée avant Matérialiser dans Fusion.

Retour historique non reçu : P44-VH01 Fusion OK 0.1.41 - commit <sha>. P64-H01V couvre désormais la reprise dense dans le package 0.1.42.

## Suite séparée

Après P64-H01V, P44-VH02 traitera les actions de suppression directe et le nommage incrémental. P44-V reste ouverte jusqu’à validation de ses correctifs contextuels ; P45 ne commence pas.
