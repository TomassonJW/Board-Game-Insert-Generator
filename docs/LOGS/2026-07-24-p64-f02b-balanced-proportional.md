# Journal — P64-F02B équilibré et proportionnel

Date : 2026-07-24

## Orientation

La fermeture couplée conserve désormais un plan F01B certifié comme baseline,
puis tente sous le budget restant deux objectifs secondaires déterministes :
égalité du volume ajouté, puis égalité du ratio d'expansion. Le candidat F02B
n'est retenu qu'après fermeture, certificat commun et amélioration stricte.

## Portée

- ajout de candidats de croissance appariée sur faces Auto/Target ;
- score et provenance publiés dans le plan final ;
- fallback exact vers F01B ;
- aucune harmonisation modulaire, nouvelle pose, valeur physique, UI ou schéma
  produit ;
- aucun benchmark, tuning ou holdout.

## Validation

Fermeture 5/5, staged 14/14, palette 29/29, suite complète 853/853 en
224,573 s avec un test natif ignoré sous Python 3.10. Ruff ciblé et contrôle du
diff passent.

## Suite

Préparer P64-L09V et sa checklist Fusion combinée. La gate humaine et la
validation d'impression restent distinctes.
