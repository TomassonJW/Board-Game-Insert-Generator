# P21 Recommendation - Variants before UI or Fusion preview

## Decision requested

Recommandation : `P21-BOX-FILL-VARIANTS-SPRINT`.

P20 prouve un placement greedy unique, deterministe et explicable. La suite rationnelle consiste a comparer quelques policies bornees, avec scores decomposes, avant de figer une UI ou une projection Fusion. Une UI persistante reste gatee par ADR-0036; une preview Fusion doit consommer un contrat resultat deja stabilise; un greedy 3D augmenterait prematurement le risque.

## Alternatives

- UX prototype : utile apres un petit espace de variantes comparable.
- Fusion preview : adaptateur futur, sans nouvelle decision moteur.
- Greedy 3D/layers : deferre; P20 couvre deja un choix de layer borne mais pas une recherche Z.

## Gate humaine

Autorisation produit requise avant P21. Aucun P21 n'est implemente par cette recommandation.
