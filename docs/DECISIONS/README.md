# Decisions techniques

Ce dossier contient les ADR (Architecture Decision Records) du projet.

Une ADR est obligatoire pour toute decision structurante, notamment :

- format de configuration ;
- separation moteur/Fusion 360 ;
- modele de layout ;
- strategie de tolerance ;
- representation des modules composites ;
- generation geometrique ;
- ajout de dependance majeure ;
- changement d'API publique, CLI ou format de fichier.

## Format recommande

```markdown
# ADR-000X - Titre court

## Statut

Propose | Accepte | Remplace | Deprecie

## Contexte

Pourquoi la decision est necessaire.

## Options

1. Option A.
2. Option B.
3. Option C.

## Decision

Choix retenu.

## Consequences

Effets positifs, negatifs et risques.

## Alternatives refusees

Pourquoi les autres options ne sont pas retenues maintenant.
```

## ADR existantes

- `ADR-0001-core-engine-before-fusion.md` - moteur Python pur avant Fusion 360.
- `ADR-0002-theoretical-cells-vs-printable-bodies.md` - separation cellule
  theorique / corps imprimable.
- `ADR-0003-json-first-csv-and-sheets-later.md` - JSON avant CSV/Sheets.
- `ADR-0004-docs-as-control-plane.md` - documentation comme plan de controle
  projet.

## Regles de maintenance

- Ne reecris pas l'historique d'une ADR acceptee pour changer la decision.
- Cree une nouvelle ADR qui remplace l'ancienne si la decision evolue.
- Mets a jour cet index a chaque nouvelle ADR.
- Lie la carte backlog concernee quand c'est utile.
