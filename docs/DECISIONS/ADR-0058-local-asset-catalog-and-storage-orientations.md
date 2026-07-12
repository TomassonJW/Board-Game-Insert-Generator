# ADR-0058 - Catalogue local d elements et orientations de rangement

## Statut

Acceptee le 2026-07-12 par validation humaine explicite : `GO` pour avancer
vers le MVP. P62 portera son implementation.

## Date

2026-07-12

## Cartes liees

- P60-R - Realignement produit apres revue Fusion
- P62 - Catalogue d elements et orientations
- P66 - Acceptance V0.1 revisee

## Contexte

Les presets P60 accelerent la saisie, mais ne couvrent ni formats de cartes
nommes, ni sleeves, ni orientations de rangement, ni presets personnels. Une
rotation geometrique ne suffit pas : des cartes a plat, debout sur grand cote ou
debout sur petit cote n ont pas la meme enveloppe, accessibilite ou contrainte
de hauteur.

## Options

1. Garder uniquement des dimensions libres par projet.
2. Utiliser un catalogue distant ou un compte cloud.
3. Fournir un catalogue local versionne et des presets personnels exportables.

## Decision proposee

Retenir l option 3.

Le catalogue integre reste petit, local, versionne et teste. Il propose des
formats nommes, mais affiche toujours les dimensions resolues. Pour les cartes,
il distingue non sleevees et sleevees, epaisseur de paquet ou comptage, et les
orientations `a plat`, `debout grand cote`, `debout petit cote`, `automatique`.
L orientation est resolue dans le coeur avant le dimensionnement du conteneur.

Les presets personnels sont stockes hors du package remplace par les mises a
jour, sans compte ni cloud. Ils sont nommes, versionnes, importables,
exportables et copiables dans un projet. Les mesures saisies explicitement ont
priorite sur le preset.

Le terme d interface principal devient `Elements du jeu`; `Asset` reste le nom
technique interne. `Confiance de mesure` quitte le parcours normal tant qu elle
n a aucun effet moteur.

## Consequences

- La saisie devient rapide sans masquer les dimensions reelles.
- Les orientations affectent explicitement cavite, hauteur et accessibilite.
- Une migration additive du schema est necessaire.
- Le stockage local des presets doit etre atomique et testable.

## Alternatives refusees

- Catalogue cloud au MVP : dependance, compte et maintenance injustifies.
- Preset opaque : impossible a auditer et dangereux pour la precision.

## Validation attendue

- Tests de resolution preset, surcharge, sleeve et orientation.
- Import/export aller-retour d un preset personnel.
- Affichage compact et detaille des dimensions finales.
