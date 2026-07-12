# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055.

## Derniere mission terminee

P57 - solveur de partition et expansion conjointe.

Le coeur pur produit bgig.partition_plan.v1 depuis bgig.project.v1, P40 et P55.
Il place uniquement les bacs demandes et complements exacts explicites, remplit
le volume imprimable hors jeux techniques, revalide les enveloppes finales et
maintient automatic_body_count a zero. Les impossibilites indiquent une action
corrective. La palette declenche ce calcul sans logique metier JavaScript.

Preuves : 9 tests solveur, 7 tests bridge, 5 tests DOM, 87 tests Fusion
historiques, grande cardinalite 50 bacs et determinisme par digest. Aucun CAD,
statut fusion-validated ou print-validated n est revendique.

## Prochaine mission prete

P58 - Resultat premium dans la palette Fusion.

Resultat attendu : afficher le plan P57 reel, ses bacs/contenus, cavites,
enveloppes minimale/finale, surplus, positions, pile, supports, complements,
alertes, vue dessus et coupe derivees des placements. Le resultat devient
obsolete apres toute modification et aucune illustration indicative n est
presentee comme solution.

## Releases bloquees

P59 depend de P58. P44 a P50 restent bloques jusqu a P60.

## Gate humaine active

Aucune avant P60. Le retour humain obligatoire reste le smoke final du parcours
complet dans Fusion, prepare automatiquement par Codex.

## Fin de chaque mission

Tests pertinents, git diff --check, commit atomique, integration directe dans
main, push, puis mission suivante seulement si ses dependances sont terminees.
