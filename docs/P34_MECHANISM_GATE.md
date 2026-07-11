# P34-GATE - Premier mecanisme de couvercle

## Declencheur

P31 a valide de vrais bacs ouverts dans Fusion. P33 a rendu forme et style visibles, sans creer de geometrie de finition. Un couvercle, une rainure, un clip ou une charniere ajoute des jeux physiques, des surfaces de frottement et des risques de casse : il serait faux de les choisir ou les annoncer sans validation humaine et sans prototype imprime.

## Etat actuel

- Bacs P31 : parois, fond et cavite ouverte ; aucun couvercle.
- Valeurs existantes : parois et fond de 1.2 mm pour le smoke ; elles ne sont pas encore calibrees par impression.
- P33 : une apparence peut suggerer une forme, mais aucune forme de mecanisme ne passe dans Fusion.
- Fusion et l export savent generer et exporter des bodies simples ; aucune geometrie de rainure, clip ou charniere n existe.
- `print-validated: false` reste obligatoire.

## Options

| Option | Ce que voit l utilisateur | Interet | Risques et cout |
| --- | --- | --- | --- |
| A - Pas de couvercle | Bac ouvert, eventuellement retenu par la boite | Le plus simple, acces immediat | Ne protege pas le contenu hors de la boite |
| B - Couvercle pose | Un capot amovible qui se pose sur le bac, sans clip | Protection et empilage, faible complexite, echec non destructif | Demande jeu lateral et hauteur disponible a mesurer |
| C - Couvercle coulissant | Un capot qui glisse dans deux rails | Aspect premium et fermeture nette | Frottement, poussiere, deformations et tolerance XY sensibles |
| D - Clip ou charniere | Fermeture solidaire du bac | Usage autonome hors boite | Flexion, fatigue, materiau et orientation d impression rendent le premier prototype risque |

## Recommandation

Retenir **B - couvercle pose amovible V0**, exclusivement comme contrat experimental puis coupon imprime.

Il donne une valeur claire sans supposer qu un clip va survivre. Il se compose de deux pieces separees : un bac et un capot, sans charniere ni verrou. Le futur contrat devra reserver la hauteur, declarer un jeu de couvercle independant des tolerances existantes, refuser les bacs trop bas et marquer tout resultat `a valider par impression reelle`.

## Ce que Codex fera apres validation

1. Ecrire l ADR acceptee et le contrat `removable_lid_v0`.
2. Ajouter les contraintes abstraites et les refus explicites, sans changer les defaults de tolerance.
3. Generer un petit coupon bac + capot dans la CAD IR, puis verifier Fusion.
4. Preparer un protocole d impression et de mesures avant toute promesse produit.

## Hors scope apres validation

- pas de clip, aimant, charniere, glissiere, vis, mousse ou quincaillerie ;
- pas de modification globale des valeurs de tolerance ;
- pas de declaration `print-validated` avant mesures reelles ;
- pas de Fusion comme source de calcul.

## Validation demandee

Reponds simplement : **`P34 couvercle pose approuve`** pour lancer ce chemin, ou indique l option A, C ou D si tu veux une autre priorite.