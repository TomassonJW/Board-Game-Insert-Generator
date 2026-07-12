# Contrat P33 - Forme et apparence V0

> Statut 2026-07-12 : prototype historique `deferred-until-v0.1`. Il ne constitue
> pas la V0.2 et doit rester hors du parcours principal jusqu'a la gate P43.

## But

Donner une direction visible et sauvegardee a un projet BGIG sans modifier le plan, les tolerances, la CAD IR executable ou la scene Fusion.

## Donnee versionnee

Le brouillon Studio accepte le champ optionnel `appearance` :

```json
{
  "schema_version": "bgig.appearance.v0",
  "shape": {
    "corner_style": "rounded|straight|chamfered",
    "corner_radius_mm": 0.0,
    "chamfer_mm": 0.0,
    "notch_style": "none|front_scoop|thumb_notch"
  },
  "visual": {
    "theme": "atelier|graphite|playful",
    "label_mode": "none|module_name|module_name_and_role",
    "typography": "quiet|bold"
  }
}
```

Les anciens projets sans `appearance` restent compatibles : ils recoivent la direction `atelier` avec coins arrondis lors de l ouverture.

## Bornes

- rayon d apercu : 0 a 12 mm ;
- biseau d apercu : 0 a 6 mm ;
- toutes les enums sont refusees si elles sont inconnues ;
- le Studio limite visuellement rayon et biseau a la taille du bac affiche.

## Effet dans P33

- le Studio met a jour le theme, les formes 2D, la prise symbolique et les labels en direct ;
- le choix est sauvegarde dans le projet, la selection et les metadata CAD IR ;
- le solveur P21, les dimensions, les placements, les tolerances, les murs, le fond et les cavites restent identiques ;
- la metadata CAD IR porte `appearance_status: stored_for_preview_only_not_materialized`.

## Ce que P33 ne promet pas

P33 ne genere pas encore de congé, biseau, gravure, etiquette ou encoche de forme correspondante dans Fusion. Ces geometries seront des lots ulterieurs, soumis a contraintes de resistance et validation physique avant toute promesse de fabrication.