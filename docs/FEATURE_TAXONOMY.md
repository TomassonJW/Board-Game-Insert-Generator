# Feature Taxonomy

## Objectif

Ce document formalise les aides de prise de cavites sans autoriser de nouvelle
geometrie Fusion. La taxonomie est CAD-agnostic : elle decrit l'intention, les
parametres attendus et le statut de validation avant tout adaptateur CAD.

## Parametres communs

Chaque feature de cavite peut porter :

- `kind` : compatibilite historique du schema V0 (`finger_notch`, `side_notch`,
  `center_notch`, `half_moon_notch`, `rounded_floor`, `grip_aid`) ;
- `taxonomy` : type ergonomique explicite, optionnel si derivable depuis `kind` ;
- `placement` : paroi ou zone cible (`front`, `back`, `left`, `right`,
  `front_center`, `cavity_floor`, etc.) ;
- `position_mm` : position locale dans la cavite ;
- `size_mm` : largeur, profondeur de coupe ou volume d'intention ;
- `radius_mm` : rayon abstrait quand le profil le demande ;
- statut de generation Fusion et statut d'impression separes.

La taxonomie expose aussi les intentions suivantes :

- ouverture vers le haut ou fenetre fermee ;
- traversant ou non traversant ;
- profil : rectangle, demi-lune, rounded-rect, scoop ou rayon de fond ;
- besoin futur d'epaisseur minimale de peau exterieure pour les scoops non
  traversants.

## Types P6-M003

| Taxonomy | Profil | Top-open | Traversant | Statut Fusion | Statut impression | Role |
| --- | --- | --- | --- | --- | --- | --- |
| `top_open_rectangular_notch` | rectangle | oui | oui | `fusion-validated` | `print-validated: false` | Morsure rectangulaire ouverte depuis le haut d'une paroi. |
| `top_open_half_moon_notch` | half_moon | oui | oui | fallback rectangulaire valide | `print-validated: false` | Intention de demi-lune courbe future ; Fusion utilise encore `top_open_rectangular_notch`. |
| `through_wall_window` | rectangle | non | oui | `abstract_only` | `print-validated: false` | Fenetre fermee dans une paroi, distincte d'une encoche utilisable. |
| `blind_internal_thumb_scoop` | scoop | non | non | `abstract_only` | `print-validated: false` | Creux interne non traversant, avec peau exterieure a preserver. |
| `side_relief_notch` | rectangle | oui | oui | `abstract_only` | `print-validated: false` | Degagement lateral pour cartes, tuiles ou assets plats. |
| `dual_side_card_access` | rectangle | oui | oui | `abstract_only` | `print-validated: false` | Acces bilateral pour sortir un paquet de cartes ou tuiles. |
| `rounded_floor_intent` | floor_radius | non | non | `abstract_only` | `print-validated: false` | Intention de rayon de fond, hors generation Fusion reelle. |

## Compatibilite avec les kinds V0

| Kind V0 | Taxonomie par defaut |
| --- | --- |
| `finger_notch` | `top_open_rectangular_notch` |
| `half_moon_notch` | `top_open_half_moon_notch` |
| `side_notch` | `side_relief_notch` |
| `center_notch` | `blind_internal_thumb_scoop` |
| `grip_aid` | `dual_side_card_access` |
| `rounded_floor` | `rounded_floor_intent` |

Une configuration peut declarer `taxonomy` explicitement. Le loader refuse les
valeurs inconnues et la validation refuse les couples `kind` / `taxonomy`
incoherents.

## Statut Fusion

`top_open_rectangular_notch` est la seule taxonomie d'aide de prise validee dans
Fusion a ce stade, et uniquement comme coupe rectangulaire top-open. Pour
`top_open_half_moon_notch`, la CAD IR conserve l'intention demi-lune, mais la
generation Fusion actuelle reste un fallback rectangulaire top-open.

Aucune demi-lune courbe, scoop interne non traversant, fillet, conge, fond
arrondi, boolean avance, grille 3D ou module composite n'est autorise par cette
mission.
