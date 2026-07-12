# P60 - UX presets, corps pleins et dimensions

## Contexte

Le runtime 0.1.8 est observe dans Fusion jusqu au calcul, au resultat et a la
materialisation. Le retour utilisateur demande une palette initiale plus grande,
des valeurs de depart utiles, des corps sans cavite et le controle des dimensions
de chaque bac.

## Decision reversible

- La palette devient 1280 x 1100 au minimum sans reduire une taille utilisateur
  plus grande.
- Les presets sont produits par le coeur Python pur et restent de simples brouillons
  editables ; aucun solveur metier n est ajoute au JavaScript.
- Le bloc plein reutilise le contrat explicite fill_elements.kind = solid.
- Les champs X/Y/Z de locked_outer_dimensions_mm quittent le mode avance. Un champ
  vide conserve le choix automatique du moteur.

## Perimetre

Presets Jetons, Cartes sleevees, Des et Pions ; Bac vide, Bloc plein / cale et
Separateur ; packaging 0.1.9 ; tests moteur, bridge, DOM et installateur.

L empilement vertical n est pas simule dans ce lot. Il devient P61 apres P60 et
commencera par une ADR distinguant etages, corps, quantites et supports.

## Validation

La suite complete, la syntaxe JavaScript, le parsing PowerShell, py_compile,
git diff --check et l absence de adsk dans le coeur sont requis avant integration.
La gate Fusion P60 reste ouverte pour le package 0.1.9. Aucune validation
d impression n est revendiquee.
