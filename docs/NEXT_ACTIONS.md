# Next Actions

Derniere mise a jour : 2026-07-07

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici, sauf gate humaine.

## Politique active - Integration Git autonome

Statut : `active`.

Le chemin standard est `direct-to-main` : une mission doit etre testee, commitee,
integree directement dans `main`, puis poussee vers `origin/main` avant selection
d'une mission suivante. Les pull requests sont reservees aux cas de repli :
protection GitHub, review imposee, conflit, divergence non triviale, risque
structurant, authentification absente ou refus de push direct.

## Gate humaine active

Statut : `manual_validation_required`.

La gate `P11-NEXT-GATE` est validee pour un sprint P12-UI limite a l'interface Fusion, aux parametres de generation et a la regeneration par relance. `P12-M001` implemente le premier increment : bouton toolbar `Generate Board Game Insert` relancable dans `Design workspace > Utilities > Add-Ins`, commande classique conservee et fichiers texte locaux limites aux defaults/fallbacks.

Action humaine requise : smoke test Fusion `P12-M001V` avant de declarer ce lancement UI `fusion-validated` et avant de passer a une palette persistante ou a un flux de generation depuis config BGIG.

## Mission ready non gated

Aucune mission non-gated supplementaire n'est recommandee tant que le smoke test `P12-M001V` du bouton toolbar relancable n'est pas realise. La prochaine extension P12 potentielle est une palette persistante ou une regeneration plus riche, mais elle doit attendre cette validation ou un choix explicite de continuer en experimental.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

`P12-M001V - Valider manuellement le bouton toolbar Fusion relancable`.

- Capability : `C-FUSION-UI`, `C-FUSION-EXPLODED`, `C-COMPOSITE`, `C-SOLVER`,
  `C-GRID-3D`, `C-CALIBRATION` selon l'option choisie.
- Objectif : choisir explicitement la prochaine vague : UI produit plus complete,
  solveur plus automatique, modules composites, generation volumetrique plus
  avancee, export ou impression/calibration.
- Statut : `blocked` jusqu'a validation humaine.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
