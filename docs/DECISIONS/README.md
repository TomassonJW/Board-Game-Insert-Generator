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
- ADR-0024-fusion-hidden-source-helper-occurrences.md - decision remplacee apres KO
  critique P12-UI-M002V4.
- ADR-0025-fusion-initial-occurrence-as-compact-view.md - occurrence
  initiale `addNewComponent` comme vue compacte officielle.

- ADR-0026-fusion-generated-scene-root-ownership.md - occurrence racine unique taguee et suppression par `deleteMe()` pour la scene Fusion BGIG.

- [ADR-0027 - Registry Fusion BGIG et inspection read-only](ADR-0027-fusion-bgig-registry-and-inspection.md)
- [ADR-0028 - Fusion quick_asset_box input V0](ADR-0028-fusion-quick-asset-input-v0.md)
- [ADR-0029 - Count-aware asset storage sizing V0](ADR-0029-count-aware-asset-storage-sizing-v0.md)
- [ADR-0030 - Asset-fit cavity V0](ADR-0030-asset-fit-cavity-v0.md)
- [ADR-0031 - Asset-specific compartments V0](ADR-0031-asset-specific-compartments-v0.md)
- [ADR-0032 - Per-compartment access notches V0](ADR-0032-per-compartment-access-notches-v0.md)

## Regles de maintenance

- Ne reecris pas l'historique d'une ADR acceptee pour changer la decision.
- Cree une nouvelle ADR qui remplace l'ancienne si la decision evolue.
- Mets a jour cet index a chaque nouvelle ADR.
- Lie la carte backlog concernee quand c'est utile.
- Ne cree pas d'ADR pour une micro-implementation reversible sans decision
  structurante ; documente plutot dans le log de mission.

- `ADR-0033-tray-semantics-v0.md` - Semantique V0 z/count/grid/grouping pour bacs asset-first utilisables.
- ADR-0034-flat-tray-2d-packing-v0.md - Packing 2D ergonomique des piles flat tray V0.
- ADR-0035-printable-export-preprint-v0.md - Export imprimable Fusion-only et manifeste preprint V0.

- ADR-0036-ux-architecture-roadmap.md - Roadmap UX: commande Fusion dev, palette/app sous gate.
- ADR-0037-box-fill-plan-v0.md - Contrat executable, versionne et CAD-agnostic du BoxFillPlan manuel P19.

- ADR-0038-box-fill-greedy-2d-v0.md - Placement greedy 2D borne P20.
- ADR-0039-box-fill-variants-v0.md - Portefeuille de variantes deterministes P21.
- ADR-0040-local-composer-loopback-adapter.md - prototype React/Vite P23, supersede pour le MVP par ADR-0055.
- ADR-0041-local-composer-selection-cad-ir-bridge.md - Pont CAD IR de la selection locale P21 vers Fusion P28.
- ADR-0042-studio-primary-fusion-palette-secondary.md - ancienne direction Studio principal, supersedee par ADR-0055.
- ADR-0043-open-top-trays-from-p21-selection.md - Proposition de bacs ouverts depuis une selection P21 (P31-GATE).

- ADR-0044-removable-lid-contract-v0.md - proposition de couvercle pose non retenue.
- ADR-0045-sliding-lid-contract-v0.md - premier mecanisme ferme : coulissant experimental sous coupon.

- ADR-0046-additive-prism-join-for-sliding-lid-coupon.md - join rectangulaire borne pour les rails du coupon coulissant.

- ADR-0047-canonical-release-order-and-mvp-critical-path.md - ordre V0.1, V0.2, V0.3 et verrou du chemin critique MVP.

- ADR-0048-user-first-project-v1-contract.md - contrat utilisateur V0.1 et migration additive depuis le Studio P23.

- ADR-0049-derived-container-plan-before-box-solver.md - plan de bacs derive
  avant le solveur global de boite.
- ADR-0050-flat-stack-reservation-before-global-placement.md - reservation de la
  pile superieure avant le placement global.
- ADR-0051-global-volume-closure-plan-v1.md - plan de fermeture de volume global V0.1.
- ADR-0052-functional-volume-cad-materialization-v1.md - materialisation CAD fonctionnelle P42 du plan V0.1.

- ADR-0053-product-conformance-before-v01-acceptance.md - conformite produit obligatoire avant acceptance V0.1.

- ADR-0054-fixed-cavities-expandable-container-envelopes.md - cavites calibrees, enveloppes extensibles et aucun corps automatique.
- ADR-0055-fusion-only-mvp-product-surface.md - add-in Fusion 360 comme produit MVP unique ; Studio web supersede.
- ADR-0056-reactive-project-state-and-constraint-priority.md - etats acceptes source/derive/solve/materialise et de dimensions Auto/Cible/Fixe.
- ADR-0057-top-inset-flat-reservations.md - reservations superieures encastrees acceptees ; ADR-0050 supersedee pour la cible produit.
- ADR-0058-local-asset-catalog-and-storage-orientations.md - catalogue local accepte, presets personnels et orientations de rangement.
- ADR-0059-bounded-volumetric-stage-solver.md - solveur volumetrique accepte borne par etages et surplus pondere.
- ADR-0060-progressive-disclosure-fusion-palette.md - parcours Fusion compact accepte, diagnostics discrets et divulgation progressive locale.

- ADR-0061-post-mvp-sequencing-and-complement-quarantine.md - identifiants P44-P50 conserves, P67/P68/P69 cadres et complements experimentaux mis en quarantaine avant P66.
- ADR-0062-ux-foundation-before-v02-geometry.md - proposition P67 de fondation UX dans P44 avant les geometries P45 ; decision humaine encore requise.
