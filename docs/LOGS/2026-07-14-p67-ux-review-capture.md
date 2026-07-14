# 2026-07-14 - Capture de la revue UX post-MVP

## Contexte

Apres l acceptation Fusion P66 du package 0.1.20, Thomas a realise une revue
commentee de la palette avant l ouverture des geometries V0.2. Il identifie une
prise en main correcte pour le developpement, mais une dette de densite,
d architecture d information, de vocabulaire, de cycle projet et de stabilite
pendant la saisie.

## Changements

- Creation du rapport P67 structure : observations, explications des champs
  actuels, options, priorites, horizons futurs et decisions a rendre.
- Proposition d ADR-0062 pour placer une fondation UX bornee dans P44 avant les
  geometries P45, sans accepter cette reorientation a la place de l humain.
- Definition durable de la nomenclature P/M/V/H et de la difference entre
  roadmap, backlog, STATUS, NEXT_ACTIONS, capability et ADR.
- Preparation d un decoupage P44 atomique ; P44-M001 reste bloque par P67-V.
- Maintien explicite de la quarantaine des complements, du coeur sans adsk, de
  P69 apres P50 et de `print-validated: false`.

## Constats techniques

- La fermeture de `Placement et ordre` vient de `renderAll()` qui reconstruit
  les cartes apres chaque evenement `change` et apres les derives asynchrones.
- `Verifier` est deja lance automatiquement apres 350 ms ; `Recalculer` lance le
  solveur complet ; aucune scene Fusion n est modifiee automatiquement.
- `Sauvegarder` ecrit un vrai projet atomique, mais dans un slot courant unique ;
  le cycle de document nomme reste a construire.
- L API Fusion permet une palette HTML riche et un FileDialog avec dossier
  initial ; ces capacites peuvent rester dans l adaptateur Fusion.

## Verifications

- Lecture des contrats et ADR P54-P69 directement concernes.
- Audit en lecture seule de la palette, du bridge, du projet V1, des cartes,
  reservations, preferences solveur, persistance et tests existants.
- Consultation de la documentation officielle Autodesk et de donnees
  fabricants pour borner les hypothèses de sleeves.
- Aucun fichier runtime modifie dans cette mission.

## Impact

P67 passe de `ready` a `in-review`. Le prochain acte est humain : accepter,
corriger ou refuser ADR-0062 et les decisions D67-01 a D67-11. Aucune mission
P44, P45 ou P46 n est ouverte par ce log.

## Suivi

- P67-V - Arbitrage humain du rapport.
- En cas d acceptation, rediger le contrat P44-M001 de stabilite de saisie.
- P68 peut continuer en parallele pour des observations reelles sans modifier
  les tolerances globales.
