# 2026-07-29 — P64-L09U-R8-D conteneurs finalisés

- Remplacement du schéma composite positif v2 par
  `bgig.xy_composite_container_body.v3`.
- Séparation explicite entre géométrie de fermeture et géométrie positive du
  conteneur finalisé.
- Suppression de `cad_origin_mm` et `cad_size_mm` dans les nouveaux corps.
- Ajout de `bgig.finalized_container_geometry.v1` et de son digest positif
  indépendant des opérations soustractives.
- Refus CAD IR de toute matière, union ou nouveau corps positif attribué à un
  élément plat.
- Compatibilité de lecture v1/v2 conservée pour les artefacts historiques.
- Cavités, accès, parois, grille et budgets préservés.
- Validation ciblée : `90/90`.
- Projets personnels non rejoués et SHA-256 inchangés.
- Prochaine mission : R8-E, passe d’encastrement uniquement soustractive.
