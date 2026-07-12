# 2026-07-12 - Rebase produit canonique

## Declencheur

Thomas precise que le MVP fonctionnel doit etre termine avant toute esthetique,
puis que les couvercles ne viennent qu'apres la version formes/ergonomie.

## Decision

- V0.1 : boite, pieces, groupes de bacs, plateaux/livrets, parois, jeu,
  remplissages et construction complete.
- V0.2 : arrondis, encoches et geometries ergonomiques reelles.
- V0.3 : couvercle encastrable puis coulissant interieur a trois rainures.
- P33 et P34 sont archives comme explorations prematurees.
- Le smoke P34 n'est plus une action humaine active.
- ADR-0047 verrouille le chemin critique des releases.

## Audit

Les fondations Python, BoxFillPlan, P20/P21, Studio, CAD IR, bacs P31 et palette
P32 restent utiles. Les ecarts prioritaires sont le modele `Bac cible`, la pile
plateaux/livrets, la derivation automatique des bacs, la fermeture de tous les
volumes libres et la geometrie fonctionnelle correspondante.

## Suite

P37 doit introduire le contrat projet V0.1 et sa migration compatible. Aucun
code V0.2/V0.3 ne peut redevenir prioritaire avant les gates P43/P46.
