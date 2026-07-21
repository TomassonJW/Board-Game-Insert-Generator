# Journal — P64-L03R-B solveur minimal multi-graines

Date : 2026-07-21

## Changement

Le cœur produit désormais un `minimal_layout` certifié sans fermer ni répartir
le volume libre. Le portefeuille combine lanes historiques, variantes locales,
ordres normalisés, graines, ancres et propagations sous caps monotones.

## Décisions appliquées

- ADR-0074 reste l'autorité ; aucune nouvelle ADR n'est nécessaire.
- L03R-B reste autonome et non branché au cycle Fusion.
- Les options ajoutées au beam sont internes et conservent exactement son
  comportement par défaut historique.
- Le résiduel est une classe volumique, pas un corps imprimable.
- Le cas dense 11 × 34 reste `no_solution_within_budget`.

## Validation

Tests spécifiques et régressions ciblées verts ; suite complète 617/617 verte.
Ruff ciblé et compilation ciblée verts. Les contrôles compileall, frontière adsk
et diff-check sont exécutés à la clôture Git.

## Suite

P64-L03R-C : CAD IR minimale/finalisée, digests exacts et remplacement sûr de
la seule scène BGIG possédée. Aucune gate humaine entre B et C.