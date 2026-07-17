# P64-V2H03A — Coordination des variantes internes

## Déclencheur

P64-V2H02R est fusion-validated, mais le cas dense reste non certifié. Le GO
explicite du 2026-07-18 autorise l'arbitrage P64-V2H03 / P45 avant tout runtime.

## Décision

ADR-0070 retient une frontière à deux certificats. P45 possède les sémantiques,
futures formes et certificat local. P64 possède budgets, expansion paresseuse,
sélection globale et certificat du plan complet.

La voie canonique complète reste prioritaire. Le premier runtime
multi-variantes est un fallback correctif par lanes monotones, sans produit
cartésien. Les caps numériques seront mesurés sur les fixtures avant intégration
globale.

## Portée

Le lot ajoute uniquement ADR, contrat et pilotage. Aucun code, schéma projet,
default, jeu, tolérance, valeur physique, cavité, scène ou matérialisation
automatique ne change.

## Suite

P64-V2H03B devient la seule mission `ready`. P64-V2H03C/V, P44-V et P45 restent
bloquées par leurs dépendances. `fusion-validated: false` et
`print-validated: false` pour P64-V2H03.
