# P64-L09S-A - preuve du calcul minimal sans support artificiel

mission: P64-L09S-A
status: implemented-and-tested
date: 2026-07-25

## Contrat obtenu

- Dimensions XYZ strictement egales aux enveloppes minimales selectionnees.
- Reservations plateau et livret post-certifiees comme prismes superieurs interdits.
- Certificat `reserved_prisms_certified`.
- Support `not_required_for_minimal_layout`.
- Encoches absentes du plan minimal et differees a la finition.
- SCIP, greedy et beam interdisent le prisme superieur sans expansion Z.

## Cas limite recent

- Corps minimal : 23,2 x 23,2 x 31,6 mm.
- Origine Z : 21,2 mm.
- Sommet minimal : 52,8 mm.
- Plan inferieur du plateau : 58,6 mm.
- `gap_below_tray_mm: 5.8`.
- Ancienne croissance vers 38,4 mm supprimee.
- Croissance artificielle 6,8 mm supprimee.

## Artefact SCIP

- Digest : `be3b02bfe9591c72b7a25367e4b55aae8b08462ba543eff9a70d552229aff54a`.
- Archive binaire inchangee : `0a718ea5884d6326d66777db0ab853a31fa981e6392b89f184342fde27d465c6`.
- Aucun package Fusion installe.

## Verifications

- Reservation : 9/9. Minimal : 15/15.
- SCIP : 17 reussis et 1 test natif ignore. Audit : 6/6.
- Cycle : 18/18. Free 3D : 21/21. Partition : 17/17. Contrat : 6/6.
- Variantes globales : 10/10. Cas contextuel : 1/1. Garde 0.1.65 : 6/6.
- `authorized_suite: 804/804`, 1 test natif SCIP ignore.
- 72 tests benchmark, holdout, tournament ou replay de corpus exclus selon le Goal.

## Limites

- Fermeture complete : C. Annexes XY : D. CAD IR et encoches : E.
- `fusion-validated=false`.
- `print-validated=false`.
