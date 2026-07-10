# ADR-0039 - BoxFill variants V0

## Statut

Accepted for P21 implementation.

## Decision

`box_fill_variants.v0` execute un ensemble borne de policies P20 deterministes, deduplique les layouts geometriques et expose sous-scores et provenance. Le portefeuille ne fait ni backtracking ni recherche exhaustive. Une variante bloquee ne peut pas etre recommandee.

Les profils de preference n alterent pas les sous-scores bruts ; ils selectionnent une recommandation explicable parmi les variantes valides.
