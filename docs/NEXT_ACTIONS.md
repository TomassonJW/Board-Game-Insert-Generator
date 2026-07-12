# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055.

## Derniere mission terminee

P59 - materialisation CAD et synchronisation de scene.

Le coeur pur transforme le plan P57 courant en `cad_ir.v0` deterministe : un
composant par corps demande, enveloppes finales, cavites P55 fixes, complements
uniquement explicites et zero corps automatique. La palette declenche
generate/regenerate en mode compact, inspecte ou efface uniquement la scene BGIG
et exporte les imprimables sans toucher aux objets Fusion non-BGIG.

Preuves ciblees : 8 tests CAD P59, 8 tests bridge projet, 4 tests de
synchronisation entrypoint, 5 tests resultat palette, 5 tests DOM, 87 tests
Fusion historiques et syntaxes Python/JavaScript valides. Le manifeste add-in
est 0.1.6. Aucun statut `fusion-validated` ou `print-validated` n est revendique.

## Prochaine mission prete

P60 - acceptance du vrai MVP V0.1 Fusion-only.

Resultat attendu : preparer automatiquement l add-in exact du commit P59, ouvrir
un projet Fusion compatible, parcourir les six vues, calculer la partition,
materialiser la scene, verifier corps/cavites/noms/zero automatique, regenerer
sans doublon, inspecter puis exporter. La seule preuve manquante est
l observation humaine dans Fusion.

## Releases bloquees

P44 a P50 restent bloques jusqu a l acceptation humaine P60.

## Gate humaine active

P60 uniquement. Codex doit installer et verifier l add-in local, preparer les
donnees du smoke et ne fournir a Thomas que les actions restantes dans Fusion.

## Fin de chaque mission

Apres le smoke : documenter OK/KO sans extrapoler a l impression, mettre a jour
le pilotage, committer et integrer directement dans main si la gate est acceptee.