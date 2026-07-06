# 2026-07-06 - P6-M002V KO partiel et correction top-open

## Retour de validation humaine

Thomas a reteste l'add-in apres le correctif `3760abe`.

Resultat observe :

- add-in lance : OK ;
- CAD IR `simple_finger_notch_tray` chargee : OK ;
- blank genere : OK ;
- cavite rectangulaire generee : OK ;
- une coupe volumique d'encoche est creee : OK ;
- la coupe produite est une fenetre rectangulaire fermee dans la paroi ;
- l'encoche n'est pas utilisable comme aide de prise car elle n'est pas ouverte
  depuis le haut du tray.

## Diagnostic

Le correctif precedent a resolu le passage sketch -> cut volumique, mais le
profil vertical restait borne dans la paroi. Fusion creait donc une fenetre
fermee, pas une morsure ouverte.

## Correction

- `size_mm.z` est interprete par l'adaptateur Fusion comme
  `notch_depth_from_top_mm` pour les encoches simples de paroi.
- Le bas du profil est calcule comme `body_top_z - notch_depth_from_top_mm`.
- Le haut du profil depasse le dessus du body de `1.0 mm` afin de garantir une
  coupe ouverte sur le rebord superieur.
- La coupe reste rectangulaire, limitee a l'epaisseur de paroi et au body cible
  via `participantBodies`.
- La vraie demi-lune courbe reste future et sous gate humaine separee.

## Statut

Correction codee et testee hors Fusion : 102 tests unitaires passent, CLI et
export CAD IR passent sur `simple_tray` et `simple_finger_notch_tray`. Nouveau
smoke test manuel Fusion requis pour confirmer une encoche ouverte vers le haut,
et non une fenetre fermee.

`print-validated: false` reste inchange.
