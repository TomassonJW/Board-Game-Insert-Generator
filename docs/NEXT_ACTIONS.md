# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055.

## Derniere mission terminee

P56 - editeur complet embarque dans Fusion.

La palette unique propose les six vues Boite, Pieces, Plateaux, Bacs,
Fabrication et Resultat. Elle edite bgig.project.v1, persiste atomiquement le
projet hors du dossier d installation, importe/exporte JSON et affiche les
contrats P40/P55 renvoyes par Python. Aucun navigateur, localhost, Vite ou calcul
metier JavaScript n appartient au runtime.

Preuves : 6 tests bridge, 5 tests DOM, 87 tests Fusion existants, syntaxe
JavaScript valide, packaging autonome et add-in installe dans AppData. Le smoke
visuel P56 est prepare mais non observe a cause du blocage Windows
`apply deny-read ACLs`; le statut fusion-validated reste faux.

## Prochaine mission prete

P57 - Solveur de partition et expansion des bacs.

Resultat attendu : partitionner le volume sous la pile plate entre les seuls
bacs demandes et complements explicites, distribuer le surplus dans les
parois/fonds selon P55, conserver les jeux comme vides et expliquer toute
impossibilite. Aucun corps de remplissage automatique.

## Releases bloquees

P58 depend de P57. P44 a P50 restent bloques jusqu a P60.

## Gate humaine active

Aucune avant P60. Le retour humain obligatoire reste le smoke final du parcours
complet dans Fusion, prepare automatiquement par Codex.

## Fin de chaque mission

Tests pertinents, git diff --check, commit atomique, integration directe dans
main, push, puis mission suivante seulement si ses dependances sont terminees.
