# 2026-07-12 - P61 palette Fusion reactive

## Contexte

Le GO humain accepte ADR-0056 a ADR-0060 et autorise la reprise sequentielle du
chemin V0.1 revise. P61 doit corriger l etat de palette et les diagnostics sans
anticiper P62-P65.

## Changements

- package Fusion passe en 0.1.10 ;
- digest source et lifecycle source/derive/solve/materialise fournis par Python ;
- minima recalcules apres 350 ms sans calcul metier JavaScript ;
- ancien Apercu conserve, grise et non materialisable apres edition ;
- inspect sain silencieux, rapport complet dans Details techniques ;
- mode avance global supprime au profit de details locaux ;
- parcours renomme et reordonne ;
- listes Elements/Conteneurs en densite Compact ou Detaille ;
- barre d actions persistante en trois zones.

## Verifications

- tests palette/bridge : 33 OK ;
- tests packaging P60 historiques : 3 OK ;
- tests alignement Fusion-only : 5 OK ;
- syntaxe JavaScript Node : OK ;
- suite complete : 389 tests OK.

## Limites

- aucune observation Fusion P61 ;
- aucune orientation de cartes P62 ;
- aucune reservation top-inset P63 ;
- aucun solveur multi-etages P64 ;
- aucune tolerance par defaut modifiee ;
- `print-validated: false`.

## Suivi

P62 - catalogue local d elements et orientations de rangement.
