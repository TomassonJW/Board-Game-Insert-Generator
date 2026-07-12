# P34-GATE - Premier mecanisme de couvercle

> Gate historique fermee sans suite active. Le choix C ne changeait pas la
> priorite produit ; la nouvelle specification V0.3 ne commencera qu'apres P46.

## Decision humaine recue

Le 2026-07-11, le choix C est approuve : **couvercle coulissant**.

## Etat honnete au moment de la decision

- Les bacs ouverts P31 sont observes dans Fusion ; aucune impression ne les valide encore.
- Un coulissant ajoute rails, frottement, poussiere, deformation et jeu XY.
- Les parois et le fond actuels ne sont pas recalibres par cette decision.
- `print-validated: false` reste obligatoire.

## Perimetre accepte pour P34

1. Le Studio peut sauvegarder le choix `sliding_lid` et le rendre lisible.
2. Le coeur peut verifier des dimensions minimales et refuser un module incompatible.
3. L'export peut transporter le contrat et les avertissements sans modifier le plan P21.
4. Aucun rail, capot, rainure ou operation Fusion n'est ajoute dans P34-M001.

## Contrat retenu

ADR-0045 et `SLIDING_LID_CONTRACT.md` definissent le contrat `bgig.mechanism.v0`.
Les valeurs de rail et de jeu sont experimentales, locales au mecanisme et ne
changent pas les tolerances globales.

## Etapes suivantes

1. P34-M002 : materialiser un coupon CAD IR a deux pieces, puis l'observer dans Fusion.
2. P35 : imprimer et mesurer la glisse avant toute promesse de fermeture fiable.

## Hors scope maintenu

- clips, charnieres, aimants, quincaillerie et mousse ;
- modification globale des tolerances ;
- statut `print-validated` avant mesures reelles ;
- Fusion comme source de calcul.