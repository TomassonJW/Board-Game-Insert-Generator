# 2026-07-13 - Cadrage fonctionnel P65-M003

## Contexte

P65-M001 et P65-M002 ont stabilise les jeux X-Y/Z, leurs frontieres boite et
conteneurs, l action de materialisation persistante et les sketches de reference
caches. Le retour produit demande maintenant une lecture claire des tailles de
chaque conteneur et une estimation locale avant la gate MVP P66.

## Decision de mission

P65-M003 devient `ready` avec le contrat
`docs/P65_M003_FUNCTIONAL_CONTRACT.md`.

La palette distinguera :

1. le minimum derive courant ;
2. la demande par axe Auto/Cible/Fixe ;
3. la taille calculee par le vrai plan ;
4. le statut non calcule, a jour, perime, partiel ou impossible.

`Estimer les tailles` est une operation UX qui reutilise `solve_project`. Elle
ne constitue pas un nouvel estimateur et ne modifie ni projet, ni CAD IR
materialisee, ni scene Fusion.

## Bornes confirmees

- Fusion et palette embarquee uniquement ;
- coeur Python source de verite ;
- aucune heuristique, formule de score ou tolerance modifiee ;
- aucune cale, aucun support et aucun corps automatique ;
- aucune nouvelle forme de cavite ou reservation ;
- Compact/Detaille, sans mode avance global ;
- validation Fusion et impression non revendiquees.

## Route MVP

- P65-M003 : tailles et estimation, cible 0.1.18 ;
- P65-M004 : explications finales d Apercu, cible indicative 0.1.19 ;
- P66-M001 : preparation automatique du projet canonique et de la checklist ;
- P66 : observation humaine Fusion-only ;
- P66-Hxx uniquement si un ecart borne est observe.

P44 V0.2 reste bloque tant que P66 n est pas vert. La publication/tag demeure
une gate humaine separee apres acceptation fonctionnelle du MVP V0.1.

## Impact

Documentation et pilotage uniquement. Aucun code, schema, package ou statut de
capability runtime n est modifie. Le test d alignement Fusion-only est actualise
pour verifier P65-M003, P65-M004 et P66-M001. La suite complete compte 434 tests
verts. `fusion-retest-required` et `print-validated: false` restent applicables.
