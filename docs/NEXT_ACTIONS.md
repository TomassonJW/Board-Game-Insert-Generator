# Next Actions

Derniere mise a jour : 2026-07-11

## Politique active - Integration Git autonome

Statut : `active` pour les missions non gatees. Les missions Fusion et physiques restent soumises aux gates documentees.

## Etat courant

P31 et P32 sont `fusion-validated`. P33 rend l'apparence vivante dans le Studio. Le choix humain P34 est recu : le premier mecanisme est le **couvercle coulissant**. P34-M001 livre son contrat experimental, son apercu Studio et son transport metadata, sans geometrie de rail ni capot.

Le Studio reste la surface principale. Fusion reste la surface secondaire de materialisation, inspection et export prevue par ADR-0042.

## Gate humaine active

Aucune gate produit n'est ouverte pour P34-M002 : le mecanisme choisi est explicite dans ADR-0045. La prochaine vraie validation humaine sera le smoke Fusion apres materialisation, puis l'impression et la mesure du coupon.

## Hors scope maintenu

- Fusion ne devient jamais source de verite du plan.
- Aucun statut `print-validated` ne sera utilise sans prototype mesure.
- P34-M001 n'a cree aucun rail, capot, rainure, clip ou charniere.

## Prochaine action

P34-M002 : generer un coupon coulissant a deux pieces dans la CAD IR, avec rails simples derives de `bgig.mechanism.v0`, puis preparer le smoke Fusion. La mission devra conserver les refus P34-M001 et ne changera ni le solveur ni les tolerances globales.

## Fin de chaque mission

Appliquer direct-to-main pour tout lot non gate : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`.