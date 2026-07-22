# Journal P64-L05C - Temoin certifie persistant

Date : 2026-07-22

## Contexte

Le retour humain L04V montrait qu'un plan incremental materialisable pouvait ne
plus etre retrouve depuis zero, notamment apres un changement d'effort. L05B a
livre l'acquisition de cas ; L05C devait conserver une preuve certifiee sans
faire de la scene ou du cache une source de verite.

## Decision

ADR-0078 retient un sidecar exact `bgig.certified_plan_witness.v1`, identifie par
projet normalise et jeu de frontieres P45. Il est valide fail-closed puis
recertifie dans le coeur comme incumbent. La recherche courante continue et le
certificat final commun reste obligatoire.

En Deep, le prefixe Normal historique reste sans witness ; le temoin est injecte
uniquement dans l'extension de trois lanes sous la deadline existante.

## Implementation

- producteur pur d'identite, bundle witness, validation et resume ;
- stockage local atomique par digest de compatibilite ;
- coexistence des sidecars de frontieres differentes ;
- conservation de la geometrie identique et du witness au moins aussi bien
  classe ;
- remplacement d'un sidecar corrompu apres un nouveau solve certifie ;
- recertification du candidat dans le solveur puis recherche complete ;
- transmission staged, bridge et details DOM replies.

## Validation

Tests cibles : 4 witness, 14 solveur minimal, 13 staged, 27 bridge et 38 DOM,
tous OK. Suite complete finale : 674/674 en 152,142 s. Ruff, py_compile,
compileall, JavaScript, frontiere adsk et diff-check passent.

## Limites

Aucune gate Fusion ou impression n'est revendiquee. Le manifest reste 0.1.58.
Aucun projet personnel n'est modifie ou importe. Le corpus, le replay et
l'optimisation appartiennent a L05D.
