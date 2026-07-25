# Journal - P64-L09S-D annexes XY composites bornees

## Decision appliquee

La fermeture rectangulaire globale reste le chemin prioritaire. Lorsqu'une reservation haute rend cette partition non decoupable, le finaliseur tente un repli composite borne : partition brute complete, soustraction exacte des reservations ouvertes sur le dessus, puis decomposition en prismes XY de meme base Z rattaches a un proprietaire unique.

Les liaisons par Z seul, arete ou point sont interdites. Toute annexe doit partager une vraie face verticale X ou Y avec le coeur ou une annexe deja rattachee.

## Etat produit

Le cas plateau recent atteint une proposition composite certifiee avec residuel imprimable nul. Cette proposition reste volontairement non materialisable jusqu'a P64-L09S-E, qui doit traduire les prismes en unions CAD IR et appliquer les encoches uniquement aux corps finaux concernes.

## Validation

Les tests cibles D, le cycle etage, la non-regression C et le contrat statique Fusion passent. La suite autorisee complete, hors benchmark et holdout, passe a 817/817 avec un test SCIP natif ignore sous Python 3.10.

`print-validated=false`.
