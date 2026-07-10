# Next Actions

Derniere mise a jour : 2026-07-10

## Politique active - Integration Git autonome

Statut : `active` pour les missions non gatees. Les missions Fusion et physiques restent soumises aux gates documentees.

## Etat courant

P19 a P21 donnent les contrats et propositions moteur. P22 a P27 livrent une surface locale testable : composition, import/export, allocations, demarrage guide, preparation et explication des compromis. Fusion reste un adaptateur CAD/export futur.

## Gate humaine active

`P28-GATE - Materialiser une selection locale dans Fusion` est maintenant la seule prochaine etape utile, mais elle est bloquee par une vraie validation humaine :

- autoriser ou non un scope borne qui charge une CAD IR de selection P21 dans le pipeline Fusion existant ;
- conserver le moteur Python comme source de verite, sans recalcul Fusion ;
- accepter qu un smoke test humain Fusion soit obligatoire avant tout statut `fusion-validated` ;
- ne pas franchir la gate impression, slicer ou export imprimable automatique.

## Hors scope maintenu

- Aucun solveur global, backtracking, optimisation opaque ou IA non evaluee.
- Fusion ne devient jamais source de verite du plan.
- Aucune validation d impression, de slicer ou d ergonomie reelle n est revendiquee.

## Reprise apres validation

Si P28 est autorisee, preparer le smoke local, installer l add-in via les scripts existants, generer une CAD IR de selection et ne laisser a Thomas que les actions observables dans Fusion.
## Fin de chaque mission

Appliquer direct-to-main pour tout lot non gate : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`. Pour P28, arreter avant toute mutation Fusion jusqu a validation humaine explicite.
