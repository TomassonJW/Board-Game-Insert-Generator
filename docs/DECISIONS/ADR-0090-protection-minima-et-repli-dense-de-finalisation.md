# ADR-0090 - Proteger les minima canoniques et ordonner le repli dense de finalisation

- Statut : accepte
- Date : 2026-07-26
- Portee : P64-L09S-V corrective, package 0.1.67
- Decision humaine : le lancement du Goal P64-L09S accepte ce perimetre correctif borne

## Contexte

La gate humaine `0.1.66` a montre deux violations. Une variante interne pouvait conserver ses cavites tout en reduisant l'enveloppe minimale canonique. Dans le cas observe, un minimum source `76 x 76 x 31.8 mm` devenait `53.6 x 76 x 31.8 mm`, soit environ 29,5 % de volume externe perdu. En parallele, la finalisation complexe quittait rapidement apres deux partitions guillotine et n'utilisait pas reellement le budget approfondi.

ADR-0089 interdit qu'une reservation fabrique un porteur et exige une fermeture complete du volume imprimable. Cette decision precise les invariants necessaires sans remplacer SCIP.

## Decision

1. L'enveloppe minimale canonique source est un plancher independant sur X, Y et Z.
2. Une variante interne peut reorganiser les cavites, mais son enveloppe vaut au moins le maximum, axe par axe, entre le minimum source et l'enveloppe serree du reagencement.
3. La certification locale et l'adaptateur global controlent tous deux cet invariant.
4. Une reutilisation incrementale impossible sans reduction bascule vers un calcul global explicite.
5. Pour un projet dense, une voie bornee construit d'abord une disposition au sol par etageres guillotine, acceptee seulement apres certification complete.
6. Cette voie est un raccourci constructif ; SCIP reste le solveur de faisabilite 3D complexe.
7. La finalisation suit l'ordre : fermeture rectangulaire globale, croissance continue vers `+Z` bornee par les plans reserves, puis annexes XY composites bornees.
8. Les prismes reserves superieurs sont soustraits du residuel imprimable.
9. Aucun succes n'est publie sans `finalized_plan` courant, recertifie et couvrant exactement une fois le volume imprimable hors vides techniques certifies.

## Consequences

- les anciennes variantes qui reduisaient le minimum canonique deviennent invalides ;
- certains scenarios incrementaux demandent un recalcul global honnete ;
- les projets denses compatibles gagnent un chemin deterministe et rapide ;
- les cas vraiment 3D conservent SCIP et le budget approfondi ;
- le package `0.1.66` reste `human-KO` et `do-not-run`.

## Alternatives refusees

- utiliser le volume des cavites comme seul minimum : le contrat externe serait viole ;
- augmenter un conteneur jusqu'a un plateau : interdit par ADR-0089 ;
- remplacer SCIP par un solveur 2D : les faisabilites 3D resteraient non couvertes ;
- annoncer un succes partiel avec residuel : la materialisation serait mensongere.

## Validation attendue

Le rejeu du projet complexe recent doit preserver tous les minima, calculer une disposition certifiee, finaliser avec un residuel nul et rester deterministe. La gate Fusion `0.1.67` doit confirmer les volumes, unions, encoches et la verite de l'UI. `print-validated=false`.
