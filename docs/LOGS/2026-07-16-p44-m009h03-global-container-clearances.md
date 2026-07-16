# P44-M009H03 - Jeux globaux et Réglages dense

Date : 2026-07-16

La revue Fusion du package 0.1.33 a montré que le jeu externe par bac n’apporte pas de contrôle produit pertinent et reste difficile à expliquer. La décision humaine retire donc cette logique au lieu d’ajouter un troisième correctif d’isolation.

ADR-0064 rend les jeux entre conteneurs et conteneur-boîte exclusivement globaux. Les anciennes valeurs `container_groups[].clearance_overrides_v1` restent lisibles et roundtrippables sans effet runtime. Les overrides asset, plateau et livret restent inchangés.

Le package 0.1.34 retire « Jeu externe » des cartes et remplace l’ancien panneau Réglages par une interface dense : épaisseurs minimales séparées, tableau X/Y–Z sur trois lignes et comportement dérivé. Le Z conteneur-boîte reprend la marge sous couvercle.

Suite complète : 474 tests OK. Syntaxe JavaScript et tests DOM : OK. Compileall, frontière adsk et `git diff --check` : OK. fusion-validated: false ; print-validated: false. Prochaine preuve : P44-M009H03V.