# ADR-0015 - Taxonomie des encoches et aides de prise

## Statut

Acceptee.

## Contexte

Apres `P6-M002V`, BGIG sait generer dans Fusion une encoche rectangulaire de
paroi ouverte vers le haut. Le terme historique "encoche" couvre cependant des
intentions differentes : morsure top-open, demi-lune courbe future, fenetre
fermee, scoop interne, degagement lateral ou acces bilateral pour cartes.

Sans taxonomie explicite, une feature abstraite peut etre confondue avec une
geometrie Fusion validee, ou une fenetre fermee peut etre prise pour une aide de
prise utilisable.

## Decision

Ajouter une taxonomie CAD-agnostic pour les features ergonomiques de cavites :

- `top_open_rectangular_notch` ;
- `top_open_half_moon_notch` ;
- `through_wall_window` ;
- `blind_internal_thumb_scoop` ;
- `side_relief_notch` ;
- `dual_side_card_access` ;
- `rounded_floor_intent` pour conserver l'intention existante de fond arrondi.

Le champ de configuration `taxonomy` est optionnel et additif. S'il est absent,
le moteur derive une taxonomie par defaut depuis `kind`. Les rapports et la CAD
IR exposent la taxonomie resolue, son profil, son caractere top-open/traversant,
son statut Fusion et `print_validated: false`.

## Consequences

- Le contrat reste compatible avec les configs existantes.
- La CAD IR transporte mieux l'intention sans forcer une nouvelle version de
  schema.
- La demi-lune courbe reste future : Fusion ne genere encore que le fallback
  rectangulaire top-open deja valide.
- Toute generation Fusion reelle de courbe, scoop, fillet, fond arrondi, boolean
  avance, grille 3D ou module composite reste sous gate humaine.

## Alternatives refusees

- Renommer brutalement `kind` en `taxonomy` : trop cassant pour le schema V0.
- Ajouter directement de nouvelles operations Fusion : hors perimetre P6-M003 et
  gate obligatoire.
- Laisser le terme "encoche" implicite : trop ambigu apres les retours Fusion
  P6-M002V.
