# Journal P64-V2H02 — capacité et vérité de recherche

Date : 2026-07-17

## Déclencheur

Le projet Fusion étendu à 11 conteneurs et 34 contenus retombe en absence de
candidat après un ajout pourtant visuellement plausible. Les méthodes et efforts
semblent identiques, le volume restant n'est pas exposé et la vue de dessus
montre des cavités à travers des corps supérieurs.

## Diagnostic

- la dérivation canonique place six cavités en une rangée de 273,6 mm et bloque
  avant la recherche ;
- un élagage beam exige qu'un futur corps tienne dans un seul EMS ;
- les frontières des réservations ne créent pas de points extrêmes initiaux ;
- la cavité la plus profonde interdit globalement une réservation sans tester le
  recouvrement XY ;
- les profils d'effort ne diversifient qu'une priorité ;
- le volume positif est interprété à tort comme preuve de solution.

Après correction, les 11 enveloppes sont formellement admissibles et les budgets
explorent réellement 1, 2 et 4 priorités. Le cas complet reste non certifié. Une
relaxation exacte de diagnostic hors produit conclut que les enveloppes
canoniques, origines explicites et réservations du cas ne possèdent pas de
placement valide. Aucune dépendance de diagnostic n'est ajoutée.

## Décision

Le package 0.1.53 publie une borne de capacité signée sur tous les résultats
issus du sélecteur produit,
réserve les impossibilités aux preuves formelles, conserve le statut
`no_solution_within_budget` sur le cas dense et prépare P64-V2H03 pour les
variantes internes bornées coordonnées avec P45.

L'UX de chargement est séparée en P64-U01 : elle devra être non modale, annulable
et sans vol de focus.

## Validation

Les tests automatisés, compileall, contrôle de frontière adsk, syntaxe palette,
parse PowerShell et `git diff --check` sont exigés avant intégration. La gate
Fusion P64-V2H02 porte uniquement sur capacité, vérité, budgets, vue et absence
de matérialisation automatique. `print-validated: false`.