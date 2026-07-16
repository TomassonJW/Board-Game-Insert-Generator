# Log - P44-M007H02 mesure cartes et sleeves

Date : 2026-07-16

## Contexte

Avant la gate Fusion 0.1.38, Thomas a précisé le comportement attendu des cartes :
preset non sleevé, méthode de mesure à droite, champs inactifs masqués, deltas
sleeves dans les deux modes et surcharge Z par carte même lorsque le paquet est
mesuré par son épaisseur totale.

## Décision bornée

- le preset intégré devient `Cartes`, `sleeved: false` ;
- activer les sleeves propose 3 mm au total sur X/Y et 0,19 mm par carte sur Z ;
- en mode épaisseur paquet, la quantité estimée vaut Z / 0,31 arrondi à l’entier
  le plus proche ;
- le Z résolu ajoute quantité estimée × delta Z ;
- un Z déclaré additif sépare saisie et résultat afin d’empêcher tout cumul ;
- les anciens projets sans deltas conservent leur comportement historique ;
- aucune valeur n’est revendiquée physiquement validée.

## Frontières

Le calcul de placement, les budgets, tolérances, géométrie, CAD IR et scène
Fusion ne changent pas. Les dispositions des assets non-cartes sont inscrites
pour P45 afin qu’elles aient un effet géométrique réel. La compaction du
pilotage devient P0-M010, mission documentaire distincte.

## Validation cible

Package 0.1.39, tests automatisés, gate P44-M007H02V puis preuve humaine :

`P44-M007H02 Fusion OK 0.1.39 - commit <sha>`

Cette preuve ne vaut ni calibration physique ni validation d’impression.
