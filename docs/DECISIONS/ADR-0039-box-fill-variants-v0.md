# ADR-0039 - BoxFill variants V0

## Statut

Accepted for P21 implementation.

## Decision

`box_fill_variants.v0` execute un ensemble borne de policies P20 deterministes, deduplique les layouts geometriques et expose sous-scores et provenance. Le portefeuille ne fait ni backtracking ni recherche exhaustive. Une variante bloquee ne peut pas etre recommandee.

Les profils de preference n alterent pas les sous-scores bruts ; ils selectionnent une recommandation explicable parmi les variantes valides.

## Implementation P21

Chaque policy est traduite en ordre stable de candidats tout en preservant la priorite explicite de l utilisateur. Le portefeuille est deduplique par digest de placements, puis limite a `max_variants`. Le front Pareto compare uniquement les variantes `solved`; une variante `partial` ou `blocked` n est jamais recommandee ni selectionnable.

Les sous-scores V0 restent des proxies explicites : compacite = densite des empreintes de modules dans leur enveloppe XY par layer ; espace libre = plus grande cellule libre AABB rapportee au volume de boite ; accessibilite = proxy de rotations ; printability = proportion de candidats non refuses ; simplicite = nombre de modules ; coverage = couverture declaree. Ils ne prouvent ni ergonomie ni imprimabilite physique.

Les sorties P21 sont Markdown, JSON, HTML statique et une selection portable pour metadata CAD IR. Elles ne constituent pas une palette Fusion, une app persistante ou une autorisation de materialisation Fusion.