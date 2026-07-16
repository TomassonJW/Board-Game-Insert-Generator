# 2026-07-16 - P44-M007H03 repli global et résolution sleeves

## Déclencheur

Retour Fusion sur le package 0.1.39 :

- delta sleeve X/Y absent du fait `Résolu` pour des cartes manuelles ;
- `Nb cartes` et `Résolu` parfois visuellement anciens pendant le cycle
  autosave / validation / solve ;
- ligne secondaire cartes trop large ;
- besoin d’un repli global et suppression des modes de densité obsolètes.

La capture de référence montre X = 66, Y = 88, Z = 27, sleeves actifs,
delta X/Y = 3 et delta Z/carte = 0,19. L’estimation 87 est correcte pour
27 / 0,31 ; le résultat attendu est 69 × 91 × 43,53 mm.

## Décision bornée

- ajouter `card_declared_xy_mm` au schéma v1 de façon additive ;
- résoudre X/Y manuel comme dimensions déclarées plus delta seulement si les
  sleeves sont actifs ;
- afficher `À recalculer` dès qu’une source change et ne repeindre le fait
  qu’avec une réponse dérivée courante ;
- conserver le calcul métier dans le cœur Python sans import `adsk` ;
- garder les états de repli locaux à la palette ;
- supprimer entièrement les contrôles et la persistance Compact/Détaillé.

Aucun placement, budget, tolérance, géométrie, CAD IR, valeur physique ou
comportement de scène n’est modifié.

## Validation

Le package préparé est 0.1.40. La gate P44-M007H03V doit vérifier dans Fusion la
saisie rapide, l’état transitoire, le cas 66/88/27, le repli global et individuel,
la ligne compacte et l’absence de scène automatique.

`fusion-validated: false` et `print-validated: false` jusqu’à preuve humaine.
