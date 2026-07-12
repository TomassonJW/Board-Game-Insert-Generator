# ADR-0060 - Divulgation progressive dans la palette Fusion

## Statut

Acceptee le 2026-07-12 par validation humaine explicite : `GO` pour avancer
vers le MVP. P61 puis P65 portent son implementation progressive.

## Date

2026-07-12

## Cartes liees

- P60-R - Realignement produit apres revue Fusion
- P61 - Etat reactif et architecture de palette
- P65 - Conteneurs, reglages et apercu integres

## Contexte

La palette P60 est lisible mais volumineuse. Le mode avance global cache des
controles utiles, tandis que des diagnostics techniques et des codes moteur
apparaissent au premier niveau. Afficher toutes les actions et tous les champs
en permanence ne resoudrait pas le probleme de densite.

## Options

1. Conserver le mode avance global.
2. Afficher tous les champs et toutes les actions partout.
3. Utiliser une divulgation progressive locale et une barre d actions
   contextuelle persistante.

## Decision proposee

Retenir l option 3.

Le parcours devient : `Boite`, `Plateaux et livrets`, `Elements du jeu`,
`Conteneurs`, `Reglages`, `Apercu`. Le mode avance global disparait. Les listes
Elements et Conteneurs offrent une densite `Compact` par defaut et `Detaille`,
avec un seul element developpe a la fois.

La barre basse organise les actions en trois zones : verification/recalcul,
projet/scene, navigation/sauvegarde. Les actions rares sont dans un menu.
`Materialiser dans Fusion` et `Exporter les imprimables` restent primaires dans
l Apercu seulement.

Un inspect sain est silencieux au demarrage. Les erreurs utilisateur sont
locales et actionnables ; le statut de scene reste discret en bas ; le rapport
technique complet vit dans un tiroir tronque avec `Voir plus` et copie. Aucun
code enum, digest, nom de milestone ou nom de moteur n apparait au premier
niveau. Les scores sont traduits en sous-criteres expliques.

## Consequences

- Le novice garde un parcours court sans priver l expert de controle.
- Les grandes listes deviennent parcourables.
- Les composants de liste, message et barre doivent etre testes par etat.
- L information technique reste disponible pour le support sans polluer l UX.

## Alternatives refusees

- Mode avance global : il regroupe des notions sans relation et cache des
  controles pertinents.
- Huit boutons persistants : surcharge visuelle et priorites illisibles.

## Validation attendue

- Tests DOM des densites, messages, actions et absence de fuite technique.
- Observation Fusion sur petite et grande palette.
- Navigation clavier et conservation de la densite choisie.
