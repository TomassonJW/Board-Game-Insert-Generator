# P64-H05 — Contrat commun `stage_stack`

Date : 2026-07-17

## Fait livré

La baseline H03R est désormais appelée par un adaptateur interne commun. Ses
plans publics restent inchangés, mais une solution complète est convertie en
candidat immuable puis certifiée avant d'être renvoyée.

## Invariants conservés

- chemin canonique, ordres structurés H03 et reprises hash H02 ;
- placements, digest, télémétrie H04, budgets et score existants ;
- cavités, parois, fonds, jeux, réservations, appuis et retrait ;
- aucun corps automatique, aucune scène ou matérialisation automatique.

## Preuves

Les références H04 sont identiques entre la baseline interne et l'adaptateur.
Les tests couvrent aussi l'immuabilité, le budget monotone et le refus d'une
fausse solution. Cette preuve est automatisée seulement ; elle ne constitue ni
une preuve Fusion ni une validation d'impression.

## Suite

P64-H06 est la seule prochaine mission : placement 3D libre greedy EP/EMS,
derrière le contrat et le validateur maintenant présents.
