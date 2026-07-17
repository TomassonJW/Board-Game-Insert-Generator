# P64-V2H02R — repère de la vue de dessus

## Déclencheur

Le retour Fusion sur P64-V2H02 confirme la capacité, la vérité des résultats, les
budgets, les méthodes et l'occlusion, mais constate que la vue de dessus est
miroir autour de l'axe X : elle se lit comme si l'observateur était sous la boîte.

## Décision et portée

Le correctif retourne uniquement Y lors du rendu SVG de la vue de dessus :
`y_svg = box.y + box.height - y_metier - hauteur_objet`.

X et les coordonnées métier restent inchangés. La coupe X/Z, le solveur, les
valeurs physiques, les tolérances, le schéma et la matérialisation ne changent
pas. Le package passe à 0.1.54.

## Preuve automatisée

Le test DOM exige le helper explicite `topViewY`, sa formule et l'usage exclusif
pour la projection dessus ; le script de préparation vérifie aussi les marqueurs
installés du package 0.1.54.

## Gate restante

P64-V2H02R demande seulement de confirmer dans Fusion que la vue de dessus est
orientée depuis le dessus, avec occlusion conservée et coupe X/Z inchangée.
Aucune validation physique ou d'impression n'est revendiquée.