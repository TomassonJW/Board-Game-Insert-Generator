# Next Actions

Derniere mise a jour : 2026-07-11

## Politique active - Integration Git autonome

Statut : `active` pour les missions non gatees. Les missions Fusion et physiques restent soumises aux gates documentees.

## Etat courant

P31 et P32 sont `fusion-validated`. P33 rend l'apparence vivante dans le Studio. P34-M001 sauvegarde le contrat de couvercle coulissant. P34-M002 produit maintenant un coupon CAD distinct : un bac et un capot avec deux glissieres jointes, sans modifier les bacs ranges ni le plan P21.

## Gate humaine active

Le smoke Fusion P34 est pret et attend seulement une observation humaine. La validation demandee est simple : le capot doit etre une piece unique avec deux glissieres, et le rapport Fusion doit annoncer `Joined cap rails: 2` tout en gardant `Print validation: false`.

## Hors scope maintenu

- Fusion ne devient jamais source de verite du plan.
- Aucun statut `print-validated` ne sera utilise sans prototype mesure.
- Le coupon ne couvre pas encore tous les bacs de la boite.
- Clips, charnieres, aimants et changements de tolerance globale restent hors scope.

## Prochaine action

Executer le smoke prepare par `P34_SLIDING_LID_FUSION_SMOKE.md`. Retour attendu : `P34 Fusion OK` ou `P34 Fusion KO` avec le symptome observe. Apres OK Fusion, P35 preparera le coupon imprime et son protocole de mesures.

## Fin de chaque mission

Appliquer direct-to-main pour tout lot non gate : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`.