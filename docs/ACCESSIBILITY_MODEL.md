# Accessibility Model

## Objectif

Un insert utile doit permettre de retirer les composants et modules dans un ordre
naturel. BGIG doit modeliser cette accessibilite au lieu de seulement maximiser
la compacite.

## Etat actuel

- Les features ergonomiques de cavites sont abstraites.
- P8-M002 implemente un `removal_order` abstrait et une `access_direction` sur les placements et reservations volumetriques.
- Les rapports exposent la sequence de retrait declaree, mais ne calculent pas encore de score ergonomique.
- Les rapports n'evaluent pas encore le confort humain.

## Concepts cibles

- `RemovalOrder` : sequence attendue de retrait des modules et layers.
- `ReachZone` : zone de prise ou d'acces humain.
- `GripFeature` : encoche, relief, aide de prise ou espace libre.
- `BlockedBy` : dependance de retrait entre modules.
- `SetupRole` : composant retire pendant setup, rangement ou jeu.

## Invariants

- L'accessibilite est une propriete produit, pas seulement une geometrie.
- Une validation automatisee ne remplace pas un retour humain.
- Les aides de prise doivent rester des intentions tant qu'elles ne sont pas generees et testees.

## Prochaines missions possibles

1. `P8-M003 - Ajouter des warnings d'accessibilite simples`.
2. `P9-M001 - Relier assets plats et reservations de couches`.
3. `P9-M002 - Charger des assets JSON sans generation de modules`.

## Gates

- Validation ergonomique humaine avant de declarer une configuration confortable.
- Gate Fusion avant toute generation reelle d'encoches ou formes de grip.
