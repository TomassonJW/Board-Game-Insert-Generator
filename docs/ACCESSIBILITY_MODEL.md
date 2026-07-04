# Accessibility Model

## Objectif

Un insert utile doit permettre de retirer les composants et modules dans un ordre
naturel. BGIG doit modeliser cette accessibilite au lieu de seulement maximiser
la compacite.

## Etat actuel

- Les features ergonomiques de cavites sont abstraites.
- Aucun ordre de retrait ni score d'accessibilite n'est implemente.
- Les rapports n'evaluent pas encore l'ergonomie humaine.

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

1. `P8-M005 - Specifier removal_order dans les rapports`.
2. `P8-M006 - Ajouter des warnings d'accessibilite simples`.
3. `P8-M007 - Relier grip features et ordre de retrait`.

## Gates

- Validation ergonomique humaine avant de declarer une configuration confortable.
- Gate Fusion avant toute generation reelle d'encoches ou formes de grip.
