# ADR-0042 - Studio principal et palette Fusion secondaire

## Statut

Accepte par l objectif utilisateur du 2026-07-11.

## Date

2026-07-11

## Carte liee

- `P29-M001 - Redressement produit et plan d execution premium`

## Contexte

Le Studio local P23 a ouvert une surface de conception independante de Fusion,
mais P28 a expose directement la commande Fusion technique et un resultat de
volumes bruts. Le retour utilisateur est sans ambiguite : ni cette commande ni
ses boites de message ne constituent une experience produit acceptable.

La North Star impose que Fusion reste un adaptateur CAD/export. L objectif actif
demande explicitement une UX Studio principale, une palette Fusion secondaire,
des bacs fonctionnels et des parametres vivants de forme et d esthetique.

## Options

### Option A - Continuer a enrichir le dialogue CommandInputs Fusion

- Avantage : cout local faible.
- Inconvenient : les chemins, modes et diagnostics se melangent au parcours
  utilisateur ; la presentation reste contrainte par un formulaire technique.
- Decision : refusee comme surface produit.

### Option B - Faire de Fusion l application principale

- Avantage : scene CAD immediatement disponible.
- Inconvenient : enferme les utilisateurs dans Fusion et fragilise les tests
  hors CAD ; risque de transformer la scene en source de verite.
- Decision : refusee.

### Option C - Studio local principal, palette Fusion secondaire

- Principe : le Studio porte projet, inventaire, intentions, comparaison,
  edition et apercu vivant. Une palette HTML Fusion porte la reception d une
  selection explicite, l inspection de scene et l export.
- Avantage : parcours novice clair, controles experts progressifs, moteur pur
  unique et surface CAD contextualisee.
- Cout : bridge versionne Studio -> CAD IR -> palette, tests hors Fusion et
  smoke Fusion dedie.
- Decision : retenue.

## Decision

- Le Studio devient la surface produit de reference.
- La palette Fusion devient la surface secondaire de materialisation, inspection
  et export ; le dialogue CommandInputs existant devient un mode expert/secours.
- Une selection ne peut plus etre presentee comme un insert fini tant qu elle ne
  contient pas une geometrie de bac fonctionnel (parois, fond et logements
  applicables).
- Les diagnostics CAD sont masques par defaut et accessibles dans un panneau
  expert ou un artefact d audit.
- Les parametres visuels sont des entrees versionnees du projet. Leur langage
  visuel exact reste soumis a `P30-GATE` avant implementation.

## Consequences

### Positives

- La frontiere moteur/CAD reste intacte.
- Le parcours utilisateur peut etre beau, clair et testable sans Fusion.
- Fusion peut afficher une information concise et actionnable au lieu d un dump
  de telemetrie.

### Negatives

- Le dialogue Fusion historique doit etre maintenu temporairement pour les
  smoke tests et les users experts.
- Le premier bridge de palette demande une validation Fusion humaine dediee.

### Risques

- Une palette ne doit pas dupliquer le solveur ni le format projet.
- Les fonctions mecaniques et les valeurs esthetiques qui changent la resistance
  ou les jeux restent experimentales jusqu a validation physique.

## Suivi

- P29 fixe les jalons, preuves et gates de la trajectoire.
- P30 commence par le choix explicite du langage visuel et du premier flux.
- P31 introduit la projection vers de vrais bacs avant toute promesse Fusion.