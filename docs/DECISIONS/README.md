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

## Template ADR

Utiliser `ADR-TEMPLATE.md` pour toute nouvelle ADR. Le template impose au
minimum :

- statut ;
- date ;
- carte liee ;
- contexte ;
- options comparees ;
- decision ;
- consequences positives, negatives et risques ;
- alternatives refusees ;
- suivi.

Les options doivent etre comparees selon la simplicite, l'evolutivite, le cout
de maintenance, la securite, la performance si pertinente, le risque de dette
technique, la compatibilite MVP et la facilite de test.

## Format minimal

```markdown
# ADR-000X - Titre court

## Statut

Propose | Accepte | Remplace | Deprecie

## Date

YYYY-MM-DD

## Carte liee

- `PX-MYYY - Titre de la mission`

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

## Suivi

Tests, cartes backlog ou gates humaines a preparer.
```

## ADR existantes

- `ADR-0001-core-engine-before-fusion.md` - moteur Python pur avant Fusion 360.
- `ADR-0002-theoretical-cells-vs-printable-bodies.md` - separation cellule
  theorique / corps imprimable.
- `ADR-0003-json-first-csv-and-sheets-later.md` - JSON avant CSV/Sheets.
- `ADR-0004-docs-as-control-plane.md` - documentation comme plan de controle
  projet.
- `ADR-0005-face-role-tolerance-rules.md` - regles de tolerance par role de
  face.
- `ADR-0006-explicit-print-profiles.md` - profils d'impression explicites et
  surchargeables.
- `ADR-0007-cad-agnostic-ir.md` - representation intermediaire CAD-agnostic.
- `ADR-0008-fusion-adapter-skeleton-boundary.md` - frontiere du squelette
  d'adaptateur Fusion 360.
- `ADR-0009-fusion-sketch-extrusion-blanks.md` - generation Fusion minimale par
  esquisse et extrusion.
- `ADR-0010-abstract-cavities-before-fusion-cuts.md` - cavites abstraites avant
  coupes Fusion.
- `ADR-0011-abstract-cavity-features.md` - features ergonomiques abstraites de
  cavites.

- `ADR-0012-capability-driven-product-pilotage.md` - pilotage produit par
  capabilities, milestones, gates et validations.
- `ADR-0013-fusion-rectangular-cavity-cuts.md` - coupes Fusion rectangulaires
  simples par sketch et extrusion cut.
- `ADR-0014-fusion-simple-finger-notch-cuts.md` - encoches de doigts simples
  comme coupes rectangulaires Fusion issues de la CAD IR.

- `ADR-0015-feature-taxonomy.md` - taxonomie CAD-agnostic des aides de prise.
- `ADR-0016-volumetric-grid-contract.md` - contrat declaratif de grille
  volumetrique 3D.
- `ADR-0017-volumetric-reservation-support-contract.md` - reservations typees,
  ordre de retrait et surfaces de support abstraites.
- `ADR-0018-asset-first-schema-target.md` - schema cible asset-first documente
  avant activation du loader.
- `ADR-0019-fusion-compact-grid-placement.md` - consommation Fusion compacte des
  placements grille asset-first.
- `ADR-0020-fusion-basic-exploded-view.md` - vue eclatee Fusion basique comme
  duplication d'inspection.
- `ADR-0021-fusion-linked-module-occurrences.md` - correction P7 par composants
  physiques uniques et occurrences compactes/eclatees liees.
- `ADR-0022-fusion-command-ui-and-asset-sizing.md` - commande UI Fusion minimale
  et sizing asset-first explicite grille / asset-fit / printable.

- ADR-0023-fusion-parametric-command-and-safe-clear.md - commande Fusion
  parametrique V0, generation config vers CAD IR temporaire et nettoyage par
  attributs BGIG.
- ADR-0024-fusion-hidden-source-helper-occurrences.md - composants sources Fusion
  via occurrences helpers cachees et occurrences compactes/eclatees visibles.

## Regles de maintenance

- Ne reecris pas l'historique d'une ADR acceptee pour changer la decision.
- Cree une nouvelle ADR qui remplace l'ancienne si la decision evolue.
- Mets a jour cet index a chaque nouvelle ADR.
- Lie la carte backlog concernee quand c'est utile.
- Ne cree pas d'ADR pour une micro-implementation reversible sans decision
  structurante ; documente plutot dans le log de mission.
