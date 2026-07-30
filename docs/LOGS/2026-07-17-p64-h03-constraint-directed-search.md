# 2026-07-17 — P64-H03, recherche dirigée par contraintes

## Observation

L’autosauvegarde de 250 × 180 × 70 mm contient 8 conteneurs, 12 éléments et deux
réservations supérieures. La géométrie est logeable, mais la recherche canonique
et 64 seeds hash ne trouvent pas de candidat validé après un petit ajout.

## Diagnostic

- deux cavités presque pleine hauteur doivent rester hors des réservations ;
- certaines piles conservaient leur surplus Z dans le membre inférieur ;
- le faisceau éliminait les nombres de piles moins denses ;
- les ordres de rangées XY valides n’étaient pas conservés à forte densité.

## Réalisation

- ordres structurés avant la reprise hash ;
- faisceau vertical non contigu et diversifié par nombre de piles ;
- classement par dette de hauteur irrécupérable ;
- prédiction exacte des intersections cavité/réservation ;
- transfert borné du surplus Z vers le sommet expansible ;
- variantes XY géométriques déterministes ;
- package d’essai 0.1.45 et script P64-H03V.

## Preuves locales

- état exact : 8/8 conteneurs construits ;
- +6 petits assets : construit ;
- +20 petits conteneurs : 28/28 construits, 14 intervalles Z ;
- tests ciblés volumétriques, partition et P66 : OK ;
- suite complète : 495 tests, OK.

`fusion-validated: false`, `print-validated: false`. Aucun commit n’est créé avant
le retour de l’essai Fusion demandé par Thomas.