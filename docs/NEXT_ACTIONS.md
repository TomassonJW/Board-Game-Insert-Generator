# Next Actions

Derniere mise a jour : 2026-07-11

## Politique active - Integration Git autonome

Statut : `active` pour les missions non gatees. Les missions Fusion et physiques restent soumises aux gates documentees.

## Etat courant

P31 est `fusion-validated` pour le smoke `mixed-box` : trois bacs ouverts issus d une selection P21 ont ete observes dans Fusion, chacun avec parois, fond et cavite top-open. Cette preuve ne valide ni l ajustement des assets, ni l impression.

Le Studio reste la surface principale. Fusion devient maintenant la surface secondaire de materialisation, inspection et export prevue par ADR-0042.

## Gate humaine active

P32 est `fusion-validated` : le smoke humain Fusion est accepte le 2026-07-11. La palette peut rejoindre `main`; P33 devient la prochaine mission autonome.

## Hors scope maintenu

- Fusion ne devient jamais source de verite du plan.
- Aucun statut `print-validated` ne sera utilise sans prototype mesure.
- Les compartiments asset-specific, formes, couvercles et mecanismes restent hors P32.

## Prochaine action

P33-M001 est implemente en apercu Studio. La prochaine etape est P34-GATE : choisir le premier mecanisme autorise et son protocole de validation physique avant code.

## Fin de chaque mission

Appliquer direct-to-main pour tout lot non gate : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`.