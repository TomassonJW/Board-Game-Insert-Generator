# P60 - Renforcement de l acceptance UX 0.1.9

## Probleme

La gate P60 historique validait deux bacs et zero complement. Elle ne prouvait
donc ni le bloc plein introduit dans la palette 0.1.9, ni une dimension finale
de bac saisie par l utilisateur.

## Scenario retenu

- Bac jetons : X final local verrouille a 80 mm ;
- Bac cartes : dimensionnement restant gere par P57 ;
- Cale pleine avant : corps solid explicite 20 x 238,8 x 63,4 mm ;
- resultat attendu : 3 corps, 1 complement, 3 cavites, 0 automatique ;
- scene attendue : 3 occurrences compactes et aucune occurrence eclatee.

Ce scenario est l unique candidat faisable retenu par l heuristique bornee pour
ces contraintes. Il reste deterministe et ne modifie pas le solveur.

## Protection des donnees locales

Le preparateur compare le projet courant au fixture. Un projet different est
sauvegarde dans bgig_project_v1.before-p60.json avant installation atomique du
fixture. Un second lancement sur le fixture ne remplace pas cette sauvegarde.

## Validation

Tests unitaires du fixture, construction CAD hors Fusion, generation planifiee
compacte, parsing PowerShell et dry-run du preparateur. La preuve visuelle dans
Fusion reste requise ; print-validated reste false.
