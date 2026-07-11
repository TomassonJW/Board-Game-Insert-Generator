# P34 - Contrat de couvercle coulissant

## Decision recue

L'humain a choisi l'option C, couvercle coulissant, le 2026-07-11.

## Resultat P34-M001

Le projet transporte maintenant un contrat `bgig.mechanism.v0` pour le choix
`sliding_lid`, avec bornes, evaluation par module et refus explicites. Le
Studio le rend lisible et le sauvegarde. Aucun rail, capot, changement de plan,
operation Fusion ou promesse d'impression n'est introduit.

## Preuves

- tests unitaires du contrat et du transport Local Composer ;
- tests de contrat Studio ;
- TypeScript et build Vite ;
- digest P21 inchange par le choix du mecanisme.

## Prochaine etape

P34-M002 : materialiser un coupon CAD IR a deux pieces sous le contrat accepte,
puis preparer et demander le smoke Fusion correspondant.
