# P39 - Derivation des bacs et logements

Date : 2026-07-12

## Decision

Un plan intermediaire pur `bgig.container_derivation.v1` est introduit entre la
saisie utilisateur et le solveur global. Il dimensionne les bacs requis sans
pretendre les avoir places dans la boite ou rendus imprimables.

## Resultat attendu

Le Studio calcule et affiche les dimensions minimales de chaque bac, les piles
necessaires et un blocage lisible lorsqu une mesure depasse la boite. Le resultat
reste une etape P39 : les plateaux, le volume residuel et la geometrie suivront.

## Limites gardees explicites

- pas de placement global ni de remplissage complet avant P41 ;
- pas de CAD, Fusion ou validation d impression ;
- enveloppes rectangulaires prudentes pour les formes non rectangulaires ;
- V0.2 et V0.3 ne sont pas activees.
