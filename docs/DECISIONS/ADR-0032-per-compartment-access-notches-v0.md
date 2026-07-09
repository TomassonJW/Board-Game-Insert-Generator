# ADR-0032 - Per-compartment access notches V0

Date : 2026-07-09

Statut : acceptee pour implementation P13-ASSET-M005 ; validation Fusion humaine requise via `P13-ASSET-M005V`.

## Contexte

P13-ASSET-M004 a valide des compartiments rectangulaires top-open par asset source. Ces compartiments sont lisibles mais peuvent rester difficiles a utiliser quand ils sont profonds ou etroits. Le projet dispose deja d'une generation Fusion d'encoches rectangulaires top-open pour des features de cavites CAD IR classiques.

## Decision

Ajouter la policy `per_compartment_top_open_rectangular_notch_v0` comme metadata additive sur chaque compartiment asset-specific.

Regles V0 :

- au plus une encoche par compartiment ;
- mur cible unique : front / `-Y` du module ;
- position centree sur la largeur du compartiment ;
- largeur nominale 18.0 mm, refusee sous 6.0 mm disponible apres marges laterales ;
- profondeur nominale 10.0 mm depuis le haut, refusee sous 4.0 mm utile ;
- refus si le compartiment ne touche pas le mur avant externe, afin de ne pas couper a travers un autre compartiment ou une paroi interne ;
- Fusion reutilise `FusionFingerNotchCutPlan` et la coupe rectangulaire top-open existante, avec `source_feature_kind = asset_access_notch`.

## Consequences

Le rapport Fusion expose `asset_access_features_generated`, `asset_access_policy`, `asset_access_notches_planned`, `asset_access_notches_generated`, `asset_access_notches_refused` et un diagnostic par asset/compartiment.

Cette policy ne cree ni courbe, ni demi-lune, ni scoop, ni fillet/conge. Elle ne visualise pas les assets individuels et ne genere pas de cavites par pile/item. Elle ne constitue pas une validation d'impression.

## Alternatives refusees

- Demi-lunes ou scoops reels : hors scope et plus fragiles en Fusion.
- Encoches sur parois internes ou compartiments non frontaux : refuse pour V0 afin d'eviter de traverser un autre logement.
- Solveur ergonomique global : hors scope P13-ASSET-M005.
- Toggle UI avance : reporte, car la policy active par defaut suffit au smoke V0.