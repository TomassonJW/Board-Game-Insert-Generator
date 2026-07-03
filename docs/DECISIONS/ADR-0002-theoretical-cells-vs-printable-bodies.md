# ADR-0002 - Theoretical cells vs printable bodies

## Statut

Accepte.

## Contexte

Un layout peut remplir exactement un volume disponible sur le papier. Un objet imprime doit au contraire tenir compte des jeux, de la precision de l'imprimante, du filament, de la boite reelle et des interactions entre modules.

Confondre cellule de layout et corps imprime conduit a des inserts trop serres ou incoherents.

## Options

1. Utiliser les dimensions de layout comme dimensions imprimees.
2. Appliquer une reduction globale a tous les modules.
3. Separer cellule theorique et corps imprimable, puis appliquer les tolerances par face.

## Decision

Separer explicitement `Cell` et `PrintableBody`.

Une cellule reserve un espace theorique. Un corps imprimable est calcule ensuite selon les faces exposees, les voisins et les contraintes fonctionnelles.

## Consequences

Positives :

- le modele reste explicable ;
- les jeux peuvent differer selon les faces ;
- les modules composites pourront eviter les jeux internes ;
- les rapports peuvent comparer theorie et impression.

Negatives :

- implementation plus riche qu'une simple reduction globale ;
- necessite de classifier les faces ;
- les rapports doivent montrer plus d'informations.

## Alternatives refusees

La reduction globale est refusee parce qu'elle masque les cas fonctionnels : couvercles, cavites, voisins, faces libres et primitives soudees.
