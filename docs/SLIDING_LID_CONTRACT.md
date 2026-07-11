# Contrat coulissant V0

## Ce que l'utilisateur choisit

Le projet peut garder `kind: sliding_lid` avec un sens de glisse et quatre
parametres en millimetres. Le choix est visible et sauvegarde avec le projet.
Il ne modifie ni l'organisation, ni le score, ni les dimensions du bac ouvert.

## Contrat transporte

```text
schema_version: bgig.mechanism.v0
kind: none | sliding_lid
slide_axis: x | y
lid_thickness_mm: 0.8..3.0
rail_height_mm: 0.8..3.0
rail_clearance_mm: 0.15..0.6
end_overlap_mm: 6..20
```

Quand le coulissant est choisi, chaque module imprimable recoit une lecture de
preparation. Elle ne change pas le corps du module :

- longueur minimale sur l'axe = `2 * recouvrement + 8 mm` ;
- largeur minimale transversale = `2 * hauteur_rail + 2 * jeu + 8 mm` ;
- enveloppe a reserver a terme : deux fois `(hauteur_rail + jeu)` sur l'axe
  transversal et `epaisseur_capot + hauteur_rail` en Z.

Un module trop court est refuse avec `SLIDING_LID_MODULE_TOO_SHORT`. Un module
trop etroit est refuse avec `SLIDING_LID_MODULE_TOO_NARROW`. Sinon son statut
est `planned_for_coupon` et sa validation physique reste obligatoire.

## Coupon materialise en P34-M002

Quand au moins un module est compatible, l export ajoute un seul coupon a cote de la boite : un bac ouvert et un capot. Le capot est une plaque avec deux glissieres laterales descendantes jointes par join_rectangular_prism. Il reste distinct des bacs ranges et ne couvre pas encore chaque module du jeu.

## Limite passee de P34-M001

Avant P34-M002, les rails et le capot ne sont pas materialises. `experimental_contract_not_materialized` reste le statut honnete quand aucun coupon ne peut etre prepare. Ces chiffres sont locaux au mecanisme et ne changent pas les defaults
de tolerance du projet.

## Suite de validation

1. P34-M002 : implemente hors Fusion ; smoke Fusion humain requis via `P34_SLIDING_LID_FUSION_SMOKE.md`.
2. P35 : coupon imprime avec rail, capot et jeu choisi ; mesure de glisse,
   effort, jeu lateral, deformation et hauteur reelle.
3. Seulement apres retour humain, qualifier les valeurs utilisees pour le
   profil/imprimante observe ; jamais comme promesse universelle.
