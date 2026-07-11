# Next Actions

Derniere mise a jour : 2026-07-11

## Politique active - Integration Git autonome

Statut : `active` pour les missions non gatees. Les missions Fusion et physiques restent soumises aux gates documentees.

## Etat courant

P31 et P32 sont `fusion-validated` : les bacs ouverts et la palette Fusion secondaire sont observes. P33 est integre : les apercus de forme et d esthetique sont disponibles dans le Studio sans effet sur les dimensions, Fusion ou l impression.

Le Studio reste la surface principale. Fusion reste la surface secondaire de materialisation, inspection et export prevue par ADR-0042.

## Gate humaine active

P34 est `waiting-human-decision` : le premier mecanisme impose un choix humain et un futur prototype imprime.

## Hors scope maintenu

- Fusion ne devient jamais source de verite du plan.
- Aucun statut `print-validated` ne sera utilise sans prototype mesure.
- Les couvercles, mecanismes, jeux physiques et validations d impression restent hors scope tant que P34 n est pas approuve.

## Prochaine action

P34-GATE : choisir le premier mecanisme. Recommandation : couvercle pose amovible V0. Repondre `P34 couvercle pose approuve` ou choisir A, C ou D dans `docs/P34_MECHANISM_GATE.md`.

## Fin de chaque mission

Appliquer direct-to-main pour tout lot non gate : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`.