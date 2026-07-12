# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055.

## Derniere mission terminee

P58 - resultat reel dans la palette Fusion.

Le coeur pur produit bgig.partition_result_view.v1 depuis le plan P57. La palette
affiche deux SVG au repere millimetrique, corps, cavites, contenus, minima,
enveloppes finales, surplus, positions, pile, supports, complements, digest et
zero corps automatique. Une solution impossible n est jamais dessinee et toute
modification rend le resultat obsolete.

Preuves : 5 tests projection, 4 tests palette resultat, 7 tests bridge, 5 tests
DOM, 87 tests Fusion historiques et syntaxe JavaScript valide. Aucun CAD,
statut fusion-validated ou print-validated n est revendique.

## Prochaine mission prete

P59 - Materialisation CAD et synchronisation de scene.

Resultat attendu : convertir exclusivement le plan P57 courant en CAD IR,
materialiser les enveloppes finales, soustraire les cavites fixes, synchroniser
la scene sans doublon, conserver les objets non-BGIG et activer generate,
regenerate, inspect, clear et export depuis la palette. Aucun filler historique.

## Releases bloquees

P60 depend de P59. P44 a P50 restent bloques jusqu a P60.

## Gate humaine active

Aucune avant P60. Le retour humain obligatoire reste le smoke final du parcours
complet dans Fusion, prepare automatiquement par Codex.

## Fin de chaque mission

Tests pertinents, git diff --check, commit atomique, integration directe dans
main, push, puis mission suivante seulement si ses dependances sont terminees.
